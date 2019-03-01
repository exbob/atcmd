#!/usr/bin/python3

import os
import socket
import argparse

def main():
    parser = argparse.ArgumentParser(description="AT command server.")
    parser.add_argument("dev", default="/dev/ttyUSB2", help="serial port")
    parser.add_argument("-c", dest="cmd", default="at", help="command")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1")
    args = parser.parse_args()
    message = args.dev + " " + args.cmd

    socket.setdefaulttimeout(3)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), ("localhost", 10001))
    try:
        ret = sock.recvfrom(1024)
        print(ret[0].decode())
    except socket.timeout :
        print("Timeout")
    finally:
        sock.close()

if __name__ == "__main__":
    main()