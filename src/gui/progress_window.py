"""
Progress tracking window for content generation process
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from data.models import WordPressProject, ProcessingResult
from core.content_processor import ContentProcessor
from utils.logger import get_logger

class ProgressWindow:
    def __init__(self, parent, project: WordPressProject):
        self.parent = parent
        self.project = project
        self.processor = None
        self.results = []
        self.is_running = False
        self.is_cancelled = False
        self.logger = get_logger(__name__)
        
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """Configure progress window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"Processing: {self.project.name}")
        self.window.geometry("700x500")
        self.window.resizable(True, True)
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"700x500+{x}+{y}")
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        """Create progress window widgets"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Project info
        info_frame = ttk.LabelFrame(main_frame, text="Project Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Project: {self.project.name}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Website: {self.project.website_url}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Keywords: {len(self.project.keywords)}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Status: {self.project.status.title()}").pack(anchor=tk.W)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Current item label
        self.current_label = ttk.Label(progress_frame, text="Ready to start...")
        self.current_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Progress stats
        self.stats_label = ttk.Label(progress_frame, text="0/0 completed")
        self.stats_label.pack(anchor=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = ttk.Button(button_frame, text="Start Processing", 
                                   command=self.start_processing)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.pause_btn = ttk.Button(button_frame, text="Pause", 
                                   command=self.pause_processing, state='disabled')
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", 
                                    command=self.cancel_processing)
        self.cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.close_btn = ttk.Button(button_frame, text="Close", 
                                   command=self.close_window, state='disabled')
        self.close_btn.pack(side=tk.RIGHT)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results treeview
        columns = ('Keyword', 'Status', 'Title', 'Post ID', 'Time')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=8)
        
        # Configure columns
        self.results_tree.heading('Keyword', text='Keyword')
        self.results_tree.heading('Status', text='Status')
        self.results_tree.heading('Title', text='Title')
        self.results_tree.heading('Post ID', text='Post ID')
        self.results_tree.heading('Time', text='Time (s)')
        
        self.results_tree.column('Keyword', width=150)
        self.results_tree.column('Status', width=80)
        self.results_tree.column('Title', width=200)
        self.results_tree.column('Post ID', width=80)
        self.results_tree.column('Time', width=80)
        
        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, 
                                         command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        # Pack results tree and scrollbar
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for colored text
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("info", foreground="blue")
    
    def start_processing(self):
        """Start the content generation process"""
        if self.is_running:
            return
        
        self.is_running = True
        self.is_cancelled = False
        
        # Update UI
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.close_btn.config(state='disabled')
        
        # Clear previous results
        self.results.clear()
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.log_message("Starting content generation process...", "info")
        
        # Start processing in separate thread
        self.processing_thread = threading.Thread(target=self.process_keywords, daemon=True)
        self.processing_thread.start()
    
    def pause_processing(self):
        """Pause/resume processing"""
        # This would require more complex implementation
        # For now, just show a message
        messagebox.showinfo("Info", "Pause functionality not implemented yet")
    
    def cancel_processing(self):
        """Cancel the processing"""
        if self.is_running:
            if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel processing?"):
                self.is_cancelled = True
                self.log_message("Cancelling process...", "error")
        else:
            self.close_window()
    
    def process_keywords(self):
        """Process all keywords in separate thread"""
        try:
            self.processor = ContentProcessor(self.project)
            total_keywords = len(self.project.keywords)
            
            for index, keyword in enumerate(self.project.keywords):
                if self.is_cancelled:
                    break
                
                # Update progress
                progress = (index / total_keywords) * 100
                self.window.after(0, lambda p=progress, k=keyword, i=index, t=total_keywords: 
                                 self.update_progress(p, f"Processing: {k}", i, t))
                
                # Process keyword
                try:
                    result = self.processor.process_single_keyword(keyword)
                    self.results.append(result)
                    
                    # Update UI with result
                    self.window.after(0, lambda r=result: self.add_result(r))
                    
                    if result.success:
                        self.window.after(0, lambda k=keyword: 
                                         self.log_message(f"✓ Successfully processed: {k}", "success"))
                    else:
                        self.window.after(0, lambda k=keyword, e=result.error_message: 
                                         self.log_message(f"✗ Failed to process: {k} - {e}", "error"))
                
                except Exception as e:
                    error_msg = f"Error processing {keyword}: {str(e)}"
                    self.window.after(0, lambda msg=error_msg: self.log_message(msg, "error"))
                
                # Add delay between requests
                if index < total_keywords - 1 and not self.is_cancelled:
                    time.sleep(5)
            
            # Process complete
            if not self.is_cancelled:
                final_progress = 100
                self.window.after(0, lambda: self.update_progress(final_progress, "Processing complete!", 
                                                                total_keywords, total_keywords))
                self.window.after(0, self.processing_complete)
            else:
                self.window.after(0, lambda: self.log_message("Process cancelled by user", "error"))
                self.window.after(0, self.processing_cancelled)
                
        except Exception as e:
            error_msg = f"Processing failed: {str(e)}"
            self.window.after(0, lambda: self.log_message(error_msg, "error"))
            self.window.after(0, self.processing_failed)
    
    def update_progress(self, progress, status, current, total):
        """Update progress bar and status"""
        self.progress_var.set(progress)
        self.current_label.config(text=status)
        self.stats_label.config(text=f"{current}/{total} completed")
    
    def add_result(self, result: ProcessingResult):
        """Add result to the results tree"""
        status = "✓ Success" if result.success else "✗ Failed"
        title = result.title[:30] + "..." if len(result.title) > 30 else result.title
        post_id = str(result.post_id) if result.post_id else "-"
        processing_time = f"{result.processing_time:.1f}"
        
        self.results_tree.insert('', 'end', values=(
            result.keyword,
            status,
            title,
            post_id,
            processing_time
        ))
        
        # Scroll to bottom
        children = self.results_tree.get_children()
        if children:
            self.results_tree.see(children[-1])
    
    def log_message(self, message, tag="info"):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, full_message, tag)
        self.log_text.see(tk.END)
    
    def processing_complete(self):
        """Handle processing completion"""
        self.is_running = False
        
        # Update buttons
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled')
        self.close_btn.config(state='normal')
        
        # Show summary
        successful = sum(1 for r in self.results if r.success)
        failed = len(self.results) - successful
        
        summary_msg = f"Processing complete!\nSuccessful: {successful}\nFailed: {failed}"
        self.log_message(summary_msg, "info")
        
        messagebox.showinfo("Complete", summary_msg)
    
    def processing_cancelled(self):
        """Handle processing cancellation"""
        self.is_running = False
        
        # Update buttons
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled')
        self.close_btn.config(state='normal')
    
    def processing_failed(self):
        """Handle processing failure"""
        self.is_running = False
        
        # Update buttons
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled')
        self.close_btn.config(state='normal')
        
        messagebox.showerror("Error", "Processing failed. Check the log for details.")
    
    def on_close(self):
        """Handle window close event"""
        if self.is_running:
            if messagebox.askyesno("Confirm Close", 
                                  "Processing is still running. Do you want to cancel and close?"):
                self.is_cancelled = True
                self.window.destroy()
        else:
            self.window.destroy()
    
    def close_window(self):
        """Close the window"""
        self.window.destroy()