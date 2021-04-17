#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 14:07:51 2021

@author: maxime
"""
import parameters.filtering as f
import numpy as np
import math
from scipy import stats

def compute(measurement):
    
    #init
    fs = measurement.fs
    IR = measurement.IR
    
    #Octave band filtering    
    bands=f.OctavebandFiltering(IR, fs, order=3);
    tint=len(IR)
    Schrobands = np.empty((0,tint))
    T15save = []
    T30save = []
    EDTsave=[]
    Envsave = []
    curves = []
    schro = []
    C80 = []
    C50 = []
    D50 = []
    INR = []
    
    for i in range(0,7):
        
        #Hilbert transorm
        Enveloppe = f.GetEnveloppe(bands[i])
        EnvdB=f.GetEnergyCurve(Enveloppe)
        Envsave.append(EnvdB)
        
        #Lundmine Method
        try :
            stopimpulse , noise, energiedB, energie = lundminemethod(Enveloppe,fs)
        except:
            T15save.append("?")
            T30save.append("?")
            EDTsave.append("?")
            C50.append("?")
            C80.append("?")
            D50.append("?")
            curves.append(EnvdB)
            INR.append([])
            schro.append([])
            continue
        #stopimpulse , noise, energiedB, energie = lundminemethod(bands[i],fs)
        curves.append(energiedB)
        INR.append(round(-noise,0))
        Enveloppe = Enveloppe[0:stopimpulse]
    
        #Schroeder integral
        sch = np.cumsum(Enveloppe[::-1]**2)[::-1]
        sch_db = 10.0 * np.log10(sch / np.max(sch))
        schro.append(sch_db)
        
        #T15 value 
        t15 = regression(sch_db, -5.0, -20.0, 4.0,fs)
        T15save.append(round(t15,1))
        
        #T30 value 
        t30 = regression(sch_db, -5.0, -35.0, 2.0,fs)
        T30save.append(round(t30,1))
        
        #EDT value 
        edt = regression(sch_db, 0.0, -10.0, 6.0,fs)
        EDTsave.append(round(edt,1))
        
        #C50 value
        t50ms = int(0.08 * fs)
        clarity50 = 10.0 * np.log10((np.sum(energie[:t50ms]) / np.sum(energie[t50ms:len(sch)])))
        C50.append(round(clarity50,1))
        
        #C80 value
        t80ms = int(0.08 * fs)
        clarity80 = 10.0 * np.log10((np.sum(energie[:t80ms]) / np.sum(energie[t80ms:len(sch)])))
        C80.append(round(clarity80,1))
        
        #D50 value
        D50ms = int(0.08 * fs)
        def50 = 10.0 * np.log10((np.sum(energie[:D50ms]) / np.sum(energie[:len(sch)])))
        D50.append(round(def50,1))
        
    return T15save, T30save, curves, schro,Envsave, C50, C80 , D50, EDTsave , INR
    
def detectstartimpulse(impulse):
    start_time = np.argmax(impulse)
    return start_time

def regression(sch_db,init,end,factor,fs):
    # Linear regression
    sch_init = sch_db[np.abs(sch_db - init).argmin()]
    sch_end = sch_db[np.abs(sch_db - end).argmin()]
    init_sample = np.where(sch_db == sch_init)[0][0]
    end_sample = np.where(sch_db == sch_end)[0][0]
    x = np.arange(init_sample, end_sample + 1) / fs
    y = sch_db[init_sample:end_sample + 1]
    slope, intercept = stats.linregress(x, y)[0:2]
    db_regress_init = (init - intercept) / slope
    db_regress_end = (end - intercept) / slope
    t60 = factor * (db_regress_end - db_regress_init)
    return t60
    

def lundminemethod(ir,fs):
    
    #pour plus tard
    tstart = detectstartimpulse(ir)
    
    dBtoNoise = 7  
    useDynRange = 15  # dynamic range
    
    # 1 local averaging #1
    
    # square IR
    energie =  ir**2
    energie_dB=10*np.log10(energie/max(energie))
        
    # local averaging
    
    # 1/ chop in 10ms time interval and take interval average
    taver = 0.01
    sampleaver = taver * fs
    numberofchops = len(ir)/fs / taver
    numberofchops= math.floor(numberofchops)
    timeStamp = np.zeros((numberofchops, 1))
    
    chops=[]
    for i in range(0,numberofchops):
        chops.append(mean_squared(ir[int(i*taver*fs):int((i+1)*taver*fs)]))
        timeStamp[i, 0] = i*taver*fs
    
    avrg_energie = chops
    avrg_energie = np.asarray(avrg_energie)
    avrg_energie_db= 10*np.log10(avrg_energie/max(avrg_energie))
    

    # 2 - estimate background noise (last 10% of signal averaged)
    last10Idx = -int(len(avrg_energie_db)//10)
    noiseLevel = np.mean(avrg_energie_db[last10Idx:])

    # 3 - compute slope
        #max value and index of averaged IR
    startIdx = np.argmax(avrg_energie_db)
    startValue = avrg_energie_db[int(startIdx)]
    
        # value 7dB above noise floor
    stopIdx = startIdx + np.where(avrg_energie_db[startIdx+1:]
                                  <= noiseLevel + dBtoNoise)[0][1]
    stopValue = avrg_energie_db[stopIdx]
    startIdx=timeStamp[startIdx,0]
    stopIdx=timeStamp[stopIdx,0]

        #linear regression
    yvalue = stopValue - startValue
    xvalue = stopIdx - startIdx
    
    slope = yvalue / xvalue
    t = np.arange(0, len(ir), 1)
    curvefit= slope*t + startValue
    curvenoise = np.ones((len(curvefit),))*noiseLevel

    # 4 - find crosspoint
    crosspoint = np.argwhere(np.diff(np.sign(curvefit - curvenoise))).flatten()

    
    # 5 - Choose new intervals
    result1 = np.argmax(curvefit < -10)
    result2 = np.argmax(curvefit < -20)
    numberofsample = result2 - result1
    
    newinterval = int(numberofsample // 10)
    sampleaver = newinterval
    taver = sampleaver/fs
    
    numberofchops = len(ir)/fs / taver
    numberofchops= math.floor(numberofchops)
    timeStamp = np.zeros((numberofchops, 1))
    
    chops=[]
    for i in range(0,numberofchops):
        chops.append(mean_squared(ir[int(i*taver*fs):int((i+1)*taver*fs)]))
        timeStamp[i, 0] = i*taver*fs
    
    avrg_energie = chops
    avrg_energie = np.asarray(avrg_energie)
    avrg_energie_db= 10*np.log10(avrg_energie/max(avrg_energie))
        
    temps=[]
    temps.append(avrg_energie_db)
    temps = np.asarray(temps)
    
    # 7 - iterative loop
    
    oldcross = crosspoint
    newcross = oldcross
    samplenum10percentlen=int(len(energie_dB)//10)
    latedecaydbmargin = 7
    iterate = True
    countvar = 0
    while iterate == True :
        #estimate new noise level 
        bgNoiseMargin = 10
        idxnoisestart=int(newcross + numberofsample)
        noiseLevel = np.mean(avrg_energie_db[int(idxnoisestart/newinterval):int((idxnoisestart+samplenum10percentlen)/newinterval)])
    
        #estimate late decay
        tt = noiseLevel+latedecaydbmargin
        xhigh = np.argmax(avrg_energie_db[2:] < int(tt) )
        xlow = np.argmax(avrg_energie_db[2:] < int(tt) + 15)
        
        yhigh = avrg_energie_db[xlow]
        ylow = avrg_energie_db[xhigh]
        
        xhigh=int(timeStamp[xhigh,0])
        xlow=int(timeStamp[xlow,0])
        
        slope = (ylow-yhigh)/(xhigh-xlow)
        
        curve2zero = ((xhigh*yhigh)-(xlow*ylow))/(xhigh-xlow)
        curvefit2= slope*t + curve2zero
        
        # 4 - find crosspoint
        curvenoise = np.ones((len(curvefit),))*noiseLevel
        crosspoint2 = np.argwhere(np.diff(np.sign(curvefit2 - curvenoise))).flatten()
        newcross = crosspoint2[0]
        countvar+= 1
        
        if np.abs(newcross-oldcross)<2000:
            iterate = False
            
        if countvar > 10:
            print("too many iterations")
            iterate = False
        
        oldcross=newcross
    
    return newcross,noiseLevel, energie_dB, energie

def mean_squared(x):
        return np.mean(x**2)

