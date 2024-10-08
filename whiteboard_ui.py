import logging as log
import sys
import threading
import time

import cv2
import numpy as np
import pymupdf
import win32com.client
from PIL import Image, ImageQt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QSize, Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QCursor, QImage, QPixmap
from PyQt5.QtWidgets import (QApplication, QFileSystemModel, QHBoxLayout,
                             QLabel, QMessageBox, QPushButton,
                             QStyledItemDelegate, QTreeView, QVBoxLayout,
                             QWidget)

# from smart_presentation import PresentationThread
from vwb import VideoThread

log.basicConfig(level=log.INFO)

logg = log.getLogger(__name__)

class FunThread(QThread):

    def __init__(self, frame):
        super().__init__()
        self.frame = frame
        pass

    def run(self) -> None:

        self.frame.save("vwb_data.jpg","JPG")

        log.info("Image saved Successfully!")
    
    pass


class WhiteBoardUI(QWidget):

    _vwb_width = 1280
    _vwb_height = 720

    _frame = None

    def __init__(self):
        super().__init__()
        self.custom_cursor = self.create_custom_cursor()  # Create custom cursor on init
        self.setupUi()
        pass

    def setupUi(self):
        h = 1080
        w = 1920
        self.setGeometry(0,0,w,h)
        self.setWindowTitle("Virtual Writing Board")

        self.setObjectName("Whiteboard_GUI")
        self.resize(1920, 1080)
        

        self.whiteboard = QtWidgets.QLabel(self)
        self.whiteboard.setGeometry(QtCore.QRect(10, 50, self._vwb_width, self._vwb_height))
        self.whiteboard.setFrameShape(QtWidgets.QFrame.Box)
        self.whiteboard.setFrameShadow(QtWidgets.QFrame.Raised)
        self.whiteboard.setObjectName("whiteboard")
        # Set initial cursor for QLabel
        self.whiteboard.setCursor(self.custom_cursor)

        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(1580, 10, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")

        self.Red = QtWidgets.QPushButton(self)
        self.Red.setGeometry(QtCore.QRect(1580, 70, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.Red.setFont(font)
        self.Red.clicked.connect(self.changePenColor)
        self.Red.setObjectName("Red")

        self.Green = QtWidgets.QPushButton(self)
        self.Green.setGeometry(QtCore.QRect(1580, 130, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.Green.setFont(font)
        self.Green.clicked.connect(self.changePenColor)
        self.Green.setObjectName("Green")

        self.Blue = QtWidgets.QPushButton(self)
        self.Blue.setGeometry(QtCore.QRect(1580, 190, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.Blue.setFont(font)
        self.Blue.clicked.connect(self.changePenColor)
        self.Blue.setObjectName("Blue")

        self.Eraser = QtWidgets.QPushButton(self)
        self.Eraser.setGeometry(QtCore.QRect(1580, 250, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.Eraser.setFont(font)
        self.Eraser.clicked.connect(self.changePenColor)
        self.Eraser.setObjectName("Eraser")

        self.Clear_Screen = QtWidgets.QPushButton(self)
        self.Clear_Screen.setGeometry(QtCore.QRect(1580, 310, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.Clear_Screen.setFont(font)
        self.Clear_Screen.setObjectName("Clear_Screen")

        self.save_data = QtWidgets.QPushButton(self)
        self.save_data.setGeometry(QtCore.QRect(1580, 310, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.save_data.setFont(font)
        self.save_data.clicked.connect(self.saveData)
        self.save_data.setObjectName("Save Data")

        self.start_vwb = QtWidgets.QPushButton(self)
        self.start_vwb.setGeometry(QtCore.QRect(1580, 370, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.start_vwb.setFont(font)
        self.start_vwb.clicked.connect(self.startVWB)
        self.start_vwb.setObjectName("Start VWB")

        self.stop_vwb = QtWidgets.QPushButton(self)
        self.stop_vwb.setGeometry(QtCore.QRect(1580, 430, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.stop_vwb.setFont(font)
        self.stop_vwb.clicked.connect(self.stopVWB)
        self.stop_vwb.setObjectName("Stop VWB")
        
        self.Camera = QtWidgets.QLabel(self)
        self.Camera.setGeometry(QtCore.QRect(1500, 700, 380, 201))
        self.Camera.setObjectName("Camera")

        # self.startVWB()

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        pass

    def upgrade_frames(self,frame_data):
        camera_view_width = 380
        camera_view_height = 240

        self._frame = frame_data["vwb_frame"]
        self.whiteboard.setPixmap(frame_data["vwb_frame"])
        
        camera_frame_pixmap = frame_data["camera_frame"]

        x, y = frame_data["cursor"]

        # local_cursor_pos = self.mapToGlobal(self.pos())
        # QCursor.setPos(local_cursor_pos.x() + x, local_cursor_pos.y() + y)
        
        new_size = QSize(camera_view_width, camera_view_height)
        resized_frame_pixmap = camera_frame_pixmap.scaled(new_size, Qt.KeepAspectRatio)
        self.Camera.setPixmap(resized_frame_pixmap)
        pass


    def create_custom_cursor(self):
        # Load your custom cursor image (replace 'cursor.png' with your image path)
        cursor_image = cv2.imread('assets\pencil_24.png', cv2.IMREAD_UNCHANGED)  # Read image with alpha channel
        height, width, _ = cursor_image.shape  # Get image dimensions

        # Convert cv2 image to QImage for PyQt compatibility
        qimage = QtGui.QImage(cursor_image.data, width, height, QtGui.QImage.Format_ARGB32)
        qpixmap = QtGui.QPixmap.fromImage(qimage)  # Convert QImage to QPixmap

        # Create custom cursor with hotspot (adjust hotspot based on your cursor image)
        hotspot = QtCore.QPoint(int(width / 2), int(height / 2))
        return QCursor(qpixmap, int(1), int(height))
        

    def startVWB(self):
        self.vwb = VideoThread(1)
        self.vwb.frame_signal.connect(self.upgrade_frames)
        self.vwb.start()
        pass


    def stopVWB(self):
        if self.vwb:
            self.vwb.stop()
            self.vwb.quit()
            self.vwb.wait()
            print("Thread has stopped")
            self.vwb = None
        pass

    def presenter(self,path):
        slide_path = path

        try:
            
            image = cv2.imread(slide_path)
            log.info("img read")

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(np.asarray(image), mode='RGB')
            qt_img = ImageQt.ImageQt(image)
            qpixmap = QPixmap.fromImage(qt_img)

            height = 720
            width = 1280

            new_size = QSize(width, height)
            resized_frame_pixmap = qpixmap.scaled(new_size, Qt.KeepAspectRatio)
            
            log.info("converted")

            return resized_frame_pixmap
            pass
        except Exception as e:
            print(f"Error loading or converting image: {e}")
            return None

        # return qpixmap
    pass

    def saveSlides(self,pdf_path):
        output_format = 18  # 17 corresponds to PNG format

        pdf_doc = pymupdf.open(pdf_path)
        self.total_slides = 0

        for page_num in range(len(pdf_doc)):  # Loop through each page (slide)
            self.total_slides = self.total_slides + 1
            page = pdf_doc[page_num]
            zoom = 2
            slide_image = page.get_pixmap(matrix=pymupdf.Matrix(zoom,zoom))  # Extract the page image
            slide_path = f"cache/slide_{page_num + 1}.png"
            slide_image.save(slide_path)
        pass

    def pptSetup(self,path):
        self.Application = win32com.client.Dispatch("PowerPoint.Application")
        self.Presentation = self.Application.Presentations.Open(path)
        print(self.Presentation.Name)

        pdf_path = "./cache/presen1.pdf"
        self.Presentation.SaveAs(pdf_path, FileFormat=32)

        self.saveSlides(pdf_path)
        log.info("File saved as PDF.")
        pass

    def ppts(self,path):
        self.pptSetup(path)
        time.sleep(5)
        self.vwb = VideoThread(0)
        self.vwb.frame_signal.connect(self.upgrade_slides)
        self.vwb.start()
        
        pass

    def upgrade_slides(self,frame_data):
        slide_num = frame_data["slide_num"]
        slide_pixmap = self.presenter(f"cache/slide_{slide_num}.png")

        self.whiteboard.setPixmap(slide_pixmap)
        log.info("slide is on board")
        pass

    def clearScreen(self):
        pass

    def saveData(self):
        log.info("Inside the saveData method")
        try:
            obj = FunThread(self._frame)
            obj.start()
            obj.quit()
            obj.wait()

            message_box = QMessageBox(self)  # Replace 'self' with your main window reference
            message_box.setWindowTitle("File Saved!")
            message_box.setText("File saved successfully!")
            # message_box.setButtons(QMessageBox.Ok | QMessageBox.Cancel)  # Set available buttons

            message_box.exec_()

            QTimer.singleShot(8000,message_box.close())
            pass
        except:
            log.info("Error occured while saving data.")
            pass

        def save_task():
            qimage = self._frame.toImage()

            imageData = qimage.bits().asstring()

            width = qimage.width()
            height = qimage.height()
            channels = 4

            opencv_image = cv2.cvtColor(cv2.fromstring(imageData, dtype=np.unit8, size=(width, height), channels=channels), cv2.COLOR_BGRA2RGB)

            cv2.imwrite("vwb_data.jpg", opencv_image)

            log.info("Image saved Successfully!")
            pass
        pass

    def changePenColor(self):
        clicked_button_text = self.sender().text()

        if clicked_button_text == "Red":
            print("Red button clicked!")
            self.vwb.drawColor = (0, 0, 255)
            pass
        elif clicked_button_text == "Green":
            print("Green button clicked!")
            self.vwb.drawColor = (0, 255, 0)
            pass
        elif clicked_button_text == "Blue":
            print("Blue button clicked!")
            self.vwb.drawColor = (255, 0, 0)
            pass
        elif clicked_button_text == "Eraser":
            print("Eraser is activated!")
            self.vwb.drawColor = (255, 255, 255)
            pass
        else:
            print("Unexpected button clicked:", clicked_button_text)
            pass
        pass

    def set_image(self, image):
        self.Camera.setPixmap(QtGui.QPixmap.fromImage(image))

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.whiteboard.setText(_translate("Whiteboard_GUI", "TextLabel"))
        self.pushButton.setText(_translate("Whiteboard_GUI", "Pencil"))
        self.Red.setText(_translate("Whiteboard_GUI", "Red"))
        self.Green.setText(_translate("Whiteboard_GUI", "Green"))
        self.Blue.setText(_translate("Whiteboard_GUI", "Blue"))
        self.Eraser.setText(_translate("Whiteboard_GUI", "Eraser"))
        self.Clear_Screen.setText(_translate("Whiteboard_GUI", "Clear Screen"))
        self.save_data.setText(_translate("Whiteboard_GUI", "Save Data"))
        self.start_vwb.setText(_translate("Whiteboard_GUI", "Start VWB"))
        self.stop_vwb.setText(_translate("Whiteboard_GUI", "Stop VWB"))
        self.Camera.setText(_translate("Whiteboard_GUI", "Camera"))


class WhiteBoard(QWidget):
    def __init__(self) -> None:
        super().__init__()
        pass

    def ppts(self,path):
        pass

    def virtualWritting(self):
        self.ui = WhiteBoardUI()
        self.ui.show()
        videoThread = VideoThread()

        videoThread.frame_signal.connect(self.ui.upgrade_frames)
        videoThread.start()
        pass
    pass

if __name__ == "__main__":
    print(cv2.__version__)
    app = QtWidgets.QApplication(sys.argv)
    ui = WhiteBoardUI()
    ui.show()
    sys.exit(app.exec_())
