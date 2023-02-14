# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 11:43:16 2022

@author: Mateo
"""

from Weighting import apply_weighting
from TimeParameters import TimeParameters
from SpatialParameters import SpatialParameters
#from scipy.io import savemat
import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class Acoustics:
    
    def __init__(self, filename, signal, fs, channels, cal_factor = 1, weighting = 'Z'):
        
        self.filename = filename
        self.get_date_time()
        self.signal = signal
        self.fs = fs
        self.channels = channels
        self.weighting = weighting
        self.cal_factor = cal_factor
    
    def get_date_time(self):
        data = self.filename.split(" ")
        date = data[1].split("-")
        self.year = date[0]
        self.month = date[1]
        self.day = date[2]
        
        hour_split = data[2].split("h")
        self.hour = hour_split[0]
        minute_split = hour_split[1].split("m")
        self.minute= minute_split[0]
        second_split = minute_split[1].split("s")
        self.second = second_split[0]
        
        self.datetime = data[1]+" "+data[2]
        
    def compute_parameters(self):
        
        
        self.signal = apply_weighting(self.signal, self.fs, self.weighting, self.cal_factor)
        self.time_params = TimeParameters(self.signal, self.fs, bands_fraction=3, channels=self.channels)
        if((self.channels == 2) and (self.weighting == 'A')):
            self.space_params = SpatialParameters(self.signal, self.fs, window_size = 2, running_step=0.1)  

        return self.save_parameters()
        
    def save_parameters(self):
        if((self.channels == 2) and (self.weighting == 'A')):
            results = {
                # name : variable
                "SampleRate"+self.weighting : self.fs,
                "Channels" : self.channels,
                "Weighting" : self.weighting,
                "Bands" : self.time_params.freqs,
                "Levels" : self.time_params.band_levels,
                "LEQ" : self.time_params.leq,
                "Logger" : self.time_params.logger,
                "Ln" : self.time_params.ln,
                "TimeSteps" : self.space_params.time_steps,
                "IACC" : self.space_params.iacc,
                "TIACC" : self.space_params.tiacc,
                "WIACC" : self.space_params.wiacc
                }
        else:
            results = {
                "SampleRate" : self.fs,
                "Channels" : self.channels,
                "Weighting" : self.weighting,
                "Bands" : self.time_params.freqs,
                "Levels" : self.time_params.band_levels,
                "LEQ" : self.time_params.leq,
                "Logger" : self.time_params.logger,
                "Ln" : self.time_params.ln
                }
            
        #savemat(self.datetime+" "+self.weighting+".mat", results)
        json_dump = json.dumps(results, cls=NumpyEncoder)

        return json.loads(json_dump)

        #with open(self.datetime+" "+self.weighting+".json", 'w', encoding='utf-8') as f:
        #    json.dump(json.loads(json_dump), f, ensure_ascii=False, indent=4)

