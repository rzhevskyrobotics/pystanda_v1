import tkinter as tk
from tkinter import ttk
import threading
import time
import queue

# Глобальная очередь для обмена данными между потоками
status_queue = queue.Queue()

# Функция, которая будет выполняться в отдельном потоке
def background_task():
    time.sleep(5)  # Спим 5 секунд
    status_queue.put("STOP")  # Отправляем сообщение в очередь

# Функция для обновления интерфейса
def update_interface(root, status_label):
    try:
        # Пытаемся получить сообщение из очереди
        new_status = status_queue.get_nowait()
        status_label.config(text=f"Status: {new_status}")  # Обновляем статус
    except queue.Empty:
        pass  # Если очередь пуста, ничего не делаем
    finally:
        # Планируем следующее обновление через 100 мс
        root.after(100, update_interface, root, status_label)

def create_interface():
    # Создаем главное окно
    root = tk.Tk()
    root.title("Controller Interface")
    root.geometry("600x400")  # Изначальный размер окна

    # Функция для обновления текста статуса
    def update_status(text):
        status_label.config(text=f"Status: {text}")

    # Функция для обработки нажатия кнопок
    def on_button_click(button_name):
        print(f"Button '{button_name}' clicked")


    # Создаем рамку для группировки элементов
    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(row=0, column=0, sticky="nsew")

    # Размещаем элементы в сетке (grid)

    # Первая строка: кнопки подключения контроллеров
    connect_x_button = ttk.Button(main_frame, text="X controller Connect", command=lambda: on_button_click("X controller Connect"), padding=(5, 10))
    connect_x_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    connect_y_button = ttk.Button(main_frame, text="Y controller Connect", command=lambda: on_button_click("Y controller Connect"), padding=(5, 10))
    connect_y_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    # Вторая строка: поля для портов COM
    port_x_label = ttk.Label(main_frame, text="X controller port:")
    port_x_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    port_x_entry = ttk.Entry(main_frame, width=10)
    port_x_entry.insert(0, "COM34")
    port_x_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    port_y_label = ttk.Label(main_frame, text="Y controller port:")
    port_y_label.grid(row=1, column=2, padx=5, pady=5, sticky="e")
    port_y_entry = ttk.Entry(main_frame, width=10)
    port_y_entry.insert(0, "COM35")
    port_y_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

    # Третья строка: текущая позиция
    current_pos_label = ttk.Label(main_frame, text="Current position(mm):")
    current_pos_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
    current_pos_x_label = ttk.Label(main_frame, text="X: 0.000")
    current_pos_x_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    current_pos_y_label = ttk.Label(main_frame, text="Y: 0.000")
    current_pos_y_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")

    status_label = ttk.Label(main_frame, text="Status: READY")
    status_label.grid(row=3, column=3, padx=5, pady=5, sticky="e")

    # Четвертая строка: базовая точка
    base_point_label = ttk.Label(main_frame, text="Base point (mm):")
    base_point_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
    base_point_x_label = ttk.Label(main_frame, text="X: 0.000")
    base_point_x_label.grid(row=4, column=1, padx=5, pady=5, sticky="w")
    base_point_y_label = ttk.Label(main_frame, text="Y: 0.000")
    base_point_y_label.grid(row=4, column=2, padx=5, pady=5, sticky="w")

    # Пятая строка: поля для установки позиций
    set_pos_x_label = ttk.Label(main_frame, text="Set pos X(mm):")
    set_pos_x_label.grid(row=5, column=0, padx=5, pady=5, sticky="e")
    set_pos_x_entry = ttk.Entry(
    main_frame, 
    width=10,
    validate="key",
    validatecommand=(root.register(lambda P: P == "" or (P.count('.') <= 1 
                              and P.replace('.', '').isdigit())), '%P')
    )
    set_pos_x_entry.insert(0, "0.000")
    set_pos_x_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

    set_pos_y_label = ttk.Label(main_frame, text="Set pos Y(mm):")
    set_pos_y_label.grid(row=5, column=2, padx=5, pady=5, sticky="e")
    set_pos_y_entry = ttk.Entry(
    main_frame, 
    width=10,
    validate="key",
    validatecommand=(root.register(lambda P: P == "" or (P.count('.') <= 1 
                              and P.replace('.', '').isdigit())), '%P')
    )
    set_pos_y_entry.insert(0, "0.000")
    set_pos_y_entry.grid(row=5, column=3, padx=5, pady=5, sticky="w")

    # Шестая строка: кнопки для выполнения действий
    home_x_button = ttk.Button(main_frame, text="Home X", command=lambda: on_button_click("Home X"), padding=(5, 10))
    home_x_button.grid(row=6, column=0, padx=5, pady=5, sticky="ew")

    home_y_button = ttk.Button(main_frame, text="Home Y", command=lambda: on_button_click("Home Y"), padding=(5, 10))
    home_y_button.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

    set_base_point_button = ttk.Button(main_frame, text="Set Base Point", command=lambda: on_button_click("Set Base Point"), padding=(5, 10))
    set_base_point_button.grid(row=6, column=2, padx=5, pady=5, sticky="ew")

    set_position_button = ttk.Button(main_frame, text="Set Position", command=lambda: on_button_click("Set Position"), padding=(5, 10))
    set_position_button.grid(row=6, column=3, padx=5, pady=5, sticky="ew")

    # Седьмая строка: поля для изменения дельты позиции
    delta_x_label = ttk.Label(main_frame, text="dX(mm):")
    delta_x_label.grid(row=7, column=0, padx=5, pady=5, sticky="e")
    delta_x_entry = ttk.Entry(
    main_frame, 
    width=10,
    validate="key",
    validatecommand=(root.register(lambda P: P == "" or (P.count('.') <= 1 
                              and P.replace('.', '').isdigit())), '%P')
    )
    delta_x_entry.insert(0, "0.000")
    delta_x_entry.grid(row=7, column=1, padx=5, pady=5, sticky="w")

    delta_y_label = ttk.Label(main_frame, text="dY(mm):")
    delta_y_label.grid(row=7, column=2, padx=5, pady=5, sticky="e")
    delta_y_entry = ttk.Entry(
    main_frame, 
    width=10,
    validate="key",
    validatecommand=(root.register(lambda P: P == "" or (P.count('.') <= 1 
                              and P.replace('.', '').isdigit())), '%P')
    )
    delta_y_entry.insert(0, "0.000")
    delta_y_entry.grid(row=7, column=3, padx=5, pady=5, sticky="w")

    # Восьмая строка: кнопки для циклического движения
    start_cycle_button = ttk.Button(main_frame, text="Start Cycle Movement", command=lambda: on_button_click("Start Cycle Movement"), padding=(5, 10))
    start_cycle_button.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    stop_cycle_button = ttk.Button(main_frame, text="Stop Cycle Movement", command=lambda: on_button_click("Stop Cycle Movement"), padding=(5, 10))
    stop_cycle_button.grid(row=8, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

    # Добавляем авторский текст внизу
    author_label = ttk.Label(root, text="Rzhevskiy S.S. for ITMO University", font=("Arial", 10))
    author_label.grid(row=1, column=0, pady=1, sticky="s")

    author_label = ttk.Label(root, text="2025", font=("Arial", 10))
    author_label.grid(row=2, column=0, pady=10, sticky="s")

    # Настройка веса строк и столбцов для родительского контейнера (root)
    root.grid_rowconfigure(0, weight=1)  # Главная строка получает вес 1
    root.grid_columnconfigure(0, weight=1)  # Главный столбец получает вес 1

    # Настройка веса строк и столбцов для main_frame
    for i in range(8):
        main_frame.grid_rowconfigure(i, weight=1)
    for i in range(4):
        main_frame.grid_columnconfigure(i, weight=1)

    # Запускаем обновление интерфейса
    root.after(100, update_interface, root, status_label)

    root.minsize(600,400)
    root.resizable(True, True)
    root.mainloop()

# Главная программа
if __name__ == "__main__":
    # Создаем поток для интерфейса
    interface_thread = threading.Thread(target=create_interface, daemon=True)
    interface_thread.start()

    # Создаем поток для фоновой задачи
    background_thread = threading.Thread(target=background_task, daemon=True)
    background_thread.start()

    # Ждем завершения потоков (в данном случае это не обязательно, так как потоки демонические)
    interface_thread.join()
    background_thread.join()