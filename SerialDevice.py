import serial
import threading
import time
import CommandParser
from collections import OrderedDict
import datetime

class Device():
    def __init__(self, portName = 'COM1', timeout = 2):
        #initialize serial port
        self.ComPort = serial.Serial()
        self.ComPort.baudrate = 115200
        self.ComPort.xonxoff = 0
        self.ComPort.port = portName
        self.ComPort.timeout = timeout
        
        #list of commands to transmit
        self.outgoing_command_list = []

        self.thread_send_receive = threading.Thread(target = self.port_send_and_receive)
        self.command_parser = CommandParser.Parser()
    
    def flush_buffer(self):
        self.ComPort.flushInput()    
    
    def cmd_transmit(self, command):
        self.outgoing_command_list.append(command)
        
    def port_send_and_receive(self):
        while self.ComPort.isOpen():
            #send
            if len(self.outgoing_command_list) > 0:
                print("Tx:", self.outgoing_command_list[0])
                self.ComPort.write(self.outgoing_command_list[0])
                del self.outgoing_command_list[0]
            
            #receive
            self.port_receive()
            
            #let other threads run
            time.sleep(.1)
            
    def port_receive(self):
        if self.ComPort.inWaiting() > 0:
            data = list(self.ComPort.read(self.ComPort.inWaiting()))
            print("Rx:", data)
            self.command_parser.add_bytes(data)
            
    def send_command(self, data):
        data = [0x44, len(data)] + list(data)
        self.outgoing_command_list.append(data)
        
    def command_start(self):
        self.send_command([0x01])
        
    def command_stop(self):
        self.send_command([0x02])
        
    def start(self):
        self.ComPort.open()
        self.thread_send_receive.start()
        
    def stop(self):
        #self.command_stop()
        time.sleep(1)
        self.ComPort.close()
        #wait for thread to end
        self.thread_send_receive.join(2)
        print("Serial Device Stopped")
        
    def parse_sequence_number(self, received_data):
        return int.from_bytes(received_data[3:7], 'big')
        
    def parse_data(self, received_data):
        return OrderedDict([('computer_time', str(datetime.datetime.now())),
                            ('packet_id', int.from_bytes(received_data[3:7], 'big')),
                            ('signal_quality', int.from_bytes(received_data[7:9], 'big'))])
        

