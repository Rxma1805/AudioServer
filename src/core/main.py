import socketserver
import time
import os
import wave
import threading

DictAudioClient={}
DictUserClient={}
channels = 1
frameRate=8000
secondLong=60
serverIP='192.168.2.19'
rtspServer=''
rtspPort=12349
audioCmdPort = 12345
audioFilePort = 12347
userPort = 12348

class AudioFile(socketserver.BaseRequestHandler):
    def get_time_now(self):
        end = time.strftime('%Y-%m-%d %H_%M_%S',time.localtime(time.time()))
        start = time.strftime('%Y-%m-%d %H_%M_%S',time.localtime(time.time()-secondLong))
        return start,end
    
    def save_mp3(self,data,path,start,end):   
        #start,end = get_time_now()
        fileName = path+"/"+start+'_'+end+'.mp3'
        oldData=b''
        if not os.path.exists(path):
            os.makedirs(path)
#         if os.path.exists(fileName):
#             wf=wave.open(fileName,'rb')        
#             oldData = wf.readframes(wf.getnframes())
#             wf.close() 
#                    
#         wf=wave.open(fileName,'wb')
#         wf.setnchannels(channels)
#         wf.setsampwidth(2)
#         wf.setframerate(frameRate)  
#         if(len(oldData)>0):
#             wf.writeframes(oldData)              
#         wf.writeframes(data)
#         wf.close()
#         if os.path.exists(fileName):
#             wf=wave.open(fileName,'rb')        
#             oldData = wf.readframes(wf.getnframes())
#             wf.close() 
                   
        f=open(fileName,'ab+')
        f.write(data)
        f.close()
        
    def handle(self):
        self.start=""
        self.end=""        
        print("audio file received connect %s" % self.client_address[0])
        while True:        
#             data = self.request.recv(2054).decode()
            data = self.request.recv(3072)
            if(not data):
                print("client disconnected! %s" % self.client_address[0])
                break
            elif data[0:4] == "SEND".encode():
                self.request.send(b"OK")
                self.start,self.end = self.get_time_now()
            elif data[0:4] == "DATA".encode():
                self.save_mp3(data[4:],os.path.abspath('..')+'/record/%s' % self.client_address[0],self.start,self.end)
            elif data[0:4] == "1END".encode():
                continue
            else:
                continue
class AudioCmd(socketserver.BaseRequestHandler):
    def handle(self):
        DictAudioClient[self.client_address[0]]=self.request
        print('audio cmd connect % s' % self.client_address[0])
            
        while True:
            data = self.request.recv(2048)
            if(not data):
                print("audio cmd client disconnected! %s" % self.client_address[0])
                DictAudioClient.pop(self.client_address[0])
                break
            elif(data[0:3] == "CMD".encode()):#CMD_START_DESTIP_SRCIP
                srcIP = data.decode().split('_')[3]
                DictUserClient[srcIP].send(data)
            elif data[0:3] == "DAT".encode():#DATA_SRCIP_dddd
                start_index = 5#find second'_'
                for c in data[5:]:                    
                    if chr(c) == '_':
                        break
                    start_index+=1
                srcIP = data[5:start_index].decode()#if use rtsp  then here need change
                if(srcIP in DictUserClient):
                    DictUserClient[srcIP].send(data[start_index+1:])
                else:
                    print("Device want to connect %s but the user didn't work!" % srcIP)
            else:
                continue

class UserCmd(socketserver.BaseRequestHandler):
    def handle(self):
        DictUserClient[self.client_address[0]]=self.request
        print('New user connect % s'% self.client_address[0])
        
        while True:
            data = self.request.recv(2048).decode()
            if(not data):
                print("user client disconnected! % s" % self.client_address[0])
                DictUserClient.pop(self.client_address[0])
                break
            elif(data.find("CMD") == 0):
                #CMD_START_DESTIP_SRCIP            
                destIP = data.split('_')[2]
                if(destIP in DictAudioClient):
                    DictAudioClient[destIP].send(data.encode())
                else:
                    print("User want to connect %s but it didn't work!" % destIP)
            else:
                continue
            
if __name__ == "__main__":
    AudioFileServer = socketserver.ThreadingTCPServer((serverIP,audioFilePort),AudioFile)
    t1 = threading.Thread(target=AudioFileServer.serve_forever)
    t1.start()
    
    AudioCmdServer = socketserver.ThreadingTCPServer((serverIP,audioCmdPort),AudioCmd)
    t2 = threading.Thread(target=AudioCmdServer.serve_forever)
    t2.start()
    
    UserCmdServer = socketserver.ThreadingTCPServer((serverIP,userPort),UserCmd)
#     t3 = threading.Thread(target=UserCmdServer.serve_forever)
#     t3.start()
    UserCmdServer.serve_forever()
    
    
    