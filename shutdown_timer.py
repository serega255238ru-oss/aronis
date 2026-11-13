import os
import ctypes
import customtkinter as ctk

# Настройка темы оформления
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ShutdownTimerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Таймер выключения ПК")
        self.geometry("420x480")
        self.resizable(False, False)

        self.remaining_seconds = 0
        self.total_seconds = 0
        self.timer_running = False
        self.after_id = None

        self._build_ui()

    def _build_ui(self):
        # Заголовок
        self.title_label = ctk.CTkLabel(
            self, text="Выключение ПК", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(25, 10))

        # Крупный дисплей обратного отсчета
        self.time_display = ctk.CTkLabel(
            self,
            text="00:00:00",
            font=ctk.CTkFont(family="Consolas", size=48, weight="bold"),
            text_color="#3b8ed0",
        )
        self.time_display.pack(pady=(5, 10))

        # Полоса прогресса
        self.progress_bar = ctk.CTkProgressBar(self, width=320, height=10)
        self.progress_bar.pack(pady=(0, 20))
        self.progress_bar.set(0)

        # Поля ввода (Часы, Минуты, Секунды)
        self.inputs_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.inputs_frame.pack(pady=5)

        self.hours_entry = self._create_time_input(self.inputs_frame, "Часы", "0", 0)
        self.minutes_entry = self._create_time_input(self.inputs_frame, "Минуты", "30", 1)
        self.seconds_entry = self._create_time_input(self.inputs_frame, "Секунды", "0", 2)

        # Быстрые пресеты
        self.presets_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.presets_frame.pack(pady=15)

        presets = [("+15 мин", 15), ("+30 мин", 30), ("+1 час", 60), ("Сброс", 0)]
        for text, mins in presets:
            btn = ctk.CTkButton(
                self.presets_frame,
                text=text,
                width=78,
                height=32,
                fg_color="#2b2b2b",
                hover_color="#3a3a3a",
                command=lambda m=mins: self.apply_preset(m),
            )
            btn.pack(side="left", padx=4)

        # Кнопки управления
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(pady=(15, 10))

        self.start_btn = ctk.CTkButton(
            self.controls_frame,
            text="Запустить таймер",
            width=165,
            height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#2fa572",
            hover_color="#106a43",
            command=self.start_timer,
        )
        self.start_btn.pack(side="left", padx=8)

        self.cancel_btn = ctk.CTkButton(
            self.controls_frame,
            text="Отменить",
            width=145,
            height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#d9534f",
            hover_color="#a94442",
            state="disabled",
            command=self.cancel_timer,
        )
        self.cancel_btn.pack(side="left", padx=8)

        # Статус-бар
        self.status_label = ctk.CTkLabel(
            self, text="Готов к запуску", font=ctk.CTkFont(size=13), text_color="gray"
        )
        self.status_label.pack(pady=(10, 0))

    def _create_time_input(self, parent, label_text, default_val, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=10)

        lbl = ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=12))
        lbl.pack(pady=(0, 4))

        entry = ctk.CTkEntry(
            frame,
            width=80,
            height=38,
            justify="center",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        entry.insert(0, default_val)
        entry.pack()
        return entry

    def apply_preset(self, minutes):
        if self.timer_running:
            return
        if minutes == 0:
            self._set_entries(0, 0, 0)
            return

        h, m, s = self._get_entries()
        total_m = h * 60 + m + minutes
        new_h = total_m // 60
        new_m = total_m % 60
        self._set_entries(new_h, new_m, s)

    def _get_entries(self):
        try:
            h = max(0, int(self.hours_entry.get() or 0))
            m = max(0, int(self.minutes_entry.get() or 0))
            s = max(0, int(self.seconds_entry.get() or 0))
            return h, m, s
        except ValueError:
            return 0, 0, 0

    def _set_entries(self, h, m, s):
        for entry, val in zip(
            (self.hours_entry, self.minutes_entry, self.seconds_entry), (h, m, s)
        ):
            entry.delete(0, "end")
            entry.insert(0, str(val))

    def start_timer(self):
        h, m, s = self._get_entries()
        self.total_seconds = h * 3600 + m * 60 + s

        if self.total_seconds <= 0:
            self.status_label.configure(
                text="Укажите время больше 0 секунд!", text_color="#e67e22"
            )
            return

        self.remaining_seconds = self.total_seconds
        self.timer_running = True

        self.start_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self._toggle_inputs("disabled")
        self.progress_bar.set(1.0)
        self.status_label.configure(
            text="Таймер активен. ПК выключится по завершении.", text_color="#2fa572"
        )

        self._tick()

    def _tick(self):
        if not self.timer_running:
            return

        hrs, rem = divmod(self.remaining_seconds, 3600)
        mins, secs = divmod(rem, 60)
        self.time_display.configure(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")

        if self.total_seconds > 0:
            self.progress_bar.set(self.remaining_seconds / self.total_seconds)

        if self.remaining_seconds <= 0:
            self.status_label.configure(text="Выключение ПК...", text_color="#d9534f")
            os.system("shutdown /s /t 0")
            return

        self.remaining_seconds -= 1
        self.after_id = self.after(1000, self._tick)

    def cancel_timer(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

        self.timer_running = False
        os.system("shutdown /a")  # На случай системного таймера

        self.time_display.configure(text="00:00:00")
        self.progress_bar.set(0)
        self.start_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self._toggle_inputs("normal")
        self.status_label.configure(text="Таймер отменен", text_color="gray")

    def _toggle_inputs(self, state):
        self.hours_entry.configure(state=state)
        self.minutes_entry.configure(state=state)
        self.seconds_entry.configure(state=state)


if __name__ == "__main__":
    # Улучшение четкости шрифтов на экранах с высоким разрешением (Windows)
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = ShutdownTimerApp()
    app.mainloop()
