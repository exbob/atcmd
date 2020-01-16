## 1. 项目说明

对蜂窝模块执行 AT 指令的软件。

## 2. 使用说明

这里有两个软件，功能一致，但是性能不同。

## 2.1 atcommand 

atcommand 是一个 shell 脚本，发送 AT 指令后接收模块返回的信息，然后把信息直接打印。这个脚本没有并发同步措施，所以，多个用户同时执行时可能出现错误。

语法：

```
    Usage: atcommand -h/--help
    Usage: atcommand [-v] dev default-command or atcommand dev -cmd ATxxxx
    -v:               output error message to stderr
    -h, --help:       show this help menu
    dev:              device like ttyACM0 or /dev/ttyACM0
    default-command:
        manufacturer: return 3G modem manufacturer name by AT+CGMI
        product:      return 3G modem product name by AT+CGMM
        revision:     return 3G modem software revision by AT+CGMR
        sn:           return 3G modem serial number by AT+CGSN
        imsi:         return SIM card IMSI by AT+CIMI
    -cmd command:
        -cmd ATxxxx   return the result this AT command
```

## 2.2 atserver.py 和 atclient.py

这是两个 Python 程序文件 ：

* atserver.py , Unix socket 服务器，接收客户端发来的数据帧，然后向蜂窝模块发送 AT 指令，并接收模块返回的信息，然后发送给客户端，通过多线程和线程锁实现并发和同步。
* atclient.py , Unix socket 客户端，向 Unix socket 服务器发送数据帧，然后接收服务器返回的数据帧，并解析打印。

程序基于 Python3 ，依赖 `pyserial` 模块，文档参考：[pyserial doc](https://pyserial.readthedocs.io/en/latest/shortintro.html)

两个程序的语法：

```
root@ubuntu:~/atcommand# ./atserver.py -h
usage: atserver.py [-h] [-s SOCK] [--version]

AT command server.

optional arguments:
  -h, --help  show this help message and exit
  -s SOCK     unix socket file
  --version   show program's version number and exit

root@ubuntu:~/atcommand# ./atclient.py -h
usage: atclient.py [-h] [-s SOCK] [-c CMD] [--version] dev

AT command client.

positional arguments:
  dev         serial port

optional arguments:
  -h, --help  show this help message and exit
  -s SOCK     unix socket file
  -c CMD      command
  --version   show program's version number and exit
```

举例：

```
root@ubuntu:~/atcommand# ./atserver.py &
root@ubuntu:~/atcommand# ./atclient.py /dev/ttyUSB2 -c ati

Manufacturer: Huawei Technologies Co., Ltd.
Model: ME909s-821a
Revision: 11.617.12.00.00
IMEI: 868441040255785
+GCAP: +CGSM,+DS,+ES

OK
```