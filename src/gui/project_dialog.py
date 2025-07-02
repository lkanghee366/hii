"""
Project configuration dialog for adding/editing projects
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from data.models import WordPressProject
from api.gemini_provider import GeminiProvider
from api.wordpress_api import WordPressAPI
from utils.logger import get_logger
import threading

class ProjectDialog:
    def __init__(self, parent, project=None):
        self.parent = parent
        self.project = project
        self.result = None
        self.success = False  # Add this line
        self.logger = get_logger(__name__)
        
        print(f"ProjectDialog initialized. Editing: {project is not None}")  # Debug
        
        self.setup_dialog()
        self.load_data()
    
    def setup_dialog(self):
        """Create and configure dialog window"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Project Configuration" if not self.project else f"Edit Project: {self.project.name}")
        self.dialog.geometry("600x700")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"600x700+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame with scrolling
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Project Name
        ttk.Label(main_frame, text="Project Name:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=50).grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # WordPress Configuration
        config_frame = ttk.LabelFrame(main_frame, text="WordPress Configuration", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Website URL
        ttk.Label(config_frame, text="Website URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.url_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.url_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Username
        ttk.Label(config_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.username_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.username_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # App Password
        ttk.Label(config_frame, text="App Password:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.password_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.password_var, show="*", width=40).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Category ID
        ttk.Label(config_frame, text="Category ID:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.category_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.category_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=(0, 5))
        
        # Post Status
        ttk.Label(config_frame, text="Post Status:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(config_frame, textvariable=self.status_var, 
                                   values=['draft', 'publish'], state='readonly', width=15)
        status_combo.grid(row=4, column=1, sticky=tk.W, pady=(0, 5))
        status_combo.set('draft')
        
        # AI Configuration
        ai_frame = ttk.LabelFrame(main_frame, text="AI Configuration", padding="10")
        ai_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        ai_frame.columnconfigure(1, weight=1)
        
        # AI Provider
        ttk.Label(ai_frame, text="AI Provider:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.ai_provider_var = tk.StringVar()
        ai_combo = ttk.Combobox(ai_frame, textvariable=self.ai_provider_var, 
                               values=['gemini', 'deepseek'], state='readonly', width=15)
        ai_combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        ai_combo.set('gemini')
        
        # API Key
        ttk.Label(ai_frame, text="API Key:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.api_key_var = tk.StringVar()
        ttk.Entry(ai_frame, textvariable=self.api_key_var, show="*", width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Test API button
        self.test_api_btn = ttk.Button(ai_frame, text="Test API", command=self.test_api)
        self.test_api_btn.grid(row=1, column=2, padx=(10, 0), pady=(0, 5))
        
        # Keywords Section
        keywords_frame = ttk.LabelFrame(main_frame, text="Keywords", padding="10")
        keywords_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        keywords_frame.columnconfigure(0, weight=1)
        keywords_frame.rowconfigure(1, weight=1)
        
        # Keywords buttons
        keywords_btn_frame = ttk.Frame(keywords_frame)
        keywords_btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(keywords_btn_frame, text="Import File", command=self.import_keywords).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(keywords_btn_frame, text="Clear All", command=self.clear_keywords).pack(side=tk.LEFT)
        
        # Keywords text area
        keywords_text_frame = ttk.Frame(keywords_frame)
        keywords_text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        keywords_text_frame.columnconfigure(0, weight=1)
        keywords_text_frame.rowconfigure(0, weight=1)
        
        self.keywords_text = tk.Text(keywords_text_frame, height=8, wrap=tk.WORD)
        keywords_scrollbar = ttk.Scrollbar(keywords_text_frame, orient=tk.VERTICAL, command=self.keywords_text.yview)
        self.keywords_text.configure(yscrollcommand=keywords_scrollbar.set)
        
        self.keywords_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        keywords_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Prompt Template Section
        prompt_frame = ttk.LabelFrame(main_frame, text="Prompt Template", padding="10")
        prompt_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        prompt_frame.columnconfigure(0, weight=1)
        prompt_frame.rowconfigure(1, weight=1)
        
        # Default prompt button
        ttk.Button(prompt_frame, text="Use Default Prompt", command=self.use_default_prompt).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Prompt text area
        prompt_text_frame = ttk.Frame(prompt_frame)
        prompt_text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        prompt_text_frame.columnconfigure(0, weight=1)
        prompt_text_frame.rowconfigure(0, weight=1)
        
        self.prompt_text = tk.Text(prompt_text_frame, height=6, wrap=tk.WORD)
        prompt_scrollbar = ttk.Scrollbar(prompt_text_frame, orient=tk.VERTICAL, command=self.prompt_text.yview)
        self.prompt_text.configure(yscrollcommand=prompt_scrollbar.set)
        
        self.prompt_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        prompt_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Set default prompt
        self.use_default_prompt()
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=3, pady=(20, 0))
        
        ttk.Button(buttons_frame, text="Test All Connections", command=self.test_all_connections).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Save", command=self.save_project).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def load_data(self):
        """Load existing project data if editing"""
        if self.project:
            self.name_var.set(self.project.name)
            self.url_var.set(self.project.website_url)
            self.username_var.set(self.project.username)
            self.password_var.set(self.project.app_password)
            self.category_var.set(str(self.project.category_id))
            self.status_var.set(self.project.status)
            self.ai_provider_var.set(self.project.ai_provider_type)
            self.api_key_var.set(self.project.ai_api_key)
            
            # Load keywords
            keywords_text = '\n'.join(self.project.keywords)
            self.keywords_text.delete(1.0, tk.END)
            self.keywords_text.insert(1.0, keywords_text)
            
            # Load prompt
            self.prompt_text.delete(1.0, tk.END)
            self.prompt_text.insert(1.0, self.project.prompt_template)
    
    def use_default_prompt(self):
        """Set default prompt template"""
        default_prompt = """Generate content 2000-words for the post about <keyword> with 7-10 heading 2. Intro and conclusion must contain keyword (heading 2 is better if it has keyword there).

Please write an engaging, informative article that:
- Uses the keyword naturally throughout the content
- Includes practical tips and actionable advice
- Has a clear structure with proper headings
- Provides value to readers
- Maintains a conversational tone"""
        
        self.prompt_text.delete(1.0, tk.END)
        self.prompt_text.insert(1.0, default_prompt)
    
    def import_keywords(self):
        """Import keywords from file"""
        file_path = filedialog.askopenfilename(
            title="Select Keywords File",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Parse keywords (one per line, or comma-separated)
                if file_path.endswith('.csv'):
                    keywords = [kw.strip() for line in content.split('\n') for kw in line.split(',') if kw.strip()]
                else:
                    keywords = [kw.strip() for kw in content.split('\n') if kw.strip()]
                
                # Add to text area
                current_text = self.keywords_text.get(1.0, tk.END).strip()
                if current_text:
                    keywords_text = current_text + '\n' + '\n'.join(keywords)
                else:
                    keywords_text = '\n'.join(keywords)
                
                self.keywords_text.delete(1.0, tk.END)
                self.keywords_text.insert(1.0, keywords_text)
                
                messagebox.showinfo("Success", f"Imported {len(keywords)} keywords")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import keywords: {str(e)}")
    
    def clear_keywords(self):
        """Clear all keywords"""
        if messagebox.askyesno("Confirm", "Clear all keywords?"):
            self.keywords_text.delete(1.0, tk.END)
    
    def test_api(self):
        """Test AI API connection"""
        api_key = self.api_key_var.get().strip()
        provider = self.ai_provider_var.get()
        
        if not api_key:
            messagebox.showwarning("Warning", "Please enter API key")
            return
        
        self.test_api_btn.config(state='disabled', text="Testing...")
        
        def test_thread():
            try:
                if provider == 'gemini':
                    ai_provider = GeminiProvider(api_key)
                    success = ai_provider.test_connection()
                else:
                    # DeepSeek or other providers would go here
                    success = False
                
                result = "✓ API connection successful!" if success else "✗ API connection failed"
                self.dialog.after(0, lambda: messagebox.showinfo("Test Result", result))
                
            except Exception as e:
                self.dialog.after(0, lambda: messagebox.showerror("Test Failed", f"API test failed: {str(e)}"))
            finally:
                self.dialog.after(0, lambda: self.test_api_btn.config(state='normal', text="Test API"))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def test_all_connections(self):
        """Test both WordPress and AI connections"""
        # Validate required fields
        if not self.validate_fields():
            return
        
        messagebox.showinfo("Test", "Testing connections... This may take a moment.")
        
        def test_thread():
            results = []
            
            # Test WordPress
            try:
                wp_api = WordPressAPI(
                    self.url_var.get().strip(),
                    self.username_var.get().strip(),
                    self.password_var.get().strip()
                )
                wp_result = wp_api.test_connection()
                if wp_result['success']:
                    results.append("✓ WordPress: Connected")
                else:
                    results.append(f"✗ WordPress: {wp_result['error']}")
            except Exception as e:
                results.append(f"✗ WordPress: {str(e)}")
            
            # Test AI API
            try:
                if self.ai_provider_var.get() == 'gemini':
                    ai_provider = GeminiProvider(self.api_key_var.get().strip())
                    ai_success = ai_provider.test_connection()
                    if ai_success:
                        results.append("✓ AI Provider: Connected")
                    else:
                        results.append("✗ AI Provider: Connection failed")
                else:
                    results.append("✗ AI Provider: Not implemented")
            except Exception as e:
                results.append(f"✗ AI Provider: {str(e)}")
            
            # Show results
            message = "Connection Test Results:\n\n" + "\n".join(results)
            self.dialog.after(0, lambda: messagebox.showinfo("Test Results", message))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def validate_fields(self):
        """Validate all required fields"""
        if not self.name_var.get().strip():
            messagebox.showerror("Error", "Project name is required")
            return False
        
        if not self.url_var.get().strip():
            messagebox.showerror("Error", "Website URL is required")
            return False
        
        if not self.username_var.get().strip():
            messagebox.showerror("Error", "Username is required")
            return False
        
        if not self.password_var.get().strip():
            messagebox.showerror("Error", "App password is required")
            return False
        
        try:
            int(self.category_var.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Category ID must be a number")
            return False
        
        if not self.api_key_var.get().strip():
            messagebox.showerror("Error", "API key is required")
            return False
        
        keywords = self.keywords_text.get(1.0, tk.END).strip()
        if not keywords:
            messagebox.showerror("Error", "At least one keyword is required")
            return False
        
        return True
    
    def save_project(self):
        """Save project configuration"""
        print("Save button clicked!")  # Debug
        
        try:
            # Disable save button to prevent double-click
            self.save_btn.config(state='disabled', text="Saving...")
            
            print("Starting validation...")  # Debug
            if not self.validate_fields():
                print("Validation failed!")  # Debug
                self.save_btn.config(state='normal', text="Save Project")
                return
            
            print("Validation passed, parsing data...")  # Debug
            
            # Parse keywords
            keywords_text = self.keywords_text.get(1.0, tk.END).strip()
            keywords = [kw.strip() for kw in keywords_text.split('\n') if kw.strip()]
            print(f"Parsed {len(keywords)} keywords")  # Debug
            
            # Get prompt
            prompt = self.prompt_text.get(1.0, tk.END).strip()
            print(f"Prompt length: {len(prompt)}")  # Debug
            
            # Create or update project
            if self.project:
                print("Updating existing project...")  # Debug
                self.project.update(
                    name=self.name_var.get().strip(),
                    website_url=self.url_var.get().strip(),
                    username=self.username_var.get().strip(),
                    app_password=self.password_var.get().strip(),
                    category_id=int(self.category_var.get().strip()),
                    status=self.status_var.get(),
                    keywords=keywords,
                    prompt_template=prompt,
                    ai_api_key=self.api_key_var.get().strip(),
                    ai_provider_type=self.ai_provider_var.get()
                )
                self.result = self.project
            else:
                print("Creating new project...")  # Debug
                self.result = WordPressProject.create_new(
                    name=self.name_var.get().strip(),
                    website_url=self.url_var.get().strip(),
                    username=self.username_var.get().strip(),
                    app_password=self.password_var.get().strip(),
                    category_id=int(self.category_var.get().strip()),
                    status=self.status_var.get(),
                    keywords=keywords,
                    prompt_template=prompt,
                    ai_api_key=self.api_key_var.get().strip(),
                    ai_provider_type=self.ai_provider_var.get()
                )
            
            print(f"Project created/updated successfully! ID: {self.result.id}")  # Debug
            print(f"Result object: {self.result}")  # Debug
            print("About to close dialog...")  # Debug
            
            # Set success flag before destroying
            self.success = True
            
            # Close dialog - but don't destroy immediately
            self.dialog.withdraw()  # Hide instead of destroy
            
            print(f"Dialog hidden. Result still available: {self.result is not None}")  # Debug
            
        except Exception as e:
            error_msg = f"Failed to save project: {str(e)}"
            print(f"ERROR in save_project: {error_msg}")  # Debug
            print(f"Traceback: {traceback.format_exc()}")  # Debug
            messagebox.showerror("Save Error", error_msg)
            self.save_btn.config(state='normal', text="Save Project")

    def cancel(self):
        """Cancel dialog"""
        print("Cancel button clicked!")  # Debug
        self.result = None
        self.success = False
        self.dialog.withdraw()

    def on_close(self):
        """Handle window close event"""
        print("Dialog close event triggered!")  # Debug
        if not hasattr(self, 'success'):
            self.success = False
        if not hasattr(self, 'result') or self.result is None:
            self.result = None
        self.dialog.withdraw()

    def destroy_dialog(self):
        """Properly destroy dialog"""
        if hasattr(self, 'dialog') and self.dialog.winfo_exists():
            self.dialog.destroy()