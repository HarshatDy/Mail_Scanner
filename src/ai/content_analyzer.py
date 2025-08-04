"""
Content analyzer for email processing.
Analyzes email content for relevance, quality, and topic generation potential.
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.config.config_manager import get_config
from src.utils.logger import get_logger


class ContentAnalyzer:
    """Analyze email content for topic generation."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("content_analyzer")
        
        # Keywords that indicate relevant content
        self.tech_keywords = [
            'python', 'javascript', 'react', 'vue', 'angular', 'node.js', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'machine learning', 'ai', 'ml',
            'data science', 'blockchain', 'cybersecurity', 'devops', 'api',
            'database', 'sql', 'nosql', 'git', 'github', 'agile', 'scrum',
            'testing', 'deployment', 'microservices', 'serverless', 'cloud',
            'programming', 'coding', 'development', 'software', 'web', 'mobile',
            'startup', 'entrepreneurship', 'productivity', 'tools', 'automation'
        ]
        
        self.newsletter_keywords = [
            'newsletter', 'weekly', 'monthly', 'update', 'roundup', 'digest',
            'insights', 'trends', 'analysis', 'report', 'research', 'study',
            'survey', 'statistics', 'data', 'findings', 'recommendations',
            'best practices', 'tips', 'tricks', 'guide', 'tutorial', 'how-to'
        ]
        
        self.professional_keywords = [
            'career', 'leadership', 'management', 'strategy', 'business',
            'marketing', 'sales', 'finance', 'investment', 'consulting',
            'networking', 'professional development', 'skill', 'certification',
            'industry', 'market', 'competition', 'innovation', 'growth',
            'strategy', 'planning', 'execution', 'performance', 'metrics'
        ]
    
    def analyze_email_content(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze email content for relevance and quality.
        
        Args:
            email_data: Email data dictionary
            
        Returns:
            Analysis results dictionary
        """
        try:
            subject = email_data.get('subject', '').lower()
            body = email_data.get('body', '').lower()
            sender = email_data.get('from', '').lower()
            
            # Basic content analysis
            analysis = {
                'content_length': len(body),
                'word_count': len(body.split()),
                'has_links': self._has_links(body),
                'has_attachments': len(email_data.get('attachments', [])) > 0,
                'sender_domain': self._extract_domain(sender),
                'subject_keywords': self._extract_keywords(subject),
                'body_keywords': self._extract_keywords(body),
                'relevance_score': 0.0,
                'category': 'other',
                'quality_score': 0.0,
                'topic_potential': False
            }
            
            # Calculate relevance score
            analysis['relevance_score'] = self._calculate_relevance_score(subject, body, sender)
            
            # Determine category
            analysis['category'] = self._determine_category(subject, body, sender)
            
            # Calculate quality score
            analysis['quality_score'] = self._calculate_quality_score(analysis)
            
            # Determine topic potential
            analysis['topic_potential'] = self._has_topic_potential(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing email content: {e}")
            return {
                'relevance_score': 0.0,
                'category': 'other',
                'quality_score': 0.0,
                'topic_potential': False,
                'error': str(e)
            }
    
    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address."""
        try:
            if '@' in email:
                return email.split('@')[1]
            return email
        except:
            return email
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        keywords = []
        text_lower = text.lower()
        
        # Check for tech keywords
        for keyword in self.tech_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        # Check for newsletter keywords
        for keyword in self.newsletter_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        # Check for professional keywords
        for keyword in self.professional_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        return list(set(keywords))  # Remove duplicates
    
    def _has_links(self, text: str) -> bool:
        """Check if text contains links."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return bool(re.search(url_pattern, text))
    
    def _calculate_relevance_score(self, subject: str, body: str, sender: str) -> float:
        """Calculate relevance score (0.0 to 1.0)."""
        score = 0.0
        
        # Subject relevance
        subject_keywords = self._extract_keywords(subject)
        if subject_keywords:
            score += 0.3
        
        # Body relevance
        body_keywords = self._extract_keywords(body)
        if body_keywords:
            score += 0.4
        
        # Content length (more content = higher score)
        if len(body) > 100:
            score += 0.1
        if len(body) > 500:
            score += 0.1
        
        # Sender domain relevance
        domain = self._extract_domain(sender)
        relevant_domains = [
            'github.com', 'stackoverflow.com', 'medium.com', 'dev.to',
            'techcrunch.com', 'wired.com', 'theverge.com', 'arstechnica.com',
            'substack.com', 'newsletter', 'blog', 'tech', 'dev', 'ai'
        ]
        
        for relevant_domain in relevant_domains:
            if relevant_domain in domain:
                score += 0.1
                break
        
        return min(score, 1.0)
    
    def _determine_category(self, subject: str, body: str, sender: str) -> str:
        """Determine the category of the email."""
        tech_score = 0
        newsletter_score = 0
        professional_score = 0
        
        # Count keyword matches
        all_text = f"{subject} {body}".lower()
        
        for keyword in self.tech_keywords:
            if keyword in all_text:
                tech_score += 1
        
        for keyword in self.newsletter_keywords:
            if keyword in all_text:
                newsletter_score += 1
        
        for keyword in self.professional_keywords:
            if keyword in all_text:
                professional_score += 1
        
        # Determine category based on scores
        if tech_score > newsletter_score and tech_score > professional_score:
            return 'tech'
        elif newsletter_score > tech_score and newsletter_score > professional_score:
            return 'newsletter'
        elif professional_score > tech_score and professional_score > newsletter_score:
            return 'professional'
        else:
            return 'other'
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate quality score (0.0 to 1.0)."""
        score = 0.0
        
        # Content length
        if analysis['content_length'] > 200:
            score += 0.2
        elif analysis['content_length'] > 100:
            score += 0.1
        
        # Keyword density
        keyword_count = len(analysis['subject_keywords']) + len(analysis['body_keywords'])
        if keyword_count > 5:
            score += 0.3
        elif keyword_count > 2:
            score += 0.2
        
        # Has links (indicates more detailed content)
        if analysis['has_links']:
            score += 0.1
        
        # Relevance score
        score += analysis['relevance_score'] * 0.3
        
        return min(score, 1.0)
    
    def _has_topic_potential(self, analysis: Dict[str, Any]) -> bool:
        """Determine if email has potential for topic generation."""
        # Must have sufficient relevance and quality
        if analysis['relevance_score'] < 0.3:
            return False
        
        if analysis['quality_score'] < 0.3:
            return False
        
        # Must be in a relevant category
        if analysis['category'] not in ['tech', 'newsletter', 'professional']:
            return False
        
        # Must have sufficient content
        if analysis['content_length'] < 100:
            return False
        
        return True
    
    def should_process_for_topics(self, email_data: Dict[str, Any], analysis: Dict[str, Any]) -> bool:
        """Determine if email should be processed for topic generation."""
        return analysis.get('topic_potential', False)
    
    def create_email_report(self, email_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive report for an email."""
        try:
            return {
                'email_id': email_data.get('id', ''),
                'subject': email_data.get('subject', ''),
                'from': email_data.get('from', ''),
                'date': email_data.get('date', ''),
                'content': email_data.get('body', ''),
                'category': analysis.get('category', 'other'),
                'relevance_score': analysis.get('relevance_score', 0.0),
                'quality_score': analysis.get('quality_score', 0.0),
                'topic_potential': analysis.get('topic_potential', False),
                'keywords': analysis.get('subject_keywords', []) + analysis.get('body_keywords', []),
                'content_length': analysis.get('content_length', 0),
                'word_count': analysis.get('word_count', 0),
                'has_links': analysis.get('has_links', False),
                'has_attachments': analysis.get('has_attachments', False),
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error creating email report: {e}")
            return {
                'email_id': email_data.get('id', ''),
                'subject': email_data.get('subject', ''),
                'error': str(e)
            } 