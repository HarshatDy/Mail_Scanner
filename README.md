# Gmail Email Scanner & Blog Topic Generator

An automated system that scans Gmail accounts, categorizes emails, and generates blog topics using Google's Gemini AI for tech and newsletter content.

## Features

- 🔍 **Gmail Integration**: Connect to Gmail with secure App Password authentication
- 🏷️ **Smart Categorization**: Automatically categorize emails into Tech, Newsletter, Social, and Professional
- 🚫 **Intelligent Filtering**: Exclude personal and banking emails
- 🤖 **AI-Powered Topics**: Generate blog topics using Google Gemini API
- ⏰ **Automated Scheduling**: Run scans twice daily at configurable times
- 📊 **Content Analysis**: Extract and analyze relevant content from emails
- 🔔 **Notifications**: Get notified about new topics and system status

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Gmail account with 2-Factor Authentication enabled
- Gmail App Password (see [GMAIL_SETUP.md](GMAIL_SETUP.md))
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Mail_Scanner
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the system**
   ```bash
   python main.py setup
   ```

5. **Configure your credentials**
   ```bash
   # Edit config.yaml with your Gmail and Gemini API credentials
   # See GMAIL_SETUP.md for detailed instructions
   ```

### Configuration

#### Environment Variables (Recommended)

For security, use the `.env` file to store sensitive configuration:

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials**:
   ```bash
   # Email Configuration
   EMAIL_USERNAME=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   EMAIL_IMAP_SERVER=imap.gmail.com
   EMAIL_IMAP_PORT=993
   EMAIL_SMTP_SERVER=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   
   # AI Configuration
   GEMINI_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key
   
   # Database Configuration
   DATABASE_URL=sqlite:///data/emails.db
   
   # Notification Configuration
   SLACK_WEBHOOK_URL=your_slack_webhook_url
   DISCORD_WEBHOOK_URL=your_discord_webhook_url
   
   # Web Interface
   WEB_SECRET_KEY=your_secret_key_here
   ```

3. **The system will automatically load these environment variables**

**Security Note**: The `.env` file contains sensitive information and is automatically ignored by git. Never commit your actual `.env` file to version control.

#### Direct Configuration (Alternative)

Edit `config.yaml` with your settings:

```yaml
email:
  username: your_email@gmail.com
  password: your_app_password
  
ai:
  gemini_api_key: your_gemini_api_key
```

### Running the System

1. **Validate your setup**
   ```bash
   python main.py validate
   ```

2. **Manual scan**
   ```bash
   python main.py scan
   ```

3. **Start scheduler (runs twice daily)**
   ```bash
   python main.py scheduler
   ```

4. **Check system status**
   ```bash
   python main.py status
   ```

5. **Web interface (optional)**
   ```bash
   python main.py web
   ```

## Project Structure

```
Mail_Scanner/
├── src/
│   ├── email/           # Email connection and filtering
│   ├── processing/      # Content extraction and cleaning
│   ├── database/        # Database models and operations
│   ├── ai/             # Gemini API integration
│   ├── scheduler/      # Task scheduling
│   ├── notifications/  # Notification system
│   ├── web/           # Web interface (optional)
│   ├── config/        # Configuration management
│   └── utils/         # Utility functions
├── tests/             # Unit tests
├── data/              # Database and data files
├── logs/              # Application logs
├── requirements.txt   # Python dependencies
├── config.yaml        # Configuration file
└── README.md         # This file
```

## Gmail Setup

**For detailed Gmail setup instructions, see [GMAIL_SETUP.md](GMAIL_SETUP.md)**

### Quick Gmail Setup

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate an App Password**:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Use the App Password** in your configuration (NOT your regular password)

### Important Notes

- You **must** use an App Password, not your regular Gmail password
- 2-Factor Authentication is required to generate App Passwords
- The system is specifically optimized for Gmail's IMAP interface

## AI Integration

### Gemini API Setup

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to your configuration:
   ```yaml
   ai:
     gemini_api_key: your_api_key_here
   ```

### Topic Generation

The system automatically:
- Analyzes tech and newsletter emails
- Generates relevant blog topics
- Provides topic descriptions and keywords
- Suggests content structure

## Database

The system uses SQLite by default. Data is stored in `data/emails.db`:

- Email metadata and content
- Categorization results
- Generated topics
- Processing history

## Scheduling

The system runs automatically twice daily:
- **Morning scan**: 9:00 AM
- **Evening scan**: 6:00 PM

You can customize these times in `config.yaml`:

```yaml
scheduler:
  scan_times:
    - "09:00"
    - "18:00"
  timezone: UTC
```

## Notifications

Get notified about:
- New blog topics generated
- System errors
- Weekly summaries

Configure notifications in `config.yaml`:

```yaml
notifications:
  slack_webhook: your_slack_webhook_url
  discord_webhook: your_discord_webhook_url
```

## Web Interface

Enable the web interface to:
- View email statistics
- Manage generated topics
- Configure system settings
- Export data

```yaml
web:
  enabled: true
  host: 0.0.0.0
  port: 5000
```

## Development

### Running Tests

```bash
pytest tests/
pytest tests/ --cov=src
```

### Code Formatting

```bash
black src/
flake8 src/
mypy src/
```

### Adding New Features

1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request

## Troubleshooting

### Common Issues

1. **Email Connection Failed**
   - Check credentials in `.env` file or `config.yaml`
   - Verify App Password for Gmail
   - Check firewall settings

2. **Gemini API Errors**
   - Verify API key is correct in `.env` file or `config.yaml`
   - Check API quota limits
   - Ensure internet connection

3. **Database Errors**
   - Check file permissions for data directory
   - Verify SQLite installation
   - Check disk space

### Logs

Check logs in `logs/email_scanner.log` for detailed error information.

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the logs for error details

## Roadmap

- [ ] Machine learning-based email categorization
- [ ] Support for more email providers
- [ ] Advanced topic clustering
- [ ] Content summarization
- [ ] Integration with Medium API
- [ ] Mobile app
- [ ] Team collaboration features 