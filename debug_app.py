"""
Debug version with detailed error logging
"""
import tkinter as tk
from tkinter import messagebox
import sys
import os
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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
        
        # Add debug mode
        app = MainWindow(root)
        
        # Add debug menu
        debug_menu = tk.Menu(root)
        root.config(menu=debug_menu)
        
        debug_submenu = tk.Menu(debug_menu, tearoff=0)
        debug_menu.add_cascade(label="Debug", menu=debug_submenu)
        debug_submenu.add_command(label="Check Data Directory", command=lambda: check_data_dir())
        debug_submenu.add_command(label="Test Encryption", command=lambda: test_encryption())
        debug_submenu.add_command(label="View Projects File", command=lambda: view_projects_file())
        
        # Start application
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Failed to start application: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_msg)
        messagebox.showerror("Error", error_msg)
        sys.exit(1)

def check_data_dir():
    """Check if data directory structure is correct"""
    import os
    dirs_to_check = ["data", "data/logs", "data/temp"]
    
    message = "Directory Status:\n\n"
    for directory in dirs_to_check:
        exists = os.path.exists(directory)
        writable = os.access(directory, os.W_OK) if exists else False
        message += f"{directory}: {'✓' if exists else '✗'} Exists, {'✓' if writable else '✗'} Writable\n"
    
    # Check projects file
    projects_file = "data/projects.json"
    if os.path.exists(projects_file):
        size = os.path.getsize(projects_file)
        message += f"\nprojects.json: Exists ({size} bytes)"
    else:
        message += f"\nprojects.json: Not found"
    
    messagebox.showinfo("Directory Check", message)

def test_encryption():
    """Test encryption functionality"""
    try:
        from utils.encryption import EncryptionManager
        
        enc = EncryptionManager()
        test_data = "test_password_123"
        
        # Test encrypt/decrypt
        encrypted = enc.encrypt(test_data)
        decrypted = enc.decrypt(encrypted)
        
        if decrypted == test_data:
            messagebox.showinfo("Encryption Test", "✓ Encryption working correctly")
        else:
            messagebox.showerror("Encryption Test", "✗ Encryption failed")
            
    except Exception as e:
        messagebox.showerror("Encryption Test", f"Error: {str(e)}")

def view_projects_file():
    """View contents of projects file"""
    try:
        projects_file = "data/projects.json"
        if os.path.exists(projects_file):
            with open(projects_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Show in new window
            import tkinter as tk
            from tkinter import scrolledtext
            
            window = tk.Toplevel()
            window.title("Projects File Content")
            window.geometry("600x400")
            
            text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
            text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_area.insert(tk.END, content)
            
        else:
            messagebox.showinfo("Projects File", "projects.json not found")
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read projects file: {str(e)}")

if __name__ == "__main__":
    main()