"""
Email filtering and categorization for the Email Scanner system.
Filters and categorizes emails based on sender domains, keywords, and content patterns.
"""

import re
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import logging

from src.config.config_manager import get_config
from src.utils.logger import get_logger


class EmailFilter:
    """Email filtering and categorization system."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("email_filter")
        
        # Predefined category patterns
        self.category_patterns = {
            'tech': {
                'domains': [
                    'github.com', 'stackoverflow.com', 'dev.to', 'medium.com',
                    'techcrunch.com', 'wired.com', 'arstechnica.com', 'theverge.com',
                    'hackernews.com', 'reddit.com/r/programming', 'reddit.com/r/technology',
                    'python.org', 'nodejs.org', 'reactjs.org', 'vuejs.org',
                    'angular.io', 'typescript.org', 'docker.com', 'kubernetes.io',
                    'aws.amazon.com', 'azure.microsoft.com', 'cloud.google.com',
                    'digitalocean.com', 'heroku.com', 'netlify.com', 'vercel.com',
                    'npmjs.com', 'pypi.org', 'rubygems.org', 'nuget.org',
                    'gitlab.com', 'bitbucket.org', 'atlassian.com', 'jira.com',
                    'confluence.com', 'slack.com', 'discord.com', 'teams.microsoft.com',
                    'zoom.us', 'meet.google.com', 'webex.com', 'gotomeeting.com',
                    'notion.so', 'airtable.com', 'trello.com', 'asana.com',
                    'figma.com', 'sketch.com', 'invisionapp.com', 'framer.com',
                    'stripe.com', 'paypal.com', 'square.com', 'shopify.com',
                    'wordpress.com', 'squarespace.com', 'wix.com', 'webflow.com',
                    'sentry.io', 'logrocket.com', 'mixpanel.com', 'amplitude.com',
                    'segment.com', 'intercom.com', 'zendesk.com', 'freshdesk.com'
                ],
                'keywords': [
                    'programming', 'coding', 'development', 'software', 'tech',
                    'technology', 'startup', 'ai', 'machine learning', 'data science',
                    'web development', 'mobile app', 'api', 'database', 'cloud',
                    'devops', 'cybersecurity', 'blockchain', 'cryptocurrency',
                    'javascript', 'python', 'java', 'c++', 'c#', 'go', 'rust',
                    'react', 'vue', 'angular', 'node.js', 'django', 'flask',
                    'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'github',
                    'git', 'agile', 'scrum', 'ci/cd', 'testing', 'deployment'
                ],
                'exclude_keywords': [
                    'job', 'career', 'resume', 'interview', 'salary', 'hiring',
                    'recruiter', 'headhunter', 'employment', 'position'
                ]
            },
            'newsletter': {
                'domains': [
                    'substack.com', 'mailchimp.com', 'convertkit.com', 'beehiiv.com',
                    'revue.com', 'buttondown.email', 'tinyletter.com', 'letter.so',
                    'newsletter.com', 'newsletters.com', 'digest.com', 'weekly.com',
                    'daily.com', 'monthly.com', 'quarterly.com'
                ],
                'keywords': [
                    'newsletter', 'digest', 'weekly', 'daily', 'monthly',
                    'subscribe', 'unsubscribe', 'newsletter signup', 'email list',
                    'mailing list', 'updates', 'insights', 'trends', 'analysis',
                    'report', 'summary', 'roundup', 'highlights', 'featured'
                ],
                'exclude_keywords': [
                    'spam', 'unwanted', 'unsubscribe', 'remove me'
                ]
            },
            'social': {
                'domains': [
                    'linkedin.com', 'twitter.com', 'facebook.com', 'instagram.com',
                    'youtube.com', 'tiktok.com', 'snapchat.com', 'pinterest.com',
                    'reddit.com', 'discord.com', 'slack.com', 'telegram.org',
                    'whatsapp.com', 'signal.org', 'mastodon.social', 'threads.net'
                ],
                'keywords': [
                    'social media', 'follow', 'like', 'share', 'comment',
                    'connection', 'network', 'profile', 'post', 'tweet',
                    'story', 'reel', 'video', 'live', 'stream', 'community',
                    'group', 'channel', 'server', 'chat', 'message'
                ],
                'exclude_keywords': [
                    'spam', 'bot', 'fake', 'scam', 'phishing'
                ]
            },
            'professional': {
                'domains': [
                    'linkedin.com', 'indeed.com', 'glassdoor.com', 'monster.com',
                    'careerbuilder.com', 'ziprecruiter.com', 'dice.com', 'stackoverflow.com/jobs',
                    'angel.co', 'crunchbase.com', 'pitchbook.com', 'bloomberg.com',
                    'reuters.com', 'wsj.com', 'ft.com', 'economist.com',
                    'hbr.org', 'mckinsey.com', 'bain.com', 'bcg.com',
                    'deloitte.com', 'pwc.com', 'ey.com', 'kpmg.com'
                ],
                'keywords': [
                    'business', 'industry', 'market', 'trends', 'analysis',
                    'strategy', 'management', 'leadership', 'innovation',
                    'research', 'report', 'study', 'survey', 'data',
                    'insights', 'opportunities', 'challenges', 'solutions',
                    'consulting', 'advisory', 'expertise', 'thought leadership'
                ],
                'exclude_keywords': [
                    'spam', 'scam', 'phishing', 'malware', 'virus'
                ]
            }
        }
        
        # Personal/banking domains to exclude
        self.exclude_domains = [
            'bank.com', 'chase.com', 'wellsfargo.com', 'bankofamerica.com',
            'citibank.com', 'usbank.com', 'capitalone.com', 'discover.com',
            'americanexpress.com', 'paypal.com', 'venmo.com', 'zelle.com',
            'robinhood.com', 'fidelity.com', 'vanguard.com', 'schwab.com',
            'etrade.com', 'tdameritrade.com', 'interactivebrokers.com',
            'healthcare.gov', 'medicare.gov', 'ssa.gov', 'irs.gov',
            'usps.com', 'fedex.com', 'ups.com', 'dhl.com',
            'amazon.com', 'ebay.com', 'etsy.com', 'walmart.com',
            'target.com', 'bestbuy.com', 'homedepot.com', 'lowes.com',
            'netflix.com', 'hulu.com', 'disneyplus.com', 'hbomax.com',
            'spotify.com', 'apple.com', 'microsoft.com', 'google.com',
            'facebook.com', 'instagram.com', 'twitter.com', 'linkedin.com',
            'gmail.com', 'outlook.com', 'yahoo.com', 'icloud.com'
        ]
        
        # Spam indicators
        self.spam_indicators = [
            'unsubscribe', 'click here', 'limited time', 'act now',
            'free offer', 'money back', 'guarantee', 'winner',
            'lottery', 'prize', 'inheritance', 'urgent',
            'viagra', 'cialis', 'weight loss', 'diet',
            'casino', 'poker', 'betting', 'gambling'
        ]
    
    def categorize_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Categorize an email based on its content and metadata.
        
        Args:
            email_data: Dictionary containing email information
            
        Returns:
            Dictionary with categorization results
        """
        try:
            # Extract email components
            subject = email_data.get('subject', '').lower()
            from_address = email_data.get('from', '').lower()
            body = email_data.get('body', '').lower()
            
            # Check if email should be excluded
            if self._should_exclude_email(from_address, subject, body):
                return {
                    'category': 'excluded',
                    'confidence': 1.0,
                    'reason': 'Matched exclusion criteria',
                    'email_data': email_data
                }
            
            # Categorize the email
            category_scores = {}
            
            for category, patterns in self.category_patterns.items():
                score = self._calculate_category_score(
                    from_address, subject, body, patterns
                )
                if score > 0:
                    category_scores[category] = score
            
            # Find the best category
            if category_scores:
                best_category = max(category_scores, key=category_scores.get)
                confidence = category_scores[best_category]
                
                # Only categorize if confidence is above threshold
                if confidence >= 0.3:  # 30% confidence threshold
                    return {
                        'category': best_category,
                        'confidence': confidence,
                        'reason': f'Matched {best_category} patterns',
                        'email_data': email_data,
                        'all_scores': category_scores
                    }
            
            # Default to 'other' if no clear category
            return {
                'category': 'other',
                'confidence': 0.0,
                'reason': 'No clear category match',
                'email_data': email_data,
                'all_scores': category_scores
            }
            
        except Exception as e:
            self.logger.error(f"Error categorizing email: {e}")
            return {
                'category': 'error',
                'confidence': 0.0,
                'reason': f'Error during categorization: {e}',
                'email_data': email_data
            }
    
    def _should_exclude_email(self, from_address: str, subject: str, body: str) -> bool:
        """Check if email should be excluded based on exclusion criteria."""
        
        # Check excluded domains
        domain = self._extract_domain(from_address)
        if domain in self.exclude_domains:
            return True
        
        # Check user-defined exclude domains
        if domain in self.config.email.exclude_domains:
            return True
        
        # Check for spam indicators
        spam_score = 0
        for indicator in self.spam_indicators:
            if indicator in subject or indicator in body:
                spam_score += 1
        
        if spam_score >= 3:  # Multiple spam indicators
            return True
        
        # Check user-defined exclude keywords
        for keyword in self.config.email.exclude_keywords:
            if keyword.lower() in subject or keyword.lower() in body:
                return True
        
        return False
    
    def _calculate_category_score(self, from_address: str, subject: str, body: str, patterns: Dict) -> float:
        """Calculate a score for how well an email matches a category."""
        score = 0.0
        
        # Check domain matches
        domain = self._extract_domain(from_address)
        if domain in patterns.get('domains', []):
            score += 0.4  # Strong domain match
        
        # Check keyword matches in subject
        subject_keywords = self._extract_keywords(subject)
        for keyword in patterns.get('keywords', []):
            if keyword.lower() in subject_keywords:
                score += 0.3  # Subject keyword match
        
        # Check keyword matches in body
        body_keywords = self._extract_keywords(body)
        for keyword in patterns.get('keywords', []):
            if keyword.lower() in body_keywords:
                score += 0.2  # Body keyword match
        
        # Penalize for exclude keywords
        for keyword in patterns.get('exclude_keywords', []):
            if keyword.lower() in subject or keyword.lower() in body:
                score -= 0.5  # Penalty for exclude keywords
        
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1
    
    def _extract_domain(self, email_address: str) -> str:
        """Extract domain from email address."""
        try:
            # Handle email addresses like "John Doe <john@example.com>"
            if '<' in email_address and '>' in email_address:
                email_address = email_address.split('<')[1].split('>')[0]
            
            # Extract domain
            if '@' in email_address:
                return email_address.split('@')[1].lower()
            
            return email_address.lower()
        except Exception:
            return email_address.lower()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Remove special characters and split into words
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if len(word) > 2]  # Filter out short words
    
    def filter_emails(self, emails: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Filter and categorize a list of emails.
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            Dictionary with categorized emails
        """
        categorized_emails = {
            'tech': [],
            'newsletter': [],
            'social': [],
            'professional': [],
            'other': [],
            'excluded': []
        }
        
        for email_data in emails:
            result = self.categorize_email(email_data)
            category = result['category']
            
            if category in categorized_emails:
                categorized_emails[category].append(result)
            else:
                categorized_emails['other'].append(result)
        
        # Log statistics
        total_emails = len(emails)
        for category, email_list in categorized_emails.items():
            if email_list:
                self.logger.info(f"Categorized {len(email_list)} emails as {category}")
        
        return categorized_emails
    
    def get_category_statistics(self, categorized_emails: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Get statistics about email categorization."""
        stats = {}
        total_emails = sum(len(emails) for emails in categorized_emails.values())
        
        for category, emails in categorized_emails.items():
            count = len(emails)
            if total_emails > 0:
                percentage = (count / total_emails) * 100
            else:
                percentage = 0
            
            stats[category] = {
                'count': count,
                'percentage': round(percentage, 2),
                'avg_confidence': round(
                    sum(email.get('confidence', 0) for email in emails) / count if count > 0 else 0, 
                    3
                )
            }
        
        stats['total'] = total_emails
        return stats
    
    def update_category_patterns(self, category: str, patterns: Dict):
        """Update category patterns (for dynamic learning)."""
        if category in self.category_patterns:
            self.category_patterns[category].update(patterns)
            self.logger.info(f"Updated patterns for category: {category}")
        else:
            self.category_patterns[category] = patterns
            self.logger.info(f"Added new category: {category}")
    
    def add_exclude_domain(self, domain: str):
        """Add a domain to the exclusion list."""
        if domain not in self.exclude_domains:
            self.exclude_domains.append(domain.lower())
            self.logger.info(f"Added exclude domain: {domain}")
    
    def add_exclude_keyword(self, keyword: str):
        """Add a keyword to the exclusion list."""
        if keyword.lower() not in self.config.email.exclude_keywords:
            self.config.email.exclude_keywords.append(keyword.lower())
            self.logger.info(f"Added exclude keyword: {keyword}") 