#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# Copyright (C), SBS Science & Technology Co., Ltd. 
# Author: LiShaocheng

import os
import socket
import argparse
import serial
import threading
import json
import struct

lock = threading.Lock()

class ATCmdException(Exception):
    def __init__(self, msg):
        self.msg = msg

# 向 dev 串口发送一个指令 cmd ，返回值是一个 bytes 列表，按 '\r\n' 分割
def send_command(dev, cmd):
        # open and write
        try:
            ser = serial.Serial(port=dev, baudrate=115200, timeout=0.5)
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            ser.write(cmd.encode())
        except serial.SerialException as e:
            raise ATCmdException(e)
        # read 
        result = ser.readlines()
        if len(result) == 0:
            raise ATCmdException("Read timeout")
        if ser.isOpen():
            ser.close()
        # return
        return(result)

def data_pack(version, msg):
    msg_len = len(msg) 
    data = struct.pack('2B%ds'%msg_len, version, msg_len, msg)
    return data

def handle(conn):
    t_name = threading.current_thread().name
    with conn :
        # 接收并解析数据帧的头部
        head = conn.recv(2, socket.MSG_WAITALL)
        head = struct.unpack('2B',head)
        version = head[0]
        msg_len = head[1]
        # 接收并解析数据帧的载荷
        msg = conn.recv(msg_len, socket.MSG_WAITALL)
        msg = json.loads(msg.decode())
        
        lock.acquire()
        print(t_name, " : ", msg)
        try:
            result = send_command(msg['dev'], msg['cmd'])
        except ATCmdException as e:
            err = "Error:\r\n{0}".format(e)
            conn.sendall(err.encode())
        else:            
            # 将 bytes 列表中的元素合并为一个 bytes 变量
            msg = b''
            for l in result :
                msg = msg + l 
            # 打包数据帧
            data = data_pack(version, msg)            
            # 将返回的数据发给客户端
            conn.sendall(data)
            print(t_name, " : ", data, '\r\n')
        finally:            
            lock.release()    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AT command server.")
    parser.add_argument("-s", dest="sock", default="/run/atserver.socket", help="unix socket file")
    parser.add_argument("--version", action="version", version="%(prog)s 0.2")
    args = parser.parse_args()

    sock = args.sock
    if os.path.exists(sock):
        os.remove(sock)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s :
        s.bind(sock)
        s.listen()
        print("Start listen ", sock)
        while True :
            conn, _ = s.accept()            
            t = threading.Thread(target=handle, args=(conn, ))
            t.start()

    os.remove(sock)

