#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 23:43:16 2019

@author: maxime
"""
from scipy.signal import butter, lfilter, hilbert
import numpy as np

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def GetEnveloppe(signal):
    analytic_signal = hilbert(signal)
    amplitude_envelope = np.abs(analytic_signal)
    return amplitude_envelope

def GetEnergyCurve(signal):
    E=20*np.log10(signal/max(signal))
    return E

def OctavebandFiltering(data,fs,order):
    EN61260lowcut=[100, 200, 400, 800, 1600, 3150, 6300, 12500]
    EN61260highcut=[160, 315, 630, 1250, 2500, 5000, 10000, 20000]
    #EN61260centfreq=[125, 250, 500, 1000, 2000, 4000, 8000]
    bands = np.empty((0,len(data)))
    
    for i in range(0,7):
        band=butter_bandpass_filter(data, EN61260lowcut[i], EN61260highcut[i], fs, order)
        bands = np.append(bands,[band],axis=0)
    return bands