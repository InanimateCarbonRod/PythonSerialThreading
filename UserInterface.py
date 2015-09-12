import SerialDevice
import time
import threading
from PySide import QtGui, QtCore
import serial.tools.list_ports
import sys
from functools import partial

class ProgramLayout(QtGui.QWidget):
    def __init__(self):
        super(ProgramLayout, self).__init__()
        self.initUI()
        
    def initUI(self):
        self.running = False

        self.setWindowTitle('Test Software')
        grid = QtGui.QGridLayout()
        
        #port selection
        grid.addWidget(QtGui.QLabel('Port'), 10, 0)
        
        self.cboPort = QtGui.QComboBox()
        self.cboPort.addItems([column[0] for column in self.com_port_list()])
        grid.addWidget(self.cboPort, 10, 1)
        
        
        #start button
        self.btnPortConnect = QtGui.QPushButton('Start')
        self.btnPortConnect.clicked.connect(partial(self.port_open_close, self.btnPortConnect))
        grid.addWidget(self.btnPortConnect, 10, 2)
        
        
        self.setLayout(grid)
        self.show()
    
    #if the window close button is pressed
    def closeEvent(self, event):
        if (self.running):
            self.running = False
            self.serial_device.stop()
            time.sleep(1)
            
            print("ending command thread")
            self.thread_process_commands.join(2)


    def com_port_list(self):
        #get a list of COM ports and sort it 
        serial_port_list = list(serial.tools.list_ports.comports())
        serial_port_list.sort(key=lambda portname: int(portname[0][3:5]))

        return serial_port_list
    
    def port_open_close(self, button):
        if (button.text() == "Start"):
            self.thread_process_commands = threading.Thread(target = self.process_commands)
            self.serial_device = SerialDevice.Device(self.cboPort.currentText())
            
            self.serial_device.start()

            button.setText("Stop")
            self.running = True
            self.thread_process_commands.start()
            
        elif (button.text() == "Stop"):
            self.stop()
            self.thread_process_commands.join(2)
    
    def stop(self):
            self.running = False
            self.serial_device.stop()
            time.sleep(1)

            print("ending data collection thread")            
            self.btnPortConnect.setText("Start")
    

    def process_commands(self):
        while self.running:
            #check for responses
            received_data = self.serial_device.command_parser.pop()
            
            #parse commands if there was one received
            if received_data != None:
                raw_bytes = bytes(received_data)
                if raw_bytes[2] == 0xAA: #some type of command
                    pass #do something useful here
                    
                elif raw_bytes[2] == 0xA1: #some other type of command
                    pass
            
            print("Count is ", self.serial_device.command_parser.count())
            
            #if there are no pending commands, request new data from the serial device
            if self.serial_device.command_parser.count() == 0:
            #generate a request for new data
                self.serial_device.command_get_specific_data(self.sequence_number)
                self.sequence_number += 1
                
                #let threads run if there are no more commands
                time.sleep(.1)

def main():
    app = QtGui.QApplication(sys.argv)
    window = ProgramLayout()
    window.setAttribute(QtCore.Qt.WA_DeleteOnClose, 1)
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
    