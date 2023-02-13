# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 11:51:18 2022

@author: Mateo
"""
import math
import glob, os, time
import numpy as np
from datetime import datetime

from soundfile import SoundFile
from Acoustics import Acoustics
from Correction import apply_correction_filter

rec_seconds = 60
db_offset = 27.45
calibration = math.pow(10,db_offset/20)


bands = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315,
         400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000,
         5000, 6300, 8000, 10000, 12500, 16000, 20000]
gains = [-1.4, -3.8, -4.6, -5.1, -4.2, -2.3, -0.2, -0.3, -0.9, 0.2, 0.4, 0.2, 0.4, 0, -0.6, -0.8, -1.3, -1.8, -1.5, -0.7, -0.6, -1.8, -3.6, -8.1, -10.3, -8.4, -3, -0.6, -4.1, -4.2, -0.1, -2.3, -2.7]


for g in range(len(gains)):
    gains[g] = gains[g] + 1.7

splitter = '***'

def check_available(filename, time = False):
    data = filename.split(" ")
    date = data[1].split("-")
    year = date[0]
    date_time_str = date[2]+"/"+date[1]+"/"+year[2:4]
    date_time_str += " "
    hour_split = data[2].split("h")
    date_time_str += hour_split[0]
    date_time_str += ":"
    minute_split = hour_split[1].split("m")
    date_time_str += minute_split[0]
    date_time_str += ":"
    second_split = minute_split[1].split("s")
    date_time_str += second_split[0]
    date_time_obj = datetime.strptime(date_time_str, '%d/%m/%y %H:%M:%S')
    diff = datetime.now() - date_time_obj
    delta = diff.total_seconds()
    if(not(time)):
        return(delta > rec_seconds)
    else:
        return rec_seconds - delta
    
def check_measured(filename):
    try:
        with open('Measured.txt','r') as f:
            lines = f.read().split(splitter)
            for line in lines:
                if(filename == line):
                    return True
    except FileNotFoundError:
        f = open('Measured.txt','w')
        f.close()
    return False


#path = "C:/Users/Mateo/Documents"
path="../Audios/"
os.chdir(path)

keep_measuring = True
while(keep_measuring):
    for file in glob.glob("*.wav"):
        
        if(check_measured(file)):
            #print(file," already measured")
            continue
        
        while(not(check_available(file))):
            print("Waiting for "+file)
            try:
                time.sleep(check_available(file, True) + 5)
            except KeyboardInterrupt:
                print("CANCELED")
                keep_measuring = False
                break
        if(not(keep_measuring)):
            break
        init_time = datetime.now()
        print("Started "+file)
        try:
            audio_file = SoundFile(path+"/"+file)
            data = np.asarray(audio_file.read())
            if(len(data)==0):
                continue
        #
        #data[:,1] *= 1.2302
        #
            sample_rate = audio_file.samplerate
            num_channels = audio_file.channels
            audio_file.close()
        except RuntimeError:
            print("--- Couldn't open "+file+"! ---")
            continue
        
        try:
            ######################################################
            
            print("Applying correction filter")
            data = apply_correction_filter(data, bands, gains, sample_rate)
            
            
            print("Measuring A...")
            measurement_A = Acoustics(filename=file, signal=data, fs=sample_rate, channels=num_channels, cal_factor=calibration, weighting='A')
            measurement_A.compute_parameters()
            
            
            #print("Measuring C...")
            #measurement_C = Acoustics(filename=file, signal=data, fs=sample_rate, channels=num_channels, cal_factor=calibration, weighting='C')
            #measurement_C.compute_parameters()
            
            
            print("Measuring Z...")
            measurement_Z = Acoustics(filename=file, signal=data, fs=sample_rate, channels=num_channels, cal_factor=calibration, weighting='Z')
            measurement_Z.compute_parameters()
            
        
            try:
                f = open('Measured.txt', 'a+')
            except FileNotFoundError:
                f = open('Measured.txt', 'w')
            f.write(file)
            f.write(splitter)
            f.close()
            
            end_time = datetime.now()
            print("Finished in:",end_time-init_time)
        except KeyboardInterrupt:
            print("CANCELED")
            keep_measuring = False
            break
        
    
    ## 02h29m26s