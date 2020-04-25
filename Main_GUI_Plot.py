# -*- coding: utf-8 -*-
"""
Plotting GUI for pressure, temperature or any other logged data in *.dat format.
Dedicated buttons to plot AC, PC, DC, LL, He and T from the ARPES lab and
a general LOAD LOG button for other data. 
Dedicated buttons read the log file only once when clicked and then connect
to a corresponding server to add the data to the plot.
General LOAD LOG button read the corresponding log file every self.time_frame
seconds.

Updated: 21 Feb 2020 Separate server for DC added
Updated: 12 Feb 2020
Created on Wed Jun 26 16:39:27 2019

@author: Victor Rogalev
"""
import sys, gc

import PyQt5 as PyQt5
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QFileDialog
import numpy as np
from UI_GUI_Plot import Ui_MainWindow
import pandas as pd
from NetworkGetPressure import NetworkGetPressure
import List_Of_Servers as LoS


class PlotWindow(QWidget, Ui_MainWindow):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        """ setup initial parameters """
        self.time_frame = 1  # default update time frame [s] for LOAD LOG data
        self.n_points = int(self.lineEdit_1.text())  # default N points to plot
        self.channel = 0  # channel number 0 or 1
        self.reload_flag = True  # flag that is used to reload data in LOAD LOG
        self.channels_list = []  # TODO:
        self.common_path = 'C:/Users/Preparation PC/Documents/Python scripts/Communication_LOG_SERVER/'
        self.server_dictionary = {"AC": ['132.187.37.41', 63202, 0, self.common_path + 'Analysis-Log-Dynamic.dat'],
                                  "DC": ['132.187.37.41', 63206, 1, self.common_path + 'DC-Log-Dynamic.dat'],
                                  "PC": ['132.187.37.41', 63200, 1, self.common_path + 'Preparation-Log-Dynamic.dat'],
                                  "He": ['132.187.37.41', 63201, 1, self.common_path + 'LL_He-Log-Dynamic.dat'],
                                  "LL": ['132.187.37.41', 63201, 0, self.common_path + 'LL_He-Log-Dynamic.dat'],
                                  "TA": ['132.187.37.41', 63205, 0, self.common_path + 'Lakeshore331-Log-Dynamic.dat']}

        """ connect all signals """
        for i in LoS.server_list.keys():
            self.button()
            pass

        # self.button_AC.clicked.connect(lambda: self.load_file("AC"))
        # self.button_DC.clicked.connect(lambda: self.load_file("DC"))
        # self.button_PC.clicked.connect(lambda: self.load_file("PC"))
        # self.button_He.clicked.connect(lambda: self.load_file("He"))
        # self.button_LL.clicked.connect(lambda: self.load_file("LL"))
        # self.button_TA.clicked.connect(lambda: self.load_file("TA"))
        self.lineEdit_1.returnPressed.connect(lambda: self.change_n_points(self.lineEdit_1.text()))
        self.lineEdit_2.returnPressed.connect(lambda: self.change_channel(self.lineEdit_2.text()))
        self.load_button.clicked.connect(lambda: self.load_file())
        """ create a timer for updating plot (only for Load LOG button) """
        self.timer_update = QTimer(self)
        self.timer_update.timeout.connect(self.update_plot)

    def load_file(self, *server_name):
        """ 
        Read values from saved log file into a local panda frame.
        In case *sever_name is given - starts the server client and does not load
        log file anymore, instead adds new values from the server to the displayed
        data. If there is no *server_name then it shows the open file dialog. 
        
        """
        self.stop()  # stop all running timers/server_clients

        """ Get the file name: either from servers dict or from user dialog"""
        try:
            if server_name:
                self.server_name = server_name[0]
                print(self.server_name)
                self.load_file_name = self.server_dictionary[self.server_name][3]
                self.channel = int(self.server_dictionary[self.server_name][2])
            else:
                self.load_file_name = QFileDialog.getOpenFileName(self, 'Open file', '', '*.dat')[0]
        except:
            print("error getting file name")

        """ Load data from the file self.load_file_name """
        try:
            with open(self.load_file_name, 'rb') as f:
                self.loaded_data = pd.read_csv(f, sep=",")
            #            self.channels_list = list(self.loaded_data) # should return column names!
            f.close()
        except:
            print("error loading file")
            pass

        """ Exctract necessary n_points from self.channel from panda frame """
        self.data_to_display = np.array(self.loaded_data.tail(self.n_points).iloc[1:, self.channel + 1])

        """ Start the server client or run the timer to reload data from log file """
        if server_name:
            print(f"starting smart {self.server_name} watch")
            self.start_network_client(self.server_name)
        else:
            print("starting standard log watch")
            self.start_reload_log_loop()

    def start_network_client(self, server_name: str):
        """ 
        Starts the separate thread with server client NetworkGetPressure
        to obtain pressure/temp values from the corresponding server.
        Server_dictionary is used to obtain connection parameters.
        """
        print(server_name)
        self.reload_flag = False
        self.host = self.server_dictionary[server_name][0]
        self.port = int(self.server_dictionary[server_name][1])
        self.channel = int(self.server_dictionary[server_name][2])
        self.networking = NetworkGetPressure(self.host, self.port)  # thread
        self.networking.new_value_trigger.connect(self.update_data_to_display)
        self.networking.start()  # start this thread to get pressure
        gc.collect()

    def update_data_to_display(self, pressure):
        """ Update data array when a new value comes in the networking thread"""
        try:
            self.pressure_preliminary = float(pressure.split(',')[self.channel])
            """ If we are getting temperature from the Lakeshore"""
            if self.port == 63205:
                if (self.pressure_preliminary < 500):
                    self.pressure = self.pressure_preliminary
            else:
                """ If we are getting pressure values"""
                if (self.pressure_preliminary > 0) and (self.pressure_preliminary < 0.05):
                    self.pressure = self.pressure_preliminary
                    print(self.pressure)
                else:
                    pass
        except:
            pass
        """ Append the value from server to the data which we display (with shift) """
        self.data_to_display = np.append(self.data_to_display, self.pressure)[1:]
        self.update_plot()  # call the plot update function

    def update_plot(self):
        """ 
        Updates the plot. Depending on the reload_flag it can re-load data 
        from the LOG file (in case LOAD LOG button is used) or just updates 
        the plot after the new value from the server was appended to the data 
        array.
        
        """
        if self.reload_flag:
            try:
                with open(self.load_file_name, 'rb') as f:
                    self.loaded_data = pd.read_csv(f, sep=",")
                f.close()
                self.data_to_display = np.array(self.loaded_data.tail(self.n_points).iloc[1:, self.channel + 1])
                print("reloaded")
            except:
                print("error loading data")
                pass
        """ Update plot """
        try:
            self.plot_T.clear()
            self.plot_T.plot(np.arange(0, len(self.data_to_display)) * self.time_frame,
                             self.data_to_display,
                             symbolSize=5, symbolBrush="r", symbol='o')
        except:
            print("error in plot")
            pass

    def change_n_points(self, new_n_points: int):
        """ Change number of points in the data array to plot """
        if (int(new_n_points) > 0) and (int(new_n_points) < 360 * 24):
            self.n_points = int(new_n_points)
            print("changed number of points to ", self.n_points)
        else:
            print("invalid number of points")
            pass
        """ Reload once from the log file in case reading from server """
        if not self.reload_flag:
            self.load_file(str(self.server_name))

    def change_channel(self, new_channel: int):
        """ Works only for LOAD LOG case """
        if (int(new_channel) == 0) or (int(new_channel) == 1):
            self.channel = int(new_channel)
            print("changed channel to ", self.channel)
        #            self.label_3.setText(str(self.channels_list[self.channel+1]))
        else:
            print("invalid channel")
            pass

    def start_reload_log_loop(self):
        """ Works only for LOAD LOG case """
        #        self.label_3.setText(str(self.channels_list[self.channel+1]))
        self.plot_T.clear()
        self.reload_flag = True
        self.timer_update.start(self.time_frame * 1000)

    def stop(self):
        try:
            self.timer_update.stop()
        except:
            pass
        try:
            self.data_to_display = []
        except:
            pass
        try:
            self.networking.close()
        except:
            pass

    def __del__(self):
        self.stop()
        try:
            self.timer_update.deleteLater()
        except:
            pass

    def closeEvent(self, event):
        try:
            self.__del__()
        except:
            print("error killing timer")
        event.accept()


def main():
    app = QApplication(sys.argv)
    MainWindow = PlotWindow()
    MainWindow.setWindowTitle("Display Data PyQtGraph")
    MainWindow.resize(1000, 500)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
