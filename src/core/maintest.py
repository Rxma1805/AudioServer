'''
Created on 2018年3月28日

@author: Administrator
'''
#from gevent.server import StreamServer
from pyaudio import paInt16,PyAudio
import wave
import time
import os
#import socket
import threading
#from multiprocessing import process
import socketserver


channels = 1
frameRate=8000
secondLong=60
serverIP='192.168.2.19'
rtspServer=''
rtspPort=12349
audioCmdPort = 12345
audioFilePort = 12347
userPort = 12348

DictAudioClient={}
DictUserClient={}    
    
    
def get_time_now():
    end = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()-secondLong))
    return start,end

def save_wave(data,path,start,end):   
    #start,end = get_time_now()
    fileName = path+"/"+start+'_'+end+'.wav'
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(fileName):
        os.system(r'touch %s' % fileName)
    datas=[]
    wf=wave.open(fileName,'rb')
    datas.append(wf.readframes(wf.getnframes()))
    wf.close()
    datas.append(data)
    wf=wave.open(fileName,'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(2)
    wf.setframerate(frameRate)    
    wf.writeframes(datas.append(datas))
    wf.close()
        
def audio_file_save(sock,address): 
    start=""
    end=""
    print("audio file received connect %s" % address)
    while True:        
        data = sock.recv(4096).decode()
        if(not data):
            print("client disconnected! %s" % address)
            break
        elif data == "OK":
            sock.send(b"OK")
            start,end = get_time_now()
        elif data.find("DATA"):
            save_wave(data.split('_')[1].encode(),'../record',start,end)
        elif data.find("END"):
            continue
        else:
            continue
               
def audio_cmd_handle(sock,address):
    DictAudioClient[address]=sock
    print('audio cmd connect % s' % address)
        
    while True:
        data = sock.recv(2048)
        if(not data):
            print("audio cmd client disconnected! %s" % address)
            DictAudioClient.pop(address)
            break
        elif(data.find("CMD".encode(encoding='utf_8', errors='strict'))):#CMD_START_DESTIP_SRCIP
            srcIP = data.split('_')[3]
            DictUserClient[srcIP].send(data)
        elif(data.find("DATA".encode(encoding='utf_8', errors='strict'))):#DATA_SRCIP_dddd
            srcIP = data.split('_')[1]#if use rtsp  then here need change
            DictUserClient[srcIP].send(data.split('_')[2])
        else:
            continue

def user_cmd_handle(sock,address):
    DictUserClient[address]=sock
    print('New user connect % s'% address)
    
    while True:
        data = sock.recv(2048)
        if(not data):
            print("user client disconnected! % s" % address)
            DictUserClient.pop(address)
            break
        elif(data.find("CMD".encode(encoding='utf_8', errors='strict'))):
            #CMD_START_DESTIP_SRCIP            
            destIP = data.split('_')[2]
            if(DictAudioClient.has_key(destIP)):
                DictAudioClient[destIP].send(data)
            else:
                print("User want to connect %s but it didn't work!" % destIP)
        else:
            continue
 

def server_start(server):
    server.serve_forever()
                  
if __name__ == "__main__":
    
    socketserver.TCPServer((serverIP,audioFilePort),audio_file_save)
    
    
    
    
    server = StreamServer((serverIP,audioFilePort),audio_file_save)
    #server.daemo = True
    #server.serve_forever()
    t1 = threading.Thread(target = server_start,args=(server,))
    t1.daemon=True
    t1.start()
    
    
    cmdServer = StreamServer((serverIP,audioCmdPort),audio_cmd_handle)
    #cmdServer.serve_forever()#
    t2 = threading.Thread(target = server_start,args=(cmdServer,))
    t2.daemon = True
    t2.start()
    
    userServer = StreamServer((serverIP,userPort),user_cmd_handle)
    #userServer.serve_forever()#
    #t3 = threading.Thread(target = server_start,args=(userServer,))
#       
#     t1.start()
#     t2.start()
#     t3.start()
#     t3 = threading.Thread(target=userServer.serve_forever)
#     t3.start()
   

    

        
     