from flask import Flask, render_template, request, redirect, url_for
from google.cloud import ndb
import os
from datetime import datetime

# Import environment settings
import set_env

app = Flask(__name__)

# Initialize the NDB client
client = ndb.Client()

# Define Comment model
class Comment(ndb.Model):
    content = ndb.StringProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)

def comment_wall_key():
    return ndb.Key('Commentwall', 'commentwall')

@app.route('/')
def home():
    return render_template('home.html')

# Add routes for all your pages
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
                
                new_comment = Comment(parent=comment_wall_key(),
                                    content=content)
                new_comment.put()
                return redirect(url_for('comments'))
            
            # GET request
            query = Comment.query(ancestor=comment_wall_key())
            comments = query.order(-Comment.date).fetch()
            return render_template('comments.html', mycomments=comments)
    except Exception as e:
        print(f"Error: {e}")  # For debugging
        return render_template('comments.html', 
                             error="Database connection error",
                             mycomments=[])

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True) 