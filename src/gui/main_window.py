"""
Main application window with project management
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from gui.project_dialog import ProjectDialog
from gui.progress_window import ProgressWindow
from core.project_manager import ProjectManager
from core.content_processor import ContentProcessor
from utils.logger import get_logger

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.project_manager = ProjectManager()
        self.logger = get_logger(__name__)
        
        self.setup_window()
        self.create_widgets()
        self.load_projects()
    
    def setup_window(self):
        """Configure main window"""
        self.root.title("WordPress Content Generator")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")
        
        # Set icon if available
        try:
            self.root.iconbitmap("assets/icons/app.ico")
        except:
            pass
    
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="WordPress Content Generator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.N), padx=(0, 10))
        
        # Add project button
        self.add_btn = ttk.Button(buttons_frame, text="+ Add New Project", 
                                 command=self.add_project, width=20)
        self.add_btn.pack(pady=(0, 10), fill=tk.X)
        
        # Edit project button
        self.edit_btn = ttk.Button(buttons_frame, text="Edit Project", 
                                  command=self.edit_project, width=20, state='disabled')
        self.edit_btn.pack(pady=(0, 10), fill=tk.X)
        
        # Delete project button
        self.delete_btn = ttk.Button(buttons_frame, text="Delete Project", 
                                    command=self.delete_project, width=20, state='disabled')
        self.delete_btn.pack(pady=(0, 10), fill=tk.X)
        
        # Separator
        ttk.Separator(buttons_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Run project button
        self.run_btn = ttk.Button(buttons_frame, text="🚀 Run Project", 
                                 command=self.run_project, width=20, state='disabled')
        self.run_btn.pack(pady=(0, 10), fill=tk.X)
        
        # Test connections button
        self.test_btn = ttk.Button(buttons_frame, text="Test Connections", 
                                  command=self.test_connections, width=20, state='disabled')
        self.test_btn.pack(pady=(0, 10), fill=tk.X)
        
        # Projects list frame
        list_frame = ttk.LabelFrame(main_frame, text="Projects", padding="10")
        list_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview for projects
        columns = ('Name', 'Website', 'Keywords', 'Status', 'AI Provider')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('Name', text='Project Name')
        self.tree.heading('Website', text='Website URL')
        self.tree.heading('Keywords', text='Keywords Count')
        self.tree.heading('Status', text='Post Status')
        self.tree.heading('AI Provider', text='AI Provider')
        
        self.tree.column('Name', width=150)
        self.tree.column('Website', width=200)
        self.tree.column('Keywords', width=100)
        self.tree.column('Status', width=80)
        self.tree.column('AI Provider', width=100)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid treeview and scrollbar
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.on_project_select)
        self.tree.bind('<Double-1>', self.edit_project)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def load_projects(self):
        """Load projects from storage"""
        try:
            projects = self.project_manager.load_projects()
            self.refresh_project_list()
            self.status_var.set(f"Loaded {len(projects)} projects")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load projects: {str(e)}")
            self.status_var.set("Error loading projects")
    
    def refresh_project_list(self):
        """Refresh the projects list display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add projects
        for project in self.project_manager.projects:
            keywords_count = len(project.keywords)
            self.tree.insert('', 'end', iid=project.id, values=(
                project.name,
                project.website_url,
                f"{keywords_count} keywords",
                project.status.title(),
                project.ai_provider_type.title()
            ))
    
    def on_project_select(self, event):
        """Handle project selection"""
        selection = self.tree.selection()
        if selection:
            self.edit_btn.config(state='normal')
            self.delete_btn.config(state='normal')
            self.run_btn.config(state='normal')
            self.test_btn.config(state='normal')
        else:
            self.edit_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')
            self.run_btn.config(state='disabled')
            self.test_btn.config(state='disabled')
    
    def add_project(self):
        """Open dialog to add new project"""
        print("=== ADD PROJECT STARTED ===")  # Debug
        
        try:
            print("Creating project dialog...")  # Debug
            dialog = ProjectDialog(self.root)
            
            print("Waiting for dialog to complete...")  # Debug
            # Wait for dialog to be hidden (not destroyed)
            self.root.wait_window(dialog.dialog)
            
            print(f"Dialog completed. Success: {getattr(dialog, 'success', False)}")  # Debug
            print(f"Dialog result: {dialog.result}")  # Debug
            
            if hasattr(dialog, 'success') and dialog.success and dialog.result:
                print("Dialog has valid result, adding to manager...")  # Debug
                print(f"Project data: {dialog.result.name}, {len(dialog.result.keywords)} keywords")  # Debug
                
                # Add project
                self.project_manager.add_project(dialog.result)
                
                print("Project added successfully, refreshing list...")  # Debug
                self.refresh_project_list()
                self.status_var.set(f"Project '{dialog.result.name}' added successfully")
                print("=== ADD PROJECT COMPLETED ===")  # Debug
                    
            else:
                print("No valid result from dialog - user cancelled or error occurred")  # Debug
                self.status_var.set("Project creation cancelled")
            
            # Now properly destroy the dialog
            print("Destroying dialog...")  # Debug
            dialog.destroy_dialog()
                
        except Exception as e:
            error_msg = f"Failed to add project: {str(e)}"
            print(f"ERROR in add_project: {error_msg}")  # Debug
            print(f"Traceback: {traceback.format_exc()}")  # Debug
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Error adding project")
        
        print("=== ADD PROJECT ENDED ===")  # Debug
    
    
    def edit_project(self, event=None):
        """Edit selected project"""
        selection = self.tree.selection()
        if not selection:
            return
        
        project_id = selection[0]
        project = self.project_manager.get_project(project_id)
        
        if project:
            dialog = ProjectDialog(self.root, project)
            if dialog.result:
                try:
                    self.project_manager.update_project(project_id, dialog.result)
                    self.refresh_project_list()
                    self.status_var.set("Project updated successfully")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update project: {str(e)}")
    
    def delete_project(self):
        """Delete selected project"""
        selection = self.tree.selection()
        if not selection:
            return
        
        project_id = selection[0]
        project = self.project_manager.get_project(project_id)
        
        if project:
            if messagebox.askyesno("Confirm Delete", 
                                  f"Are you sure you want to delete project '{project.name}'?"):
                try:
                    self.project_manager.delete_project(project_id)
                    self.refresh_project_list()
                    self.status_var.set("Project deleted successfully")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete project: {str(e)}")
    
    def test_connections(self):
        """Test connections for selected project"""
        selection = self.tree.selection()
        if not selection:
            return
        
        project_id = selection[0]
        project = self.project_manager.get_project(project_id)
        
        if project:
            self.status_var.set("Testing connections...")
            self.root.config(cursor="wait")
            
            def test_thread():
                try:
                    processor = ContentProcessor(project)
                    results = processor.test_connections()
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.show_test_results(results))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Test failed: {str(e)}"))
                finally:
                    self.root.after(0, lambda: self.root.config(cursor=""))
                    self.root.after(0, lambda: self.status_var.set("Ready"))
            
            threading.Thread(target=test_thread, daemon=True).start()
    
    def show_test_results(self, results):
        """Show connection test results"""
        ai_result = results.get('ai', {})
        wp_result = results.get('wordpress', {})
        
        message = "Connection Test Results:\n\n"
        
        # AI provider test
        if ai_result.get('success'):
            message += "✓ AI Provider: Connected\n"
        else:
            message += f"✗ AI Provider: {ai_result.get('error', 'Failed')}\n"
        
        # WordPress test
        if wp_result.get('success'):
            message += "✓ WordPress: Connected\n"
        else:
            message += f"✗ WordPress: {wp_result.get('error', 'Failed')}\n"
        
        if ai_result.get('success') and wp_result.get('success'):
            messagebox.showinfo("Test Results", message)
        else:
            messagebox.showwarning("Test Results", message)
    
    def run_project(self):
        """Run content generation for selected project"""
        selection = self.tree.selection()
        if not selection:
            return
        
        project_id = selection[0]
        project = self.project_manager.get_project(project_id)
        
        if not project:
            return
        
        if not project.keywords:
            messagebox.showwarning("Warning", "Project has no keywords to process.")
            return
        
        # Confirm before running
        keyword_count = len(project.keywords)
        if not messagebox.askyesno("Confirm Run", 
                                  f"This will process {keyword_count} keywords and create posts on {project.website_url}.\n\nContinue?"):
            return
        
        # Open progress window and start processing
        progress_window = ProgressWindow(self.root, project)
        progress_window.start_processing()