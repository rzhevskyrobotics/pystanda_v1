import tkinter as tk
from tkinter import ttk
import threading
import time
import queue

status_queue = queue.Queue()

class ControllerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Controller Interface")
        self.root.geometry("600x400")
        self.build_interface()
        self.root.after(100, self.update_interface)

    def build_interface(self):
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Команды
        self.connect_x_button = ttk.Button(self.main_frame, text="X controller Connect",
                                           command=lambda: self.on_button_click("X controller Connect"))
        self.connect_x_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.connect_y_button = ttk.Button(self.main_frame, text="Y controller Connect",
                                           command=lambda: self.on_button_click("Y controller Connect"))
        self.connect_y_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.status_label = ttk.Label(self.main_frame, text="Status: READY")
        self.status_label.grid(row=3, column=3, padx=5, pady=5, sticky="e")

        self.start_cycle_button = ttk.Button(self.main_frame, text="Start Cycle Movement",
                                             command=lambda: self.on_button_click("Start Cycle Movement"))
        self.start_cycle_button.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.stop_cycle_button = ttk.Button(self.main_frame, text="Stop Cycle Movement",
                                            command=lambda: self.on_button_click("Stop Cycle Movement"))
        self.stop_cycle_button.grid(row=8, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        # Author
        author_label1 = ttk.Label(self.root, text="Rzhevskiy S.S. for ITMO University", font=("Arial", 10))
        author_label1.grid(row=1, column=0, pady=1, sticky="s")
        author_label2 = ttk.Label(self.root, text="2025", font=("Arial", 10))
        author_label2.grid(row=2, column=0, pady=10, sticky="s")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        for i in range(9):
            self.main_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.main_frame.grid_columnconfigure(i, weight=1)

    def on_button_click(self, button_name):
        print(f"Button '{button_name}' clicked")
        if button_name == "Start Cycle Movement":
            threading.Thread(target=self.mock_long_motor_action, daemon=True).start()

    def mock_long_motor_action(self):
        self.update_status("WORKING...")
        time.sleep(5)  # эмуляция длительной работы
        status_queue.put("STOP")

    def update_status(self, text):
        self.status_label.config(text=f"Status: {text}")

    def update_interface(self):
        try:
            new_status = status_queue.get_nowait()
            self.update_status(new_status)
        except queue.Empty:
            pass
        self.root.after(100, self.update_interface)

def background_task():
    time.sleep(3)
    status_queue.put("STOP (from background task)")

def main():
    root = tk.Tk()
    gui = ControllerGUI(root)

    # Запускаем фоновую задачу (опционально)
    threading.Thread(target=background_task, daemon=True).start()

    root.minsize(600, 400)
    root.resizable(True, True)
    root.mainloop()

if __name__ == "__main__":
    main()
