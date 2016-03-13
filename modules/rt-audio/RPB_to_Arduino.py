import serial, time, wave, sys, getopt
import alsaaudio
from struct import unpack
import numpy as np
from multiprocessing import Process
import os
from scipy.fftpack import fft, ifft

NO_CHANNELS = 2
FRAME_RATE = 44100
# 10 secs of ring buffer buffer
RING_BUFFER_SIZE = 882000 

if os.path.isfile('/dev/ttyACM1'): 
    ser = serial.Serial('/dev/ttyACM1',  9600, timeout = 0.1)
else:
    ser = serial.Serial('/dev/ttyACM0',  9600, timeout = 0.1)

inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
inp.setchannels(NO_CHANNELS)
inp.setrate(FRAME_RATE)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
inp.setperiodsize(1024)

w = wave.open('test.wav', 'w')
w.setnchannels(NO_CHANNELS)
w.setsampwidth(2)
w.setframerate(FRAME_RATE)

#if you only want to send data to arduino (i.e. a signal to move a servo)
def send( theinput ):
    ser.write( theinput )

class RingBuffer():
    "A 1D ring buffer using numpy arrays"
    def __init__(self, numOfFrames, frameSize):
        self.data = np.zeros(numOfFrames*frameSize, dtype='int16')
        self.frameSize = frameSize
        self.numOfFrames = numOfFrames
        self.index = 0
      

    def extend(self, x):
        "adds array x to ring buffer"
        k = self.index*self.frameSize
        self.data[k:k+self.frameSize] = x 
        self.index = (self.index+1) % self.numOfFrames

    def get(self):
        "Returns the first-in-first-out data in the ring buffer"
        k = self.index * self.frameSize
        return np.concacenate((self.data[k:],self.data[0:k]))

    def getWindow(self, window):
        k = self.index * self.frameSize
        if window > self.numOfFrames*self.frameSize:
            raise ValueError("Window should be smaller than buffer size")
        if k - window >= 0:
            return self.data[k-window:k]
        else:
            return np.concatenate((self.data[k-window:],self.data[:k])) 

 
    def analyze(self, window):
        t = np.arange(256) 
        sp = np.fft.fft(self.getWindow(window)) 
        freq = np.fft.fftfreq(t.shape[-1])

        threashold =  np.abs(self.getWindow(window)).mean()   
        if threashold > 500:
            if __name__ == '__main__':
    	         p = Process(target=send, args=('42',))
    	         p.start()
    	         p.join()

        print sp[2] 

ringbuff = RingBuffer(1000,1024* NO_CHANNELS)
while True:
    length, data = inp.read()
    dataToSave = np.fromstring(data, dtype='int16')
    ringbuff.extend(dataToSave)
    ringbuff.analyze(1024)
    w.writeframes(data)
