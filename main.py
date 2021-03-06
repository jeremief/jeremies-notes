import cgi
import urllib
import urllib2

from google.appengine.ext import ndb

import os
import jinja2
import webapp2

# Set up jinja environment

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def summary_key():
    """
    Creating a key of the summary for the Google Datastore.
    """
    return ndb.Key('Summary', 'summary')


def comment_wall_key():
    """
    Creating a key for the Google Datastore.
    """
    return ndb.Key('Commentwall', 'commentwall')


def curly_cleaner(raw_string):
    """
    Clearing curly brackets and their contents
    """
    end_flag = False
    while raw_string.find('{{') != -1 and end_flag is False:
        start_curly = raw_string.find('{{')
        if raw_string.find('}}', start_curly) != -1:
            end_curly = raw_string.find('}}', start_curly) + 2
            raw_string = raw_string[:start_curly] + raw_string[end_curly:]
        else:
            end_flag = True
    return raw_string


def ref_cleaner(raw_string):
    """
    Clearing reference tags and their contents
    """
    end_flag = False
    while raw_string.find('<ref') != -1 and end_flag is False:
        start_ref = raw_string.find('<ref')
        if raw_string.find('</ref>', start_ref) != -1:
            end_ref = raw_string.find('</ref>', start_ref) + 6
            raw_string = raw_string[:start_ref] + raw_string[end_ref:]
        else:
            end_flag = True
    return raw_string


def pipe_cleaner(raw_string):
    """
    Removing pipes and the contents to their left
    """
    end_flag = False
    while raw_string.find('|') != -1 and end_flag is False:
        pipe = raw_string.find('|')
        begining_word = raw_string.rfind('[', 0, pipe)
        raw_string = raw_string[:begining_word + 1] + raw_string[pipe + 1:]
    return raw_string


def square_cleaner(raw_string):
    """
    Clearing square brackets
    """
    end_flag = False
    while raw_string.find('[[') != -1 and end_flag is False:
        start_square = raw_string.find('[[')
        if raw_string.find(']]', start_square) != -1:
            end_square = raw_string.find(']]', start_square)
            raw_string = raw_string[:start_square] + \
                raw_string[start_square + 2:
                           end_square] + raw_string[end_square + 2:]
        else:
            end_flag = True
    return raw_string


def note_cleaner(raw_string):
    """
    Clearing note tags and their contents
    """
    end_flag = False
    while raw_string.find('<!--') != -1 and end_flag is False:
        start_note = raw_string.find('<!--')
        if raw_string.find('-->', start_note) != -1:
            end_note = raw_string.find('-->', start_note) + 3
            raw_string = raw_string[:start_note] + raw_string[end_note:]
        else:
            end_flag = True
    return raw_string


def various_cleaner(raw_string):
    """
    Clearing various characters left after various cleanups
    """
    raw_string = raw_string.replace('&nbsp;', ' ')
    raw_string = raw_string.replace('(; ', '(')
    raw_string = raw_string.replace('(; ; ', '(')
    return raw_string


def text_cleaner(raw_text):
    curly_cleaned_text = curly_cleaner(raw_text)
    ref_cleaned_text = ref_cleaner(curly_cleaned_text)
    pipe_cleaned_text = pipe_cleaner(ref_cleaned_text)
    square_cleaned_text = square_cleaner(pipe_cleaned_text)
    note_cleaned_text = note_cleaner(square_cleaned_text)
    cleaned_text = various_cleaner(note_cleaned_text)
    cleaned_text = cleaned_text.decode('unicode-escape')
    cleaned_text = cleaned_text.encode('utf-8')
    return cleaned_text


def escape_comments(comments):
    escaped_comments = []
    for comment in comments:
        comment.content = cgi.escape(comment.content)
        escaped_comments.append(comment)
    return escaped_comments


class SummaryClass(ndb.Model):
    """A model for a Wikipedia summary."""
    content = ndb.StringProperty(indexed=False)
    wlink = ndb.StringProperty(indexed=False)
    time_request = ndb.DateTimeProperty(indexed=True, auto_now_add=True)


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
    def get(self, *summary):

        number_of_summaries_to_fetch = 1
        summary_query = SummaryClass.query(ancestor=summary_key()).\
            order(-SummaryClass.time_request)
        summary_list = summary_query.fetch(number_of_summaries_to_fetch)
        if summary_list:
            summary = summary_list[0]
            summary_content = summary.content
            summary_link = str(summary.wlink)

            template_values = {'summary': summary_content,
                               'wlink': summary_link, }

            template = jinja_env.get_template('stagefive.html')
            self.response.write(template.render(template_values))
        else:
            self.render("stagefive.html")


