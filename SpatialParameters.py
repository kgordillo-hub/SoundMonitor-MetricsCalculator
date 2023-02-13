# -*- coding: utf-8 -*-

import math
import numpy as np
from scipy.interpolate import interp1d

class SpatialParameters:
    
    def __init__(self, signal, fs, window_size, running_step):
        
        self.time_steps, self.iacc, self.tiacc, self.wiacc = self.__get_xcorr_descriptors(
            signal, fs, window_size, running_step)
        
    def __get_xcorr_descriptors(self, signal, fs, window_size, running_step):
        w_samples = round(window_size * fs)
        rs_samples = round(running_step * fs)
        
        time_steps = np.array([])
        
        iacc = np.array([])
        tiacc = np.array([])
        wiacc = np.array([])
        wiacc_d = np.array([])
        wiacc_u = np.array([])

        max_delay = 1 # (ms)
        dT = math.floor(max_delay * 0.001 * fs)
        t_axis_length = (2*dT) + 1
        T_AXIS = np.linspace(-max_delay, max_delay, t_axis_length)
        delta = t_axis_length//2

        
        iD = 0
        iU = w_samples
        lim = math.ceil(t_axis_length/2)-1
        
        while iU < len(signal):

            c = 0
            idx = 0
            max_value = 0
            
            ts = np.round(iD / fs, 2)

            time_steps = np.append(time_steps,ts)
            
            cll0 = np.correlate(signal[iD:iU,0], signal[iD:iU,0])
            crr0 = np.correlate(signal[iD:iU,1], signal[iD:iU,1])
            
            if((cll0 == 0) or (crr0 == 0)):
                iacc = np.append(iacc, 0)
                wiacc = np.append(wiacc, 0)
                wiacc_d = np.append(wiacc_d, 0)
                wiacc_u = np.append(wiacc_u, 0)
                
                if((cll0 == 0) and (crr0 != 0)):
                    tiacc = np.append(tiacc, 1)
                if((cll0 != 0) and (crr0 == 0)):
                    tiacc = np.append(tiacc, -1)
                else:
                    tiacc = np.append(tiacc, 0)
                
                
            
            scale = math.sqrt(cll0*crr0)
            
            iacf = np.zeros([(2*delta)+1])
            
            for tau in range(2*delta, -1, -1):
                        
                L = [0]
                R = [0]
                if(c < lim):
                    L = signal[iD+delta-c:iU, 0]
                    R = signal[iD:iU-delta+c, 1]
                elif(c == lim):
                    L = signal[iD:iU, 0]
                    R = signal[iD:iU, 1]
                else:
                    L = signal[iD:iU-c+delta, 0]
                    R = signal[iD+c-delta:iU, 1]
                    
                xcorr = np.correlate(L, R) / scale
        
                #iacf[tau, step] = xcorr
                c += 1
                
                if(xcorr > max_value):
                    max_value = xcorr
                    idx = tau


            iacc = np.append(iacc, max_value)
            tiacc_window = T_AXIS[idx]
            tiacc = np.append(tiacc, tiacc_window)
            
            alpha = 0.9*max_value
            
            idx_minus = np.linspace(idx, 0, idx+1)
            idx_plus = np.linspace(idx, t_axis_length-1, t_axis_length-idx)
            
            t_minus = -1;
            t_plus = 1;
            i_m = 0
            i_p = 0
            
            m_found = False
        
            if(len(idx_minus) > 1):
                for i in idx_minus:
                    if(iacf[int(i)] < alpha):
                        i_m = int(i)
                        if(idx-i > 0):
                            m_found = True
                            x_m = iacf[i_m:idx+1]
                            y_m = T_AXIS[i_m:idx+1]
                            t_f = interp1d(x_m, y_m, kind='linear')
                            t_minus = t_f(alpha)
                        break
                    
            p_found = False
            if(len(idx_plus) > 1):
                for i in idx_plus:
                    if(iacf[int(i)] < alpha):
                        i_p = int(i)
                        if(i-idx > 0):
                            p_found = True
                            x_p = iacf[idx:i_p+1]
                            y_p = T_AXIS[idx:i_p+1]
                            t_f = interp1d(x_p, y_p, kind='linear')
                            t_plus = t_f(alpha)
                        break


            wiacc_d = np.append(wiacc_d, t_minus)
            wiacc_u = np.append(wiacc_u, t_plus)
            if(not(m_found)):
                wiacc = np.append(wiacc, (t_plus - tiacc_window) * 2)
            elif(not(p_found)):
                wiacc = np.append(wiacc, (tiacc_window - t_minus) * 2)
            else:
                wiacc = np.append(wiacc, (t_plus - t_minus))
            
            iD += rs_samples
            iU += rs_samples
            
        return time_steps, iacc, tiacc, wiacc
        

