# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 14:46:51 2022

@author: Mateo
"""


from scipy import signal
import math
import numpy as np

def apply_correction_filter(x, bands, gains, fs, q = 8):
    
    y = x
    
    for b in range(len(bands)):
        band = bands[b]
        gain = gains[b]
        #print(band)
        b, a = get_peak_filter_coeffs(band, gain, q, fs)
        if(len(b) != 1):
            y = signal.lfilter(b, a, y, axis=0)
    return y

def get_peak_filter_coeffs(freq, gain, q, fs):
    
    k = math.tan(math.pi * freq / fs)
    if gain == 0:
        num = np.array([1])
        den = np.array([1])
    elif gain > 0:
       v0 = math.pow(10, gain/20)
       b0 = ((1+(v0/q)*k+(k**2))/(1+(1/q)*k+(k**2)))
       b1=((2*((k**2)-1))/(1+(1/q)*k+(k**2)))
       b2=((1-(v0/q)*k+(k**2)))/((1+(1/q)*k+(k**2)))
       num = np.array([b0, b1, b2])
       
       a1=((2*(k**2-1))/(1+(1/q)*k+(k**2)));
       a2=((1-(1/q)*k+(k**2)))/((1+(1/q)*k+(k**2)));   
       den = np.array([1, a1, a2])
       
    elif gain < 0:
        v0=math.pow(10,-gain/20)
        b0=((1+(1/q)*k+(k**2))/(1+(v0/q)*k+(k**2)))
        b1=((2*((k**2)-1))/(1+(v0/q)*k+(k**2)))
        b2=((1-(1/q)*k+(k**2)))/((1+(v0/q)*k+(k**2)))
        num = np.array([b0, b1, b2])
        
        a1=((2*((k**2)-1))/(1+(v0/q)*k+(k**2)))
        a2=((1-(v0/q)*k+(k**2)))/((1+(v0/q)*k+(k**2)))
        den = np.array([1, a1, a2])

        
    return num, den