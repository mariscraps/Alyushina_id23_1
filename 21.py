import sys
import random
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QTimer


# функция для загрузки данных столбов из файла JSON
def load_poles_data(file_path='poles_data.json'):
    if os.path.exists(
            file_path):  # проверяем, существует ли файл с данными столбов
        with open(file_path, 'r') as file:  # открываем файл для чтения
            try:
                data = json.load(file)  # загружаем данные из файла
                print("Data loaded from JSON:",
                      data)  # выводим данные для проверки
                return data  # возвращаем загруженные данные
            except json.JSONDecodeError:  # если файл поврежден или содержит ошибки
                print(
                    "Error reading JSON file. Creating default data.")  # выводим сообщение об ошибке
    return create_default_poles_data(
        file_path)  # если файл не существует или ошибка, создаем данные по умолчанию


# функция для создания данных по умолчанию и записи их в JSON
def create_default_poles_data(file_path):
    default_data = [{"x": x, "strength": 5} for x in range(150, 750,
                                                           120)]  # создаем список столбов с интервалом 120
    with open(file_path, 'w') as file:  # открываем файл для записи
        json.dump(default_data, file, indent=4)  # записываем данные в файл
    print("Default data created:", default_data)  # выводим данные для проверки
    return default_data  # возвращаем данные по умолчанию


# Класс птиц
class Bird:
    def __init__(self, x, y, speed):
        self.x = x  # координата X начального положения птицы
        self.y = y  # координата Y начального положения птицы
        self.speed_x = random.uniform(1, 3) * (
            -1 if random.random() < 0.5 else 1)  # скорость по X, случайная с направлением
        self.speed_y = speed  # скорость по Y
        self.on_pole = False  # флаг, сидит ли птица на столбе
        self.sitting_time = random.randint(20,
                                           60)  # время, которое птица сидит на столбе (в тиках таймера от 1 до 3 секунд)
        self.sitting_on_pole_time = 0  # время, проведенное на текущем столбе
        self.moving_up = False  # флаг, движется ли птица вверх
        self.moving_to_another_pole = False  # новая переменная для пересадки на другой столб
        self.target_pole_coords = None  # координаты жердочки, на которую летит птица
        self.random_offset_x = 0  # смещение по X для разнообразия

    def move_to(self, post_x, perch_y):
        self.x += (post_x - self.x) * 0.05  # плавное движение к цели по X
        self.y += (perch_y - self.y) * 0.05  # плавное движение к цели по Y

    def move(self):
        if self.on_pole:  # если птица сидит на столбе
            self.sitting_on_pole_time += 1  # увеличиваем время сидения
            if self.sitting_on_pole_time >= self.sitting_time:  # если время сидения истекло
                self.on_pole = False  # птица покидает столб
                if random.random() < 0.5:  # 50% шанс, что она улетит
                    self.moving_up = True  # птица начинает лететь вверх
                else:
                    self.moving_to_another_pole = True  # птица перелетает на другой столб
                    self.find_new_pole()  # ищем новую жердочку

        elif self.moving_up:  # если птица летит вверх
            self.y -= self.speed_y  # уменьшаем координату Y (движение вверх)
            self.x += self.speed_x  # двигаем по X с текущей скоростью
            if self.y < -10:  # если птица улетела за пределы экрана
                self.reset_position()  # сбрасываем позицию

        elif self.moving_to_another_pole and self.target_pole_coords:  # если птица летит на другую жердочку
            self.move_to(self.target_pole_coords[0] + self.random_offset_x,
                         self.target_pole_coords[
                             1] - 50)  # двигаем птицу к жердочке
            if abs(self.y - (self.target_pole_coords[
                                 1] - 50)) < 5:  # если птица приблизилась к цели
                self.on_pole = True  # птица села на жердочку
                self.y = self.target_pole_coords[
                             1] - 50  # устанавливаем точные координаты
                self.x = self.target_pole_coords[
                             0] + self.random_offset_x  # устанавливаем точные координаты по X
                self.sitting_on_pole_time = 0  # обнуляем время сидения
                self.moving_to_another_pole = False  # прекращаем движение

        else:  # если птица просто падает вниз
            self.y += self.speed_y  # увеличиваем координату Y (движение вниз)
            if self.target_pole_coords:  # если есть цель (жердочка)
                self.move_to(self.target_pole_coords[0] + self.random_offset_x,
                             self.target_pole_coords[
                                 1] - 50)  # двигаем птицу к цели

            if self.target_pole_coords and abs(
                    self.y - (self.target_pole_coords[
                                  1] - 50)) < 5:  # если достигли цели
                self.on_pole = True  # птица садится на жердочку
                self.y = self.target_pole_coords[1] - 50  # точная координата Y
                self.x = self.target_pole_coords[
                             0] + self.random_offset_x  # точная координата X

    def reset_position(self):
        self.x = random.randint(100,
                                700)  # устанавливаем случайное положение по X
        self.y = random.randint(-50,
                                -10)  # устанавливаем случайное положение по Y (над экраном)
        self.on_pole = False  # птица не на столбе
        self.moving_up = False  # птица не движется вверх
        self.moving_to_another_pole = False  # птица не летит к другой жердочке
        self.sitting_on_pole_time = 0  # обнуляем время сидения
        self.target_pole_coords = None  # очищаем цель жердочки

    def find_new_pole(self):
        if SimulationWindow.instance.perch_coords:  # если есть доступные жердочки
            new_perch = random.choice(
                SimulationWindow.instance.perch_coords)  # выбираем случайную жердочку
            self.target_pole_coords = new_perch  # устанавливаем её как цель
            self.random_offset_x = random.uniform(-30,
                                                  30)  # добавляем случайное смещение по X

        else:
            self.moving_up = True  # если нет жердочек, птица улетает вверх


