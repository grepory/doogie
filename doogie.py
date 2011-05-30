#!/usr/bin/python

# Doogie - Markdown CLI client for blogger.google.com
# Copyright 2011 Greg Poirier - Some rights reserved
# See LICENSE for details

from sys import exit
from os.path import exists
from os import system
from gdata import service
import atom
import gdata
import argparse
import markdown

class Post(object):

    def __init__(self, post_name):
        self.md_file = post_name + ".md"
        self.meta_file = post_name + ".meta"
        # determine if post is new
        if not exists(self.meta_file):
            self.new = True
        else:
            self.new = False
        self.html = None

    def get_html(self):
        if not self.html:
            f = open(self.md_file)
            text = f.read()
            self.html = '<html>'
            self.html += markdown.markdown(text)
            self.html += '</html>'
            f.close()
        return self.html

def main(user, password, post_name):
    blogger = service.GDataService(user, password)
    blogger.source = 'doogie-howser-md'
    blogger.service = 'blogger'
    blogger.account_type = 'GOOGLE'
    blogger.server = 'www.blogger.com'
    blogger.ProgrammaticLogin()
    blog_id = select_blog(blogger)
    
    post = Post(post_name)
    if post.new:
        response = publish_post(blogger, blog_id, post)
    else:
        response = update_post(blogger, blog_id, post)

def publish_post(blogger_service, blog_id, post):
    # get a title for the post
    title = raw_input("Title: ")
    entry = gdata.GDataEntry()
    entry.title = atom.Title('xhtml', title)
    entry.content = atom.Content(content_type='html', text=post.get_html())
    return blogger_service.Post(entry, '/feeds/%s/posts/default' % blog_id)

def update_post(blogger, post):
    pass

def select_blog(blogger_service):
    query = service.Query()
    query.feed = '/feeds/default/blogs'
    feed = blogger_service.Get(query.ToUri())

    print feed.title.text
    for i in xrange(len(feed.entry)):
        print "\t (%d) " % (i+1,) + feed.entry[i].title.text
    selection = int(raw_input("Select blog: ")) - 1
    blog = feed.entry[selection]
    return blog.GetSelfLink().href.split("/")[-1]

def parse_argv():
    parser = argparse.ArgumentParser(description="A CLI blogger client using markdown.")
    parser.add_argument('-u', '--user', help='blogger username', required=True)
    parser.add_argument('-d', '--dir', help='path to posts', required=False, default='posts')
    parser.add_argument('post_file', help='path to markdown file for post')
    args = parser.parse_args()
    return (args.user, args.post_file)

if __name__ == '__main__':
    # parse arguments
    (user, post_file) = parse_argv()
    system('stty -echo')
    password = raw_input("Password: ")
    system('stty echo')
    post_name = post_file.split(".")[0]
    main(user, password, post_name)
