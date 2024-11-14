from flask import Flask, render_template, request, redirect, url_for, jsonify
from google.cloud import ndb
import os
from datetime import datetime
import re
import json
import urllib.request
import urllib.parse
import logging
logging.basicConfig(level=logging.INFO)

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
                content = request.form.get('content', '').strip()
                if not content:
                    return render_template('comments.html', 
                                         error="Comment cannot be empty",
                                         mycomments=[])
                
                try:
                    new_comment = Comment(parent=comment_wall_key(),
                                        content=content)
                    new_comment.put()
                    logging.info("Successfully added comment")
                except Exception as e:
                    logging.error(f"Failed to save comment: {e}")
                    return render_template('comments.html', 
                                         error="Failed to save comment",
                                         mycomments=[])
                
                return redirect(url_for('comments'))
            
            try:
                query = Comment.query(ancestor=comment_wall_key())
                comments = query.order(-Comment.date).fetch()
                logging.info(f"Retrieved {len(comments)} comments")
                return render_template('comments.html', mycomments=comments)
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
    # Add debug logging
    print("Content-Type:", request.headers.get('Content-Type'))
    print("Request data:", request.get_data())
    
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
        
    try:
        data = request.get_json()
        search_term = data.get('search', '')
        
        if not search_term:
            return jsonify({'error': 'No search term provided'}), 400
            
        with client.context():
            # Check cache
            query = SummaryClass.query()
            query = query.filter(SummaryClass.search == search_term)
            result = query.get()
            
            if result:
                return jsonify({'summary': result.summary})
            
            # If not in cache, fetch from Wikipedia
            search_term_encoded = urllib.parse.quote(search_term)
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_term_encoded}"
            
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())
            
            if 'extract' in data:
                summary = clean_text(data['extract'])
                
                # Store in cache
                new_summary = SummaryClass(
                    search=search_term,
                    summary=summary
                )
                new_summary.put()
                
                return jsonify({'summary': summary})
            
            return jsonify({'error': 'No summary found'}), 404
    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500

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

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)