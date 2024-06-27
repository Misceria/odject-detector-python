
from PyQt5 import QtCore, QtGui, QtWidgets, uic
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
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator

import skvideo.io as io
import ffmpeg



WEIGHTS = 'yolo//drone.pt'
MODEL = YOLO(WEIGHTS)

class MainWindow(QWidget):
    def __init__(self, videos=False, web_cams=False, ip_cams=False, raw_stream=False):
        super().__init__()
        self.setWindowTitle("Video Cameras View")
        #self.height, self.width = self.screen.size().height(), self.screen.size().width()
        uic.loadUi('main.ui', self)
        self.showMaximized()
        
        self.num_of_vids = self.comboBox.currentText()
        print(self.num_of_vids)
        
        self.caps = []
        cap = cv2.VideoCapture(0)
        self.caps.append(cap)
        iteration = 1
        if videos:
            self.caps=[cv2.VideoCapture('Imgs\DSC_1067.MOV'),
                       cv2.VideoCapture('Imgs\DSC_1068.MOV'),
                       cv2.VideoCapture('Imgs\DSC_1076.MOV'),
                       cv2.VideoCapture('Imgs\DSC_1080.MOV'),]
        elif web_cams:
            while cap.isOpened():
                cap = cv2.VideoCapture(iteration)
                self.caps.append(cap)
                iteration += 1
        elif ip_cams:
            self.caps=[
                cv2.VideoCapture("rtsp://192.168.1.168:554/stream_1"),
                cv2.VideoCapture("rtsp://admin:YWRBUX@192.168.1.169:554")
            ]
        elif raw_stream:
            self.caps=[
                cv2.VideoCapture("PLACE_HERE_IP_CAMERA") # Change THIS LINE 
            ]
            caps_dict = [{
                "fps": 60,
                "width": 1920,
                "height": 1080
            }]
            self.caps[0].set(cv2.CAP_PROP_FRAME_WIDTH, caps_dict[0]['width']) # Change to your WIDTH
            self.caps[0].set(cv2.CAP_PROP_FRAME_HEIGHT, caps_dict[0]['height'])# Change to your HEIGHT
            
            
        print(self.gridLayout.geometry().topLeft())
        print(self.gridLayout.geometry().bottomRight())
        
        #self.getCamerasGrid()
        self.width = 480*2
        self.height = 270*2
        # create vid 1
        self.image_label = QLabel(self)
        # create vid 2
        self.image_label2 = QLabel(self)
        # create vid 3
        self.image_label3 = QLabel(self)
        # create vid 4
        self.image_label4 = QLabel(self)

        # create a vertical boxs layout and add the two labels
        vbox = self.gridLayout
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
        # set the vbox layout as the widgets layouts
        self.setLayout(vbox)   
        # create a grey pixmap
        grey = QPixmap(self.width, self.height)
        grey.fill(QColor('darkGray'))
        # set the image image to the grey pixmap
        self.image_label.setPixmap(grey)
        self.image_label2.setPixmap(grey)
        self.image_label3.setPixmap(grey)
        self.image_label4.setPixmap(grey)
        self.labels = [self.image_label, self.image_label2,
                       self.image_label3, self.image_label4]
        
        self.image_label.mousepressevent = self.test
        self.image_label2.mousepressevent = self.test
        self.image_label3.mousepressevent = self.test
        self.image_label4.mousepressevent = self.test
    
        
        #self.cap = cv2.VideoCapture(0)
        #ret, frame = self.cap.read()
        
        self.timer = QTimer()
        self.timer.setInterval(1)  # 30 мс между обновлениями кадров
        self.timer.timeout.connect(self.update_frames)
        self.timer.start()
        
         
        print(f"Label 1 coors = ({self.image_label.geometry()}, {self.image_label.y()})")
        print(f"Label 2 coors = ({self.image_label2.geometry()}, {self.image_label2.y()})")
        print(f"Label 3 coors = ({self.image_label3.geometry()}, {self.image_label3.y()})")
        print(f"Label 4 coors = ({self.image_label4.geometry()}, {self.image_label4.y()})")
        
        
    
    def test(self):
        print(f"{self} clicked")
        
    
    def getCamerasGrid(self, num_of_cameras):
        max_videos_in_row = 3
        if num_of_cameras == 1:
            self.labels = [QLabel(self)]
            vbox = QGridLayout()
            vbox.setSpacing(0)
            vbox.setHorizontalSpacing(0)
            vbox.setVerticalSpacing(0)
            vbox.addWidget(self.labels[0], 0, 0)
            grey = QPixmap(self.width, self.height)
            grey.fill(QColor('darkGray'))
            for x in self.labels:
                x.setPixmap(grey)
            return self.height, self.width
        
    
        
    def mousePressEvent(self, QMouseEvent):
        print(QMouseEvent.pos(), self.image_label.pos(), (self.image_label.x(), self.image_label.x()+self.width), (self.image_label.y(), self.image_label.y()+self.height))
        print(self.image_label2.pos()) 
        
        
    def update_frames(self, stream=False, raw_stream=False):
        #print("Update") 
        self.num_of_vids = self.comboBox.currentText()
        
        
        if raw_stream:
            for cam_number in range(len(self.caps)):
                    ret, frame = self.caps[cam_number].read()
                    res = MODEL.predict(frame, imgsz=640, save=False)
                    for r in res:
                        try:
                            annotator = Annotator(frame)
                            
                            boxes = r.boxes
                            for box in boxes:
                                
                                b = box.xyxy[0]  # get box coordinates in (left, top, right, bottom) format
                                c = box.cls
                                annotator.box_label(b, MODEL.names[int(c)])
                        except: 
                            pass
                    try:
                        frame = cv2.resize(frame, (940, 520))
                        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
                        frame = QPixmap.fromImage(image)
                        self.labels[cam_number].setPixmap(frame)
                    except Exception as e:
                        #print(f"Image {cam_number} not read")
                        pass     
        else:
            if stream:
                res = MODEL.predict("cams.streams", stream=True, save=False)
                print(res)
                iter = 0
                for x in res:
                    iter +=1
                    if iter % 2 == 0:
                        cam_number = 0
                    else:
                        cam_number = 1
                    
                    #ret, frame = self.caps[cam_number].read()
                    try:
                        annotator = Annotator(x.orig_img)
                        
                        boxes = x.boxes
                        for box in boxes:
                            
                            b = box.xyxy[0]  # get box coordinates in (left, top, right, bottom) format
                            c = box.cls
                            annotator.box_label(b, MODEL.names[int(c)])
                    except:
                        pass
                    try:
                        frame = cv2.resize(x.orig_img, (940, 520))
                        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
                        frame = QPixmap.fromImage(image)
                        self.labels[cam_number].setPixmap(frame)
                    except Exception as e:
                        #print(f"Image {cam_number} not read")
                        pass
            else:
                for cam_number in range(len(self.caps)):
                    ret, frame = self.caps[cam_number].read()
                    res = MODEL.predict(frame, save=False)
                    for r in res:
                        try:
                            annotator = Annotator(frame)
                            
                            boxes = r.boxes
                            for box in boxes:
                                
                                b = box.xyxy[0]  # get box coordinates in (left, top, right, bottom) format
                                c = box.cls
                                annotator.box_label(b, MODEL.names[int(c)])
                        except:
                            pass
                    try:
                        frame = cv2.resize(frame, (940, 520))
                        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
                        frame = QPixmap.fromImage(image)
                        self.labels[cam_number].setPixmap(frame)
                    except Exception as e:
                        #print(f"Image {cam_number} not read")
                        pass
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = MainWindow(videos=True, web_cams=False, ip_cams=False, raw_stream=False)
    a.show()
    sys.exit(app.exec_())