import tkinter as tk
from tkinter import messagebox
import threading
import time
import pyautogui
import pytesseract
import keyboard
from pynput import mouse
import os
from PIL import ImageTk

# Add Tesseract to system PATH so pytesseract can find it automatically
os.environ["PATH"] += os.pathsep + r'C:\OCR\Tesseract-OCR'

class RerollerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto-Reroller")
        self.root.geometry("300x400")
        self.root.attributes("-topmost", True)  # Keep window on top
        
        self.step = 0
        self.pos_recall = None
        self.pos_store = None
        self.pos_reroll = None
        self.region_center = None
        
        self.max_roll = 0
        self.is_running = False
        self.reroll_delay = 0.5
        
        self.last_debug_image = None
        
        # UI Elements
        self.lbl_instructions = tk.Label(root, text="Welcome! Click 'Start Setup' to begin.", wraplength=280, font=("Helvetica", 11))
        self.lbl_instructions.pack(pady=(10, 5))
        
        self.btn_setup = tk.Button(root, text="Start Setup", command=self.start_setup, font=("Helvetica", 10, "bold"), bg="#4CAF50", fg="white", width=20)
        self.btn_setup.pack(pady=2)
        
        self.btn_start = tk.Button(root, text="Start Rerolling", command=self.start_rerolling, font=("Helvetica", 10, "bold"), state=tk.DISABLED, bg="#2196F3", fg="white", width=20)
        self.btn_start.pack(pady=2)
        
        self.lbl_max_roll = tk.Label(root, text="Current Max Roll: 0", font=("Helvetica", 14, "bold"))
        self.lbl_max_roll.pack(pady=(10, 5))
        
        self.btn_clear_max = tk.Button(root, text="Clear Max Roll", command=self.clear_max_roll, font=("Helvetica", 9, "bold"), bg="#FF9800", fg="white", width=15)
        self.btn_clear_max.pack(pady=2)
        
        # Speed control
        frame_speed = tk.Frame(root)
        frame_speed.pack(pady=5)
        tk.Label(frame_speed, text="Delay (s):").pack(side=tk.LEFT, padx=2)
        self.speed_var = tk.DoubleVar(value=self.reroll_delay)
        self.spin_speed = tk.Spinbox(frame_speed, from_=0.1, to=5.0, increment=0.1, textvariable=self.speed_var, width=5, command=self.on_speed_change)
        self.spin_speed.pack(side=tk.LEFT)
        self.spin_speed.bind("<KeyRelease>", self.on_speed_change)
        
        tk.Label(root, text="Tip: Hold '+' or '-' while running to adjust speed", font=("Helvetica", 8, "italic")).pack(pady=2)
        
        # Debug control
        self.debug_var = tk.BooleanVar(value=False)
        self.chk_debug = tk.Checkbutton(root, text="Debug (Show Image)", variable=self.debug_var, command=self.on_debug_toggle)
        self.chk_debug.pack(pady=2)
        
        self.lbl_debug_image = tk.Label(root)
        self.lbl_debug_image.pack(pady=2)

    def update_debug_image(self, photo=None, text=""):
        if photo:
            self.lbl_debug_image.config(image=photo, text="")
            self.lbl_debug_image.image = photo
        else:
            self.lbl_debug_image.config(image='', text=text)
            self.lbl_debug_image.image = None

    def on_debug_toggle(self):
        if self.debug_var.get():
            if self.last_debug_image:
                try:
                    debug_photo = ImageTk.PhotoImage(self.last_debug_image)
                    self.update_debug_image(photo=debug_photo)
                except Exception:
                    self.update_debug_image(text="Debug image error")
            else:
                self.update_debug_image(text="No image")
        else:
            self.update_debug_image(text="")

    def on_speed_change(self, event=None):
        try:
            val = float(self.speed_var.get())
            if val >= 0.1:
                self.reroll_delay = val
        except ValueError:
            pass

    def clear_max_roll(self):
        self.max_roll = 0
        self.lbl_max_roll.config(text=f"Current Max Roll: {self.max_roll}")

    def start_setup(self):
        self.btn_setup.config(state=tk.DISABLED)
        self.step = 1
        self.update_instructions("Click on the 'Recall' button.")
        
        self.root.after(300, lambda: mouse.Listener(on_click=self.on_click).start())
        
    def update_instructions(self, text):
        self.lbl_instructions.config(text=text)
        
    def on_click(self, x, y, button, pressed):
        if not pressed:
            return
            
        if self.step == 1:
            self.pos_recall = (x, y)
            self.step = 2
            self.root.after(0, self.update_instructions, "Click on the 'Store' button.")
        elif self.step == 2:
            self.pos_store = (x, y)
            self.step = 3
            self.root.after(0, self.update_instructions, "Click on the CENTER of the total roll number.")
        elif self.step == 3:
            self.region_center = (x, y)
            self.step = -1
            self.root.after(0, self.update_instructions, "Reading initial max roll...")
            threading.Thread(target=self.read_initial_max_roll, daemon=True).start()
        elif self.step == 4:
            self.pos_reroll = (x, y)
            self.root.after(0, self.update_instructions, "Setup Complete! Click 'Start Rerolling'.")
            self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.btn_setup.config(state=tk.NORMAL))
            return False

    def _get_ocr_value(self):
        width, height = 50, 40
        left = int(self.region_center[0] - width // 2)
        top = int(self.region_center[1] - height // 2)
        region = (left, top, width, height)
        
        img = pyautogui.screenshot(region=region).convert('L')
        self.last_debug_image = img
        
        if self.debug_var.get():
            try:
                debug_photo = ImageTk.PhotoImage(img)
                self.root.after(0, lambda p=debug_photo: self.update_debug_image(photo=p))
            except Exception as e:
                print(f"Debug image error: {e}")
            
        try:
            text = pytesseract.image_to_string(img, config='--psm 7 -c tessedit_char_whitelist=0123456789')
            clean_text = "".join(filter(str.isdigit, text))
            return int(clean_text) if clean_text else -1
        except pytesseract.TesseractNotFoundError:
            return None
        except Exception as e:
            print(f"OCR Error: {e}")
            return -1

    def read_initial_max_roll(self):
        val = self._get_ocr_value()
        if val is not None and val != -1:
            self.max_roll = val
            self.root.after(0, self.lbl_max_roll.config, {"text": f"Current Max Roll: {self.max_roll}"})
            
        self.step = 4
        self.root.after(0, self.update_instructions, "Click on the 'Reroll' button.")

    def start_rerolling(self):
        self.btn_start.config(state=tk.DISABLED)
        self.is_running = True
        self.update_instructions("Rerolling... Hold 'x' to stop.")
        
        # Start loop in a separate thread to keep UI responsive
        threading.Thread(target=self.reroll_loop, daemon=True).start()
        
    def reroll_loop(self):
        while self.is_running:
            if keyboard.is_pressed('x'):
                self.is_running = False
                break
                
            current_roll = self._get_ocr_value()
            
            if current_roll is None:
                self.root.after(0, messagebox.showerror, "Error", "Tesseract OCR not found. Please install it and/or set its path in the script.")
                self.is_running = False
                break
                
            # 4. Check against max roll
            if current_roll > self.max_roll:
                self.max_roll = current_roll
                # Update UI safely
                self.root.after(0, self.lbl_max_roll.config, {"text": f"Current Max Roll: {self.max_roll}"})
                
                # Click Store button
                pyautogui.click(self.pos_store[0], self.pos_store[1])
                time.sleep(0.5)  # Pause to allow storing animation
                
                if self.max_roll >= 108:
                    self.is_running = False
                    break
                
            # 5. Click Reroll button
            pyautogui.click(self.pos_reroll[0], self.pos_reroll[1])
            
            # Delay to allow animation/UI update before next capture
            # We sleep in small increments so we can detect speed changes smoothly
            sleep_time = 0.0
            while sleep_time < self.reroll_delay and self.is_running:
                if keyboard.is_pressed('+') or keyboard.is_pressed('add'):
                    self.reroll_delay = max(0.1, self.reroll_delay - 0.05)
                    self.root.after(0, self.speed_var.set, round(self.reroll_delay, 2))
                elif keyboard.is_pressed('-') or keyboard.is_pressed('subtract'):
                    self.reroll_delay += 0.05
                    self.root.after(0, self.speed_var.set, round(self.reroll_delay, 2))
                
                time.sleep(0.05)
                sleep_time += 0.05
            
        # Cleanup when stopped
        self.root.after(0, self.finish_rerolling)
        
    def finish_rerolling(self):
        # Click recall whenever we stop rerolling
        if self.pos_recall:
            pyautogui.click(self.pos_recall[0], self.pos_recall[1])
            
        self.update_instructions("Process stopped.")
        self.btn_start.config(state=tk.NORMAL)
        self.btn_setup.config(state=tk.NORMAL)
        messagebox.showinfo("Max Roll Obtained", f"Process stopped.\nMax roll obtained: {self.max_roll}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RerollerApp(root)
    root.mainloop()
