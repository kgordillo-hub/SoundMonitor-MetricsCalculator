# -*- coding: utf-8 -*-

import math
import scipy
import numpy as np


class TimeParameters:
    
    def __init__(self, signal, fs, bands_fraction, channels, logger_length = 1):
                
        self.logger, self.leq = self.__get_leq(signal, fs, channels, logger_length)
     
        self.ln = self.__get_ln(channels)
        
        self.freqs, self.band_levels = self.__get_band_levels(signal, fs, channels, bands_fraction)
        
    def __get_leq(self, x, fs, channels, logger_length):
        
        length = fs*logger_length
        frames = int(len(x)/length)
        count = 0
        LOGGER = np.zeros([frames, channels])
        LEQ = np.zeros([1, channels])
        
        for f in range(frames):
            iD = math.ceil(count)
            iU = math.floor(count+length)
            for c in range(channels):
                if(channels > 1):
                    frame = x[iD:iU,c]
                else:
                    frame = x[iD:iU]
                p = self.__get_rms(frame[:])
                level = round(20*math.log10(p/20e-6), 1)
                LOGGER[f, c] = level
            count += length
            
        for c in range(channels):
            if(channels > 1):
                p = self.__get_rms(x[:,c])
            else:
                p = self.__get_rms(x[:])
            LEQ[0,c] = round(20*math.log10(p/0.00002), 1)
        
        print(LEQ[0,:])
        return LOGGER, LEQ
        
    def __get_rms(self, array):
        
        c = 0
        for i in range(len(array)):
            c += math.pow(array[i], 2)
        return math.sqrt(c / len(array))
    
    def __get_ln(self, channels):
        
        ln = np.zeros([100, channels])
        for i in range (1, 100):
            if(channels > 1):
                for c in range(channels):
                    ln[i,c] = round(np.percentile(self.logger[:,c], 100-i), 1)
            else:
                ln[i,0] = round(np.percentile(self.logger, 100-i), 1)
        return ln
            
    def __get_band_levels(self, signal, fs, channels, fraction):
        
        window_size = self.__next_pow_2(len(signal))
        
        if(window_size > len(signal)):
            zeros_to_add = (window_size) - len(signal)
            if(channels > 1):
                self.signal = np.pad(signal, ((0, zeros_to_add), (0, 0)), mode='constant')
            else:
                self.signal = np.pad(signal, ((0, zeros_to_add)), mode='constant')
        else:
            self.signal = signal
        
                               
        fc = []
        corr_db = -3
        if(fraction == 3):
            fc = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315,
                  400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000,
                  5000, 6300, 8000, 10000, 12500, 16000, 20000]
            fg = [0.185, 0.327, 0.531, 0.773, 0.891,
                  0.920, 1.0, 1/0.920, 1/0.891,
                  1/0.773, 1/0.531, 1/0.327, 1/0.185]
            gg = [1.0839e-5, 1.6218e-5, 9.2257e-5, 0.2089e-3, 0.7079, 
                  0.9772, 1, 0.98855, 0.6998, 0.4786e-3,
                  1.1220e-5, 2.4831e-6, 1.5488e-6]
        else:
            return 0
        
        levels = np.zeros([len(fc), channels])
        
        complexData = scipy.fft.fft(self.signal, axis=0)
                
        abs_signal = np.abs(complexData[0:window_size//2])
        
        den = 2e-5*window_size//2
    
        dfreq = fs / window_size
        for b in range(len(fc)):
            
            iC = math.floor(fc[b] / dfreq) - 1
            rate = 0.8908987181403393
            iD = math.ceil(iC*rate)-1
            iU = math.floor(iC/rate)-1
            acum = np.zeros([1, channels])
            

            freqs = np.zeros(len(fg))
            for i in range(len(fg)):
                freqs[i] = fg[i] * iC
            
            if(iU > len(abs_signal)):
                iU = len(abs_signal)
                   
      
            for idx in range (iD, iU+1):
                if(idx<len(abs_signal)):
                    
                    #gain = amp(idx)
                    gain= 1
                        
                    if(channels > 1):
                        for c in range(channels):        
                            v = math.pow(abs_signal[idx, c]/den,2)
                            acum[0, c] = acum[0, c] + (v)
                    else:
                        v = math.pow(abs_signal[idx]/2e-5, 2)
                        acum[0, 0] = acum[0, 0] + (v)

            for c in range(channels):
                l = 10 * math.log10(acum[0, c])
                levels[b, c] = round(l + corr_db, 1)
        return fc, levels
        
    def __next_pow_2(self, x):
        return 2**(x-1).bit_length()
        
