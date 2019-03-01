#!/usr/bin/python3

import os
import socketserver
import argparse
import serial
import threading

lock = threading.Lock()

class ATCmdException(Exception):
    def __init__(self, msg):
        self.msg = msg

class at_server(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        conn = self.request[1]
        addr = self.client_address

        args = data.decode().split()
        dev = args[0]
        cmd = args[1]
        # send at command
        lock.acquire()
        try:
            lines = self.send_command(dev,cmd)
        except ATCmdException as e:
            msg = "error:\r\n{0}".format(e)
            conn.sendto(msg.encode(), addr)
        else:
            # bytes list to string, send result to client
            result = []
            for line in lines :
                result.append(line.decode())
            msg = ''.join(result)
            print(msg)
            conn.sendto(msg.encode(), addr)
        finally:
            lock.release()      

    def send_command(self, dev, cmd):
        cmd = cmd+"\r"
        # open and write
        try:
            ser = serial.Serial(port=dev, baudrate=115200, timeout=float(1))
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            ser.write(cmd.encode())
        except serial.SerialException as e:            
            raise ATCmdException(e)
        # read
        lines = ser.readlines()
        if len(lines) == 0:
            raise ATCmdException("Read timeout")
        if ser.isOpen():
            ser.close()
        # return
        return(lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AT command server.")
    parser.add_argument("port", type=int, default=10001, help="UDP port")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1")
    args = parser.parse_args()
    
    server = socketserver.ThreadingUDPServer(("localhost", args.port), at_server)
    print("Listenning ...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Close socket")
        server.shutdown()
        server.server_close()