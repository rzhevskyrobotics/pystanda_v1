#   Скрипт для управления позиционером STANDA 8MTF, драйвер  8SMC5
#   Версия 21.03.25, пока сырая. Use it well :)


import time

try: 
    from pyximc import *
except ImportError as err:
    print ("Can't import pyximc module. The most probable reason is that you changed the relative location of the testpython.py and pyximc.py files. See developers' documentation for details.")
    exit()
except OSError as err:
    print ("Can't load libximc library. Please add all shared libraries to the appropriate places. It is decribed in detail in developers' documentation. On Linux make sure you installed libximc-dev package.\nmake sure that the architecture of the system and the interpreter is the same")
    print(err)
    exit()


# Класс для управления осями, в контроллерах их по два. Коварная фигня - оси могут быть инвертированными!
class Axis:
    def __init__(self, lib, axis_id: int, is_inverted=False, step_to_mm_conversion_coeff=0.0025):
        """
        Инициализация линейного транслятора.
        :param lib: Указатель на ctypes dll
        :param axis_id: Уникальный идентификатор оси.
        :param is_inverted: Инвертированная ось = если движение ОТ хоминга = негативное движение
        :param step_to_mm_conversion_coeff: Коэф перевода из шагов в мм - по спецификации
        """
        self.axis_id = axis_id
        self.lib = lib
        self.is_inverted = is_inverted
        self.step_to_mm_conversion_coeff = step_to_mm_conversion_coeff
    
    #Хоминг оси - пока блокирующая
    def home(self):
        result = self.lib.command_home(self.axis_id)
        time.sleep(0.2) #Для корректного статуса. Потом убрать/разобраться
        while self.is_moving():
            time.sleep(0.1)
        result = self.lib.command_zero(self.axis_id)
        time.sleep(0.2) #Для корректного статуса. Потом убрать/разобраться
        return result
    
    #Движение по шагам и микрошагам
    def move(self, distance, udistance):
        if self.is_inverted: 
            result = self.lib.command_move(self.axis_id, -distance, -udistance)
        else:
            result = self.lib.command_move(self.axis_id, distance, udistance)
        time.sleep(0.2) #Для корректного статуса. Потом убрать/разобраться
        return result
    
    #Статус
    def get_status(self):
        status = status_t()
        result = self.lib.get_status(self.axis_id, byref(status))
        if result == Result.Ok:
            return status
        else:
            return None
        
    #Текущие координаты в шагах и микрошагах
    def get_position(self):
        pos = get_position_t()
        result = self.lib.get_position(self.axis_id, byref(pos))
        print("Result: " + repr(result))
        if self.is_inverted:
            return -pos.Position, -pos.uPosition
        else:
            return pos.Position, pos.uPosition
        
    #Параметры скрости. Расшифровка в pyximc.py
    def get_speed_params(self):
        mvst = move_settings_t()
        # Get current move settings from controller
        result = self.lib.get_move_settings(self.axis_id, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        print("Read command result: " + repr(result))    
        return mvst
    
    def set_microstep_mode_256(self):
        # Create engine settings structure
        eng = engine_settings_t()
        # Get current engine settings from controller
        result = self.lib.get_engine_settings(self.axis_id, byref(eng))
        # Print command return status. It will be 0 if all is OK
        #print("Read command result: " + repr(result))
        # Change MicrostepMode parameter to MICROSTEP_MODE_FRAC_256
        # (use MICROSTEP_MODE_FRAC_128, MICROSTEP_MODE_FRAC_64 ... for other microstep modes)
        eng.MicrostepMode = MicrostepMode.MICROSTEP_MODE_FRAC_256
        # Write new engine settings to controller
        result = self.lib.set_engine_settings(self.axis_id, byref(eng))
        # Print command return status. It will be 0 if all is OK
        #print("Write command result: " + repr(result))    
    
    def get_move_params(self):
        # Create move settings structure
        mvst = move_settings_t()
        # Get current move settings from controller
        result = self.lib.get_move_settings(self.axis_id, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        return mvst
    
    
    def set_speed(self, speed_steps):
        # Create move settings structure
        mvst = move_settings_t()
        # Get current move settings from controller
        result = self.lib.get_move_settings(self.axis_id, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        print("Read command result: " + repr(result))
        print("The speed was equal to {0}. We will change it to {1}".format(mvst.Speed, speed_steps))
        # Change current speed
        mvst.Speed = int(speed_steps)
        # Write new move settings to controller
        result = self.lib.set_move_settings(self.axis_id, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        print("Write command result: " + repr(result))
    
    def set_accel(self, accel_steps):
        # Create move settings structure
        mvst = move_settings_t()
        # Get current move settings from controller
        result = self.lib.get_move_settings(self.axis_id, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        print("Read command result: " + repr(result))
        print("The accel was equal to {0}. We will change it to {1}".format(mvst.Accel, accel_steps))
        # Change current accel
        mvst.Accel = int(accel_steps)
        # Write new move settings to controller
        result = self.lib.set_move_settings(self.axis_id, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        print("Write command result: " + repr(result))
    
    def set_decel(self, decel_steps):
        # Create move settings structure
        mvst = move_settings_t()
        # Get current move settings from controller
        result = self.lib.get_move_settings(self.axis_id, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        print("Read command result: " + repr(result))
        print("The decel was equal to {0}. We will change it to {1}".format(mvst.Decel, decel_steps))
        # Change current accel
        mvst.Decel = int(decel_steps)
        # Write new move settings to controller
        result = self.lib.set_move_settings(self.axis_id, byref(mvst))
        # Print command return status. It will be 0 if all is OK
        print("Write command result: " + repr(result))
            
    #Получаем статус движения
    def is_moving(self) -> bool:
        """
        Проверяет, движется ли ось.
        :return: True, если ось в движении, иначе False.
        """
        status = self.get_status()
        return (status.MoveSts > 0) and (status.MvCmdSts & MvcmdStatus.MVCMD_RUNNING) != 0
    
    def mm_to_steps(self, mm_distance):
        """
        Конвертирует расстояние в мм в количество шагов и микрошагов.

        :param mm_distance: Расстояние в мм
        :return: (steps, usteps) – целые шаги и микрошаги
        """
        total_steps = mm_distance / self.step_to_mm_conversion_coeff  # Общее количество шагов (может быть дробным)
        steps = int(total_steps)  # Целая часть – это полные шаги
        usteps = int((total_steps - steps) * 256)  # Дробную часть переводим в микрошаги (256 уровней)

        return steps, usteps

    def move_mm(self, mm_distance):
        """
        Двигает ось на указанное расстояние в мм, автоматически переводя в шаги.

        :param mm_distance: Расстояние в мм
        """
        steps, usteps = self.mm_to_steps(mm_distance)
        return self.move(steps, usteps)

# Основная программа
if __name__ == "__main__":


    # variable 'lib' points to a loaded library - классическое "очевидно, что"
    # note that ximc uses stdcall on win - ну и черт с ним
    print("Library loaded")

    #Получаем версию библы - просто потому что можем
    sbuf = create_string_buffer(64)
    lib.ximc_version(sbuf)
    print("Library version: " + sbuf.raw.decode().rstrip("\0"))

    #Инициализируем коннекторы - ЗАМЕНИТЬ НОМЕРА ПОРТОВ НА НУЖНЫЕ!
    # Важно - ось I инвертированная, это важно! Подобрать из портов нужный можно методом тыка
    
    # X = "I" = Axis 1 разъем
    open_name_X = r"xi-com:\\.\COM25"
    device_id_X = lib.open_device(open_name_X.encode())
    print("Device id X: " + repr(device_id_X))

    # X = "J" = Axis 2 разъем
    open_name_Y = r"xi-com:\\.\COM26"
    device_id_Y = lib.open_device(open_name_Y.encode())
    print("Device id Y: " + repr(device_id_Y))

    #Инициализируем объекты управления устройством
    # X(="I") - инвертированная
    axis_X = Axis(lib, device_id_X, True)
    axis_Y = Axis(lib, device_id_Y)

    axis_X.set_speed(5000)
    axis_X.set_accel(5000)
    axis_X.set_decel(7000)

    axis_Y.set_speed(5000)
    axis_Y.set_accel(5000)
    axis_Y.set_decel(7000)

    #params = axis_X.get_speed_params()

    #print("Speed: ", params.Speed)
    #print("Accel: ", params.Accel)
    #print("Decel: ", params.Decel)

    #ЖУЧАРА!
    #exit()

    #"Полезные" действия
    print("Хоминг...")

    axis_X.home()
    axis_Y.home()


    print("Ok!")


    #Движение в точку старта
    print("Движение в точку старта цикла...")

    axis_X.move_mm(5.0)
    axis_Y.move_mm(5.0)

    while axis_X.is_moving():
        time.sleep(0.1)
    

    #Пользовательская пауза. Начнет работу после нажатия на любую клавишу
    input("Нажмите любую клавишу для продолжения...")

    points = [(5, 5), (7, 5), (7, 7), (5, 7)]  # Массив точек (X, Y)
    index = 0  # Начальный индекс
    threshold_mm = 1.7  # МАГИЧЕСКИЙ ПАРАМЕТР. Пока его нужно подбирать. Суть - начинается новое движение тогда, когда до цели осталось меньше, чем ЭТО

    #Начинаем движение по циклу. Прерывать Ctrl-C
    while True:
        x_target, y_target = points[index]  # Берём следующую цель
        print(f"Двигаемся к точке ({x_target}, {y_target})")

        axis_X.move_mm(x_target)
        axis_Y.move_mm(y_target)

        while True:
            # Получаем текущие координаты
            x_current = -(axis_X.get_status().CurPosition) * axis_X.step_to_mm_conversion_coeff
            y_current = axis_Y.get_status().CurPosition * axis_Y.step_to_mm_conversion_coeff

            # Рассчитываем оставшееся расстояние
            distance_x = abs(x_target - x_current)
            distance_y = abs(y_target - y_current)

            # Проверяем, нужно ли стартовать следующее движение
            if distance_x <= threshold_mm and distance_y <= threshold_mm:
                index = (index + 1) % len(points)  # Переход к следующей точке
                break  # Начинаем следующее движение

            time.sleep(0.1)  # Проверяем статус каждые 100 мс