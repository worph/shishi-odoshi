import threading
import time

import numpy as np
import pygame

from Screenshot import Screenshot

CORNER_MARGIN = 100  # Define the margin size to exclude from comparison


class Watcher:
    def __init__(self):
        self.screenNumber = None
        self.screenShotTool = Screenshot()
        self.running = False
        self.prev_screenshot = None
        self.lastActivityTime = None
        self.checkActivity = False #True for activity checkin and False for Inactivity checking
        self.intervalSecond = 10
        self.tolerancePixel = 100

    def play_sound(self):
        pygame.mixer.music.load("resources/audio/shishi-odoshi-sound.mp3")
        pygame.mixer.music.play()

    def start(self,screenNumber):
        self.lastActivityTime = time.time()
        self.running = True
        self.screenNumber = screenNumber
        thread = threading.Thread(target=self.watch_loop)
        thread.start()

    def stop(self):
        self.running = False
        self.lastActivityTime = None

    @staticmethod
    def computeDifferences(img1, img2):
        arr1 = np.array(img1)
        arr2 = np.array(img2)

        # Exclude the top-left and top-right corners
        arr1[:CORNER_MARGIN, :CORNER_MARGIN] = 0
        arr1[:CORNER_MARGIN, -CORNER_MARGIN:] = 0
        arr2[:CORNER_MARGIN, :CORNER_MARGIN] = 0
        arr2[:CORNER_MARGIN, -CORNER_MARGIN:] = 0

        diff = np.abs(arr1 - arr2)
        diffNumber = np.count_nonzero(diff > 0)
        print("Diff compute result :" + str(diffNumber))
        return diffNumber

    def watch_loop(self):
        while self.running:
            current_screenshot = self.screenShotTool.capture(self.screenNumber)

            if self.prev_screenshot:
                if(self.checkActivity):
                    #chek for screen activity (notify when the screen is active)
                    # a screen is active when two consecutive screenshot are different
                    if self.computeDifferences(current_screenshot, self.prev_screenshot) > self.tolerancePixel:
                        print("SIGNIFICANT screen change detected. Ringing the bell!")
                        self.checkActivity = False # switch to checking inactivity
                        self.play_sound()
                        self.lastActivityTime = time.time()
                else:
                    #chek for inactivity (notify when the screen is inactive)
                    #A screen is incative when 2 consecutive screenshot are the same
                    if self.computeDifferences(current_screenshot, self.prev_screenshot) < self.tolerancePixel:
                        print("NO significant screen change detected. Ringing the bell!")
                        self.checkActivity = True #switch to checking activity
                        self.play_sound()
                        self.lastActivityTime = time.time()

            self.prev_screenshot = current_screenshot
            time.sleep(self.intervalSecond)
