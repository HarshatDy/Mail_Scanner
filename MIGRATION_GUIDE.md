# Migration Guide: SMTP/IMAP to Gmail API

This guide helps you migrate from the old SMTP/IMAP authentication to the new Gmail API authentication.

## Why Migrate to Gmail API?

### Benefits
- **More Secure**: Uses OAuth2 instead of app passwords
- **Better Performance**: Direct API access is faster than IMAP
- **More Features**: Access to Gmail-specific features like labels, threads, etc.
- **Future-Proof**: Google is moving away from app passwords
- **No SMTP Required**: Send emails directly through Gmail API

### Drawbacks
- **Initial Setup**: Requires Google Cloud Console setup
- **OAuth Flow**: First-time authentication requires browser interaction

## Migration Steps

### Step 1: Prepare Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### Step 2: Create OAuth 2.0 Credentials

1. In Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application"
4. Give it a name (e.g., "Email Scanner")
5. Click "Create"
6. Download the credentials file
7. Rename it to `credentials.json` and place in project root

### Step 3: Update Configuration

#### Option A: Update config.yaml

Change your `config.yaml` from:
```yaml
email:
  username: "your_email@gmail.com"
  password: "your_app_password"
  imap_server: "imap.gmail.com"
  imap_port: 993
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
```

To:
```yaml
email:
  use_gmail_api: true
  credentials_file: "credentials.json"
  token_file: "token.json"
```

#### Option B: Update Environment Variables

Change your `.env` file from:
```bash
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_IMAP_PORT=993
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

To:
```bash
EMAIL_USE_GMAIL_API=true
EMAIL_CREDENTIALS_FILE=credentials.json
EMAIL_TOKEN_FILE=token.json
```

### Step 4: Test the Migration

1. **Validate configuration**:
   ```bash
   python main.py validate
   ```

2. **Test Gmail API connection**:
   ```bash
   python test_gmail_api.py
   ```

3. **Run a test scan**:
   ```bash
   python main.py scan
   ```

### Step 5: Clean Up (Optional)

After confirming everything works:

1. **Remove old credentials**:
   - Delete or archive your old app password
   - Remove username/password from config files

2. **Update documentation**:
   - Update any custom scripts that reference old config
   - Update team documentation

## Troubleshooting Migration

### "Credentials file not found"

- Make sure `credentials.json` is in the project root
- Verify the file name is exactly `credentials.json`
- Check file permissions

### "Authentication failed"

- Delete `token.json` if it exists
- Run the application again to trigger OAuth flow
- Make sure you're using the correct Google account

### "Permission denied"

- Check that Gmail API is enabled in Google Cloud Console
- Verify OAuth consent screen is configured
- Make sure you granted all requested permissions

### "No emails found"

- Check that your Gmail account has emails
- Verify the search query is correct
- Check the `days_back` setting

### "Rate limit exceeded"

- Gmail API has generous limits (1B queries per 100 seconds)
- This is usually not an issue for normal usage
- If you hit limits, reduce `max_emails_per_scan`

## Rollback Plan

If you need to rollback to SMTP/IMAP:

1. **Set use_gmail_api to false**:
   ```yaml
   email:
     use_gmail_api: false
     username: "your_email@gmail.com"
     password: "your_app_password"
   ```

2. **Regenerate app password** if needed:
   - Go to Google Account Security
   - 2-Step Verification > App passwords
   - Generate new password for "Mail"

3. **Test the rollback**:
   ```bash
   python main.py validate
   python main.py scan
   ```

## Configuration Comparison

| Feature | SMTP/IMAP | Gmail API |
|---------|-----------|-----------|
| Authentication | App Password | OAuth2 |
| Security | Good | Better |
| Setup Complexity | Simple | Moderate |
| Performance | Good | Better |
| Features | Basic | Advanced |
| Future Support | Limited | Full |

## Environment Variables Reference

### Old (SMTP/IMAP)
```bash
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_IMAP_PORT=993
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

### New (Gmail API)
```bash
EMAIL_USE_GMAIL_API=true
EMAIL_CREDENTIALS_FILE=credentials.json
EMAIL_TOKEN_FILE=token.json
```

## Support

If you encounter issues during migration:

1. Check the logs in `logs/email_scanner.log`
2. Run `python test_gmail_api.py` for diagnostics
3. Verify your Google Cloud Console setup
4. Check the [GMAIL_SETUP.md](GMAIL_SETUP.md) for detailed instructions

## Timeline

- **Phase 1**: Test Gmail API in parallel with existing setup
- **Phase 2**: Switch to Gmail API for new deployments
- **Phase 3**: Migrate existing deployments
- **Phase 4**: Deprecate SMTP/IMAP support (future)

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- Store credentials securely
- OAuth tokens can be revoked at any time
- Consider using environment variables for sensitive data 