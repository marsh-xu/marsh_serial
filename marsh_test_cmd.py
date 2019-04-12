# -*- coding: UTF-8 -*-
import serial
import serial.tools.list_ports
import time
import struct
import threading
import platform
import winsound
import binascii
import string

command = [
    {'cmd': 'cpld_test_cmd right_earbud get_earbud_version\r\n',
     'rsp': 'SV',
     'timeout': 1,
     'delay': 0,
     'repeat': 3,
     'status': 0,
     },
    {'cmd': 'cpld_test_cmd left_earbud enter_fty\r\n',
     'rsp': 'CPLD_COMMAND_ENTER_FTY',
     'timeout': 1,
     'delay': 0,
     'repeat': 3,
     'status': 0,
     },
    {'cmd': 'cpld_test_cmd left_earbud single_work_mode\r\n',
     'rsp': 'single_pair_ok',
     'timeout': 1,
     'delay': 0,
     'repeat': 3,
     'status': 0,
     }
]

class Serial_Marsh:
    def __init__(self):
        self.serial = None
        self.badurate_list = [921600, 115200, 19200, 9600]
        self.baudrate = 115200
        self.timeout = 0.005
        self.port_name = None
        self.alive = False
        self.waitEnd = None
        self.log_file_enable = True
        self.log_file_name = 'gtk_eq_'+time.strftime("%Y%m%d%H%M%S",time.localtime(time.time()))+'.txt'
        self.fileObject = None
        self.serial = serial.Serial()
        self.pending = False
        self.color = False
        self.cmd_file_name = 'cmd.txt'
        self.cmd_switch = False
        self.current_eq_step = 0
        self.current_ok_num = 0
        self.current_ng_num = 0

        if 'Linux' == platform.system():
            self.color = True

        print "===============     Serial Marsh     =====================\r\n"

    def choose_serial_port(self):
        port_list = list(serial.tools.list_ports.comports())
        flag = False
        if len(port_list) <= 0:
            print "The Serial port can't find!"
        else:
            while True:
                print "Serial port list:"
                for i in range(0,len(port_list)):
                    print i, port_list[i]
                index = raw_input("please input port number:")
                try:
                    ser_index = int(index)
                    if ser_index >= len(port_list):
                        print("Input number is invalid")
                    else:
                        port_list_0 =list(port_list[ser_index])
                        self.port_name = port_list_0[0]
                        self.serial.port = self.port_name
                        return True
                        break
                except ValueError:
                    print("Please input valid number")
        return False

    def select_serial_baudrate(self):
        while True:
            print "serial baudrate list:"
            for i in range(0,len(self.badurate_list)):
                print i, self.badurate_list[i]
            index = raw_input("please select baudrate:")
            try:
                ser_index = int(index)
                if ser_index >= len(self.badurate_list):
                    print("Input number is invalid")
                else:
                    self.baudrate = self.badurate_list[ser_index]
                    self.serial.baudrate = self.baudrate
                    break
            except ValueError:
                print("Please input valid number")

    def select_log_file_switch(self):
        while True:
            print "Please select if enable log file function:"
            print "0  Enable"
            print "1  Disable"
            index = raw_input("please input port number:")
            try:
                ser_index = int(index)
                if ser_index >= 2:
                    print("Input number is invalid")
                else:
                    if ser_index == 0:
                        self.log_file_enable = True
                        print("Enable log file function")
                    elif ser_index == 1:
                        self.log_file_enable = False
                        print("Disable log file function")
                    break
            except ValueError:
                print("Please input valid number")

    def serial_receive(self):
        if self.log_file_enable:
            self.fileObject = open(self.log_file_name, 'w')
            print self.log_file_name
        while self.alive:
            str = self.serial.readlines()
            for line in str:
                if self.pending == True:
                    continue
                out_line = '['+self.GetNowTime()+'] '+line
                #print out_line

                if command[self.current_eq_step]['status'] == 1:
                    if command[self.current_eq_step]['rsp'] in out_line:
                        command[self.current_eq_step]['status'] = 2
                self.fileObject.write(out_line)

        self.waitEnd.set()
        self.alive = False

    def serial_send(self):
        while self.alive:
            print"============== OK num is %d, NG num is %d==============================\r\n"%(self.current_ok_num, self.current_ng_num)

            for i in range(len(command)):
                self.current_eq_step = i
                repeat_num = 0
                command[i]['status'] = 0
                while repeat_num < command[i]['repeat']:
                    wait_count = 0
                    if command[i]['status'] == 0:
                        self.serial.write(command[i]['cmd'])
                        command[i]['status'] = 1
                    while command[i]['status'] == 1:
                        wait_count += 1
                        time.sleep(0.01)
                        if wait_count >= (100 * command[i]['timeout']):
                            break
                    if command[i]['status'] == 2:
                        break
                    else:
                        repeat_num += 1
                if command[i]['status'] == 2:
                    time.sleep(command[i]['delay'])
                else:
                    self.play_ng_audio_report()
                    self.current_ng_num += 1
                    continue
            time.sleep(1)
            self.play_ok_audio_report()
            self.current_ok_num += 1

        self.waitEnd.set()
        self.alive = False

    def serial_cmd(self):
        while self.alive:
            self.pending = False
            cmd = raw_input()
            if cmd == 'q':
                break
            elif cmd == 'b':
                self.pending = True
                self.select_serial_baudrate()
            elif cmd == 'c':
                self.pending = True
                ser_cmd = raw_input()
                print "Serial CMD: "+ser_cmd
                self.serial.write(ser_cmd+'\r\n')
            elif cmd == 's':
                if self.cmd_switch:
                    self.cmd_switch = False
                else:
                    self.cmd_switch = True
            elif cmd == 'h':
                self.pending = True
                print "User guide:"
                print "    <h> help of marsh serial application"
                print "    <q> quit marsh serial application"
                print "    <c> input serial command"
                print "    <b> switch serial baudrate"
                print "    <s> start/stop run command in cmd.txt"
                raw_input()
            elif cmd == 't':
                winsound.Beep(600,500)

        self.waitEnd.set()
        self.alive = False

    def open_serial_port(self):
        self.serial.timeout = self.timeout
        self.serial.open()
        if self.serial.isOpen():
            self.waitEnd = threading.Event()
            self.alive = True
            self.thread_read = None
            self.thread_read = threading.Thread(target=self.serial_receive)
            self.thread_read.setDaemon(1)
            self.thread_read.start()
            self.thread_write = None
            self.thread_write = threading.Thread(target=self.serial_send)
            self.thread_write.setDaemon(1)
            self.thread_write.start()
            self.thread_cmd = None
            self.thread_cmd = threading.Thread(target=self.serial_cmd)
            self.thread_cmd.setDaemon(1)
            self.thread_cmd.start()
            return True
        else:
            return False

    def play_ok_audio_report(self):
        winsound.Beep(500, 500)

    def play_ng_audio_report(self):
        winsound.Beep(1000, 500)

    def start(self):
        if self.choose_serial_port():
            self.select_serial_baudrate()
            self.select_log_file_switch()
            flag = self.open_serial_port()
            return flag
        else:
            return False

    def waiting(self):
        if not self.waitEnd is None:
            self.waitEnd.wait()

    def SetStopEvent(self):
        if not self.waitEnd is None:
            self.waitEnd.set()
        self.alive = False
        self.stop()

    def stop(self):
        self.alive = False
        self.thread_read.join()
        if self.serial.isOpen():
            self.serial.close()

    def GetNowTime(self):
        return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))

if __name__=='__main__':
    ser = Serial_Marsh()
    try:
        if ser.start():
            ser.waiting()
            ser.stop()
        else:
            pass
    except Exception as se:
        print(str(se))

    del ser
    print "\r\n===============    Serial Marsh End    =====================\r\n"