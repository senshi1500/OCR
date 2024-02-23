"""
TODO Hay que crear una ineterfaz con un menu que tenga opcciones para leer imagenesdesde una dirreccion
o sacar un screen shot de la pantalla como region o pantalla completa o leer un pdf, poder cambiar el idioma que leera,
y la opccion de que lo copee al porta papeles
"""
import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon, QPixmap, QPainter, QPen, QColor
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


user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
ancho, alto = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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

        # self.Text = QTextEdit()

        # toolbar = QToolBar("My main toolbar")
        # toolbar.setIconSize(QSize(16, 16))
        # self.addToolBar(toolbar)

        button_action = QAction(QIcon("bug.png"), "&Capturar region", self)
        button_action.setStatusTip("Capturar region")
        button_action.triggered.connect(self.captureRegion)
        button_action.setCheckable(True)
        # toolbar.addAction(button_action)

        # toolbar.addSeparator()

        button_action2 = QAction(QIcon("bug.png"), "Your &button2", self)
        button_action2.setStatusTip("This is your button2")
        button_action2.triggered.connect(self.onMyToolBarButtonClick)
        button_action2.setCheckable(True)
        # toolbar.addAction(button_action2)

        # toolbar.addWidget(QLabel("Hello"))
        # toolbar.addWidget(QCheckBox())

        self.setStatusBar(QStatusBar(self))

        self.menu = self.menuBar()

        file_menu = self.menu.addMenu("&File")
        file_menu.addAction(button_action)
        file_menu.addSeparator()

        file_submenu = file_menu.addMenu("Submenu")
        file_submenu.addAction(button_action2)

    def mouseMoveEvent(self, e):
        # self.label.setText("mouseMoveEvent")

        print(e.pos().x())
        self.actPoints = e.pos()

        self.drawRectangle(self.begPoints.x(), self.begPoints.y(),
                           self.actPoints.x()-self.begPoints.x(), self.actPoints.y()-self.begPoints.y())




    def mousePressEvent(self, e):
        # self.label.setText("mousePressEvent")
        print(e.pos())
        self.begPoints = e.pos()


    def mouseReleaseEvent(self, e):
        # self.label.setText("mouseReleaseEvent")
        print(e.pos())
        if self.capture:
            self.showMinimized()

            self.capture = 0



    def onMyToolBarButtonClick(self, s):
        print("click", s)
        # self.showMinimized()

    def captureRegion(self, s):
        self.setWindowOpacity(0.2)  # Le da un valor de opacidad a la ventana completa
        self.showFullScreen()  # Sirve para que entre en modo pantalla completa
        # self.label.hide()
        self.menu.hide()
        self.label.show()
        self.capture = 1

        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Sirve para quitar los bores (Botones de min max close)

    def drawRectangle(self, x, y, h, w):
        # canvas = self.label.pixmap()
        canvas = QPixmap(ancho, alto)
        canvas.fill(Qt.GlobalColor.white)
        painter = QPainter(canvas)
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor("#EB5160"))
        painter.setPen(pen)
        painter.drawRect(x, y, h, w)
        painter.end()
        self.label.setPixmap(canvas)


if __name__== '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()