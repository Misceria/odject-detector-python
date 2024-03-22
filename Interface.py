
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog, QWidget, QApplication, QLabel, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QImage, QPixmap, QColor
import sys
import cv2, imutils
import time
import numpy as np


import numpy as np
import cv2
import pyshine as ps
from threading import Thread



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt static label demo")
        self.resize(1920, 1080)
        width = 470*2
        height = 260*2
        # create vid 1
        self.image_label = QLabel(self)
        # create vid 2
        self.image_label2 = QLabel(self)
        # create vid 3
        self.image_label3 = QLabel(self)
        # create vid 4
        self.image_label4 = QLabel(self)

        # create a vertical box layout and add the two labels
        vbox = QGridLayout()
        vbox.setSpacing(0)
        vbox.setHorizontalSpacing(0)
        vbox.setVerticalSpacing(0)
        """vbox.setVerticalSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.image_label.setSizePolicy(sizePolicy)
        self.image_label2.setSizePolicy(sizePolicy)
        self.image_label3.setSizePolicy(sizePolicy)
        self.image_label4.setSizePolicy(sizePolicy)"""
        vbox.addWidget(self.image_label, 0, 0)
        vbox.addWidget(self.image_label2, 1, 0)
        vbox.addWidget(self.image_label3, 0, 1)
        vbox.addWidget(self.image_label4, 1, 1)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)   
        # create a grey pixmap
        grey = QPixmap(width, height)
        grey.fill(QColor('darkGray'))
        # set the image image to the grey pixmap
        self.image_label.setPixmap(grey)
        self.image_label2.setPixmap(grey)
        self.image_label3.setPixmap(grey)
        self.image_label4.setPixmap(grey)
        
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        
        self.timer = QTimer()
        self.timer.setInterval(30)  # 30 мс между обновлениями кадров
        self.timer.timeout.connect(self.update_frames)
        self.timer.start()
        
        
    def update_frames(self):
        print("Update")
        ret, frame = self.cap.read()
        frame = cv2.resize(frame, (940, 520))
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
        frame = QPixmap.fromImage(image)
        self.image_label.setPixmap(frame)
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = MainWindow()
    a.show()
    sys.exit(app.exec_())