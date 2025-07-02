"""
Data models for the application
"""
from dataclasses import dataclass, asdict
from typing import List, Optional
import uuid
from datetime import datetime

@dataclass
class WordPressProject:
    id: str
    name: str
    website_url: str
    username: str
    app_password: str
    category_id: int
    status: str  # 'draft' or 'publish'
    keywords: List[str]
    prompt_template: str
    ai_api_key: str
    ai_provider_type: str = 'gemini'
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    @classmethod
    def create_new(cls, name: str, website_url: str, username: str, 
                   app_password: str, category_id: int, status: str,
                   keywords: List[str], prompt_template: str, 
                   ai_api_key: str, ai_provider_type: str = 'gemini') -> 'WordPressProject':
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            website_url=website_url.rstrip('/'),
            username=username,
            app_password=app_password,
            category_id=category_id,
            status=status,
            keywords=keywords,
            prompt_template=prompt_template,
            ai_api_key=ai_api_key,
            ai_provider_type=ai_provider_type
        )
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WordPressProject':
        return cls(**data)
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()

@dataclass
class ProcessingResult:
    keyword: str
    success: bool
    title: str = ""
    post_id: int = None
    post_url: str = ""
    error_message: str = ""
    processing_time: float = 0.0