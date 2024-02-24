"""
TODO Hay que crear una ineterfaz con un menu que tenga opcciones para leer imagenesdesde una dirreccion o leer un pdf,
poder cambiar el idioma que leera, y la opccion de que lo copee al porta papeles admas de agregar una opccion para que
se leea en vos alta lo que halla escrita en el texto
"""
import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon, QPixmap, QPainter, QPen, QColor, QBrush
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar,
    QTextEdit,
    QVBoxLayout,
    QLayout,
)

import ctypes
import pyautogui

import cv2
import numpy as np
import pytesseract
import pyperclip

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
ancho, alto = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.actPoints = None
        self.capture = None
        self.setWindowTitle("My App")
        self.resize(400, 300)

        """TODO Para que pueda capturar una region de la pantalla hay que crear una segunda ventana transparente 
        en pantalla completa y con la que se pueda dibujar y actualizar un rectangulo en el que se enmarque el 
        area que se recortara para poder realizar el OCR, al realizar el ocr es importante que se minimize o desapresca 
        la ventana principal"""
        # self.setWindowOpacity(0.5) # Le da un valor de opacidad a la ventana completa
        # self.showFullScreen() # Sirve para que entre en modo pantalla completa
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint) # Sirve para quitar los bores (Botones de min max close)
        self.canvas = QPixmap(ancho, alto)
        self.canvas.fill(Qt.GlobalColor.white)

        self.label = QLabel()
        self.label.setPixmap(self.canvas)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.label)
        self.vertical_layout = QVBoxLayout(self.label)
        self.vertical_layout.setSpacing(0)
        # self.vertical_layout.setSizeConstraint(
        #     QLayout.SetDefaultConstraint
        # )
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.label.hide()

        self.Text = QTextEdit()
        self.vertical_layout.addWidget(self.Text)
        self.setCentralWidget(self.Text)

        button_action_full_screen = QAction(QIcon("bug.png"), "&OCR Pantalla completa", self)
        button_action_full_screen.setStatusTip("realizar el OCR a la pantalla completa")
        button_action_full_screen.triggered.connect(self.captureFullScren)

        button_action_capture_region = QAction(QIcon("bug.png"), "&OCR region", self)
        button_action_capture_region.setStatusTip("Realizar el OCR a una region")
        button_action_capture_region.triggered.connect(self.captureRegion)

        button_action2 = QAction(QIcon("bug.png"), "Your &button2", self)
        button_action2.setStatusTip("This is your button2")
        button_action2.triggered.connect(self.onMyToolBarButtonClick)
        # button_action2.setCheckable(True)
        # toolbar.addAction(button_action2)

        # toolbar.addWidget(QLabel("Hello"))
        # toolbar.addWidget(QCheckBox())

        self.setStatusBar(QStatusBar(self))

        self.menu = self.menuBar()

        file_menu = self.menu.addMenu("&Fill")
        file_menu.addAction(button_action2)
        file_menu.addSeparator()

        file_submenu = file_menu.addMenu("OCR")
        file_submenu.addAction(button_action_full_screen)
        file_submenu.addAction(button_action_capture_region)

    def mouseMoveEvent(self, e):
        # self.label.setText("mouseMoveEvent")

        # print(e.pos().x())
        self.actPoints = e.pos()

        self.drawRectangle(self.begPoints.x(), self.begPoints.y(),
                           self.actPoints.x() - self.begPoints.x(), self.actPoints.y() - self.begPoints.y())

    def mousePressEvent(self, e):
        # self.label.setText("mousePressEvent")
        # print(e.pos())
        if self.capture == 1:
            self.begPoints = e.pos()

    def mouseReleaseEvent(self, e):
        # self.label.setText("mouseReleaseEvent")
        x = self.begPoints.x()
        y = self.begPoints.y()
        w = e.pos().x() - self.begPoints.x()
        h = e.pos().y() - self.begPoints.y()

        if self.capture:
            self.showMinimized()
            # Toma la captura de pantalla
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            # screenshot.show()

            canvas = QPixmap(ancho, alto)
            canvas.fill(Qt.GlobalColor.white)
            self.label.setPixmap(canvas)

            self.setWindowOpacity(1)
            self.label.hide()
            self.showMaximized()
            # self.showNormal()
            self.menu.show()

            self.Text = QTextEdit()
            self.vertical_layout.addWidget(self.Text)
            self.setCentralWidget(self.Text)
            self.Text.show()

            self.resize(400, 300)

            texto = self.OCR(screenshot=screenshot)

            self.Text.setPlainText(texto)

            self.capture = 0

    def onMyToolBarButtonClick(self, s):
        print("click", s)
        # self.showMinimized()

    # FIXME hay que hacer que la ventana aparesca en su tmaño correcto
    def captureFullScren(self):
        self.showMinimized()
        screenshot = pyautogui.screenshot()

        # self.setWindowOpacity(1)
        # self.label.hide()
        self.showMaximized()
        # self.showNormal()
        self.menu.show()
        self.Text.show()
        self.resize(400, 300)

        texto = self.OCR(screenshot=screenshot)
        self.Text.setPlainText(texto)

    def captureRegion(self, s):
        self.setWindowOpacity(0.2)  # Le da un valor de opacidad a la ventana completa
        self.showFullScreen()  # Sirve para que entre en modo pantalla completa
        # self.label.hide()
        self.menu.hide()
        self.Text.hide()

        self.canvas = QPixmap(ancho, alto)
        self.canvas.fill(Qt.GlobalColor.white)

        self.label = QLabel()
        self.label.setPixmap(self.canvas)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.label)
        self.vertical_layout = QVBoxLayout(self.label)
        self.vertical_layout.setSpacing(0)

        self.setCentralWidget(self.label)
        self.label.show()
        self.capture = 1

    def drawRectangle(self, x, y, h, w):
        # canvas = self.label.pixmap()
        canvas = QPixmap(ancho, alto)
        canvas.fill(Qt.GlobalColor.white)
        painter = QPainter(canvas)
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor("#EB5160"))
        brush = QBrush(Qt.GlobalColor.black,
                       Qt.BrushStyle.SolidPattern)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(x, y, h, w)
        painter.end()
        self.label.setPixmap(canvas)

    def OCR(self, screenshot):
        gray = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2GRAY)
        threshold_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        text = pytesseract.image_to_string(threshold_img)
        # print(text)
        pyperclip.copy(text)

        return text


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()
