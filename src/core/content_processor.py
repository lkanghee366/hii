"""
Handles the content generation and posting workflow
"""
from data.models import WordPressProject, ProcessingResult
from api.gemini_provider import GeminiProvider
from api.wordpress_api import WordPressAPI
from utils.logger import get_logger
import time
from typing import List, Callable, Optional

class ContentProcessor:
    def __init__(self, project: WordPressProject):
        self.project = project
        self.logger = get_logger(__name__)
        
        # Initialize APIs
        self.ai_provider = GeminiProvider(project.ai_api_key)
        self.wp_api = WordPressAPI(
            project.website_url,
            project.username,
            project.app_password
        )
    
    def process_all_keywords(self, progress_callback: Optional[Callable] = None) -> List[ProcessingResult]:
        """
        Process all keywords in the project
        """
        results = []
        total_keywords = len(self.project.keywords)
        
        self.logger.info(f"Starting processing of {total_keywords} keywords")
        
        for index, keyword in enumerate(self.project.keywords):
            try:
                # Update progress
                if progress_callback:
                    progress_callback(index, total_keywords, f"Processing: {keyword}")
                
                # Process single keyword
                result = self.process_single_keyword(keyword)
                results.append(result)
                
                # Log result
                if result.success:
                    self.logger.info(f"✓ Successfully processed: {keyword}")
                else:
                    self.logger.error(f"✗ Failed to process: {keyword} - {result.error_message}")
                
                # Add delay between requests to avoid rate limits
                if index < total_keywords - 1:  # Don't delay after last item
                    time.sleep(5)
                    
            except Exception as e:
                error_msg = f"Unexpected error processing {keyword}: {str(e)}"
                self.logger.error(error_msg)
                
                results.append(ProcessingResult(
                    keyword=keyword,
                    success=False,
                    error_message=error_msg
                ))
        
        # Final progress update
        if progress_callback:
            progress_callback(total_keywords, total_keywords, "Processing complete")
        
        # Log summary
        successful = sum(1 for r in results if r.success)
        failed = total_keywords - successful
        self.logger.info(f"Processing complete. Success: {successful}, Failed: {failed}")
        
        return results
    
    def process_single_keyword(self, keyword: str) -> ProcessingResult:
        """
        Process a single keyword: generate content and post to WordPress
        """
        start_time = time.time()
        
        try:
            # Step 1: Generate content
            prompt = self.project.prompt_template.replace('<keyword>', keyword)
            content_data = self.ai_provider.generate_content(prompt)
            
            title = content_data['title']
            content = content_data['content']
            
            # Step 2: Create slug from keyword
            slug = self._create_slug(keyword)
            
            # Step 3: Post to WordPress
            wp_result = self.wp_api.create_post(
                title=title,
                content=content,
                slug=slug,
                category_id=self.project.category_id,
                status=self.project.status
            )
            
            processing_time = time.time() - start_time
            
            if wp_result['success']:
                return ProcessingResult(
                    keyword=keyword,
                    success=True,
                    title=title,
                    post_id=wp_result['post_id'],
                    post_url=wp_result['post_url'],
                    processing_time=processing_time
                )
            else:
                return ProcessingResult(
                    keyword=keyword,
                    success=False,
                    title=title,
                    error_message=wp_result['error'],
                    processing_time=processing_time
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            return ProcessingResult(
                keyword=keyword,
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    def _create_slug(self, keyword: str) -> str:
        """Create URL-friendly slug from keyword"""
        import re
        
        # Convert to lowercase
        slug = keyword.lower()
        
        # Replace spaces with hyphens
        slug = slug.replace(' ', '-')
        
        # Remove special characters
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        
        # Remove multiple hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        return slug
    
    def test_connections(self) -> dict[str, dict]:
        """Test both AI and WordPress connections"""
        results = {}
        
        # Test AI provider
        try:
            ai_test = self.ai_provider.test_connection()
            results['ai'] = {'success': ai_test, 'error': None if ai_test else 'Connection failed'}
        except Exception as e:
            results['ai'] = {'success': False, 'error': str(e)}
        
        # Test WordPress API
        wp_test = self.wp_api.test_connection()
        results['wordpress'] = wp_test
        
        return results