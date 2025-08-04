# Email Sending Feature Guide

This guide explains how to use the email sending functionality in the Email Scanner & Blog Topic Generator.

## Overview

The system now includes a complete email sending feature that:

1. **Scans emails** from your Gmail account
2. **Analyzes content** for relevance and quality
3. **Generates blog topics** using AI (Gemini or OpenAI)
4. **Sends notification emails** with the generated topics

## Features

### ✅ Email Sending via Gmail API
- Uses OAuth2 authentication (no SMTP passwords needed)
- Sends HTML-formatted emails with beautiful styling
- Supports CC and BCC recipients
- Automatic error handling and retry logic

### ✅ AI-Powered Topic Generation
- Analyzes email content for relevance
- Generates blog topics using Gemini or OpenAI
- Categorizes topics by difficulty and category
- Provides keywords and descriptions

### ✅ Automated Workflow
- Runs on schedule (configurable times)
- Automatically processes relevant emails
- Sends topic summaries via email
- Logs all activities for monitoring

## Setup Instructions

### 1. Configure Environment Variables

Add these to your environment or `.env` file:

```bash
# Gmail API Configuration
EMAIL_USE_GMAIL_API=true
EMAIL_CREDENTIALS_FILE=credentials.json
EMAIL_TOKEN_FILE=token.json

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here

# Notification Configuration
NOTIFICATION_EMAIL=your_email@gmail.com
```

### 2. Update Configuration

Edit your `config.yaml` to enable email notifications:

```yaml
notifications:
  enabled: true
  email_notifications: true
  notification_email: ${NOTIFICATION_EMAIL}
  new_topics: true
  errors: true
  scan_complete: false
  weekly_summary: true

ai:
  provider: "gemini"  # or "openai"
  gemini_api_key: ${GEMINI_API_KEY}
  openai_api_key: ${OPENAI_API_KEY}
  model: "gemini-pro"
  max_tokens: 1000
  temperature: 0.7
  max_topics_per_scan: 10
```

### 3. Test the Setup

Run the test script to verify everything works:

```bash
python test_email_sending.py
```

This will:
- Test Gmail API connection
- Send a test email
- Test AI topic generation
- Verify all components are working

## Usage

### Manual Email Scan

Run a manual scan that will send topics via email:

```bash
python main.py scan
```

### Automated Scheduler

Start the automated scheduler that runs scans at scheduled times:

```bash
python main.py scheduler
```

The scheduler will:
1. Scan emails at configured times (default: 7:18 AM and 7:18 PM)
2. Process relevant emails for topic generation
3. Generate blog topics using AI
4. Send a beautifully formatted email with the topics

### Email Format

The generated emails include:

- **Subject**: "📝 Blog Topics Generated - [Date]"
- **HTML formatting** with professional styling
- **Topic details** including:
  - Title and description
  - Difficulty level (Beginner/Intermediate/Advanced)
  - Category (Tech/Newsletter/Professional)
  - Keywords for SEO
- **Color-coded** difficulty and category badges
- **Responsive design** that works on all devices

## Configuration Options

### Email Processing Settings

```yaml
email:
  max_emails_per_scan: 100
  scan_unread_only: false
  days_back: 7
  gmail_labels: ["INBOX", "Primary", "Social", "Promotions"]
```

### AI Topic Generation Settings

```yaml
ai:
  provider: "gemini"  # or "openai"
  model: "gemini-pro"
  max_tokens: 1000
  temperature: 0.7
  max_topics_per_scan: 10
  min_content_length: 100
  relevance_threshold: 0.7
```

### Scheduler Settings

```yaml
scheduler:
  scan_times:
    - "09:00"
    - "18:00"
  timezone: "UTC"
  max_retries: 3
  retry_delay: 300
```

## Troubleshooting

### Common Issues

1. **"Credentials file not found"**
   - Make sure `credentials.json` is in the project root
   - Download from Google Cloud Console

2. **"Authentication failed"**
   - Delete `token.json` and re-authenticate
   - Check that Gmail API is enabled in Google Cloud Console

3. **"No topics generated"**
   - Check that AI API keys are configured
   - Verify emails have sufficient content
   - Check relevance thresholds in config

4. **"Email not sent"**
   - Verify `NOTIFICATION_EMAIL` is set
   - Check Gmail API permissions
   - Ensure `email_notifications: true` in config

### Debug Mode

Enable debug logging to see detailed information:

```yaml
logging:
  level: "DEBUG"
  file: "logs/email_scanner.log"
```

### Manual Testing

Test individual components:

```bash
# Test email sending only
python -c "
from src.email_processing.sender import EmailSender
sender = EmailSender()
print('Connection:', sender.test_connection())
"

# Test topic generation only
python -c "
from src.ai.topic_generator import TopicGenerator
generator = TopicGenerator()
print('Connection:', generator.test_connection())
"
```

## Security Notes

- **Never commit** `credentials.json` or `token.json` to version control
- Use environment variables for sensitive configuration
- OAuth tokens can be revoked if needed
- Gmail API has rate limits (respect them)

## Advanced Features

### Custom Email Templates

You can customize the email template by modifying the `format_topics_as_html()` function in `src/scheduler/jobs.py`.

### Multiple Recipients

To send to multiple recipients, modify the `send_topics_email()` function:

```python
# Send to multiple recipients
recipients = ["user1@gmail.com", "user2@gmail.com"]
for recipient in recipients:
    email_sender.send_email(to=recipient, subject=subject, body=html_body)
```

### Custom Topic Categories

Add custom categories in the AI configuration:

```yaml
ai:
  categories:
    - "Technology Trends"
    - "Programming & Development"
    - "AI & Machine Learning"
    - "Startup & Business"
    - "Productivity & Tools"
    - "Your Custom Category"
```

## Monitoring

### Log Files

Check the logs for detailed information:

```bash
tail -f logs/email_scanner.log
```

### Email Delivery

- Check your email's spam folder if emails don't arrive
- Verify the sender email is trusted
- Monitor Gmail API quotas and limits

### Performance

- The system processes emails efficiently
- AI topic generation is rate-limited
- Email sending uses Gmail API for reliability

## Support

If you encounter issues:

1. Check the logs in `logs/email_scanner.log`
2. Run `python test_email_sending.py` to test components
3. Verify all environment variables are set
4. Ensure Google Cloud Console settings are correct

## Example Output

Here's what a generated email looks like:

```
Subject: 📝 Blog Topics Generated - 2025-01-15

🚀 Blog Topics Generated
Generated on: 2025-01-15 19:18:47

1. Building Scalable Microservices with Python
   Description: Learn how to design and implement scalable microservices using Python frameworks like FastAPI and Django.
   Difficulty: Intermediate | Category: Tech
   Keywords: python, microservices, fastapi, django, scalability

2. The Future of AI in Web Development
   Description: Explore how artificial intelligence is transforming web development workflows and tools.
   Difficulty: Advanced | Category: Tech
   Keywords: ai, web development, automation, machine learning

3. Effective Newsletter Strategies for Tech Companies
   Description: Discover proven strategies for creating engaging newsletters that drive engagement and conversions.
   Difficulty: Beginner | Category: Newsletter
   Keywords: newsletter, marketing, engagement, content strategy
```

The email sending feature is now fully implemented and ready to use! 🎉 