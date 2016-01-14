import cgi
import urllib
import urllib2
import webbrowser

from google.appengine.ext import ndb

import os
import jinja2
import webapp2
import pprint

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
    def get(self,*summary):

        summary = self.request.get('summary','')
        # self.render("stagefive.html")
        # self.response.out.write(summary)

        # summary = "This is the summary"

        template_values = {
            'summary': summary,
        }

        template = jinja_env.get_template('stagefive.html')
        self.response.write(template.render(template_values))


class ApiExemple(Handler):
    def get(self):

        num_characters_before_id = 9
        num_characters_before_redirect = 0
        redirect_flag = False

        user_entry = self.request.get("article")
        # self.response.out.write(user_entry)

        while redirect_flag == False:
            #Extract text from URL
            user_entry = user_entry.title()
            modified_user_entry = user_entry.replace(" ", "_")
            print modified_user_entry
            url_for_api = 'https://en.wikipedia.org/w/api.php?action=query&titles=' + modified_user_entry +'&prop=revisions&rvprop=content&format=json'
            response = urllib2.urlopen(url_for_api)
            res = response.read()
            response.close()

            # Find page ID
            start_pageid = res.find("pages") + num_characters_before_id
            end_pageid = res.find('"',start_pageid)
            page_id = res[start_pageid:end_pageid]
            page_id = int(page_id)

            if page_id == -1:
                print "No such page"
                redirect_flag = True
            else:
                # if there is a REDIRECT, use it as a new user entry
                redirect_flag = True
                start_redirect = res.find("REDIRECT")
                if start_redirect != -1:
                    first_curly_before_redirect = res.find('[',start_redirect)
                    num_characters_before_redirect = first_curly_before_redirect - start_redirect + 2
                    end_redirect = res.find(']]',start_redirect)
                    redirect = res[start_redirect + num_characters_before_redirect:end_redirect]
                    user_entry = redirect
                    redirect_flag = False


        start_summary = res.find("'''")
        end_summary = res.find("==")
        print start_summary
        print end_summary
        raw_summary = res[start_summary:end_summary]
        print raw_summary

        self.redirect('/five?summary=' + raw_summary)




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
                               ('/api',ApiExemple),
                               ('/comments',CommentsPage)],
                              debug=True)
