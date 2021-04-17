# roomparameters

Simple GUI app that extract room acoustics parameters from an Impulse Response (IR) measurements. This project is made as an educationnal projet and as not been correctly tested yet. Please use with caution.

Features :
- Acoustical parameters (EDT,T15,T30,C50,C80, D50)
- Impulse to Noise Ratio (INR)
- Schroeder integration on valid part of the impulse (using Lundeby method)
- Energy decay curves plotting on each frequency band.

The projet only implements 3rd order bandpass filtering for each octave bands which is probably not enough according to the standards. I will fix this in future commits.

In order for the code to run as expected, please provide a mono file with a sufficient dynamic range.

![Alt text](roomparameters.png?raw=true "Main Window")
