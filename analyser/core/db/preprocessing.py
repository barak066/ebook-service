# -*- coding: utf-8 -*-
import re

from analyser.adds import logger

def preprocess_bookinfo(bookinfo):
    bookinfo.title = preprocess_title(bookinfo.title)
    bookinfo.authors = preprocess_authors(bookinfo.authors)
    bookinfo.pagelink = preprocess_pagelink(bookinfo.pagelink)
    bookinfo.language = preprocess_language(bookinfo.language)
    bookinfo.summary = preprocess_summary(bookinfo.summary)
    bookinfo.links = preprocess_links(bookinfo.links)
    bookinfo.tags = preprocess_tags(bookinfo.tags)
    return bookinfo

def preprocess_string(s):
    return s.strip(" ,.")

def preprocess_tags(tags):
    new_tags = []
    for tag in tags:
        new_tags.append( preprocess_tag(tag) )
    return new_tags

def preprocess_tag(tag):
    processed = tag.lower()
    processed = processed.strip()
    processed = re.sub(r"\n", r" ", processed)
    processed = re.sub(r"\s+", r" ", processed)
    processed = re.sub(r"\"", r"", processed)
    return processed

def preprocess_authors(authors):
    new_authors = []
    splitted_authors = []
    for author in authors:
        for author2 in  author.split(','):
            for author3 in  author2.split(';'):
                splitted_authors.append(author3)
    new_authors += [ preprocess_author(a) for a in splitted_authors]
    new_authors = filter( lambda author: author, new_authors)
    return new_authors

def preprocess_author(author):
    author = author.strip()
    m = re.match("Author:(.+)",author)
    if m and m.groups(0):
        author = m.groups(0)[0]
    author = author.strip()
#    m = re.match(u"Автор:(.+)",author)
#    if m and m.groups(0):
#        author = m.groups(0)[0]
    return author

def preprocess_title(title):
    processed = re.sub(r"_", r" ", title)
    processed = re.sub(r"\s+", r" ", processed)
    processed = processed.lstrip(', .')
    processed = processed.rstrip(', ')
    return processed.strip()

def preprocess_pagelink(pagelink):
    return pagelink.strip()

def preprocess_language(language):
    language = language.lower()
    variants = { u"рус" : "ru", \
                 u"rus" : "ru", \
                 u"eng" : "en", \
                 u"esp" : "es", \
                 u"fre" : "fr", \
               }
    if language in variants:
        language = variants[language]
    if language != '?' and len(language) != 2:
        logger.to_file('lang_processing', 'can not preprocess language', lang=language)
        language = '?'
    return language

def preprocess_summary(summary):
    if summary:
        summary =  summary.strip()
    return summary

def preprocess_links(links):
    new_links = {}
    for format, link in links.items():
        format = format.lower().strip()
        new_links[format] = link.strip()
    return new_links

