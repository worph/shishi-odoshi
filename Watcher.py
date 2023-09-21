import threading
import time

import numpy as np
import pygame

from Assets import getAssetPath
from Screenshot import Screenshot

class Watcher:
    def __init__(self):
        self.thread = None
        self.screenNumber = None
        self.screenShotTool = Screenshot()
        self.prev_screenshot = None
        self.lastActivityTime = None
        self.checkActivity = False #True for activity checkin and False for Inactivity checking
        self.intervalSecond = 10
        self.tolerancePixel = 100
        self.stop_event = threading.Event()

    def play_sound(self):
        pygame.mixer.music.load(getAssetPath("resources/audio/shishi-odoshi-sound.mp3"))
        pygame.mixer.music.play()

    def start(self,screenNumber):
        self.lastActivityTime = time.time()
        self.running = True
        self.screenNumber = screenNumber
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.watch_loop)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()  # Wait for the thread to actually stop
        self.lastActivityTime = None

    @staticmethod
    def computeDifferences(img1, img2):
        arr1 = np.array(img1)
        arr2 = np.array(img2)

        # Exclude the bottom 6% of both images
        exclude_height = int(0.06 * arr1.shape[0])
        arr1[-exclude_height:, :] = 0
        arr2[-exclude_height:, :] = 0

        diff = np.abs(arr1 - arr2)
        diffNumber = np.count_nonzero(diff > 0)
        print("Diff compute result :" + str(diffNumber))
        return diffNumber


    def watch_loop(self):
        while not self.stop_event.is_set():
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
            # This will either sleep for self.intervalSecond or until stop_event is set.
            self.stop_event.wait(self.intervalSecond)
