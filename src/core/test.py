'''
Created on 2018年3月29日

@author: Administrator
'''
import os
import wave
from pyaudio import PyAudio,paInt16
import time
import socket
def get_time_now():
    end = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()-5))
    return start,end
    
    
IP='192.168.2.19'
PORT = 12348

tcp_clent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_clent.connect((IP,PORT))
tcp_clent.send("CMD_START_192.168.2.118_192.168.2.19".encode(encoding='utf_8', errors='strict'))
while True:
    pass