class ApiExemple(Handler):

    def post(self):

        num_characters_before_id = 9
        num_characters_before_redirect = 0
        redirect_flag = False

        user_entry = self.request.get("article")

        if user_entry != "":

            while redirect_flag is False:
                # Extract text from URL
                user_entry = user_entry.title()
                modified_user_entry = user_entry.replace(" ", "_")
                print modified_user_entry
                url_for_api = ('https://en.wikipedia.org/w/api.php?action=' +
                               'query&titles=' + modified_user_entry +
                               '&prop=revisions&rvprop=content&format=json')
                response = urllib2.urlopen(url_for_api)
                res = response.read()
                response.close()

                # Find page ID
                start_pageid = res.find("pages") + num_characters_before_id
                end_pageid = res.find('"', start_pageid)
                page_id = res[start_pageid:end_pageid]
                page_id = int(page_id)

                if page_id == -1:
                    # print "No such page"
                    redirect_flag = True
                else:
                    # if there is a REDIRECT, use it as a new user entry
                    redirect_flag = True
                    start_redirect = res.find("REDIRECT")
                    if start_redirect != -1:
                        first_curly_before_redirect = res.find('[',
                                                               start_redirect)
                        num_characters_before_redirect = \
                            first_curly_before_redirect - start_redirect + 2
                        end_redirect = res.find(']]', start_redirect)
                        redirect = res[start_redirect +
                                       num_characters_before_redirect:
                                       end_redirect]
                        user_entry = redirect
                        redirect_flag = False

        MySummary = SummaryClass(parent=summary_key())

        if user_entry != "":

            if page_id != -1:
                start_summary = res.find("'''")
                end_summary = res.find("==")

                if start_summary != -1 and start_summary < end_summary:
                    raw_summary = res[start_summary:end_summary]
                    raw_summary = text_cleaner(raw_summary)
                    MySummary.content = raw_summary
                    MySummary.wlink = 'http://en.wikipedia.org/?curid=' + \
                        str(page_id)
                    MySummary.put()
                    self.redirect('/five#summary')

                else:
                    MySummary.content = "Unfortunately, we couldn't generate \
                    a summary for this page. Please follow the link below to \
                    find out more."
                    MySummary.wlink = 'http://en.wikipedia.org/?curid=' + \
                                      str(page_id)
                    MySummary.put()
                    self.redirect('/five#summary')

            else:
                MySummary.content = "No such page referenced by Wikipedia \
                or summary is not accessible. Please enter another search."
                MySummary.wlink = 'None'
                MySummary.put()

                self.redirect('/five#summary')

        else:
            MySummary.content = "No search query was entered. Please enter \
            query in search box"
            MySummary.wlink = 'None'
            MySummary.put()
            self.redirect('five#summary')


class Comment(ndb.Model):
    """A main model for representing an individual comment."""
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class CommentsPage(Handler):
    """Keeping comments structure in line with the rest of the pages"""
    def get(self):

        error = self.request.get('error', '')
        number_of_records_to_fetch = 20

        comments_query = Comment.query(
            ancestor=comment_wall_key()).order(-Comment.date)
        comments = comments_query.fetch(number_of_records_to_fetch)

        escaped_comments = escape_comments(comments)

        self.render("comments.html", mycomments=escaped_comments, error=error)

    def post(self):
        comment = Comment(parent=comment_wall_key())

        comment.content = self.request.get('content')
        if comment.content != "":
            comment.put()
            self.redirect('/comments')
        else:
            self.redirect('/comments?error=No empty comment please')


app = webapp2.WSGIApplication([('/', HomePage),
                               ('/zero', ZeroPage),
                               ('/one', OnePage),
                               ('/two', TwoPage),
                               ('/three', ThreePage),
                               ('/four', FourPage),
                               ('/five', FivePage),
                               ('/api', ApiExemple),
                               ('/comments', CommentsPage)],
                              debug=True)
