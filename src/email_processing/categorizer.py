"""
Email categorizer for the Email Scanner system.
Provides additional categorization logic and utilities.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib

from src.config.config_manager import get_config
from src.utils.logger import get_logger


class EmailCategorizer:
    """Advanced email categorization with content analysis."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("email_categorizer")
        
        # Content type patterns
        self.content_patterns = {
            'article': [
                r'\barticle\b', r'\bpost\b', r'\bblog\b', r'\bstory\b',
                r'\bnews\b', r'\bupdate\b', r'\bannouncement\b'
            ],
            'newsletter': [
                r'\bnewsletter\b', r'\bdigest\b', r'\bweekly\b', r'\bmonthly\b',
                r'\broundup\b', r'\bsummary\b', r'\bhighlights\b'
            ],
            'notification': [
                r'\bnotification\b', r'\balert\b', r'\breminder\b', r'\bupdate\b',
                r'\bstatus\b', r'\bprogress\b', r'\bresult\b'
            ],
            'promotional': [
                r'\boffer\b', r'\bdeal\b', r'\bdiscount\b', r'\bsale\b',
                r'\bpromotion\b', r'\bspecial\b', r'\blimited\b'
            ]
        }
        
        # Language patterns for content analysis
        self.language_indicators = {
            'technical': [
                'api', 'database', 'server', 'client', 'protocol', 'algorithm',
                'framework', 'library', 'dependency', 'deployment', 'infrastructure',
                'microservice', 'container', 'orchestration', 'monitoring', 'logging'
            ],
            'business': [
                'strategy', 'market', 'revenue', 'growth', 'investment', 'partnership',
                'acquisition', 'merger', 'ipo', 'valuation', 'funding', 'startup'
            ],
            'educational': [
                'tutorial', 'guide', 'learn', 'course', 'training', 'workshop',
                'documentation', 'example', 'demo', 'sample', 'best practice'
            ]
        }
    
    def analyze_email_content(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform detailed content analysis of an email.
        
        Args:
            email_data: Dictionary containing email information
            
        Returns:
            Dictionary with content analysis results
        """
        try:
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            from_address = email_data.get('from', '')
            
            analysis = {
                'content_type': self._determine_content_type(subject, body),
                'language_style': self._analyze_language_style(body),
                'sentiment': self._analyze_sentiment(subject, body),
                'readability': self._calculate_readability(body),
                'key_topics': self._extract_key_topics(body),
                'links': self._extract_links(body),
                'has_attachments': len(email_data.get('attachments', [])) > 0,
                'word_count': len(body.split()),
                'character_count': len(body),
                'content_hash': self._generate_content_hash(body),
                'timestamp': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing email content: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _determine_content_type(self, subject: str, body: str) -> str:
        """Determine the type of content in the email."""
        text = f"{subject} {body}".lower()
        
        scores = {}
        for content_type, patterns in self.content_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text):
                    score += 1
            scores[content_type] = score
        
        # Return the content type with the highest score
        if scores:
            return max(scores, key=scores.get)
        
        return 'general'
    
    def _analyze_language_style(self, body: str) -> Dict[str, float]:
        """Analyze the language style of the email content."""
        text = body.lower()
        scores = {}
        
        for style, indicators in self.language_indicators.items():
            score = 0
            for indicator in indicators:
                if indicator in text:
                    score += 1
            scores[style] = score / len(indicators) if indicators else 0
        
        return scores
    
    def _analyze_sentiment(self, subject: str, body: str) -> str:
        """Simple sentiment analysis of email content."""
        text = f"{subject} {body}".lower()
        
        positive_words = [
            'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome',
            'good', 'nice', 'happy', 'excited', 'successful', 'achieved',
            'improved', 'better', 'best', 'love', 'like', 'enjoy'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'disappointing', 'failed',
            'error', 'problem', 'issue', 'broken', 'wrong', 'hate', 'dislike',
            'angry', 'frustrated', 'sad', 'worried', 'concerned'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_readability(self, body: str) -> Dict[str, float]:
        """Calculate readability metrics for the email content."""
        sentences = re.split(r'[.!?]+', body)
        words = body.split()
        
        if not sentences or not words:
            return {'flesch_reading_ease': 0, 'avg_sentence_length': 0}
        
        # Calculate average sentence length
        avg_sentence_length = len(words) / len(sentences)
        
        # Simple Flesch Reading Ease approximation
        # Higher score = easier to read
        syllables = self._count_syllables(body)
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (syllables / len(words)))
        flesch_score = max(0, min(100, flesch_score))  # Clamp between 0 and 100
        
        return {
            'flesch_reading_ease': round(flesch_score, 2),
            'avg_sentence_length': round(avg_sentence_length, 2)
        }
    
    def _count_syllables(self, text: str) -> int:
        """Count syllables in text (approximation)."""
        text = text.lower()
        count = 0
        vowels = "aeiouy"
        on_vowel = False
        
        for char in text:
            is_vowel = char in vowels
            if is_vowel and not on_vowel:
                count += 1
            on_vowel = is_vowel
        
        return count
    
    def _extract_key_topics(self, body: str) -> List[str]:
        """Extract key topics from email content."""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        words = re.findall(r'\b\w+\b', body.lower())
        word_freq = {}
        
        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top 10 most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def _extract_links(self, body: str) -> List[str]:
        """Extract links from email content."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, body)
    
    def _generate_content_hash(self, body: str) -> str:
        """Generate a hash of the email content for duplicate detection."""
        return hashlib.md5(body.encode('utf-8')).hexdigest()
    
    def is_duplicate_content(self, content_hash: str, existing_hashes: List[str]) -> bool:
        """Check if content hash already exists (duplicate detection)."""
        return content_hash in existing_hashes
    
    def get_content_summary(self, email_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate a summary of the email content."""
        subject = email_data.get('subject', 'No subject')
        from_address = email_data.get('from', 'Unknown sender')
        word_count = analysis.get('word_count', 0)
        content_type = analysis.get('content_type', 'general')
        sentiment = analysis.get('sentiment', 'neutral')
        
        summary = f"Email from {from_address}: '{subject}' "
        summary += f"({word_count} words, {content_type} content, {sentiment} sentiment)"
        
        return summary
    
    def should_process_for_topics(self, email_data: Dict[str, Any], analysis: Dict[str, Any]) -> bool:
        """Determine if email should be processed for topic generation."""
        # Skip if too short
        if analysis.get('word_count', 0) < 50:
            return False
        
        # Skip if content type is not suitable
        unsuitable_types = ['notification', 'promotional']
        if analysis.get('content_type') in unsuitable_types:
            return False
        
        # Skip if sentiment is negative (might be complaints, etc.)
        if analysis.get('sentiment') == 'negative':
            return False
        
        # Skip if readability is too low
        readability = analysis.get('readability', {})
        if readability.get('flesch_reading_ease', 100) < 30:
            return False
        
        return True
    
    def get_processing_priority(self, email_data: Dict[str, Any], analysis: Dict[str, Any]) -> int:
        """Calculate processing priority for the email (higher = more important)."""
        priority = 0
        
        # Content type priority
        content_type_priority = {
            'article': 5,
            'newsletter': 4,
            'educational': 3,
            'general': 2,
            'notification': 1,
            'promotional': 0
        }
        priority += content_type_priority.get(analysis.get('content_type', 'general'), 0)
        
        # Language style priority
        language_scores = analysis.get('language_style', {})
        if language_scores.get('technical', 0) > 0.3:
            priority += 3
        if language_scores.get('educational', 0) > 0.3:
            priority += 2
        
        # Length priority (moderate length is preferred)
        word_count = analysis.get('word_count', 0)
        if 100 <= word_count <= 1000:
            priority += 2
        elif word_count > 1000:
            priority += 1
        
        # Sentiment priority
        sentiment_priority = {'positive': 1, 'neutral': 0, 'negative': -1}
        priority += sentiment_priority.get(analysis.get('sentiment', 'neutral'), 0)
        
        return priority
    
    def create_email_report(self, email_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive report for an email."""
        return {
            'email_id': email_data.get('uid', 'unknown'),
            'subject': email_data.get('subject', ''),
            'from': email_data.get('from', ''),
            'date': email_data.get('date', ''),
            'analysis': analysis,
            'summary': self.get_content_summary(email_data, analysis),
            'should_process': self.should_process_for_topics(email_data, analysis),
            'priority': self.get_processing_priority(email_data, analysis),
            'processed_at': datetime.now().isoformat()
        } 