import sys
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import QTimer, Qt


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Движущаяся точка по окружности")
        self.setGeometry(100, 100, 600, 600)

        self.angle = 0  # начальный угол в радианах
        self.radius = 200  # радиус окружности
        self.speed = 2  # скорость движения точки (угловая скорость)

        self.timer = QTimer(self)  # таймер нужен для обновления позиции точки
        self.timer.timeout.connect(self.update_position)
        self.timer.start(20)  # обновление каждые 20 мс

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.darkBlue, 4, Qt.SolidLine))
        painter.drawEllipse(100, 100, 400, 400)

        center_x = self.width() // 2  # для точки
        center_y = self.height() // 2

        point_x = center_x + self.radius * math.cos(self.angle)  # вычисляем координаты точки на окружности
        point_y = center_y + self.radius * math.sin(self.angle)

        painter.setBrush(QColor(30, 250, 5))  # рисуем точку
        painter.drawEllipse(point_x - 5, point_y - 5, 10,
                            10)  # точка с радиусом 5

    def update_position(self):
        self.angle += self.speed * (math.pi / 180)  # увеличиваем/уменьшаем угол
        if self.angle >= 2 * math.pi:  # если угол больше 2π, сбрасываем его
            self.angle -= 2 * math.pi
        self.update()  # перерисовываем виджет



App = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(App.exec())