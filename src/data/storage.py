"""
Data persistence functionality with permission handling
"""
import json
import os
import tempfile
from typing import List
from data.models import WordPressProject
from utils.encryption import EncryptionManager
from utils.file_handler import ensure_directories, get_data_dir, test_write_permission
from utils.logger import get_logger

class DataStorage:
    def __init__(self):
        self.data_dir = get_data_dir()
        self.projects_file = os.path.join(self.data_dir, "projects.json")
        self.logger = get_logger(__name__)
        
        # Ensure directories exist
        ensure_directories()
        
        # Test permissions and setup encryption
        self._setup_storage()
    
    def _setup_storage(self):
        """Setup storage with permission checking"""
        try:
            # Test write permissions
            if not test_write_permission(self.data_dir):
                # Try alternative location
                alt_data_dir = os.path.join(tempfile.gettempdir(), "wp_content_gen")
                os.makedirs(alt_data_dir, exist_ok=True)
                
                if test_write_permission(alt_data_dir):
                    self.data_dir = alt_data_dir
                    self.projects_file = os.path.join(self.data_dir, "projects.json")
                    self.logger.warning(f"Using alternative data directory: {self.data_dir}")
                else:
                    raise PermissionError("Cannot write to any data directory")
            
            # Initialize encryption
            self.encryption = EncryptionManager(self.data_dir)
            
        except Exception as e:
            self.logger.error(f"Storage setup failed: {e}")
            raise
    
    def save_projects(self, projects: List[WordPressProject]) -> None:
        """Save projects to JSON file"""
        try:
            print(f"DataStorage.save_projects called with {len(projects)} projects")  # Debug
            
            # Test write permission before attempting
            if not test_write_permission(self.data_dir):
                raise PermissionError(f"No write permission to {self.data_dir}")
            
            # Convert projects to dictionaries and encrypt sensitive data
            projects_data = []
            for project in projects:
                print(f"Processing project for save: {project.name}")  # Debug
                project_dict = project.to_dict()
                
                # Encrypt sensitive fields
                project_dict['app_password'] = self.encryption.encrypt(project_dict['app_password'])
                project_dict['ai_api_key'] = self.encryption.encrypt(project_dict['ai_api_key'])
                
                projects_data.append(project_dict)
            
            print(f"Processed {len(projects_data)} projects for saving")  # Debug
            
            # Write to temporary file first, then rename (atomic operation)
            temp_file = self.projects_file + ".tmp"
            print(f"Writing to temp file: {temp_file}")  # Debug
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'version': '1.0',
                    'projects': projects_data
                }, f, indent=2, ensure_ascii=False)
            
            print(f"Data written to temp file. Size: {os.path.getsize(temp_file)} bytes")  # Debug
            
            # Atomic rename
            if os.path.exists(self.projects_file):
                print(f"Removing existing file: {self.projects_file}")  # Debug
                os.remove(self.projects_file)
            
            print(f"Renaming {temp_file} to {self.projects_file}")  # Debug
            os.rename(temp_file, self.projects_file)
            
            final_size = os.path.getsize(self.projects_file)
            print(f"Final file size: {final_size} bytes")  # Debug
            
            self.logger.info(f"Saved {len(projects)} projects to {self.projects_file}")
            
        except Exception as e:
            print(f"Error in save_projects: {e}")  # Debug
            self.logger.error(f"Failed to save projects: {e}")
            raise

    def load_projects(self) -> List[WordPressProject]:
        """Load projects from JSON file"""
        try:
            print(f"DataStorage.load_projects called")
            
            if not os.path.exists(self.projects_file):
                self.logger.info("Projects file not found, starting with empty list")
                return []
            
            with open(self.projects_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            projects = []
            projects_data = data.get('projects', [])
            
            for project_dict in projects_data:
                try:
                    # Decrypt sensitive fields
                    project_dict['app_password'] = self.encryption.decrypt(project_dict['app_password'])
                    project_dict['ai_api_key'] = self.encryption.decrypt(project_dict['ai_api_key'])
                    
                    # Create project object
                    project = WordPressProject.from_dict(project_dict)
                    projects.append(project)
                    
                except Exception as e:
                    self.logger.error(f"Failed to load project {project_dict.get('name', 'unknown')}: {e}")
                    # Skip corrupted projects
                    continue
            
            self.logger.info(f"Loaded {len(projects)} projects from {self.projects_file}")
            return projects
            
        except Exception as e:
            self.logger.error(f"Failed to load projects: {e}")
            return []
    
    def backup_projects(self) -> str:
        """Create backup of projects file"""
        try:
            if not os.path.exists(self.projects_file):
                raise FileNotFoundError("No projects file to backup")
            
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.data_dir, f"projects_backup_{timestamp}.json")
            
            shutil.copy2(self.projects_file, backup_file)
            self.logger.info(f"Created backup: {backup_file}")
            
            return backup_file
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            raise