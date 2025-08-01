# Gmail Setup Guide for Email Scanner

This guide will help you set up the Email Scanner to work with your Gmail account.

## Prerequisites

- A Gmail account
- 2-Factor Authentication enabled on your Google account
- Python 3.9+ installed
- Gemini API key (for AI features)

## Step 1: Enable 2-Factor Authentication

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click on "2-Step Verification"
3. Follow the prompts to enable 2-Factor Authentication
4. Make sure to add a backup phone number

## Step 2: Generate Gmail App Password

**Important**: You cannot use your regular Gmail password. You must generate an App Password.

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under "2-Step Verification", click on "App passwords"
3. Select "Mail" from the dropdown
4. Click "Generate"
5. Copy the 16-character password that appears
6. **Save this password securely** - you'll need it for the configuration

## Step 3: Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

## Step 4: Install and Setup

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the setup command:
   ```bash
   python main.py setup
   ```

4. Edit the `config.yaml` file with your credentials:
   ```yaml
   email:
     username: "yourname@gmail.com"
     password: "your-16-character-app-password"
   
   ai:
     gemini_api_key: "your-gemini-api-key"
   ```

## Step 5: Validate Configuration

Test your setup:
```bash
python main.py validate
```

You should see:
```
✅ Gmail connection successful!
✅ Configuration is ready to use.
```

## Step 6: Run Your First Scan

Test the email scanner:
```bash
python main.py scan
```

## Configuration Options

### Email Settings

```yaml
email:
  username: "yourname@gmail.com"
  password: "your-app-password"
  max_emails_per_scan: 100
  scan_unread_only: false
  days_back: 7
  gmail_labels: ["INBOX", "Primary", "Social", "Promotions"]
```

### Filtering Settings

```yaml
email:
  exclude_domains:
    - "bank.com"
    - "paypal.com"
    - "amazon.com"
  
  exclude_keywords:
    - "unsubscribe"
    - "spam"
    - "promotion"
  
  include_categories:
    - "tech"
    - "newsletter"
    - "social"
    - "professional"
```

### AI Settings

```yaml
ai:
  provider: "gemini"
  gemini_api_key: "your-api-key"
  model: "gemini-pro"
  max_tokens: 1000
  temperature: 0.7
  max_topics_per_scan: 10
```

## Troubleshooting

### "Authentication failed" error

- Make sure you're using an App Password, not your regular Gmail password
- Verify that 2-Factor Authentication is enabled
- Check that the App Password was generated for "Mail"

### "Connection failed" error

- Check your internet connection
- Verify the Gmail IMAP settings are correct
- Make sure your Gmail account allows IMAP access

### "No emails found" message

- Check the `days_back` setting in your configuration
- Verify the `gmail_labels` include the folders you want to scan
- Make sure you have emails in the specified time range

### Rate limiting issues

- Gmail has rate limits for IMAP connections
- The scanner includes built-in delays to respect these limits
- If you encounter issues, try reducing `max_emails_per_scan`

## Security Notes

- **Never commit your config.yaml file to version control**
- Store your App Password securely
- The App Password is specific to this application and can be revoked if needed
- Consider using environment variables for sensitive data

## Environment Variables

You can also set credentials via environment variables:

```bash
export EMAIL_USERNAME="yourname@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export GEMINI_API_KEY="your-gemini-api-key"
```

## Advanced Configuration

### Custom Categories

You can customize the email categorization by modifying the patterns in the code:

- `src/email/filter.py` - Email filtering and categorization
- `src/email/categorizer.py` - Content analysis

### Scheduling

Set up automated scanning:

```bash
python main.py scheduler
```

This will run scans at the configured times (default: 9 AM and 6 PM).

### Web Interface

Enable the web interface for easier management:

```yaml
web:
  enabled: true
  host: "0.0.0.0"
  port: 5000
```

Then run:
```bash
python main.py web
```

## Support

If you encounter issues:

1. Check the logs in the `logs/` directory
2. Run `python main.py validate` to test your configuration
3. Ensure all prerequisites are met
4. Verify your Gmail settings

## Privacy

- The scanner only reads emails, it never sends emails
- Email content is processed locally
- No email data is stored permanently unless configured
- The Gemini API processes content for topic generation 