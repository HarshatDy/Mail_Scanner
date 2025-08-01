"""
Web interface for the Email Scanner system.
Provides a web-based dashboard for monitoring and managing the system.
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os

from ..config.config_manager import get_config
from ..database.operations import get_statistics, get_recent_emails, get_recent_topics
from ..scheduler.jobs import test_gmail_connection
from ..utils.logger import get_logger


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    config = get_config()
    logger = get_logger("web_app")
    
    # Configure app
    app.config['SECRET_KEY'] = config.web.secret_key or os.urandom(24)
    app.config['DEBUG'] = config.web.debug
    
    @app.route('/')
    def index():
        """Main dashboard page."""
        try:
            stats = get_statistics()
            return render_template('dashboard.html', stats=stats)
        except Exception as e:
            logger.error(f"Error loading dashboard: {e}")
            return render_template('error.html', error=str(e))
    
    @app.route('/api/status')
    def api_status():
        """API endpoint for system status."""
        try:
            stats = get_statistics()
            connection_status = test_gmail_connection()
            
            return jsonify({
                'status': 'success',
                'data': {
                    'statistics': stats,
                    'gmail_connection': connection_status,
                    'timestamp': datetime.now().isoformat()
                }
            })
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    @app.route('/api/emails')
    def api_emails():
        """API endpoint for recent emails."""
        try:
            limit = request.args.get('limit', 10, type=int)
            emails = get_recent_emails(limit)
            
            return jsonify({
                'status': 'success',
                'data': emails
            })
        except Exception as e:
            logger.error(f"Error getting emails: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    @app.route('/api/topics')
    def api_topics():
        """API endpoint for recent topics."""
        try:
            limit = request.args.get('limit', 10, type=int)
            topics = get_recent_topics(limit)
            
            return jsonify({
                'status': 'success',
                'data': topics
            })
        except Exception as e:
            logger.error(f"Error getting topics: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    @app.route('/api/test-connection')
    def api_test_connection():
        """API endpoint for testing Gmail connection."""
        try:
            success = test_gmail_connection()
            
            return jsonify({
                'status': 'success',
                'data': {
                    'connection_successful': success,
                    'timestamp': datetime.now().isoformat()
                }
            })
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {error}")
        return render_template('error.html', error="Internal server error"), 500
    
    return app


def create_basic_templates():
    """Create basic HTML templates if they don't exist."""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create basic dashboard template
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gmail Email Scanner - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2em; font-weight: bold; color: #2196F3; }
        .stat-label { color: #666; margin-top: 5px; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .status-connected { background: #4CAF50; }
        .status-disconnected { background: #f44336; }
        .btn { background: #2196F3; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #1976D2; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Gmail Email Scanner Dashboard</h1>
            <p>Monitor your email scanning system and generated topics</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_emails }}</div>
                <div class="stat-label">Total Emails Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.categorized_emails }}</div>
                <div class="stat-label">Emails Categorized</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.topics_generated }}</div>
                <div class="stat-label">Topics Generated</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.db_size }}</div>
                <div class="stat-label">Database Size</div>
            </div>
        </div>
        
        <div class="stat-card">
            <h3>System Status</h3>
            <p><span class="status-indicator status-connected"></span>Gmail Connection: Connected</p>
            <p>Last Scan: {{ stats.last_scan }}</p>
            <button class="btn" onclick="testConnection()">Test Connection</button>
            <button class="btn" onclick="refreshStats()">Refresh Stats</button>
        </div>
    </div>
    
    <script>
        function testConnection() {
            fetch('/api/test-connection')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('Connection test: ' + (data.data.connection_successful ? 'SUCCESS' : 'FAILED'));
                    } else {
                        alert('Error: ' + data.error);
                    }
                });
        }
        
        function refreshStats() {
            location.reload();
        }
    </script>
</body>
</html>'''
    
    # Create error template
    error_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - Gmail Email Scanner</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .error { color: #f44336; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Error</h1>
        <p class="error">{{ error }}</p>
        <a href="/">Return to Dashboard</a>
    </div>
</body>
</html>'''
    
    # Create 404 template
    not_found_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Not Found - Gmail Email Scanner</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container">
        <h1>Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
        <a href="/">Return to Dashboard</a>
    </div>
</body>
</html>'''
    
    # Write templates
    with open(os.path.join(templates_dir, 'dashboard.html'), 'w') as f:
        f.write(dashboard_html)
    
    with open(os.path.join(templates_dir, 'error.html'), 'w') as f:
        f.write(error_html)
    
    with open(os.path.join(templates_dir, '404.html'), 'w') as f:
        f.write(not_found_html) 