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
import _thread
import gc
import logging
import sys

import PyQt5
import numpy as np
import pandas as pd
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QFileDialog

import List_Of_Servers as LoS
from NetworkGetPressure import NetworkGetPressure
from UI_GUI_Plot import Ui_MainWindow


class PlotWindow(QWidget, Ui_MainWindow):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        """ setup initial parameters """
        self.time_frame = 1  # default update time frame [s] for LOAD LOG data
        self.n_points = int(self.lineEdit_1.text())  # default N points to plot
        self.channel = 0  # channel number 0 or 1
        self.reload_flag = True  # flag that is used to reload data in LOAD LOG
        self.common_path = 'C:/Users/Preparation PC/Documents/Python scripts/Communication_LOG_SERVER_2020/'
        """ connect all signals """
        for i in self.buttons_dict:
            """ direct construction of lambda with argument and state of the button (not used but has to be there) """
            self.buttons_dict[i].clicked.connect(lambda state, b=i: self.load_file(b))
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
                self.port = LoS.server_list[self.server_name][1]
                self.servers_with_port = [k for k,v in LoS.server_list.items() if v[1] == self.port]  # return servers with this port
                print (self.servers_with_port)
                # TODO: provide full path from log folder
                self.load_file_name = str(self.common_path) + str(self.servers_with_port[0]) + '-log-dynamic.dat'  # takes the first server log with this port
                print(self.load_file_name)
                self.channel = int(LoS.server_list[self.server_name][4])
            else:
                self.load_file_name = QFileDialog.getOpenFileName(self, 'Open file', '', '*.dat')[0]
        except:
            print("error getting file name")

        """ Load data from the file self.load_file_name """
        try:
            with open(self.load_file_name, 'rb') as f:
                self.loaded_data = pd.read_csv(f, sep=",")
            f.close()
        except:
            self.loaded_data = []
            print("error loading file")
            pass

        """ Exctract necessary n_points from self.channel from panda frame """
        if len(self.loaded_data) != 0:
            self.data_to_display = np.array(self.loaded_data.tail(self.n_points).iloc[1:, self.channel + 1])
        else:
            self.data_to_display = np.array([])

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
        print("connecting to server ", server_name)
        self.reload_flag = False
        self.host = LoS.server_list[self.server_name][0]
        self.port = int(LoS.server_list[self.server_name][1])
        self.channel = int(LoS.server_list[self.server_name][4])
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
            self.pressure = 0.0
            pass
        """ Append the value from server to the data which we display (with shift) """
        if len(self.data_to_display) >= self.n_points:
            self.data_to_display = np.append(self.data_to_display, self.pressure)[1:]
        else:
            self.data_to_display = np.append(self.data_to_display, self.pressure)

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
        """Check the data prior plot"""
        for i in range(len(self.data_to_display)):
            try:
                self.data_to_display[i] = float(self.data_to_display[i])
            except:
                self.data_to_display[i] = 0.0
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
        except Exception as e:
            logging.exception(e)
            print(e)
        try:
            self.data_to_display = np.array([])
        except:
            pass
        try:
            self.networking.quit()
            self.networking.wait()
        except Exception as e:
            logging.exception(e)
            print (e)
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
            self.stop()
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
