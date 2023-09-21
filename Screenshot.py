from PIL import Image, ImageTk
import mss

class Screenshot:

    def __init__(self):
        pass

    def list_monitors(self):
        with mss.mss() as sct:
            return sct.monitors[1:]  # The first item is the combined screen, so we skip it

    def capture(self, monitor_number=1):
        with mss.mss() as sct:
                if monitor_number > len(sct.monitors) - 1:
                    print(f"No monitor found for number {monitor_number}.")
                    return []
                sct_img = sct.grab(sct.monitors[monitor_number])
                img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                return img

'''
#USAGE:
import tkinter as tk
def display(images):
    root = tk.Tk()
    root.title("Screenshots")

    for image in images:
        screenshot_image = ImageTk.PhotoImage(image)
        label = tk.Label(root, image=screenshot_image)
        label.image = screenshot_image  # keep a reference to prevent GC
        label.pack()

    root.mainloop()

if __name__ == "__main__":
    screenshot_tool = Screenshot()

    print("Available monitors:")
    for index, monitor in enumerate(screenshot_tool.list_monitors(), start=1):
        print(f"Monitor {index}: {monitor}")

    choice = input("Enter the monitor number to capture: ")
    monitor_number = int(choice)
    screenshot = screenshot_tool.capture(monitor_number)
    display([screenshot])
'''