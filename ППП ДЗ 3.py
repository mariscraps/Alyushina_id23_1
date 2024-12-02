import sys
import random
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QSizePolicy
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSpinBox
from PyQt5.QtWidgets import QPushButton  # Импортируем класс кнопки
import math


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
        self.arc_progress = 0  # Прогресс дуги (от 0 до 1)
        self.arc_start_coords = None  # Начальная точка дуги
        self.arc_peak_y = None  # Пиковая высота дуги

    def move_to_arc(self):

        if not self.arc_start_coords or self.arc_peak_y is None:
            self.find_new_pole()  # Убедиться, что дуга настроена

        """Перелёт по дуге с плавным подлётом."""
        if self.arc_progress < 1:  # Пока дуга не завершена
            # Увеличиваем прогресс по дуге
            self.arc_progress += 0.02  # Скорость движения по дуге
            t = self.arc_progress

            # Линейная интерполяция по X
            target_x = (1 - t) * self.arc_start_coords[0] + t * \
                       self.target_pole_coords[0]

            # Квадратичная интерполяция по Y (парабола)
            target_y = (
                    (1 - t) ** 2 * self.arc_start_coords[
                1] +  # Вклад начальной точки
                    2 * (1 - t) * t * self.arc_peak_y +  # Вклад пика дуги
                    t ** 2 * (self.target_pole_coords[1] - 50)
            # Вклад конечной точки
            )

            # Плавное подведение текущих координат к расчётным
            self.x += (target_x - self.x) * 0.1  # Замедленное приближение по X
            self.y += (target_y - self.y) * 0.1  # Замедленное приближение по Y

        else:  # Когда дуга завершена
            # Завершающее плавное движение к точной цели
            dx = (self.target_pole_coords[0] + self.random_offset_x) - self.x
            dy = (self.target_pole_coords[1] - 50) - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)  # Расстояние до цели

            if distance > 0.5:  # Если птица ещё не достигла цели
                self.x += dx * 0.1  # Замедленное движение к цели по X
                self.y += dy * 0.1  # Замедленное движение к цели по Y
            else:
                # Фиксация координат при достижении цели
                self.x = self.target_pole_coords[0] + self.random_offset_x
                self.y = self.target_pole_coords[1] - 50
                self.on_pole = True
                self.moving_to_another_pole = False
                self.arc_progress = 0
                self.sitting_on_pole_time = 0

    def move_to(self, post_x, perch_y):
        # Разница между текущей и целевой позицией
        dx = post_x - self.x
        dy = perch_y - self.y

        # Расстояние до цели
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Задаём скорость, уменьшающуюся с расстоянием (но не меньше минимума)
        speed = max(0.05,
                    min(0.05, distance * 0.1))  # Скорость зависит от расстояния

        # Обновляем координаты с учётом скорости
        self.x += dx * speed
        self.y += dy * speed

        # Если расстояние до цели меньше 1, фиксируем птицу на месте
        if distance < 1:
            self.x = post_x
            self.y = perch_y

    def move(self):
        if self.on_pole:  # Если птица сидит на жердочке
            self.sitting_on_pole_time += 1  # Увеличиваем время сидения
            if self.sitting_on_pole_time >= self.sitting_time:  # Если время истекло
                self.on_pole = False  # Птица покидает жердочку
                if random.random() < 0.5:  # 50% шанс, что птица улетит
                    self.moving_up = True  # Птица начинает улетать вверх
                else:
                    self.moving_to_another_pole = True  # Птица летит к другой жердочке
                    self.find_new_pole()  # Выбираем новую цель

        elif self.moving_up:  # Если птица улетает вверх
            self.y -= self.speed_y  # Уменьшаем Y (движение вверх)
            self.x += self.speed_x  # Добавляем движение по X
            self.x += math.sin(self.y * 0.1) * 2
            if self.y < -10:  # Если птица улетела за пределы экрана
                self.reset_position()  # Сбрасываем её позицию

        elif self.moving_to_another_pole and self.target_pole_coords:  # Если птица перелетает на другую жердочку
            self.move_to_arc()  # Используем перелёт по дуге

        else:  # Если птица в начале полёта (сверху экрана к жердочке)
            if self.target_pole_coords:  # Если цель установлена (жердочка)
                # Целевые координаты на жердочке
                target_x = self.target_pole_coords[0] + self.random_offset_x
                target_y = self.target_pole_coords[1] - 50

                # Плавное подведение текущих координат к целевым
                self.x += (
                                      target_x - self.x) * 0.1  # Замедленное приближение по X
                self.y += (
                                      target_y - self.y) * 0.1  # Замедленное приближение по Y

                # Проверка достижения цели
                distance = math.sqrt(
                    (self.x - target_x) ** 2 + (self.y - target_y) ** 2)
                if distance < 2:  # Если птица практически достигла цели
                    self.on_pole = True  # Птица садится на жердочку
                    self.x = target_x  # Фиксируем точное положение
                    self.y = target_y
            else:
                self.y += self.speed_y  # Если цели нет, птица падает вниз

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
        if SimulationWindow.instance.perch_coords:  # Если есть доступные жердочки
            current_pole = None

            # Определяем текущий столб, если птица уже сидела
            if self.target_pole_coords:
                current_pole = self.target_pole_coords[0]

            # Находим жердочку на другом столбе
            available_perches = [
                perch for perch in SimulationWindow.instance.perch_coords
                if perch[0] != current_pole
            ]
            if available_perches:
                new_perch = random.choice(
                    available_perches)  # Случайно выбираем доступную жердочку
            else:
                new_perch = random.choice(
                    SimulationWindow.instance.perch_coords)  # Если все жердочки на одном столбе

            self.target_pole_coords = new_perch  # Устанавливаем цель
            self.random_offset_x = random.uniform(-30,
                                                  30)  # Добавляем случайное смещение по X

            # Настраиваем начальную точку и параметры дуги
            self.arc_start_coords = (self.x, self.y)

            # Задаём высоту дуги, увеличив пиковую высоту
            self.arc_peak_y = min(self.y, self.target_pole_coords[1] - 50) - random.randint(150, 250)


        else:
            self.moving_up = True  # Если нет жердочек, птица улетает вверх


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
        self.setGeometry(100, 100, 1000,
                         800)  # задаем размеры и положение окна

        # загружаем данные из JSON и создаем столбы
        poles_data = load_poles_data()
        self.poles = [Pole(pole["x"], pole["strength"]) for pole in
                      poles_data]  # создаем столбы по данным из файла
        self.spin_boxes = []
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
            500)  # новые столбы появляются каждые 0.5 секунды
        # self.create_spin_boxes()

        # Интерфейс
        self.main_layout = QVBoxLayout()  # Макет, для выстраивания виджетов вертикально
        self.canvas = QWidget(self)  # Виджет для рисования
        # self.canvas.setMinimumSize(0, 0)
        self.main_layout.addWidget(self.canvas)

        # Панель управления
        self.control_panel = QHBoxLayout()  # Макет для панели управления
        self.main_layout.addLayout(self.control_panel)

        # Добавляем кнопку для создания нового столба
        self.add_pole_button = QPushButton("Добавить столб", self)
        self.add_pole_button.clicked.connect(
            self.add_new_pole)  # Связываем кнопку с обработчиком
        self.main_layout.addWidget(self.add_pole_button)

        # Метка для частоты
        self.spawn_label = QLabel("Частота появления птиц (мс):", self)
        self.control_panel.addWidget(self.spawn_label)

        # SpinBox для настройки частоты птиц
        self.spawn_spinbox = QSpinBox(self)
        self.spawn_spinbox.setRange(100,
                                    5000)  # Ограничиваем интервал от 100 мс до 5 сек
        self.spawn_spinbox.setValue(1000)  # Значение по умолчанию 1 секунда
        self.spawn_spinbox.setSingleStep(10)
        """ # (строчка выше) Changes the value by 10 units each time"""
        self.spawn_spinbox.valueChanged.connect(self.update_spawn_frequency)
        self.control_panel.addWidget(self.spawn_spinbox)

        # Метка для частоты столбов
        self.pole_label = QLabel("Частота появления столбов (мс):", self)
        self.control_panel.addWidget(self.pole_label)

        # SpinBox для настройки частоты столбов
        self.pole_spinbox = QSpinBox(self)
        self.pole_spinbox.setRange(100,
                                   5000)  # Ограничиваем интервал от 100 мс до 5 секунд
        self.pole_spinbox.setValue(500)  # Значение по умолчанию 500 мс
        self.pole_spinbox.setSingleStep(10)
        """ # (строчка выше) Changes the value by 10 units each time"""
        self.pole_spinbox.valueChanged.connect(self.update_pole_frequency)
        self.control_panel.addWidget(self.pole_spinbox)

        self.create_spin_boxes()
        self.setLayout(self.main_layout)

    def add_new_pole(self):
        """Добавляет новый столб с жердочкой и SpinBox."""
        # Генерируем случайное положение для нового столба
        max_attempts = 100
        new_x = None

        for _ in range(max_attempts):
            candidate_x = random.randint(100, 800)  # it was (150, 750)
            # Проверяем, есть ли достаточно места для нового столба
            if not any(abs(candidate_x - pole.x) < 50 for pole in self.poles):
                new_x = candidate_x
                break

            # Если не удалось найти подходящее место, просто выходим
        if new_x is None:
            print("Нет свободного места для нового столба!")
            return

        # Создаем новый столб
        new_pole = Pole(new_x, strength=5)
        self.poles.append(new_pole)

        # Создаем SpinBox для нового столба
        spin_box = QSpinBox(self)
        spin_box.setMinimum(1)
        spin_box.setMaximum(10)
        spin_box.setValue(new_pole.strength)
        spin_box.setGeometry(new_pole.x - 20, new_pole.y + 10, 50, 20)
        """spin_box"""
        spin_box.setFixedSize(50, 40)
        spin_box.valueChanged.connect(
            lambda value, p=new_pole: self.update_pole_strength(p, value))  # Связываем изменение значения SpinBox с обновлением силы столба
        spin_box.show()
        self.spin_boxes.append(spin_box)

        # Обновляем координаты жердочек
        self.update_perch_coords()

    def update_pole_frequency(self, value):
        """Обновляет частоту появления новых столбов."""
        self.new_pole_timer.start(value)

    def update_spawn_frequency(self, value):
        """Обновляет частоту появления птиц."""
        self.spawn_timer.start(value)

    def create_spin_boxes(self):
        """Создаёт SpinBox для каждого столба."""
        for pole in self.poles:
            spin_box = QSpinBox(self)
            spin_box.setMinimum(1)  # Минимальная прочность
            spin_box.setMaximum(10)  # Максимальная прочность
            spin_box.setValue(pole.strength)  # Текущая прочность
            """spin_box"""
            spin_box.setFixedSize(50, 40)
            spin_box.setGeometry(pole.x - 20, pole.y + 10, 50,
                                 20)  # Позиционируем под столбом
            # spin_box.adjustSize()
            spin_box.setSizePolicy(QSizePolicy.Preferred,
                                   QSizePolicy.Preferred)
            spin_box.valueChanged.connect(
                lambda value, p=pole: self.update_pole_strength(p, value))   # Связываем изменение значения SpinBox с обновлением силы столба
            spin_box.show()
            self.spin_boxes.append(spin_box)

    def update_spin_boxes(self):
        """Обновляет позиции SpinBox и удаляет их, если столб упал."""
        for i in reversed(range(len(
                self.spin_boxes))):  # Итерируем в обратном порядке для корректного удаления
            if i >= len(self.poles):  # Защита от несоответствия списков
                self.spin_boxes[i].hide()
                self.spin_boxes.pop(
                    i)  # Удаляем SpinBox, если столб отсутствует
                continue

            pole = self.poles[i]
            if pole.fallen:
                self.spin_boxes[i].hide()  # Скрываем SpinBox
            else:
                self.spin_boxes[i].setGeometry(pole.x - 20, pole.y + 10, 50,
                                               20)  # Обновляем позицию
                """spin_box"""
                self.spin_boxes[i].setFixedSize(50, 40)
                self.spin_boxes[i].show()  # Показываем SpinBox, если он скрыт

    def update_pole_strength(self, pole, value):
        """Обновляет прочность столба на основе SpinBox."""
        pole.strength = value

    def spawn_birds(self):
        for _ in range(20):  # создаем 20 новых птиц
            bird = Bird(random.randint(-100, 1000), random.randint(-50, -10),  # (100, 700)
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
        self.update_spin_boxes()
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
        """Обработка падения столба: удаляем его из доступных для птиц и ждем восстановления"""
        self.perch_coords = [(x, y) for (x, y) in self.perch_coords if
                             x != fallen_pole.x]  # убираем столб из списка жердочек

        for bird in self.birds:  # обрабатываем каждую птицу
            if bird.on_pole and bird.target_pole_coords == (
            fallen_pole.x, fallen_pole.y):  # если птица на упавшем столбе
                bird.on_pole = False  # птица покидает столб
                bird.target_pole_coords = None  # убираем цель жердочки

                # 50% шанс перелета на другую жердочку
                if random.random() < 0.5 and self.perch_coords:
                    bird.moving_to_another_pole = True  # птица летит на другую жердочку
                    bird.find_new_pole()  # ищем новую жердочку для перелета
                    bird.arc_progress = 0  # начинаем новый перелет по дуге
                    bird.arc_start_coords = (
                    bird.x, bird.y)  # сохраняем начальную точку дуги
                    bird.arc_peak_y = random.randint(150,
                                                     250)  # случайная высота дуги
                else:
                    bird.moving_up = True  # если не перелетает, улетает вверх

            elif not bird.on_pole and bird.target_pole_coords == (
            fallen_pole.x, fallen_pole.y):  # если цель - упавший столб
                bird.target_pole_coords = None  # очищаем цель

                # 50% шанс перелета на другую жердочку
                if random.random() < 0.5 and self.perch_coords:
                    bird.moving_to_another_pole = True  # птица летит на другую жердочку
                    bird.find_new_pole()  # ищем новую жердочку для перелета
                    bird.arc_progress = 0  # начинаем новый перелет по дуге
                    bird.arc_start_coords = (
                    bird.x, bird.y)  # сохраняем начальную точку дуги
                    bird.arc_peak_y = random.randint(150,
                                                     250)  # случайная высота дуги
                else:
                    bird.moving_up = True  # если не перелетает, улетает вверх

        # Удаляем SpinBox для упавшего столба
        for i, pole in enumerate(self.poles):
            if pole == fallen_pole:
                self.spin_boxes[i].hide()
                self.spin_boxes.pop(i)
                self.poles.pop(i)
                break

    def update_perch_coords(self):
        """обновляем список координат жердочек (вершины столбов)"""
        self.perch_coords = [(pole.x, pole.y) for pole in self.poles if
                             not pole.fallen]  # сохраняем только активные столбы

    def create_new_pole(self):
        if len(self.poles) < 5:  # Ограничение на количество столбов
            new_pole_x = self.find_safe_pole_position()  # Находим безопасную позицию для нового столба
            new_pole = Pole(new_pole_x,
                            5)  # Создаём новый столб с начальной силой (например, 5)
            self.poles.append(new_pole)  # Добавляем столб в список

            # Создаём QSpinBox для управления силой столба
            new_spin_box = QSpinBox(self)
            new_spin_box.setMinimum(1)  # Минимальное значение силы
            new_spin_box.setMaximum(10)  # Максимальное значение силы
            new_spin_box.setValue(
                new_pole.strength)  # Устанавливаем текущую силу столба
            new_spin_box.setGeometry(new_pole.x - 20, new_pole.y + 10, 50,
                                     20)  # Позиционируем SpinBox
            """spin_box"""
            new_spin_box.setFixedSize(50, 40)
            new_spin_box.valueChanged.connect(
                lambda value, p=new_pole: self.update_pole_strength(p,
                                                                    value))  # Связываем изменение значения SpinBox с обновлением силы столба
            new_spin_box.show()  # Отображаем SpinBox

            self.spin_boxes.append(
                new_spin_box)  # Сохраняем SpinBox для дальнейшего управления

            self.update_perch_coords()  # Обновляем координаты насеста

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
            qp.drawEllipse(int(bird.x) - 10, int(bird.y) - 10, 20,
                           20)  # рисуем птицу в виде эллипса (x, y, ширина, высота)


if __name__ == '__main__':  # этот блок проверяет, запущен ли данный файл как основная программа.
    app = QApplication(
        sys.argv)  # здесь создается объект QApplication, который управляет основным циклом событий для PyQt5-приложения. sys.argv передается для обработки командной строки, если есть такие параметры
    window = SimulationWindow()  # создаем экземпляр основного окна симуляции — SimulationWindow
    window.show()  # отображаем окно на экране
    sys.exit(
        app.exec_())  # запускает основной цикл обработки событий PyQt5-приложения.


