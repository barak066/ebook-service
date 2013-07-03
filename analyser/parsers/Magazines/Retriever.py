# -*- coding: utf-8 -*-

import re
from analyser.core.info.ArticleInfo import ArticleInfo
from analyser.core.info.MagazineInfo import MagazineInfo


class Retriever:
    magazine_name_regexp='[a-z_0-9]+' #magazine id name
    @staticmethod
    def get_links_on_magazines(soup):
        links = soup.findAll('a', onfocus='blur()', href=re.compile('^/%s/$' % Retriever.magazine_name_regexp))
        deprecated = ('/authors/', '/reviews/', '/about/')
        links = [link['href'] for link in links]
        links = list( set(links) )
        return filter(lambda l: l not in deprecated, links)

    @staticmethod
    def get_magazine_info(soup):
        magazine = MagazineInfo()
        magazine.name = soup.find('h1', {'class':'title'}).font.text
        magazine.cover = soup.find('img', src=re.compile('^/image/%s/' % Retriever.magazine_name_regexp))['src']
        magazine.about = soup.find('font', {'class':'story'} ).text
        descriptions = soup.findAll('div', {'class':'soder'})
        magazine.description = reduce(lambda was, a : was+unicode(a.text), descriptions, unicode('') )
        return magazine

    @staticmethod
    def get_links_magazine_issue(soup):
        tds = soup.findAll('td', {'class':'arc_nmtd'})
        anchors = [td.a for td in tds if td.a]
        links = [anchor['href'] for anchor in anchors]
        return links

    @staticmethod
    def get_issue_articles(soup):
        articles = []
        categories = soup.findAll('h3', align='center')
        for category in categories:
            article = ArticleInfo()
            article.category = category.text
            ul = category.findNext('ul', type='disc')
            for li in ul.findAll('li'):
                if li.a and not li.a.has_key('href'):
                    continue
                article = ArticleInfo()
                article.category = category.text
                article.authors = li.b.text if li.b else None
                article.link = li.a['href'] if li.a else None
                article.title = li.a.text if li.a else None
                description =  li.find('i')
                article.description = description.text if description else None
                articles.append(article)
        return articles

    @staticmethod
    def get_issue_year_number_by_link(link):
        m = re.search('/([0-9]{4})/([0-9]+)/$', link)
        year, number = m.groups()
        return year, number

    @staticmethod
    def print_version(link):
        ext = '.html'
        pr = '-pr'
        link_before = link[:-len(ext)]
        return link_before+pr+ext

