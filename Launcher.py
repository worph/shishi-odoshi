import sys
import time
import tkinter as tk
from tkinter import ttk, font

import pygame
from PIL import Image, ImageTk, ImageDraw
from pystray import MenuItem as item, Icon as icon

from Assets import getAssetPath
from Screenshot import Screenshot
from Watcher import Watcher

import threading


class Application:
    def __init__(self, root):
        self.root = root
        self.screenNumber = 1
        self.watcher = Watcher()
        self.screenShotTool = Screenshot()
        print(self.screenShotTool.list_monitors())  # an array of monitor
        self.screenVar = tk.StringVar()
        self.screen_dropdown = None  # to be defined in setup_gui
        self.is_watching = False
        self.labelImg = None
        self.intervalVar = tk.StringVar(value="10")  # default value of 10 seconds
        self.setup_gui()
        self.create_tray_icon()
        # Bind the close window event to exit_app
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    @staticmethod
    def round_corners(image, radius):
        mask = Image.new('L', image.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
        return Image.composite(image, Image.new('RGBA', image.size, (0, 0, 0, 0)), mask)

    def create_tray_icon(self):
        image = Image.open(getAssetPath('resources/image/shishi-odoshi.png'))
        menu = (
            item('Open', self.show_window),
            item('Exit', self.exit_app)
        )

        self.tray = icon("Shishi Odoshi", image, "Shishi Odoshi", menu)
        threading.Thread(target=self.tray.run, daemon=True).start()

    def setup_gui(self):
        self.root.title("Shishi Odoshi")
        pygame.mixer.init()

        self.windowWidth = 450
        self.windowHeight = 380
        self.root.geometry(f'{self.windowWidth}x{self.windowHeight}')
        self.root.resizable(False, False)
        self.root.configure(bg='#FFFFFF')
        self.root.iconbitmap(getAssetPath('resources/image/shishi-odoshi.ico'))  # Set the icon for the window

        # Bind the event when the window is minimized
        self.root.bind("<Unmap>", lambda e: self.hide_window() if self.root.state() == 'iconic' else None)

        # Custom font for titles
        regular_font = font.Font(size=11)

        # Image
        self.labelImg = ttk.Label(self.root, background="#FFFFFF")
        self.labelImg.grid(row=0, column=0, columnspan=4, padx=10, pady=20)
        self.resetImage()

        # Overview
        overview = ttk.Label(self.root,
                             text="Shishi Odoshi is a PC Screen Motion Alert Tool designed to emit an auditory alert when there's no motion detected on the PC screen.",
                             wraplength=400,
                             font=regular_font,
                             background="#FFFFFF")
        overview.grid(row=1, column=0, columnspan=4, padx=20, pady=0)

        # notification counter text
        self.time_label = ttk.Label(self.root, text="", font=regular_font, background="#FFFFFF")
        self.time_label.grid(row=2, column=0, columnspan=4, padx=20, pady=0)

        # start stop button
        self.toggle_btn = ttk.Button(self.root, text="Start", command=self.toggle_watch, width=20)
        self.toggle_btn.grid(row=3, column=0, padx=0, pady=0)

        # Get the list of monitors
        monitors = self.screenShotTool.list_monitors()
        monitorIds = ["Screen " + str(i) for i in range(1, len(monitors) + 1)]

        self.screen_dropdown = ttk.Combobox(self.root, textvariable=self.screenVar, values=monitorIds, state="readonly")
        self.screen_dropdown.set("Screen " + str(self.screenNumber))  # Set the initial value
        self.screen_dropdown.bind("<<ComboboxSelected>>", self.update_screen_selection)
        self.screen_dropdown.grid(row=3, column=1, columnspan=1, padx=0, pady=0)

        self.interval_spinbox = ttk.Spinbox(self.root, from_=1, to=3600, textvariable=self.intervalVar,
                                            width=5)  # allowing values between 1 second and 1 hour
        self.interval_spinbox.grid(row=3, column=3, padx=5, pady=0)
        self.intervalVar.trace_add("write", self.on_interval_changed)

        interval_label = ttk.Label(self.root, text="Interval (s):", background="#FFFFFF")
        interval_label.grid(row=3, column=2, padx=5, pady=0, sticky="e")

        self.updateTimeLabel()
        self.updateScreenshotLabel()

    def toggle_watch(self):
        if self.is_watching:
            self.stop()
            self.toggle_btn.config(text="Start")
        else:
            self.start()
            self.toggle_btn.config(text="Stop")
        self.is_watching = not self.is_watching

    def start(self):
        self.watcher.start(self.screenNumber)
        self.displaySceenShot()

    def stop(self):
        self.watcher.stop()
        self.resetImage()

    def on_interval_changed(self, *args):
        self.watcher.intervalSecond = int(self.intervalVar.get())

    def resetImage(self):
        image_url = getAssetPath("resources/image/shishi-odoshi.gif")
        innerWidth = int(self.windowWidth * 0.8)
        image = Image.open(image_url).resize((innerWidth, int(innerWidth*(9/16))))
        image = self.round_corners(image, 10)
        self.photo = ImageTk.PhotoImage(image)

        # Update the image in the label
        self.labelImg.config(image=self.photo)
        self.labelImg.image = self.photo

    def update_screen_selection(self, event):
        self.screenNumber = int(self.screenVar.get().replace("Screen ", ""))
        print(f"Selected Screen: {self.screenNumber}")
        self.updateScreenshotLabel()  # Update screenshot immediately after selecting

    def displaySceenShot(self):
        # Get and process the new screenshot
        screenshot = self.screenShotTool.capture(self.screenNumber)
        image = screenshot.resize((int(self.windowWidth * 0.8), int(self.windowHeight * 0.5)))
        image = self.round_corners(image, 10)
        self.photo = ImageTk.PhotoImage(image)

        # Update the image in the label
        self.labelImg.config(image=self.photo)
        self.labelImg.image = self.photo

    def updateScreenshotLabel(self):
        if self.watcher.lastActivityTime:
            self.displaySceenShot()
        self.root.after(int(self.intervalVar.get()) * 1000, self.updateScreenshotLabel)

    def show_window(self, icon, item):
        self.root.deiconify()

    def hide_window(self):
        self.root.withdraw()

    def exit_app(self, icon=None, item=None):
        if self.tray:
            self.tray.stop()
        self.watcher.stop()
        self.root.quit()
        #sys.exit()

    def updateTimeLabel(self):
        if self.watcher.lastActivityTime:
            elapsed_time = int(time.time() - self.watcher.lastActivityTime)
            minutes, seconds = divmod(elapsed_time, 60)
            self.time_label.config(text=f"Time since last notification: {minutes:02}:{seconds:02}")
        else:
            self.time_label.config(text=f"")
        self.root.after(500, self.updateTimeLabel)


if __name__ == "__main__":
    print("Started")
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
