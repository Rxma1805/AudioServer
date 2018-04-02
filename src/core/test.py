'''
Created on 2018年3月29日

@author: Administrator
'''
import os
import wave
from pyaudio import PyAudio,paInt16

data=[]
fileName = '1.wav'
wf=wave.open(fileName,'rb')
data.append(wf.readframes(wf.getnframes()))
wf.close()

wf=wave.open(fileName,'wb')
wf.setnchannels(1)
wf.setsampwidth(2)
wf.setframerate(8000)
wf.writeframes(data.append(data))
wf.close()