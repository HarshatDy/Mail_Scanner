"""
AI-powered topic generator for blog content.
Uses Gemini API to generate relevant blog topics from email content.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Lazy imports to avoid Python 3.14 compatibility issues
genai = None
OpenAI = None

try:
    import google.generativeai as genai
except (ImportError, TypeError) as e:
    # Handle Python 3.14 compatibility issue with protobuf
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from src.config.config_manager import get_config
from src.utils.logger import get_logger


class TopicGenerator:
    """Generate blog topics from email content using AI."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("topic_generator")
        self.gemini_model = None
        self.openai_client = None
        
        # Initialize AI providers
        self._setup_ai_providers()
    
    def _setup_ai_providers(self):
        """Setup AI providers based on configuration."""
        try:
            if self.config.ai.provider == "gemini":
                if genai is None:
                    self.logger.error("google.generativeai could not be imported. This may be due to Python 3.14 compatibility issues. Please use Python 3.11 or 3.12, or update protobuf/google-generativeai packages.")
                    return
                if self.config.ai.gemini_api_key:
                    genai.configure(api_key=self.config.ai.gemini_api_key)
                    self.gemini_model = genai.GenerativeModel(self.config.ai.model)
                    self.logger.info("Gemini AI provider initialized")
                else:
                    self.logger.warning("Gemini API key not configured")
                    
            elif self.config.ai.provider == "openai":
                if OpenAI is None:
                    self.logger.error("openai package could not be imported. Please install it with: pip install openai")
                    return
                if self.config.ai.openai_api_key:
                    self.openai_client = OpenAI(api_key=self.config.ai.openai_api_key)
                    self.logger.info("OpenAI provider initialized")
                else:
                    self.logger.warning("OpenAI API key not configured")
                    
        except Exception as e:
            self.logger.error(f"Error setting up AI providers: {e}")
    
    def generate_topics(self, processed_emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate blog topics from processed emails.
        
        Args:
            processed_emails: List of processed email data
            
        Returns:
            List of generated topics with metadata
        """
        if not processed_emails:
            self.logger.info("No emails to process for topic generation")
            return []
        
        try:
            self.logger.info(f"Generating topics from {len(processed_emails)} emails")
            
            # Group emails by category for better topic generation
            categorized_emails = self._categorize_emails(processed_emails)
            
            topics = []
            for category, emails in categorized_emails.items():
                if emails:
                    category_topics = self._generate_category_topics(category, emails)
                    topics.extend(category_topics)
            
            # Limit topics based on configuration
            max_topics = self.config.ai.max_topics_per_scan
            if len(topics) > max_topics:
                topics = topics[:max_topics]
                self.logger.info(f"Limited topics to {max_topics} as per configuration")
            
            self.logger.info(f"Generated {len(topics)} topics")
            return topics
            
        except Exception as e:
            self.logger.error(f"Error generating topics: {e}")
            return []
    
    def _categorize_emails(self, emails: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group emails by their category."""
        categorized = {}
        
        for email in emails:
            category = email.get('category', 'other')
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(email)
        
        return categorized
    
    def _generate_category_topics(self, category: str, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate topics for a specific category of emails."""
        try:
            # Prepare content for AI analysis
            content_summary = self._prepare_content_summary(emails)
            
            if not content_summary:
                return []
            
            # Generate topics using AI
            if self.config.ai.provider == "gemini":
                topics = self._generate_with_gemini(category, content_summary)
            elif self.config.ai.provider == "openai":
                topics = self._generate_with_openai(category, content_summary)
            else:
                self.logger.warning(f"Unknown AI provider: {self.config.ai.provider}")
                return []
            
            # Add source email information to each topic
            for topic in topics:
                topic['source_emails'] = [
                    {
                        'subject': email.get('subject', ''),
                        'from': email.get('from', ''),
                        'date': email.get('date', ''),
                        'category': email.get('category', ''),
                        'relevance_score': email.get('relevance_score', 0.0),
                        'quality_score': email.get('quality_score', 0.0)
                    }
                    for email in emails
                ]
            
            return topics
                
        except Exception as e:
            self.logger.error(f"Error generating topics for category {category}: {e}")
            return []
    
    def _prepare_content_summary(self, emails: List[Dict[str, Any]]) -> str:
        """Prepare a summary of email content for AI analysis."""
        try:
            summary_parts = []
            
            for email in emails:
                subject = email.get('subject', '')
                content = email.get('content', '')
                sender = email.get('from', '')
                
                # Truncate content to reasonable length
                if len(content) > 500:
                    content = content[:500] + "..."
                
                summary_parts.append(f"From: {sender}")
                summary_parts.append(f"Subject: {subject}")
                summary_parts.append(f"Content: {content}")
                summary_parts.append("---")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            self.logger.error(f"Error preparing content summary: {e}")
            return ""
    
    def _generate_with_gemini(self, category: str, content_summary: str) -> List[Dict[str, Any]]:
        """Generate topics using Gemini API."""
        try:
            if genai is None:
                self.logger.error("google.generativeai is not available. Please use Python 3.11/3.12 or fix the import issue.")
                return []
            if not self.gemini_model:
                self.logger.error("Gemini model not initialized")
                return []
            
            prompt = self._create_topic_prompt(category, content_summary)
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.ai.temperature,
                    max_output_tokens=self.config.ai.max_tokens
                )
            )
            
            return self._parse_gemini_response(response.text)
            
        except Exception as e:
            self.logger.error(f"Error generating topics with Gemini: {e}")
            return []
    
    def _generate_with_openai(self, category: str, content_summary: str) -> List[Dict[str, Any]]:
        """Generate topics using OpenAI API."""
        try:
            if OpenAI is None:
                self.logger.error("openai package is not available. Please install it with: pip install openai")
                return []
            if not self.openai_client:
                self.logger.error("OpenAI client not initialized")
                return []
            
            prompt = self._create_topic_prompt(category, content_summary)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates blog topics from email content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.ai.max_tokens,
                temperature=self.config.ai.temperature
            )
            
            return self._parse_openai_response(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Error generating topics with OpenAI: {e}")
            return []
    
    def _create_topic_prompt(self, category: str, content_summary: str) -> str:
        """Create a prompt for topic generation."""
        return f"""
        Based on the following email content from the {category} category, generate 3-5 relevant blog topics.
        
        Email Content:
        {content_summary}
        
        Please generate topics that are:
        1. Relevant to the content provided
        2. Engaging and interesting for readers
        3. Specific and actionable
        4. Suitable for a tech/professional blog
        
        For each topic, provide:
        - Title: A catchy, SEO-friendly title
        - Description: A brief description of what the post would cover
        - Keywords: 3-5 relevant keywords
        - Difficulty: Beginner, Intermediate, or Advanced
        
        Format your response as JSON:
        {{
            "topics": [
                {{
                    "title": "Topic Title",
                    "description": "Topic description",
                    "keywords": ["keyword1", "keyword2", "keyword3"],
                    "difficulty": "Beginner|Intermediate|Advanced",
                    "category": "{category}"
                }}
            ]
        }}
        
        Only return valid JSON, no additional text.
        """
    
    def _parse_gemini_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse Gemini API response into structured topics."""
        try:
            # Clean the response text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_data = json.loads(response_text)
            topics = response_data.get('topics', [])
            
            # Add metadata
            for topic in topics:
                topic['generated_at'] = datetime.now().isoformat()
                topic['ai_provider'] = 'gemini'
            
            return topics
            
        except Exception as e:
            self.logger.error(f"Error parsing Gemini response: {e}")
            return []
    
    def _parse_openai_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse OpenAI API response into structured topics."""
        try:
            # Clean the response text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_data = json.loads(response_text)
            topics = response_data.get('topics', [])
            
            # Add metadata
            for topic in topics:
                topic['generated_at'] = datetime.now().isoformat()
                topic['ai_provider'] = 'openai'
            
            return topics
            
        except Exception as e:
            self.logger.error(f"Error parsing OpenAI response: {e}")
            return []
    
    def generate_blog_content(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete blog post (title and content) from a single email.
        
        Args:
            email_data: Dictionary containing email information
            
        Returns:
            Dictionary with blog title and content
        """
        try:
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('from', '')
            
            # Prepare content for AI
            email_content = f"Subject: {subject}\n\nContent: {body[:2000]}"  # Limit content length
            
            # Generate blog content using AI
            if self.config.ai.provider == "gemini":
                blog_data = self._generate_blog_with_gemini(email_content, sender)
            elif self.config.ai.provider == "openai":
                blog_data = self._generate_blog_with_openai(email_content, sender)
            else:
                self.logger.warning(f"Unknown AI provider: {self.config.ai.provider}")
                return {
                    'title': subject,
                    'content': body,
                    'source_email': sender,
                    'error': 'Unknown AI provider'
                }
            
            # Add source email information
            blog_data['source_email'] = sender
            blog_data['source_subject'] = subject
            blog_data['generated_at'] = datetime.now().isoformat()
            
            return blog_data
            
        except Exception as e:
            self.logger.error(f"Error generating blog content: {e}")
            return {
                'title': email_data.get('subject', 'Untitled'),
                'content': email_data.get('body', ''),
                'source_email': email_data.get('from', ''),
                'error': str(e)
            }
    
    def _generate_blog_with_gemini(self, email_content: str, sender: str) -> Dict[str, Any]:
        """Generate blog content using Gemini API."""
        try:
            if genai is None:
                self.logger.error("google.generativeai is not available. Please use Python 3.11/3.12 or fix the import issue.")
                return {'title': '', 'content': '', 'error': 'Gemini library not available'}
            if not self.gemini_model:
                self.logger.error("Gemini model not initialized")
                return {'title': '', 'content': '', 'error': 'Model not initialized'}
            
            prompt = self._create_blog_prompt(email_content, sender)
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.ai.temperature,
                    max_output_tokens=self.config.ai.max_tokens * 3  # More tokens for full content
                )
            )
            
            return self._parse_blog_response(response.text)
            
        except Exception as e:
            self.logger.error(f"Error generating blog with Gemini: {e}")
            return {'title': '', 'content': '', 'error': str(e)}
    
    def _generate_blog_with_openai(self, email_content: str, sender: str) -> Dict[str, Any]:
        """Generate blog content using OpenAI API."""
        try:
            if OpenAI is None:
                self.logger.error("openai package is not available. Please install it with: pip install openai")
                return {'title': '', 'content': '', 'error': 'OpenAI library not available'}
            if not self.openai_client:
                self.logger.error("OpenAI client not initialized")
                return {'title': '', 'content': '', 'error': 'Client not initialized'}
            
            prompt = self._create_blog_prompt(email_content, sender)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a technical blog writer specializing in Software Engineering topics."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.ai.max_tokens * 3,  # More tokens for full content
                temperature=self.config.ai.temperature
            )
            
            return self._parse_blog_response(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Error generating blog with OpenAI: {e}")
            return {'title': '', 'content': '', 'error': str(e)}
    
    def _create_blog_prompt(self, email_content: str, sender: str) -> str:
        """Create a prompt for blog content generation."""
        return f"""
        Based on the following email content from {sender}, create a complete blog post about Software Engineering topics.
        
        Email Content:
        {email_content}
        
        Please create:
        1. A catchy, SEO-friendly blog title (focused on Software Engineering, System Design, Design Patterns, or Programming)
        2. A well-structured blog post content (at least 500 words) that:
           - Expands on the key concepts from the email
           - Includes relevant Software Engineering topics (system design, design patterns, programming languages, etc.)
           - Is educational and informative
           - Has clear sections with headings
           - Includes practical examples or explanations
           - Is suitable for a technical blog audience
        
        Format your response as JSON:
        {{
            "title": "Blog Title Here",
            "content": "Full blog post content here with proper formatting and sections..."
        }}
        
        Only return valid JSON, no additional text.
        """
    
    def _parse_blog_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into blog title and content."""
        try:
            # Clean the response text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_data = json.loads(response_text)
            return {
                'title': response_data.get('title', 'Untitled'),
                'content': response_data.get('content', '')
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing blog response: {e}")
            # Try to extract title and content manually
            lines = response_text.split('\n')
            title = lines[0] if lines else 'Untitled'
            content = '\n'.join(lines[1:]) if len(lines) > 1 else response_text
            return {
                'title': title.replace('#', '').strip(),
                'content': content
            }
    
    def test_connection(self) -> bool:
        """Test the AI provider connection."""
        try:
            if self.config.ai.provider == "gemini":
                if genai is None:
                    self.logger.error("google.generativeai is not available")
                    return False
                if not self.gemini_model:
                    self.logger.error("Gemini model not initialized")
                    return False
                
                # Test with a simple prompt
                response = self.gemini_model.generate_content("Hello, test")
                return response.text is not None
                
            elif self.config.ai.provider == "openai":
                if OpenAI is None:
                    self.logger.error("openai package is not available")
                    return False
                if not self.openai_client:
                    self.logger.error("OpenAI client not initialized")
                    return False
                
                # Test with a simple prompt
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello, test"}],
                    max_tokens=10
                )
                return response.choices[0].message.content is not None
                
            else:
                self.logger.error(f"Unknown AI provider: {self.config.ai.provider}")
                return False
                
        except Exception as e:
            self.logger.error(f"AI connection test failed: {e}")
            return False 