class Pole:
    def __init__(self, x, strength):
        self.x = x  # положение столба по X
        self.y = 550  # положение столба по Y (фиксированное значение)
        self.strength = strength  # максимальная нагрузка, которую столб может выдержать
        self.current_load = 0  # текущая нагрузка на столб (количество сидящих птиц)
        self.fallen = False  # флаг, упал ли столб
        self.recovery_time = 30  # время восстановления столба после падения (2.5 секунды)
        self.recovery_timer = 0  # таймер восстановления столба

    def fall(self):
        self.fallen = True  # устанавливаем флаг падения столба
        self.recovery_timer = self.recovery_time  # запускаем таймер восстановления

    def recover(self):
        self.fallen = False  # столб восстановлен
        self.current_load = 0  # сбрасываем текущую нагрузку на столб


class SimulationWindow(QWidget):
    instance = None  # статическая переменная для создания синглтона

    def __init__(self):
        super().__init__()
        SimulationWindow.instance = self  # создаем единственный экземпляр SimulationWindow (синглтон)
        self.setWindowTitle(
            'Birds and Poles Simulation')  # устанавливаем заголовок окна
        self.setGeometry(100, 100, 800, 600)  # задаем размеры и положение окна

        # загружаем данные из JSON и создаем столбы
        poles_data = load_poles_data()
        self.poles = [Pole(pole["x"], pole["strength"]) for pole in
                      poles_data]  # создаем столбы по данным из файла

        self.birds = []  # список птиц
        self.perch_coords = []  # список координат жердочек (верхушки столбов)
        self.update_perch_coords()  # инициализируем координаты жердочек

        self.timer = QTimer(self)  # таймер для обновления симуляции
        self.timer.timeout.connect(
            self.update_simulation)  # связываем с функцией обновления
        self.timer.start(
            50)  # запускаем таймер с интервалом 50 мс (20 обновлений в секунду)

        self.spawn_timer = QTimer(self)  # таймер для появления новых птиц
        self.spawn_timer.timeout.connect(
            self.spawn_birds)  # связываем с функцией создания птиц
        self.spawn_timer.start(1000)  # создаем птиц каждую секунду

        self.new_pole_timer = QTimer(
            self)  # таймер для появления нового столба
        self.new_pole_timer.timeout.connect(
            self.create_new_pole)  # связываем с функцией создания столбов
        self.new_pole_timer.start(
            2000)  # новые столбы появляются каждые 2 секунды

    def spawn_birds(self):
        for _ in range(20):  # создаем 20 новых птиц
            bird = Bird(random.randint(100, 700), random.randint(-50, -10),
                        random.uniform(3, 6))  # птицы появляются случайно
            self.birds.append(bird)  # добавляем новую птицу в список

    def update_simulation(self):
        for pole in self.poles:  # обновляем состояние столбов
            if not pole.fallen:  # если столб не упал
                # подсчитываем количество птиц, сидящих на столбе
                pole.current_load = sum(1 for bird in self.birds if
                                        bird.on_pole and bird.target_pole_coords == (
                                            pole.x, pole.y))
                if pole.current_load >= pole.strength:  # если нагрузка превышает прочность столба
                    pole.fall()  # столб падает
                    self.handle_fallen_pole(
                        pole)  # обрабатываем падение столба

            elif pole.fallen:  # если столб упал
                pole.recovery_timer -= 1  # уменьшаем таймер восстановления
                if pole.recovery_timer <= 0:  # когда таймер истекает
                    # перемещаем столб на случайную позицию после паузы, проверяя безопасное расстояние
                    new_x = self.find_safe_pole_position()  # находим безопасное место для нового столба
                    pole.x = new_x  # перемещаем столб на новое место
                    pole.recover()  # восстанавливаем столб
                    self.update_perch_coords()  # обновляем список координат жердочек

        for bird in self.birds:  # обновляем положение каждой птицы
            bird.move()  # двигаем птицу

            # если птица покинула жердочку и не летит вверх, ищем ближайшую
            if not bird.on_pole and not bird.moving_up and bird.target_pole_coords is None:
                if self.perch_coords:  # если есть доступные жердочки
                    closest_perch = min(self.perch_coords,
                                        key=lambda coords: abs(
                                            bird.x - coords[
                                                0]))  # находим ближайшую жердочку
                    bird.target_pole_coords = closest_perch  # устанавливаем её как цель
                    bird.random_offset_x = random.uniform(-30,
                                                          30)  # добавляем случайное смещение по X

        self.birds = [bird for bird in self.birds if
                      bird.y > -10]  # удаляем птиц, улетевших за пределы экрана
        self.update()  # перерисовываем экран

    def find_safe_pole_position(self):
        """находит безопасное место для нового столба, не задев другие."""
        max_attempts = 100  # максимальное количество попыток
        for _ in range(max_attempts):
            new_x = random.randint(150,
                                   750)  # генерируем случайное положение по X
            # проверяем, что расстояние до других столбов достаточно велико
            if all(abs(new_x - pole.x) > 60 for pole in self.poles if
                   not pole.fallen):  # минимум 60 пикселей между столбами
                return new_x  # если место безопасно, возвращаем его
        return random.randint(150,
                              750)  # если не удалось найти безопасное место, выбираем случайное

    def handle_fallen_pole(self, fallen_pole):
        """обработка падения столба: удаляем его из доступных для птиц и ждем восстановления"""
        self.perch_coords = [(x, y) for (x, y) in self.perch_coords if
                             x != fallen_pole.x]  # убираем столб из списка жердочек

        for bird in self.birds:  # обрабатываем каждую птицу
            if bird.on_pole and bird.target_pole_coords == (
                    fallen_pole.x,
                    fallen_pole.y):  # если птица на упавшем столбе
                bird.on_pole = False  # птица покидает столб
                bird.target_pole_coords = None  # убираем цель жердочки

                # 50% шанс перелета на другую жердочку
                if random.random() < 0.5 and self.perch_coords:
                    bird.moving_to_another_pole = True  # птица летит на другую жердочку
                    bird.find_new_pole()  # ищем новую жердочку для перелета
                else:
                    bird.moving_up = True  # если не перелетает, улетает вверх

            if not bird.on_pole and bird.target_pole_coords == (
                    fallen_pole.x, fallen_pole.y):  # если цель - упавший столб
                bird.target_pole_coords = None  # очищаем цель

                # 50% шанс перелета на другую жердочку
                if random.random() < 0.5 and self.perch_coords:
                    bird.moving_to_another_pole = True  # птица летит на другую жердочку
                    bird.find_new_pole()  # ищем новую жердочку для перелета
                else:
                    bird.moving_up = True  # если не перелетает, улетает вверх

    def update_perch_coords(self):
        """обновляем список координат жердочек (вершины столбов)"""
        self.perch_coords = [(pole.x, pole.y) for pole in self.poles if
                             not pole.fallen]  # сохраняем только активные столбы

    def create_new_pole(self):
        if len(self.poles) < 5:
            new_pole_x = self.find_safe_pole_position()  # находим безопасную позицию для нового столба
            self.poles.append(Pole(new_pole_x, 5))
            self.update_perch_coords()
            # new_x = self.find_safe_pole_position()  # находим безопасное место для нового столба
            # new_strength = random.randint(4,
            # 7)  # прочность нового столба случайная
            # new_pole = Pole(new_x, new_strength)  # создаем новый столб
            # self.poles.append(new_pole)  # добавляем новый столб в список
            # self.update_perch_coords()  # обновляем список координат жердочек

    def paintEvent(self, event):
        """обработка отрисовки на экране."""
        qp = QPainter(self)  # создаем объект для рисования
        for pole in self.poles:  # рисуем столбы
            if not pole.fallen:  # если столб не упал
                qp.setBrush(QBrush(QColor(169, 169, 169),
                                   Qt.SolidPattern))  # устанавливаем цвет и стиль для столба
                qp.drawRect(pole.x - 5, pole.y - 50, 10,
                            50)  # рисуем столб (x, y, ширина, высота)
                qp.drawRect(pole.x - 30, pole.y - 50, 60, 10)

        for bird in self.birds:
            qp.setBrush(QBrush(QColor(0, 0, 255),
                               Qt.SolidPattern))  # устанавливаем цвет для птицы
            qp.drawEllipse(bird.x - 10, bird.y - 10, 20,
                           20)  # рисуем птицу в виде эллипса (x, y, ширина, высота)


if __name__ == '__main__':  # этот блок проверяет, запущен ли данный файл как основная программа.
    app = QApplication(
        sys.argv)  # здесь создается объект QApplication, который управляет основным циклом событий для PyQt5-приложения. sys.argv передается для обработки командной строки, если есть такие параметры
    window = SimulationWindow()  # создаем экземпляр основного окна симуляции — SimulationWindow
    window.show()  # отображаем окно на экране
    sys.exit(
        app.exec_())  # запускает основной цикл обработки событий PyQt5-приложения.
