import serial
import serial.tools.list_ports
import time
import struct
import threading

class Serial_Marsh:
    def __init__(self):
        self.serial = None
        self.baudrate = 115200
        self.timeout = 0.005
        self.port_name = None
        self.alive = False
        self.waitEnd = None
        self.log_file_enable = True
        self.log_file_name = 'marsh_log_'+time.strftime("%Y%m%d%H%M%S",time.localtime(time.time()))+'.txt'
        self.fileObject = None

        print "\033[1;32;40m \r\n===============     Serial Marsh     =====================\r\n"

    def choose_serial_port(self):
        port_list = list(serial.tools.list_ports.comports())
        flag = False
        if len(port_list) <= 0:
            print "\033[1;31;40m The Serial port can't find!"
        else:
            while True:
                print "\033[1;32;40m Serial port list:"
                for i in range(0,len(port_list)):
                    print "\033[1;37;40m"
                    print i, port_list[i]
                index = raw_input("\033[1;32;40m please input port number:")
                try:
                    ser_index = int(index)
                    if ser_index >= len(port_list):
                        print("\033[1;31;40m Input number is invalid")
                    else:
                        port_list_0 =list(port_list[ser_index])
                        self.port_name = port_list_0[0]
                        break
                except ValueError:
                    print("\033[1;31;40m Please input valid number")

    def select_log_file_switch(self):
        while True:
            print "\033[1;32;40m Please select if enable log file function:"
            print "\033[1;37;40m0  Enable"
            print "\033[1;37;40m1  Disable"
            index = raw_input("\033[1;32;40m please input port number:")
            try:
                ser_index = int(index)
                if ser_index >= 2:
                    print("\033[1;31;40m Input number is invalid")
                else:
                    if ser_index == 0:
                        self.log_file_enable = True
                        print("\033[1;32;40m Enable log file function")
                    elif ser_index == 1:
                        self.log_file_enable = False
                        print("\033[1;32;40m Disable log file function")
                    break
            except ValueError:
                print("\033[1;31;40m Please input valid number")

    def serial_receive(self):
        print "\033[1;32;40m \r\n===============Serial Start Reveive=====================\r\n"

        if self.log_file_enable:
            self.fileObject = open(self.log_file_name, 'w')
            print self.log_file_name
        while self.alive:
            str = self.serial.readlines()
            for line in str:
                print "\033[1;37;40m",
                out_line = '['+self.GetNowTime()+'] '+line
                print out_line

                if self.log_file_enable:
                    self.fileObject.write(out_line)

        self.waitEnd.set()
        self.alive = False

    def serial_send(self):
        print "\033[1;32;40m \r\n===============Serial Start Send=====================\r\n"
        while self.alive:
            cmd = 'cpld_test_cmd left_earbud get_earbud_version\r\n'
            #self.serial.write(cmd)
            time.sleep(1)

        self.waitEnd.set()
        self.alive = False

    def serial_cmd(self):
        print "\033[1;32;40m \r\n===============Serial Start Cmd=====================\r\n"
        while self.alive:
            cmd = raw_input()
            if cmd == 'q':
                break

        self.waitEnd.set()
        self.alive = False

    def open_serial_port(self):
        self.serial = serial.Serial()
        self.serial.port = self.port_name
        self.serial.baudrate = self.baudrate
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
        self.choose_serial_port()
        self.select_log_file_switch()
        flag = self.open_serial_port()
        return flag

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
    print "\033[1;32;40m \r\n===============    Serial Marsh End    =====================\r\n"
