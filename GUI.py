#  TODO I have to refactor it

import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon, QPixmap, QPainter, QPen, QColor, QBrush, QShortcut, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QLayout,
    QFileDialog,
    QDialog,
    QPushButton,
    QLineEdit,
    QDialogButtonBox

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

class Dialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(Dialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("Abouth")
        self.setFixedSize(350, 200)

        self.but_exit = QPushButton("Ok")
        self.text_About = QLabel()

        self.text_About.setText("""
        Abouth this aplications
        
        This apliction is a simple experiment with OCR whith Python
        """)

        self.text_About.setAlignment(self.text_About.alignment().AlignCenter)
        self.but_exit.clicked.connect(self.Exit)

        self.vertical_layout_search = QVBoxLayout(self)
        self.vertical_layout_search.addWidget(self.text_About)
        self.vertical_layout_search.addWidget(self.but_exit)

    def Exit(self):
        self.close()





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.name = None
        self.actPoints = None
        self.capture = None
        self.setWindowTitle("OCR")
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

        self.Text.setStyleSheet('''
                                        QTextEdit {
                                            font: 10pt "Consolas";
                                            background-color: white;
                                            color: black;
                                        }
                                        ''')

        button_action_full_screen = QAction("&OCR Pantalla completa", self)
        button_action_full_screen.setStatusTip("realizar el OCR a la pantalla completa")
        button_action_full_screen.triggered.connect(self.captureFullScren)

        button_action_capture_region = QAction("&OCR region", self)
        button_action_capture_region.setStatusTip("Realizar el OCR a una region")
        button_action_capture_region.triggered.connect(self.captureRegion)

        save_action = QAction("Save", self)
        save_action.setStatusTip("Save the document")
        save_action.triggered.connect(self.SaveDocument)
        save_action.setShortcut(QKeySequence("Ctrl+S"))


        save_as_action = QAction("Save as", self)
        save_as_action.setStatusTip("Save the document whit a name")
        save_as_action.triggered.connect(self.SaveAsDocument)
        save_as_action.setShortcut(QKeySequence("Ctrl+Alt+S"))
        # save_action.setCheckable(True)
        # toolbar.addAction(save_action)

        Exit_action = QAction("Exit", self)
        Exit_action.setStatusTip("Save the document whit a diferent name")
        Exit_action.triggered.connect(self.ExitA)
        Exit_action.setShortcut(QKeySequence("Ctrl+E"))# TODO Ponerr los Shorcuts restantes

        # toolbar.addWidget(QLabel("Hello"))
        # toolbar.addWidget(QCheckBox())

        undo_action = QAction("Undo", self)
        undo_action.triggered.connect(self.UndoText)
        undo_action.setShortcut(QKeySequence("Ctrl+Z"))

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.CopyText)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))

        cut_action = QAction("Cut", self)
        cut_action.triggered.connect(self.CutText)
        cut_action.setShortcut(QKeySequence("Ctrl+X"))

        paste_action = QAction("page", self)
        paste_action.triggered.connect(self.PasteText)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))

        clear_action = QAction("Clear all", self)
        clear_action.setStatusTip("borra todo")
        clear_action.triggered.connect(self.ClearAll)
        clear_action.setShortcut(QKeySequence("Ctrl+B"))

        # search_action = QAction("Search", self)
        # search_action.setStatusTip("find a word")
        # search_action.triggered.connect(self.Search)
        # search_action.setShortcut(QKeySequence("Ctrl+F"))
        #
        # remplace_action = QAction("Remplace", self)
        # remplace_action.setStatusTip("remplace a word")
        # remplace_action.triggered.connect(self.Remplace)
        # remplace_action.setShortcut(QKeySequence("Ctrl+R"))
        #
        # options_action = QAction("Options", self)
        # options_action.triggered.connect(self.onMyToolBarButtonClick)

        abouth_action = QAction("Abouth", self)
        abouth_action.setStatusTip("Information abouth this program")
        abouth_action.triggered.connect(self.Abouth)

        self.setStatusBar(QStatusBar(self))

        self.menu = self.menuBar()

        file_menu = self.menu.addMenu("&Fill")
        OCR_menu = self.menu.addMenu("&OCR")
        Edition_menu = self.menu.addMenu(
            "&Edition")  # TODO Agregar funcinalidades buscar y remplazar
        help_menu = self.menu.addMenu("&Help")

        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(Exit_action)

        OCR_menu.addAction(button_action_full_screen)
        OCR_menu.addAction(button_action_capture_region)

        Edition_menu.addAction(undo_action)
        Edition_menu.addSeparator()
        Edition_menu.addAction(copy_action)
        Edition_menu.addAction(cut_action)
        Edition_menu.addAction(paste_action)
        Edition_menu.addAction(clear_action)
        # Edition_menu.addSeparator()
        # Edition_menu.addAction(search_action)
        # Edition_menu.addAction(remplace_action)

        # help_menu.addAction(options_action)
        help_menu.addAction(abouth_action)

        # file_submenu = file_menu.addMenu("OCR")
        # file_submenu.addAction(button_action_full_screen)
        # file_submenu.addAction(button_action_capture_region)

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

        # Cambia las cordenadas del rectangulo para que no haya errores en el Screenshot

        if w < 0:
            w = w*(-1)
            x = e.pos().x()
        if h < 0:
            h = h*(-1)
            y = e.pos().y()

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

    def SaveDocument(self):
        if self.name is None:
            dialog = QFileDialog(self)
            self.name, filter = dialog.getSaveFileName(self, "select directory", "C:\\", "text (*.txt)")
            Title = self.name.split('/')
            print(Title[-1])
            self.Text.setDocumentTitle(Title[-1])

        f = open(f'{self.name}', 'w')
        f.write(self.Text.toPlainText())
        f.close()

    def SaveAsDocument(self):
        dialog = QFileDialog(self)
        self.name, filter = dialog.getSaveFileName(self, "select directory", "C:\\", "text (*.txt)")
        Title = self.name.split('/')
        print(Title[-1])
        self.Text.setDocumentTitle(Title[-1])

        f = open(f'{self.name}', 'w')
        f.write(self.Text.toPlainText())
        f.close()

    def ExitA(self):
        self.close()

    def UndoText(self):
        self.Text.undo()

    def CopyText(self):
        self.Text.copy()

    def CutText(self):
        self.Text.cut()

    def PasteText(self):
        self.Text.paste()

    def ClearAll(self):
        self.Text.clear()

    # def Search(self): # TODO Agregar la opccion de buscar, remplazar y opcciones
    #     pass

    # def Remplace(self):
    #     pass

    # def Options(self):
    #     pass

    def Abouth(self):
        dialog = Dialog(self)
        dialog.show()

    def captureFullScren(self):
        self.showMinimized()
        screenshot = pyautogui.screenshot()


        self.showMaximized()

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

        # texto = self.OCR(screenshot=screenshot)
        # self.Text.setPlainText(texto)


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
