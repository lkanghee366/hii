"""
WordPress Content Generator - Main Entry Point
"""
import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from gui.main_window import MainWindow
from utils.logger import setup_logging
from utils.file_handler import ensure_directories

def main():
    try:
        # Setup logging and directories
        setup_logging()
        ensure_directories()
        
        # Create main window
        root = tk.Tk()
        app = MainWindow(root)
        
        # Start application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()