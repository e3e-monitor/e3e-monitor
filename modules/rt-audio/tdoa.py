from __future__ import division
import serial, time, wave, sys, getopt
import alsaaudio
from struct import unpack
import numpy as np


c_speed = 345
d = 0.200

def tdoa(x1, x2, th=0.5, interp=1, Fs=44100):
    '''
    This function computes the time difference of arrival (TDOA)
    of the signal at the two microphones. This in turns is used to infer
    the direction of arrival (DOA) of the signal.
    
    Specifically if s(k) is the signal at the reference microphone and
    s_2(k) at the second microphone, then for signal arriving with DOA
    theta we have
    
    s_2(k) = s(k - tau)
    
    with
    
    tau = Fs*d*sin(theta)/c
    
    where d is the distance between the two microphones and c the speed of sound.
    
    We recover tau using the Generalized Cross Correlation - Phase Transform (GCC-PHAT)
    method. The reference is
    
    Knapp, C., & Carter, G. C. (1976). The generalized correlation method for estimation of time delay. 
    Acoustics, Speech and Signal Processing, IEEE Transactions on, 24(4), 320–327. http://doi.org/10.1109/TASSP.1976.1162830
    
    Argument
    --------
    x1 : nd-array
        The signal of the reference microphone
    x2 : nd-array
        The signal of the second microphone
    th : float, optional (default 0.5)
        A threshold for signal detection
    interp : int, optional (default 1)
        The interpolation value for the cross-correlation, it can
        improve the time resolution (and hence DOA resolution)
    Fs : int, optional (default 44100 Hz)
        The sampling frequency of the input signal
        
    Return
    ------
    theta : float
        the angle of arrival (in radian (I think))
    pwr : float
        the magnitude of the maximum cross correlation coefficient
    delay : float
        the delay between the two microphones (in seconds)
    '''
    
    # zero padded length for the FFT
    n = (x1.shape[0]+x2.shape[0])

    # Generalized Cross Correlation Phase Transform
    # Used to find the delay between the two microphones
    # up to line 71
    X1 = np.fft.rfft(x1, n=n)
    X2 = np.fft.rfft(x2, n=n)

    X1 /= np.abs(X1)
    X2 /= np.abs(X2)

    cc = np.fft.irfft(X1*np.conj(X2), n=interp*n)

    # maximum possible delay given distance between microphones
    t_max = d/c_speed*(interp*Fs)

    # reorder the cross-correlation coefficients
    cc = np.concatenate((cc[-t_max:],cc[:t_max]))

    # pick max cross correlation index as delay
    tau = np.argmax(np.abs(cc))
    pwr = np.abs(cc[tau])
    tau -= t_max  # because zero time is at the center of the array

    # get the sine of the angle from the delay in samples
    D = tau/(interp*Fs)*c_speed/d
    
    # sanity check (sine cannot be larger than 1)
    if np.abs(D) > 1:
        D = np.sign(D)*1
        
    # compute angle from its sine value
    theta = np.arcsin(D)

    return theta, pwr, tau/(Fs*interp)

if __name__ == "__main__":

    # audio interface settings
    NO_CHANNELS = 2
    FRAME_RATE = 44100
    FRAME_SIZE = 64

    window = np.hanning(FRAME_SIZE)
    
    # interpolation factor of 4
    tdoa_interp = 4

    # setup audio interface
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
    inp.setchannels(NO_CHANNELS)
    inp.setrate(FRAME_RATE)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(FRAME_SIZE)

    l_pwr = 0.9
    pwr_avg = 0.

    while True:
        length, data = inp.read()
        buf = np.fromstring(data, dtype='int16')

        # compute DOA
        theta, pwr, tau = tdoa(buf[0::2]*window, buf[1::2]*window, interp=tdoa_interp)
        
        # Leaky averaging of cross-correlation magnitude
	if pwr_avg == 0:
            pwr_avg = pwr
        else:
            pwr_avg = l_pwr*pwr_avg + (1-l_pwr)*pwr
        if pwr > 2*pwr_avg:
            print pwr_avg,pwr
	
	# If instantaneous power deviates from the average, print angle
        if pwr > 0.5/tdoa_interp:
            print theta/2/np.pi*360,' -- pwr=',pwr


