# 时钟
import tkinter as tk
import time


class Clock:
    def __init__(self):
        self.root = tk.Tk()
        # 设置窗口无边框、背景透明
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.1)  # 设置透明度
        self.root.configure(background="black")
        self.root.overrideredirect(True)
        self.root.bind("<Escape>", lambda x: self.root.quit())

        self.time_label = tk.Label(
            self.root, text="", font=("Arial", 80), fg="white", bg="black"
        )
        self.time_label.place(relx=0.5, rely=0.4, anchor="center")

        self.date_label = tk.Label(
            self.root, text="", font=("Arial", 30), fg="white", bg="black"
        )
        self.date_label.place(relx=0.5, rely=0.6, anchor="center")

    def get_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.get_time)

    def get_date(self):
        current_date = time.strftime("%Y-%m-%d")
        self.date_label.config(text=current_date)
        self.root.after(60000, self.get_date)

    def run(self):
        self.get_time()
        self.get_date()
        self.root.mainloop()


if __name__ == "__main__":
    clock = Clock()
    clock.run()
