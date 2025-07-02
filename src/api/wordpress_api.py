"""
WordPress REST API integration
"""
import requests
from typing import Dict, Optional
import time
from utils.logger import get_logger

class WordPressAPI:
    def __init__(self, website_url: str, username: str, app_password: str):
        self.website_url = website_url.rstrip('/')
        self.username = username
        self.app_password = app_password
        self.logger = get_logger(__name__)
        
        # Setup session for reuse
        self.session = requests.Session()
        self.session.auth = (self.username, self.app_password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'WordPress-Content-Generator/1.0'
        })
    
    def create_post(self, title: str, content: str, slug: str, 
                   category_id: int, status: str) -> Dict:
        """
        Create a new WordPress post
        """
        try:
            url = f'{self.website_url}/wp-json/wp/v2/posts'
            
            # Prepare post data
            post_data = {
                'title': title,
                'content': content,
                'slug': self._sanitize_slug(slug),
                'categories': [category_id],
                'status': status,
                'meta': {
                    'generated_by': 'content-generator'
                }
            }
            
            self.logger.info(f"Creating post: {title}")
            
            response = self.session.post(url, json=post_data, timeout=30)
            
            if response.status_code == 201:
                post_info = response.json()
                self.logger.info(f"Post created successfully. ID: {post_info['id']}")
                
                return {
                    'success': True,
                    'post_id': post_info['id'],
                    'post_url': post_info['link'],
                    'slug': post_info['slug']
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(f"Failed to create post: {error_msg}")
                
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except requests.exceptions.Timeout:
            error_msg = "Request timeout"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except requests.exceptions.ConnectionError:
            error_msg = "Connection error"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def test_connection(self) -> Dict[str, any]:
        """Test WordPress API connection"""
        try:
            # Test basic API access
            url = f'{self.website_url}/wp-json/wp/v2/posts'
            response = self.session.get(url, params={'per_page': 1}, timeout=10)
            
            if response.status_code == 200:
                self.logger.info("WordPress connection test successful")
                return {'success': True, 'message': 'Connection successful'}
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(f"WordPress connection test failed: {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            error_msg = f"Connection test failed: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def get_categories(self) -> Dict:
        """Get available categories"""
        try:
            url = f'{self.website_url}/wp-json/wp/v2/categories'
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                categories = response.json()
                return {'success': True, 'categories': categories}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _sanitize_slug(self, slug: str) -> str:
        """Sanitize slug for WordPress"""
        # Convert to lowercase
        slug = slug.lower()
        
        # Replace spaces and underscores with hyphens
        slug = slug.replace(' ', '-').replace('_', '-')
        
        # Remove special characters except hyphens and alphanumeric
        import re
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        return slug[:50]  # Limit length