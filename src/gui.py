#   Скрипт для управления позиционером STANDA 8MTF, драйвер  8SMC5, GUI
#
# 
#   Версия 2.04.25, пока сырая. Use it well :)

# Архитектура: 2 потока GuiThread + PositionerThread, их координирует AppController

import tkinter as tk
from tkinter import ttk
import threading
import time
import queue
import sys
import signal

#Скрипт с ядром контроллера движка
import standa


#Либы станды
try: 
    from pyximc import *
except ImportError as err:
    print ("Can't import pyximc module. The most probable reason is that you changed the relative location of the testpython.py and pyximc.py files. See developers' documentation for details.")
    exit()
except OSError as err:
    print ("Can't load libximc library. Please add all shared libraries to the appropriate places. It is decribed in detail in developers' documentation. On Linux make sure you installed libximc-dev package.\nmake sure that the architecture of the system and the interpreter is the same")
    print(err)
    exit()


WINDOW_TITLE = "Serg's Standa Controller Interface"
THREAD_MESSAGE_DELAY_MS = 100

DEFAULT_PORT_X = "COM7"
DEFAULT_PORT_Y = "COM8"

#Класс GUI
class GuiThread:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title(WINDOW_TITLE)
        self.root.geometry("600x400")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.build_interface()
        self.root.after(THREAD_MESSAGE_DELAY_MS, self.update_interface)

    #Модифицировать интерфейс здесь!
    def build_interface(self):
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.connect_x_button = ttk.Button(self.main_frame, text="X controller Connect",
                                           command=self.connect_x_button_on_click, padding=(5, 10))
        self.connect_x_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.connect_y_button = ttk.Button(self.main_frame, text="Y controller Connect", command=self.connect_y_button_on_click, padding=(5, 10))
        self.connect_y_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Вторая строка: поля для портов COM
        self.port_x_label = ttk.Label(self.main_frame, text="X controller port:")
        self.port_x_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.port_x_entry = ttk.Entry(self.main_frame, width=10)
        self.port_x_entry.insert(0, DEFAULT_PORT_X)
        self.port_x_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.port_y_label = ttk.Label(self.main_frame, text="Y controller port:")
        self.port_y_label.grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.port_y_entry = ttk.Entry(self.main_frame, width=10)
        self.port_y_entry.insert(0, DEFAULT_PORT_Y)
        self.port_y_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Третья строка: текущая позиция
        self.current_pos_label = ttk.Label(self.main_frame, text="Current position(mm):")
        self.current_pos_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.current_pos_x_label = ttk.Label(self.main_frame, text="X: 0.000")
        self.current_pos_x_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.current_pos_y_label = ttk.Label(self.main_frame, text="Y: 0.000")
        self.current_pos_y_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        self.status_label = ttk.Label(self.main_frame, text="Status: READY")
        self.status_label.grid(row=3, column=3, padx=5, pady=5, sticky="e")

        # Четвертая строка: базовая точка
        self.base_point_label = ttk.Label(self.main_frame, text="Base point (mm):")
        self.base_point_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.base_point_x_label = ttk.Label(self.main_frame, text="X: 0.000")
        self.base_point_x_label.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.base_point_y_label = ttk.Label(self.main_frame, text="Y: 0.000")
        self.base_point_y_label.grid(row=4, column=2, padx=5, pady=5, sticky="w")

        # Пятая строка: поля для установки позиций
        self.set_pos_x_label = ttk.Label(self.main_frame, text="Set pos X(mm):")
        self.set_pos_x_label.grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.set_pos_x_entry = ttk.Entry(
        self.main_frame, 
        width=10,
        validate="key",
        validatecommand=(self.root.register(lambda P: P == "" or (P.count('.') <= 1 
                                and P.replace('.', '').isdigit())), '%P')
        )
        self.set_pos_x_entry.insert(0, "0.000")
        self.set_pos_x_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        self.set_pos_y_label = ttk.Label(self.main_frame, text="Set pos Y(mm):")
        self.set_pos_y_label.grid(row=5, column=2, padx=5, pady=5, sticky="e")
        self.set_pos_y_entry = ttk.Entry(
        self.main_frame, 
        width=10,
        validate="key",
        validatecommand=(self.root.register(lambda P: P == "" or (P.count('.') <= 1 
                                and P.replace('.', '').isdigit())), '%P')
        )
        self.set_pos_y_entry.insert(0, "0.000")
        self.set_pos_y_entry.grid(row=5, column=3, padx=5, pady=5, sticky="w")

        # Шестая строка: кнопки для выполнения действий
        self.home_x_button = ttk.Button(self.main_frame, text="Home X", command=self.home_x_button_on_click, padding=(5, 10))
        self.home_x_button.grid(row=6, column=0, padx=5, pady=5, sticky="ew")

        self.home_y_button = ttk.Button(self.main_frame, text="Home Y", command=self.home_y_button_on_click, padding=(5, 10))
        self.home_y_button.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

        self.set_base_point_button = ttk.Button(self.main_frame, text="Set Base Point", command=self.set_base_point_button_on_click, padding=(5, 10))
        self.set_base_point_button.grid(row=6, column=2, padx=5, pady=5, sticky="ew")

        self.set_position_button = ttk.Button(self.main_frame, text="Set Position", command=self.set_position_button_on_click, padding=(5, 10))
        self.set_position_button.grid(row=6, column=3, padx=5, pady=5, sticky="ew")

        # Седьмая строка: поля для изменения дельты позиции
        self.delta_x_label = ttk.Label(self.main_frame, text="dX(mm):")
        self.delta_x_label.grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.delta_x_entry = ttk.Entry(
        self.main_frame, 
        width=10,
        validate="key",
        validatecommand=(self.root.register(lambda P: P == "" or (P.count('.') <= 1 
                                and P.replace('.', '').isdigit())), '%P')
        )
        self.delta_x_entry.insert(0, "0.000")
        self.delta_x_entry.grid(row=7, column=1, padx=5, pady=5, sticky="w")

        self.delta_y_label = ttk.Label(self.main_frame, text="dY(mm):")
        self.delta_y_label.grid(row=7, column=2, padx=5, pady=5, sticky="e")
        self.delta_y_entry = ttk.Entry(
        self.main_frame, 
        width=10,
        validate="key",
        validatecommand=(self.root.register(lambda P: P == "" or (P.count('.') <= 1 
                                and P.replace('.', '').isdigit())), '%P')
        )
        self.delta_y_entry.insert(0, "0.000")
        self.delta_y_entry.grid(row=7, column=3, padx=5, pady=5, sticky="w")

        # Восьмая строка: кнопки для циклического движения
        self.start_cycle_button = ttk.Button(self.main_frame, text="Start Cycle Movement", command=self.start_cycle_button_on_click, padding=(5, 10))
        self.start_cycle_button.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.stop_cycle_button = ttk.Button(self.main_frame, text="Stop Cycle Movement", command=self.stop_cycle_button_on_click, padding=(5, 10))
        self.stop_cycle_button.grid(row=8, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        # Добавляем авторский текст внизу
        self.author_label = ttk.Label(self.root, text="Rzhevskiy S.S. for ITMO University", font=("Arial", 10))
        self.author_label.grid(row=1, column=0, pady=1, sticky="s")

        self.author_label = ttk.Label(self.root, text="2025", font=("Arial", 10))
        self.author_label.grid(row=2, column=0, pady=10, sticky="s")

        # Настройка веса строк и столбцов для родительского контейнера (root)
        self.root.grid_rowconfigure(0, weight=1)  # Главная строка получает вес 1
        self.root.grid_columnconfigure(0, weight=1)  # Главный столбец получает вес 1

        # Настройка веса строк и столбцов для self.main_frame
        for i in range(8):
            self.main_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.main_frame.grid_columnconfigure(i, weight=1)

    def update_interface(self):
        return
        try:
            # Пытаемся получить сообщение из очереди
            new_status = self.controller.status_queue.get_nowait()
            self.status_label.config(text=f"Status: {new_status}")  # Обновляем статус
        except queue.Empty:
            pass  # Если очередь пуста, ничего не делаем
        finally:
            # Планируем следующее обновление через THREAD_MESSAGE_DELAY_MS мс
            self.root.after(THREAD_MESSAGE_DELAY_MS, self.update_interface)

    #Обработчики кнопок
    def connect_x_button_on_click(self):

        port = self.port_x_entry.get()
        
        self.controller.status_queue.put({
            "cmd": "connect",
            "axis" : "X",
            "port": port
        })

    def connect_y_button_on_click(self):
        port = self.port_y_entry.get()
        
        self.controller.status_queue.put({
            "cmd": "connect",
            "axis" : "Y",
            "port": port
        })

    def home_x_button_on_click(self):
        self.controller.status_queue.put({
            "cmd": "home",
            "axis" : "X"
        })
    
    def home_y_button_on_click(self):
        self.controller.status_queue.put({
            "cmd": "home",
            "axis" : "Y"
        })

    def set_base_point_button_on_click(self):
        print("Hello")

    def set_position_button_on_click(self):
        print("Hello")

    def start_cycle_button_on_click(self):
        print("Hello")

    def stop_cycle_button_on_click(self):
        print("Hello")

    #На выходе
    def on_close(self):
        print("Закрытие окна. Завершаем приложение...")
        self.controller.shutdown()
        self.root.destroy()

# Главный контроллер приложения
class AppController:
    def __init__(self):
        self.status_queue = queue.Queue()
        self.positioner = PositionerThread(self.status_queue)
        self.root = tk.Tk()
        self.gui = GuiThread(self.root, self)

    def run(self):
        print("Запуск приложения...")
        self.positioner.start()

        # Обработка Ctrl-C
        signal.signal(signal.SIGINT, self.signal_handler)

        self.root.mainloop()

        # После выхода из mainloop
        self.shutdown()

    def shutdown(self):
        print("Завершаем потоки...")
        self.positioner.stop()
        self.positioner.join()
        print("Завершено.")

    def signal_handler(self, sig, frame):
        print("\nПолучен SIGINT (Ctrl-C).")
        self.shutdown()
        sys.exit(0)



class PositionerThread(threading.Thread):
    def __init__(self, status_queue):
        super().__init__(daemon=True)
        self.status_queue = status_queue
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            try:
                # Пытаемся получить сообщение из очереди
                command = self.status_queue.get(timeout=0.1)
                self.handle_command(command)
            except queue.Empty:
                pass  # Если очередь пуста, ничего не делаем

        self.status_queue.put("Positioner: stopped.")

    def handle_command(self, command):
        cmd_type = command.get("cmd")

        #Соединение с контроллером
        if cmd_type == "connect":
            axis_type = command.get("axis")
            if axis_type == "X":  
                port = command.get("port")
                connect_str = fr"xi-com:\\.\{port}"
                device_id = lib.open_device(connect_str.encode())
                print("Device id X: " + repr(device_id))

                self.axis_X = standa.Axis(lib, device_id, True)
            elif axis_type == "Y": 
                port = command.get("port")
                connect_str = fr"xi-com:\\.\{port}"
                device_id = lib.open_device(connect_str.encode())
                print("Device id Y: " + repr(device_id))

                self.axis_Y = standa.Axis(lib, device_id)

        #Хоминг
        elif cmd_type == "home":
            axis_type = command.get("axis")
            if axis_type == "X":
                if hasattr(self, "axis_X"):
                    self.axis_X.home()
            elif axis_type == "Y":
                if hasattr(self, "axis_Y"):
                    self.axis_Y.home()
        else:
            self.status_queue.put(f"Unknown command: {cmd_type}")


    def stop(self):
        self._stop_event.set()



def main():
    AppController().run()


if __name__ == "__main__":
    main()