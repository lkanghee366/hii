"""
Project management functionality
"""
from typing import List, Optional
from data.models import WordPressProject
from data.storage import DataStorage
from utils.logger import get_logger

class ProjectManager:
    def __init__(self):
        self.storage = DataStorage()
        self.projects: List[WordPressProject] = []
        self.logger = get_logger(__name__)
    
    def add_project(self, project: WordPressProject) -> bool:
        """Add new project"""
        try:
            print(f"ProjectManager.add_project called with: {project.name}")  # Debug
            
            # Check for duplicate names
            if any(p.name == project.name for p in self.projects):
                raise ValueError("Project with this name already exists")
            
            print(f"Adding project to list. Current count: {len(self.projects)}")  # Debug
            self.projects.append(project)
            print(f"Project added to list. New count: {len(self.projects)}")  # Debug
            
            print("Saving projects to storage...")  # Debug
            success = self.save_projects()
            
            if success:
                self.logger.info(f"Added project: {project.name}")
                print(f"Project saved successfully: {project.name}")  # Debug
                return True
            else:
                print("Failed to save projects to storage")  # Debug
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to add project: {e}")
            print(f"Error in add_project: {e}")  # Debug
            raise

    def save_projects(self) -> bool:
        """Save projects to storage"""
        try:
            print(f"Saving {len(self.projects)} projects...")  # Debug
            self.storage.save_projects(self.projects)
            self.logger.info("Projects saved successfully")
            print("Projects saved to storage successfully")  # Debug
            return True
        except Exception as e:
            self.logger.error(f"Failed to save projects: {e}")
            print(f"Error saving projects: {e}")  # Debug
            return False

    def load_projects(self) -> List[WordPressProject]:
        """Load projects from storage"""
        try:
            print("Loading projects from storage...")  # Debug
            self.projects = self.storage.load_projects()
            self.logger.info(f"Loaded {len(self.projects)} projects")
            print(f"Loaded {len(self.projects)} projects from storage")  # Debug
            
            # Debug: print project names
            for project in self.projects:
                print(f"  - {project.name} (ID: {project.id})")  # Debug
                
            return self.projects
        except Exception as e:
            self.logger.error(f"Failed to load projects: {e}")
            print(f"Error loading projects: {e}")  # Debug
            self.projects = []
            return self.projects
    
    def update_project(self, project_id: str, updated_project: WordPressProject) -> bool:
        """Update existing project"""
        try:
            for i, project in enumerate(self.projects):
                if project.id == project_id:
                    # Keep the same ID
                    updated_project.id = project_id
                    self.projects[i] = updated_project
                    self.save_projects()
                    self.logger.info(f"Updated project: {updated_project.name}")
                    return True
            
            raise ValueError("Project not found")
        except Exception as e:
            self.logger.error(f"Failed to update project: {e}")
            raise
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project"""
        try:
            for i, project in enumerate(self.projects):
                if project.id == project_id:
                    project_name = project.name
                    del self.projects[i]
                    self.save_projects()
                    self.logger.info(f"Deleted project: {project_name}")
                    return True
            
            raise ValueError("Project not found")
        except Exception as e:
            self.logger.error(f"Failed to delete project: {e}")
            raise
    
    def get_project(self, project_id: str) -> Optional[WordPressProject]:
        """Get project by ID"""
        for project in self.projects:
            if project.id == project_id:
                return project
        return None
    
    def get_project_by_name(self, name: str) -> Optional[WordPressProject]:
        """Get project by name"""
        for project in self.projects:
            if project.name == name:
                return project
        return None