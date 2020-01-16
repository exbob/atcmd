#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# Copyright (C), SBS Science & Technology Co., Ltd. 
# Author: LiShaocheng

import os
import socket
import argparse
import json
import struct

def data_pack(dev, cmd):
    # 协议帧的载荷是 json 格式，转换为 bytes 类型
    msg=json.dumps({'dev':dev, 'cmd':cmd+'\r'}).encode()
    # 协议帧的头部
    version = 1 # 版本号，占一个字节
    msg_len = len(msg) # 载荷的长度，单位是字节，占一个字节，
    # 把数据帧转换为 bytes 类型
    data = struct.pack('2B%ds'%msg_len, version, msg_len, msg)
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AT command client.")
    parser.add_argument("-s", dest="sock", default="/run/atserver.socket", help="unix socket file")
    parser.add_argument("dev", default="/dev/ttyUSB2", help="serial port")
    parser.add_argument("-c", dest="cmd", default="at", help="command")
    parser.add_argument("--version", action="version", version="%(prog)s 0.2")
    args = parser.parse_args()

    sock = args.sock
    data = data_pack(args.dev, args.cmd)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s :
        try :
            s.connect(sock)
            s.sendall(data)
            # 接收并解析返回的数据帧头部
            head = s.recv(2, socket.MSG_WAITALL)
            head = struct.unpack('2B',head)
            version = head[0]
            msg_len = head[1]
            # 接收数据帧的载荷
            msg = s.recv(msg_len, socket.MSG_WAITALL)            
        except OSError as err :
            print(err)
        else :
            print(msg.decode())
