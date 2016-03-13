from __future__ import division
import serial, time, wave, sys, getopt
import alsaaudio
from struct import unpack
import numpy as np
import sys
import os
from multiprocessing import Process
import serial

from sigproc import critical_bands, binning

from tdoa import tdoa

def send_string(ser, s):
    ser.write( s )

def send_event(ser, P, tau):

    print 'Send event!'
    
    s = '$%d,%d#' % (int(P),int(tau*1e6))

    if __name__ == '__main__':
         p = Process(target=send_string, args=(ser, s,))
         p.start()
         p.join()
    

if __name__ == "__main__":

    # open serial device
    if os.path.isfile('/dev/ttyACM1'): 
        ser = serial.Serial('/dev/ttyACM1',  9600, timeout = 0.1)
    else:
        ser = serial.Serial('/dev/ttyACM0',  9600, timeout = 0.1)

    NO_CHANNELS = 2
    FRAME_RATE = 44100
    FRAME_SIZE = 512

    NFFT = FRAME_SIZE*2
    OVERLAP = FRAME_SIZE

    fft_buf = np.zeros((NO_CHANNELS, NFFT))

    bands = critical_bands(FRAME_RATE, NFFT)

    # detect when Time domain peak is larger than 70 dB
    threshold_detect = 75

    # DOA parameters
    d = 0.2             # inter mic distance
    doa_interp = 4
    c_speed = 345       # approximate speed of sound
    tau_max = np.ceil(d/c_speed*FRAME_RATE)
    doa_frame = 4*tau_max
    doa_win = np.hanning(doa_frame)
    print doa_frame

    # Audio IF params
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
    inp.setchannels(NO_CHANNELS)
    inp.setrate(FRAME_RATE)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(FRAME_SIZE)

    # processing loop
    while True:

        # get data from audio i/f
        length, data = inp.read()
        if length < 0:
            print 'Frame missed'
            continue
        buf = np.fromstring(data, dtype='int16').reshape((-1,2))

        # overlapping buffer update
        fft_buf[:,:NFFT/2] = fft_buf[:,NFFT/2:]
        fft_buf[:,NFFT/2:] = buf.T

        # compute max amplitude in dB
        iP = np.argmax(np.abs(fft_buf[:,NFFT/4:3*NFFT/4]), axis=1)
        if np.abs(fft_buf[0,iP[0]]) > np.abs(fft_buf[1,iP[1]]):
            c = 0
        else:
            c = 1
        t = iP[c] + NFFT/4
        P = 20.*np.log10(np.abs(fft_buf[c,t]))

        # detect the event!
        if P > threshold_detect:

            x = fft_buf[:,t-doa_frame/2:t+doa_frame/2]*doa_win

            theta, pwr, tau = tdoa(x[0,:], x[1,:], interp=doa_interp, Fs=FRAME_RATE)
            send_event(ser, P, tau)
            print 'Loud event! peak:',P,'tau:',tau,'theta',theta/2/np.pi*360



