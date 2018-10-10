import serial
import serial.tools.list_ports
import time
import struct
import threading
import platform

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
        self.log_file_name = 'marsh_log_'+time.strftime("%Y%m%d%H%M%S",time.localtime(time.time()))+'.txt'
        self.fileObject = None
        self.serial = serial.Serial()
        self.pending = False
        self.color = False
        self.cmd_file_name = 'cmd.txt'
        self.cmd_switch = False

        if 'Linux' == platform.system():
            self.color = True

        if self.color:
            print "\033[1;32;40m"
        print "===============     Serial Marsh     =====================\r\n"

    def choose_serial_port(self):
        port_list = list(serial.tools.list_ports.comports())
        flag = False
        if len(port_list) <= 0:
            if self.color:
                print "\033[1;31;40m"
            print "The Serial port can't find!"
        else:
            while True:
                if self.color:
                    print "\033[1;32;40m"
                print "Serial port list:"
                for i in range(0,len(port_list)):
                    if self.color:
                        print "\033[1;37;40m"
                    print i, port_list[i]
                if self.color:
                    print "\033[1;32;40m"
                index = raw_input("please input port number:")
                try:
                    ser_index = int(index)
                    if ser_index >= len(port_list):
                        if self.color:
                            print("\033[1;31;40m")
                        print("Input number is invalid")
                    else:
                        port_list_0 =list(port_list[ser_index])
                        self.port_name = port_list_0[0]
                        self.serial.port = self.port_name
                        return True
                        break
                except ValueError:
                    if self.color:
                        print "\033[1;31;40m"
                    print("Please input valid number")
        return False

    def select_serial_baudrate(self):
        while True:
            if self.color:
                print "\033[1;32;40m"
            print "serial baudrate list:"
            for i in range(0,len(self.badurate_list)):
                if self.color:
                    print "\033[1;37;40m"
                print i, self.badurate_list[i]
            if self.color:
                print "\033[1;32;40m"
            index = raw_input("please select baudrate:")
            try:
                ser_index = int(index)
                if ser_index >= len(self.badurate_list):
                    if self.color:
                        print "\033[1;31;40m"
                    print("Input number is invalid")
                else:
                    self.baudrate = self.badurate_list[ser_index]
                    self.serial.baudrate = self.baudrate
                    break
            except ValueError:
                if self.color:
                    print "\033[1;31;40m"
                print("Please input valid number")

    def select_log_file_switch(self):
        while True:
            if self.color:
                print "\033[1;32;40m"
            print "Please select if enable log file function:"
            if self.color:
                print "\033[1;37;40m"
            print "0  Enable"
            print "1  Disable"
            if self.color:
                print "\033[1;32;40m"
            index = raw_input("please input port number:")
            try:
                ser_index = int(index)
                if ser_index >= 2:
                    if self.color:
                        print "\033[1;31;40m"
                    print("Input number is invalid")
                else:
                    if self.color:
                        print "\033[1;32;40m"
                    if ser_index == 0:
                        self.log_file_enable = True
                        print("Enable log file function")
                    elif ser_index == 1:
                        self.log_file_enable = False
                        print("Disable log file function")
                    break
            except ValueError:
                if self.color:
                    print "\033[1;31;40m"
                print("Please input valid number")

    def serial_receive(self):
        if self.color:
            print "\033[1;32;40m"
        print "\r\n===============Serial Start Reveive=====================\r\n"

        if self.log_file_enable:
            self.fileObject = open(self.log_file_name, 'w')
            print self.log_file_name
        while self.alive:
            str = self.serial.readlines()
            for line in str:
                if self.pending == True:
                    continue
                if self.color:
                    print "\033[1;37;40m",
                out_line = '['+self.GetNowTime()+'] '+line
                print out_line

                if self.log_file_enable:
                    self.fileObject.write(out_line)

        self.waitEnd.set()
        self.alive = False

    def serial_send(self):
        if self.color:
            print "\033[1;32;40m",
        print "\r\n===============Serial Start Send=====================\r\n"
        while self.alive:
            cmd = file(self.cmd_file_name,"r+")
            cmd = cmd.read()
            cmd=cmd.split("\n")
            for cmd_s in cmd:
                if self.cmd_switch:
                    self.serial.write(cmd_s)
                    time.sleep(1)
            time.sleep(2)

        self.waitEnd.set()
        self.alive = False

    def serial_cmd(self):
        if self.color:
            print "\033[1;32;40m",
        print "\r\n===============Serial Start Cmd=====================\r\n"
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
                if self.color:
                    print "\033[1;32;40m",
                print "Serial CMD: "+ser_cmd
                self.serial.write(ser_cmd+'\r\n')
            elif cmd == 's':
                if self.cmd_switch:
                    self.cmd_switch = False
                else:
                    self.cmd_switch = True
            elif cmd == 'h':
                self.pending = True
                if self.color:
                    print "\033[1;32;40m",
                print "User guide:"
                print "    <h> help of marsh serial application"
                print "    <q> quit marsh serial application"
                print "    <c> input serial command"
                print "    <b> switch serial baudrate"
                print "    <s> start/stop run command in cmd.txt"
                raw_input()

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
