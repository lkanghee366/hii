"""
Google Gemini API integration for content generation
"""
import google.generativeai as genai
from typing import Dict, Optional
import re
import time
from utils.logger import get_logger

class GeminiProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = 'gemini-2.0-flash'
        self.logger = get_logger(__name__)
        self._configure_api()
    
    def _configure_api(self):
        """Configure Gemini API"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.logger.info("Gemini API configured successfully")
        except Exception as e:
            self.logger.error(f"Failed to configure Gemini API: {e}")
            raise
    
    def generate_content(self, prompt: str) -> Dict[str, str]:
        """
        Generate content using Gemini API
        Returns: {'title': str, 'content': str}
        """
        try:
            # Enhanced prompt for better structure
            enhanced_prompt = f"""
{prompt}

Please provide your response in the following format:
TITLE: [Create an engaging, SEO-friendly title]
CONTENT: [Write the full article content with proper HTML formatting including headings, paragraphs, and structure]

Make sure to:
- Use H2 tags for main headings
- Include the keyword naturally throughout the content
- Write in a conversational, engaging tone
- Provide valuable, actionable information
- Include an introduction and conclusion
"""
            
            self.logger.info("Generating content with Gemini...")
            
            response = self.model.generate_content(enhanced_prompt)
            
            if not response.text:
                raise Exception("Empty response from Gemini API")
            
            # Parse the response
            parsed_content = self._parse_response(response.text)
            
            self.logger.info("Content generated successfully")
            return parsed_content
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """Parse Gemini response to extract title and content"""
        try:
            # Look for TITLE: and CONTENT: markers
            title_match = re.search(r'TITLE:\s*(.+?)(?:\n|CONTENT:)', response_text, re.IGNORECASE | re.DOTALL)
            content_match = re.search(r'CONTENT:\s*(.+)', response_text, re.IGNORECASE | re.DOTALL)
            
            if title_match and content_match:
                title = title_match.group(1).strip()
                content = content_match.group(1).strip()
            else:
                # Fallback: try to extract from different format
                lines = response_text.strip().split('\n')
                title = lines[0].strip() if lines else "Generated Article"
                content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else response_text
            
            # Clean up title (remove any markdown or extra formatting)
            title = re.sub(r'^#+\s*', '', title)  # Remove markdown headers
            title = re.sub(r'\*\*(.+?)\*\*', r'\1', title)  # Remove bold markdown
            
            # Ensure content has basic HTML structure
            if not re.search(r'<[^>]+>', content):
                # Convert plain text to basic HTML
                content = self._convert_to_html(content)
            
            return {
                'title': title[:200],  # Limit title length
                'content': content
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse response: {e}")
            # Fallback
            return {
                'title': "Generated Article",
                'content': response_text
            }
    
    def _convert_to_html(self, text: str) -> str:
        """Convert plain text to basic HTML"""
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        html_content = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # Check if it looks like a heading
            if len(para) < 100 and not para.endswith('.'):
                html_content += f"<h2>{para}</h2>\n"
            else:
                html_content += f"<p>{para}</p>\n"
        
        return html_content
    
    def test_connection(self) -> bool:
        """Test Gemini API connection"""
        try:
            test_prompt = "Write a short test message to verify API connection."
            response = self.model.generate_content(test_prompt)
            return bool(response.text)
        except Exception as e:
            self.logger.error(f"Gemini connection test failed: {e}")
            return False