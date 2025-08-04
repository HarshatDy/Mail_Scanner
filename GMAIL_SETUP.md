# Gmail API Setup Guide for Email Scanner

This guide will help you set up the Email Scanner to work with your Gmail account using the Gmail API.

## Prerequisites

- A Gmail account
- Python 3.9+ installed
- Gemini API key (for AI features)

## Step 1: Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click on "Gmail API" and then "Enable"

## Step 2: Create OAuth 2.0 Credentials

1. In the Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "Email Scanner")
5. Click "Create"
6. Download the credentials file (it will be named something like `client_secret_xxxxx.json`)
7. Rename it to `credentials.json` and place it in the project root directory

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

4. Edit the `config.yaml` file with your settings:
   ```yaml
   email:
     use_gmail_api: true
     credentials_file: "credentials.json"
     token_file: "token.json"
   
   ai:
     gemini_api_key: "your-gemini-api-key"
   ```

## Step 5: First Authentication

When you run the application for the first time, it will:

1. Open your default web browser
2. Ask you to sign in to your Google account
3. Request permission to access your Gmail
4. Create a `token.json` file for future use

## Step 6: Validate Configuration

Test your setup:
```bash
python main.py validate
```

You should see:
```
✅ Gmail API connection successful!
✅ Configuration is ready to use.
```

## Step 7: Run Your First Scan

Test the email scanner:
```bash
python main.py scan
```

## Configuration Options

### Email Settings

```yaml
email:
  use_gmail_api: true
  credentials_file: "credentials.json"
  token_file: "token.json"
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

### "Credentials file not found" error

- Make sure `credentials.json` is in the project root directory
- Verify the file name is exactly `credentials.json`
- Check that the file contains valid OAuth 2.0 credentials

### "Authentication failed" error

- Delete the `token.json` file and try again
- Make sure you're using the correct Google account
- Verify that Gmail API is enabled in your Google Cloud project

### "Permission denied" error

- Make sure you granted the necessary permissions during OAuth flow
- Check that your Google account has access to Gmail
- Verify that the OAuth consent screen is configured properly

### "No emails found" message

- Check the `days_back` setting in your configuration
- Verify the `gmail_labels` include the folders you want to scan
- Make sure you have emails in the specified time range

### Rate limiting issues

- Gmail API has rate limits (1,000,000,000 queries per 100 seconds per user)
- The scanner includes built-in delays to respect these limits
- If you encounter issues, try reducing `max_emails_per_scan`

## Security Notes

- **Never commit your credentials.json or token.json files to version control**
- Store your credentials securely
- The OAuth token can be revoked if needed
- Consider using environment variables for sensitive data

## Environment Variables

You can also set credentials via environment variables:

```bash
export EMAIL_USE_GMAIL_API="true"
export EMAIL_CREDENTIALS_FILE="credentials.json"
export EMAIL_TOKEN_FILE="token.json"
export GEMINI_API_KEY="your-gemini-api-key"
```

## Advanced Configuration

### Custom Categories

You can customize the email categorization by modifying the patterns in the code:

- `src/email_processing/filter.py` - Email filtering and categorization
- `src/email_processing/categorizer.py` - Content analysis

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
4. Verify your Google Cloud Console settings

## Privacy

- The scanner only reads emails, it never sends emails unless configured
- Email content is processed locally
- No email data is stored permanently unless configured
- The Gemini API processes content for topic generation
- OAuth tokens are stored locally and can be revoked at any time

## Migration from SMTP/IMAP

If you were previously using SMTP with app passwords:

1. Set `use_gmail_api: true` in your config
2. Follow the Gmail API setup steps above
3. Remove the old username/password configuration
4. The application will automatically use Gmail API instead of SMTP/IMAP 