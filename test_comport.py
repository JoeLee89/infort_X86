import pytest
import time
import serial
from serial.tools import list_ports
import serial.tools.list_ports
import os
import subprocess
from common_func import *

class Data:
    def __init__(self):
        self.default_speed=115200
        self.comport_name_list=[]
        self.comport_speed = [2400, 4800, 7200, 9600, 14400, 19200, 38400, 57600, 115200]
        self.comport_bit = [5, 6, 7, 8]
        self.comport_parity = [serial.PARITY_EVEN, serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE]

    def comport_list(self):
        re=list_ports.grep(r'Communications Port')
        for i in re:
            self.comport_name_list.append(i.device)
        return self.comport_name_list

    def set_data_length(self,length,size=16):
        data_array=[]
        bytes_5 = bytes(bytearray(range(32)))  # 0~31
        bytes_6 = bytes(bytearray(range(64)))  # 0~63
        bytes_7 = bytes(bytearray(range(128)))  # 0~127
        bytes_8 = bytes(bytearray(range(256)))  # 0~255
        if length == 5:
            data_array=bytes_5

        elif length == 6:
            data_array = bytes_6

        elif length == 7:
            data_array = bytes_7

        elif length == 8:
            data_array = bytes_8

        for i in range(0,len(data_array),size):
            yield data_array[i:i+size]


class Test_Loopback:
    def teardown_class(self):
        print('save log to file to recognize the class has been tested before')

    def setup_method(self):
        self.s=serial.Serial()
        self.verificationErrors=[]
        self.timeout=0
        self.data=Data()
        self.comportlist=self.data.comport_list()

    def teardown_method(self):
        self.verificationErrors = []
        for aa in self.comportlist:
            self.s.port = aa
            # print(self.s.is_open)
            self.s.close()

    def read_write(self,datasize):
        if not self.s.is_open:
            self.s.open()
        for block in self.data.set_data_length(self.s.bytesize):
            print(" ")
            print("COM port setting= " + str(self.s))
            print('Sending Data: ' + str(block))

            length = len(block)
            self.s.write(block)
            # there might be a small delay until the character is ready (especially on win32)
            time.sleep(0.05)
            yield [block,self.s.read(length)]
            # assert self.s.read(length) == block

    def test_read_empty(self):
        time.sleep(0.05)
        for ports in self.comportlist:
            self.s.port=ports
            self.s.timeout=self.timeout
            if not self.s.is_open:
                self.s.open()

                # print(self.s)

            assert self.s.read(1)== b''
            print('\n PASS: %s: Buffer checking should be empty' % ports)

    def test_speed(self):
        for ports in self.comportlist:
            for speed in self.data.comport_speed:
                self.s.port = ports
                self.s.baudrate = speed
                self.s.timeout=self.timeout
                print('port=',ports)
                re=self.read_write(self.s.bytesize)
                for write,read in re:
                    assert write == read , "Confirm if write = read data, and read=%s , write=%s" % (write,read)


    def test_bit(self):
        for ports in self.comportlist:
            for bit in self.data.comport_bit:
                self.s.baudrate=self.data.default_speed
                self.s.port = ports
                self.s.bytesize = bit
                self.s.timeout=self.timeout
                print('port=',ports)
                re = self.read_write(bit)
                for write, read in re:
                    assert write == read, "Confirm if write = read data, and read=%s , write=%s" % (write, read)


    def test_parity(self):
        for ports in self.comportlist:
            for parity in self.data.comport_parity:
                self.s.baudrate=self.data.default_speed
                self.s.port = ports
                self.s.parity = parity
                self.s.timeout=self.timeout
                print('port=',ports)
                re = self.read_write(self.s.bytesize)
                for write, read in re:
                    assert write == read, "Confirm if write = read data, and read=%s , write=%s" % (write, read)


    @pytest.mark.parametrize("value", [True, False])
    def test_RTS(self,value):
        for ports in self.comportlist:
            self.s.baudrate = self.data.default_speed
            self.s.port=ports
            self.s.timeout = self.timeout
            if not self.s.is_open:
                self.s.open()
            self.s.rts=value

            assert self.s.cts == self.s.rts, "Confirm if RTS = CTS status, and RTS=%s , CTS=%s" % (self.s.rts, self.s.cts)
            print(f'PASS: {ports} RTS/CTS status matchs, while set RTS->{value}')

    @pytest.mark.parametrize("value", [True, False])
    def test_DTR(self, value,request):
        data = ActManage(item_total_path(), request.node.name)
        data.bios_set([[None, None, 'default']]).act()
        for ports in self.comportlist:
            self.s.baudrate = self.data.default_speed
            self.s.port = ports
            self.s.timeout = self.timeout
            if not self.s.is_open:
                self.s.open()
            self.s.dtr = value

            assert self.s.dtr == self.s.dsr, "Confirm if DTR = DSR = RI status, and DTR=%s , DSR=%s , RI=%s" % (self.s.dtr, self.s.dsr, self.s.ri)
            assert self.s.dtr == self.s.ri
            print(f'PASS: {ports} DTR/DSR/RI status matchs, while set DTR->{value}')

    def test_ACPI_S3(self):
        process=subprocess.Popen(r'.\tool\sleeper\sleeper.exe -S0010 -R 30 -N 1 -E',shell=True)
        process.wait()
        for ports in self.comportlist:
            self.s.baudrate = self.data.default_speed
            self.s.port = ports
            self.s.timeout = self.timeout
            re = self.read_write(self.s.bytesize)
            for write, read in re:
                assert write == read, "Confirm if write = read data, and read=%s , write=%s" % (write, read)

    def test_ACPI_S4(self):
        process=subprocess.Popen(r'.\tool\sleeper\sleeper.exe -S0001 -R 30 -N 1 -E',shell=True)
        process.wait()
        for ports in self.comportlist:
            self.s.baudrate = self.data.default_speed
            self.s.port = ports
            self.s.timeout = self.timeout
            re = self.read_write(self.s.bytesize)
            for write, read in re:
                assert write == read, "Confirm if write = read data, and read=%s , write=%s" % (write, read)

    def test_disable_com1(self,request):
        data = ActManage(item_total_path(), request.node.name)
        data.bios_set([['Serial Port', 'value' , '0','Token	=62']]).act()
        assert 1==1


    # def test_enable_com1(self):


