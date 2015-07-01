#!/usr/bin/env python3
# TODO: mayoral mentions
# TODO: clipboard integration
# TODO: fetch from feed (probably not rss, too polluted)

import os
import sys
import subprocess
import re
import itertools
import collections
import requests
import codecs
from bs4 import BeautifulSoup

DEBUGMODE = True
bodyLines = 4
outputFile = './output.html'
sources = ['Daily News']


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(itertools.islice(iterable, n))


def parse(source, pageHtml):
    soup = BeautifulSoup(pageHtml)
    if source == 'Daily News':
        headline = soup.find(itemprop="headline").string
        try:
            author = soup.find(rel="author").string
        except AttributeError:
            author = soup.find(id="a-credits").string
        rawBody = soup.find_all('p', limit=bodyLines)
        body = ''
        for i in range(bodyLines):
            body += (rawBody[i].text)
    else:
        raise NameError("The specified 'source' is not valid")
    return headline, author, body


def make_hyperlink(url, text):
    hyperlink = '<a href="' + url + '">' + text + '</a>'
    return(hyperlink)


def output_to_html(source, articles, outFile):
    with codecs.open(outFile, encoding='utf-8', mode='w') as output:
        output.write('<meta charset="utf-8">')
        output.write(source.upper() + '<br><br>')
        for url, article in articles.items():
            output.write(make_hyperlink(article['url'], article['headline']) + ' - ' + article['author'] + '<br>')
        output.write('<br><br>')
        for url, article in articles.items():
            output.write(make_hyperlink(article['url'], article['headline']) + '<br>')
            output.write(source.upper() + ' - ' + article['author'] + '<br>')
            output.write(article['body'] + '<br>')


def output_to_term(source, articles):
    print("\n================================================================================")
    print("--------------------------------- Output ---------------------------------------")
    print("================================================================================")
    print(source.upper() + '\n')
    for url, article in articles.items():
        print(article['headline'] + ' - ' + article['author'])

    print('\n\n')
    for url, article in articles.items():
        print(article['headline'])
        print(source.upper() + ' - ' + article['author'])
        print(article['body'] + '\n')


def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


def prompt_for_source_key(keywords):
    "Prompts for a key from keywords, and returns a string with the selected key"
    sourcePrompt = "Select a source from the following choices: "
    for key in keywords:
        sourcePrompt = sourcePrompt + key + ', '
    sourcePrompt = sourcePrompt[:-2] + '\n'
    source = input(sourcePrompt)
    while source not in keywords:
        print("That's not a valid source!")
        source = input(sourcePrompt)
    return source


def fetch_page(url):
    pageHtml = requests.get(url).text
    return pageHtml


def fetch_and_parse(source, url):
    """Takes a source name and url, and returns a parsed article"""
    article = collections.OrderedDict()
    article['url'] = url
    article['headline'], article['author'], article['body'] = parse(source, fetch_page(url))
    return article


def mode_interactive():
    """Interactive Mode: terminal prompts for a source then repeatedly for a url"""
    #source = prompt_for_source_key(sources)
    source = 'Daily News'
    articles = collections.OrderedDict()

    url = input('\nEnter a URL: ')
    #url = 'http://www.nydailynews.com/news/crime/n-y-prison-break-cool-hand-luke-meets-shawshank-article-1.2275096'
    while url != '':
        try:
            article = fetch_and_parse(source, url)
        except Exception as e:
            print('========= ERROR! =========\nArticle cannot be parsed')
            if (DEBUGMODE):
                print(type(e))
                print(e)
        else:
            articles[url] = article
            print('Got article: "' + articles[url]['headline'] + '"\n')
        url = input("Enter a URL (press enter to end): ")

    #output_to_term(source, articles)
    output_to_html(source, articles, outputFile)
    open_file(outputFile)


def mode_clipboard_watch():
    """Clipboard Watch Mode: watches for a new string on the clipboard, and tries to fetch that URL"""
    pass


def main():
    mode_interactive()


if __name__ == "__main__":
    main()