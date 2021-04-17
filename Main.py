

from scipy.io.wavfile import read
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QErrorMessage, QTableWidgetItem)
from PyQt5.QtCore import *
from PyQt5.uic import loadUiType
from os.path import dirname, realpath, join
from sys import argv
import sys
import numpy as np
import parameters.reverbtime as rvb


scriptDir = dirname(realpath(__file__))
FROM_MAIN, _ = loadUiType(join(dirname(__file__), "GUI/mainwindow.ui"))


class Main(QMainWindow, FROM_MAIN):
    
    def __init__(self, parent = FROM_MAIN):

        super(Main, self).__init__()
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.import_button.clicked.connect(self.browse_folder)
        self.combo_freq.currentIndexChanged.connect(self.plot)
        self.checkBox_schro.stateChanged.connect(self.plot)
        self.error_dialog = QErrorMessage()

    def browse_folder(self):
        global filename

            # options = QFileDialog.Options()
            # options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Open", "", "WAV Files (*.wav);;All Files (*)")
        if filename:
            try :
                samplerate, data = read(filename)
                idx = np.argmax(data**2)
                data = data[idx:]
                self.measurement = Measurement(data,samplerate)
  
                try :
                    self.measurement.T15,self.measurement.T30, self.measurement.energycurve, self.measurement.schrodercurves, self.measurement.env, self.measurement.C50, self.measurement.C80,self.measurement.D50,self.measurement.EDT,self.measurement.INR = rvb.compute(self.measurement)
                except Exception as e:
                    print(e)
                    self.error_dialog.showMessage('Impulse is not a Room Impulse')
                
                self.plot()
                self.loaddata()

            except : 
                pass
        

    def plot(self):

        index = self.combo_freq.currentIndex()
        try :
            self.room_display.clear()
            self.room_display.update_graph(self.measurement.xaxis[self.measurement.starttime:], 
                                           self.measurement.energycurve[index][self.measurement.starttime:],
                                           self.measurement.fs,
                                           1)
            if self.checkBox_schro.isChecked():
                self.room_display.update_graph(self.measurement.xaxis[self.measurement.starttime:], 
                                           self.measurement.schrodercurves[index],
                                           self.measurement.fs,
                                           2)

        except Exception as e:
            print(e)

        
    def loaddata(self):
        try :
            for i in range(0,7):
                self.tableWidget.setItem(0,i,QTableWidgetItem(str(self.measurement.INR[i])+ " dB"))
                self.tableWidget.setItem(1,i,QTableWidgetItem(str(self.measurement.EDT[i])))
                self.tableWidget.setItem(2,i,QTableWidgetItem(str(self.measurement.T15[i])))
                self.tableWidget.setItem(3,i,QTableWidgetItem(str(self.measurement.T30[i])))
                self.tableWidget.setItem(4,i,QTableWidgetItem(str(self.measurement.C50[i])))
                self.tableWidget.setItem(5,i,QTableWidgetItem(str(self.measurement.C80[i])))
                self.tableWidget.setItem(6,i,QTableWidgetItem(str(self.measurement.D50[i])))
        except Exception as e:
                print(e)
            
class Measurement():
    
    def __init__(self,IR,fs):
        self.IR = IR
        self.fs = fs
        self.T15 = []
        self.T30 = []
        self.T60 = []
        self.C50 = []
        self.C80 = []
        self.D50 = []
        self.INR = []
        self.EDT = []
        self.energycurve = []
        self.schrodercurves = []
        self.env = []
        self.xaxis = np.linspace(0.0,  round(len(IR)/fs),int(len(IR)))
        self.starttime = np.argmax(IR)

def main():
        #QApplication.setGraphicsSystem("raster")
        app = QApplication(argv)
        window = Main()
        # window.showFullScreen() # Start at position full screen
        #window.showMaximized()  # Start position max screen
        window.show()
        #app.exec_()
        
        #timer = QTimer()
        #timer.timeout.connect(lambda: None)
        #timer.start(100)
        
        sys.exit(app.exec_())
       
if __name__ == '__main__':
    main()
    