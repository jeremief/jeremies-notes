import cgi
import urllib

from google.appengine.ext import ndb

import os
import jinja2
import webapp2

# Set up jinja environment

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

comments_header = open("templates/comments_header_template.html")
COMMENTS_PAGE_HEADER_TEMPLATE = comments_header.read()
comments_header.close()

comments_footer = open("templates/comments_footer_template.html")
COMMENTS_PAGE_FOOTER_TEMPLATE = comments_footer.read()
comments_footer.close()


def comment_wall_key():
    """
    Creating a key for the Google Datastore.
    """
    return ndb.Key('Commentwall', 'commentwall')


def swear_check(swear_check_text):
    """
    Checking the content of each post for profanity. Alter the post's content
    if some is found.
    """
    connection = urllib.urlopen("http://www.wdyl.com/profanity?q=" +
                                swear_check_text)
    output = connection.read()
    connection.close()
    if "true" in output:
        final_text = "I will not write that!"
    else:
        final_text = swear_check_text
    return final_text


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class HomePage(Handler):
    def get(self):
        self.render("home.html")


class ZeroPage(Handler):
    def get(self):
        self.render("stagezero.html")


class OnePage(Handler):
    def get(self):
        self.render("stageone.html")


class TwoPage(Handler):
    def get(self):
        self.render("stagetwo.html")


class ThreePage(Handler):
    def get(self):
        self.render("stagethree.html")


class FourPage(Handler):
    def get(self):
        self.render("stagefour.html")


class FivePage(Handler):
    def get(self):
        self.render("stagefive.html")


class Comment(ndb.Model):
    """A main model for representing an individual comment."""
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class CommentsPage(webapp2.RequestHandler):
    def get(self):

        error = self.request.get('error', '')
        number_of_records_to_fetch = 20


        comments_query = Comment.query(
            ancestor=comment_wall_key()).order(-Comment.date)
        comments = comments_query.fetch(number_of_records_to_fetch)

        self.response.write(COMMENTS_PAGE_HEADER_TEMPLATE % error)

        for comment in comments:
            self.response.write('<blockquote>%s</blockquote><br>' %
                                cgi.escape(comment.content))

        self.response.write(COMMENTS_PAGE_FOOTER_TEMPLATE)

    def post(self):
        comment = Comment(parent=comment_wall_key())

        comment.content = self.request.get('content')
        if comment.content != "":
            swear_check_text = str(comment.content)
            comment.content = swear_check(swear_check_text)
            comment.put()
            self.redirect('/comments')
        else:
            self.redirect('/comments?error=No empty comment please')


app = webapp2.WSGIApplication([('/', HomePage),
                               ('/zero', ZeroPage),
                               ('/one',OnePage),
                               ('/two',TwoPage),
                               ('/three',ThreePage),
                               ('/four',FourPage),
                               ('/five',FivePage),
                               ('/comments',CommentsPage)],
                              debug=True)
