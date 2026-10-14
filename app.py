"""app.py - jalankan dari folder proyek:  python app.py"""
import tkinter as tk
from frontend.ui import Aplikasi
 
if __name__ == "__main__":
    root = tk.Tk()
    Aplikasi(root)
    root.mainloop()