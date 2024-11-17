from flask import Flask, render_template, request, redirect, url_for, jsonify
from google.cloud import ndb
import os
from datetime import datetime
import re
import json
import urllib.request
import urllib.parse
import logging
from markupsafe import escape
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix
import bleach

logging.basicConfig(level=logging.INFO)
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Security headers configuration
csp = {
    'default-src': "'self'",
    'script-src': ["'self'", "'unsafe-inline'", 
                   "https://code.jquery.com",
                   "https://www.googletagmanager.com"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': ["'self'", "data:", "https:"],
    'connect-src': ["'self'", "https://en.wikipedia.org"]
}

# Initialize Talisman
Talisman(app,
         content_security_policy=csp,
         force_https=True,
         strict_transport_security=True,
         session_cookie_secure=True,
         session_cookie_http_only=True)

# Use ProxyFix to handle proxy headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Update the database context handling
def get_client():
    try:
        if os.getenv('GAE_ENV', '').startswith('standard'):
            return ndb.Client()
        else:
            os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8081"
            return ndb.Client()
    except Exception as e:
        logging.error(f"Failed to create client: {e}")
        raise

client = get_client()

# Models
class Comment(ndb.Model):
    content = ndb.StringProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)

class SummaryClass(ndb.Model):
    time_request = ndb.DateTimeProperty(auto_now_add=True)
    search = ndb.StringProperty(required=True)
    summary = ndb.TextProperty(required=True)

# Helper functions
def comment_wall_key():
    return ndb.Key('Commentwall', 'commentwall')

def curly_cleaner(text):
    return re.sub(r'\{.*?\}', '', text)

def ref_cleaner(text):
    return re.sub(r'\[\d+\]', '', text)

def html_cleaner(text):
    return re.sub(r'<.*?>', '', text)

def clean_text(text):
    # Sanitize HTML and potentially dangerous content
    text = bleach.clean(text, strip=True)
    text = curly_cleaner(text)
    text = ref_cleaner(text)
    text = html_cleaner(text)
    return text

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/comments', methods=['GET', 'POST'])
def comments():
    try:
        with client.context():
            if request.method == 'POST':
                # Sanitize and validate input
                content = bleach.clean(request.form.get('content', '').strip())
                if not content:
                    return render_template('comments.html', 
                                         error="Comment cannot be empty",
                                         mycomments=[])
                
                # Validate content length
                if len(content) > 1000:  # Example limit
                    return render_template('comments.html', 
                                         error="Comment too long",
                                         mycomments=[])
                
                try:
                    new_comment = Comment(parent=comment_wall_key(),
                                        content=escape(content))  # Escape content
                    new_comment.put()
                    logging.info("Successfully added comment")
                except Exception as e:
                    logging.error(f"Failed to save comment: {e}")
                    return render_template('comments.html', 
                                         error="Failed to save comment",
                                         mycomments=[])
                
                return redirect(url_for('comments'))
            
            # Fetch and escape comments for display
            try:
                query = Comment.query(ancestor=comment_wall_key())
                comments = query.order(-Comment.date).fetch()
                # Escape comment content before rendering
                escaped_comments = [
                    {'content': escape(c.content), 'date': c.date} 
                    for c in comments
                ]
                logging.info(f"Retrieved {len(comments)} comments")
                return render_template('comments.html', mycomments=escaped_comments)
            except Exception as e:
                logging.error(f"Failed to fetch comments: {e}")
                return render_template('comments.html', 
                                     error="Failed to load comments",
                                     mycomments=[])
    except Exception as e:
        logging.error(f"Database context error: {e}")
        return render_template('comments.html', 
                             error="Database connection error",
                             mycomments=[])

@app.route('/api', methods=['POST'])
def api():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
        
    try:
        data = request.get_json()
        search_term = bleach.clean(data.get('search', ''))
        
        # Validate search term
        if not search_term or len(search_term) > 100:  # Example limit
            return jsonify({'error': 'Invalid search term'}), 400
            
        with client.context():
            # Check cache with sanitized search term
            query = SummaryClass.query()
            query = query.filter(SummaryClass.search == search_term)
            result = query.get()
            
            if result:
                return jsonify({'summary': escape(result.summary)})
            
            # Fetch from Wikipedia with sanitized term
            search_term_encoded = urllib.parse.quote(search_term)
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_term_encoded}"
            
            # Add timeout to prevent hanging
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read())
            
            if 'extract' in data:
                summary = clean_text(data['extract'])
                
                # Store sanitized summary in cache
                new_summary = SummaryClass(
                    search=search_term,
                    summary=escape(summary)
                )
                new_summary.put()
                
                return jsonify({'summary': summary})
            
            return jsonify({'error': 'No summary found'}), 404
    except urllib.error.URLError as e:
        logging.error(f"Wikipedia API error: {e}")
        return jsonify({'error': 'Failed to fetch data'}), 503
    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/zero')
def zero():
    return render_template('stagezero.html')

@app.route('/one')
def one():
    return render_template('stageone.html')

@app.route('/two')
def two():
    return render_template('stagetwo.html')

@app.route('/three')
def three():
    return render_template('stagethree.html')

@app.route('/four')
def four():
    return render_template('stagefour.html')

@app.route('/five')
def five():
    return render_template('stagefive.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == '__main__':
    # Only use debug mode in development
    debug_mode = not os.getenv('GAE_ENV', '').startswith('standard')
    app.run(host='localhost', port=8080, debug=debug_mode)