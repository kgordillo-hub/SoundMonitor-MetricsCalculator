# -*- coding: utf-8 -*-

from scipy import signal
import math
import numpy as np


    
def apply_weighting(x, fs, weighting, gain):
    if(weighting == 'A'):
        return __a_weighting_filter(x, fs, gain)
    if(weighting == 'C'):
        return __c_weighting_filter(x, fs, gain)
    else:
        return x*gain

def __a_weighting_filter(x, fs, gain):
    
    b, a = __get_a_coeffs(fs, gain)
    y = signal.lfilter(b, a, x, axis=0)
    return y
def __c_weighting_filter(x, fs, gain):
    
    b, a = __get_c_coeffs(fs, gain)
    y = signal.lfilter(b, a, x, axis=0)
    return y

def __get_a_coeffs(fs, gain):

    f1 = 20.598997
    f2 = 107.65265
    f3 = 737.86223
    f4 = 12194.217
    A1000 = 1.9997
    
    GA = math.pow(10, A1000/20) * gain
    pi = 3.14159265358979
    
    num = [math.pow((2*pi*f4), 2)*GA, 0, 0, 0, 0]
    
    v1 = np.array([1, (4*pi*f4), (2*pi*f4)**2])
    v2 = np.array([1, (4*pi*f1), (2*pi*f1)**2])
    
    den = np.convolve(v1, v2)
    den = np.convolve(den, [1, 2*pi*f3])
    den = np.convolve(den, [1, 2*pi*f2])
    
    z, p = signal.bilinear(num, den, fs)
    
    return z, p
def __get_c_coeffs(fs, gain):
    
    f1 = 20.598997
    f4 = 12194.217
    C1000 = 0.0619
    GC = math.pow(10, C1000/20) * gain
    pi = 3.14159265358979
    
    num = [math.pow((2*pi*f4), 2)*GC, 0, 0]
    
    v1 = np.array([1, (4*pi*f4), (2*pi*f4)**2])
    v2 = np.array([1, (4*pi*f1), (2*pi*f1)**2])
    
    den = np.convolve(v1, v2)
    
    z, p = signal.bilinear(num, den, fs)
    
    return z, p
