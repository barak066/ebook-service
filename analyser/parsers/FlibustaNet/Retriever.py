# -*- coding: utf-8 -*-

import re
from analyser.adds.helpers import make_correct_link
from analyser.adds import logger

class Retriever:

    @staticmethod
    def get_summary(soup):
        annotation_text = soup.find('h2',text=u'Аннотация')
        annotation_tag = annotation_text.parent
        paragraph_with_summary = 1;
        p_with_summary = annotation_tag.findNextSiblings('p')
        if len(p_with_summary) < 2:
            return None
        p_with_summary = p_with_summary[paragraph_with_summary]
        # check on case with empty annotation:
        ch = p_with_summary.findChildren()
        if ch:
            if ch[0].name == u'a':
                return None
        return p_with_summary.text

    @staticmethod
    def get_links(soup, page_link):
        links = {}
        select = soup.find('select', id='useropt')
        if select:
            format_options = select.findAll('option')
            formats = []
            for format_option in format_options:
                formats.append(format_option['value'])
            for format in formats:
                link = "%s/%s" % (page_link, format)
                links[format] = make_correct_link(page_link, link)
        else:
            number = Retriever.get_booknumber_from_link(page_link)
            anchors = soup.findAll('a', href=re.compile('/b/%s/[A-z]+$' % number ))
            anchors = filter(Retriever.is_available_anchor, anchors)
            for link in anchors:
                format = Retriever.get_format_from_anchor(link)
                correct_link = make_correct_link(page_link, link['href'])
                links[format] =  correct_link
        return links

    @staticmethod
    def is_available_anchor(anchor):
        unavailable = ('forum','read','edit','complain')
        m = re.search('/b/[0-9]+/([A-z]+)', anchor['href'])
        if not m:
            return False
        format = m.groups()[0]
        if format in unavailable:
            return False
        return True

    @staticmethod
    def get_format_from_anchor(anchor):
        m = re.search('/b/[0-9]+/([A-z]+)', anchor['href'])
        format = m.groups()[0]
        if format == 'download':
            format = anchor.text.split()[1]
            format = format[:-1] #clean up from  ')'
        return format

    @staticmethod
    def get_booknumber_from_link(link):
        m = re.search('/b/([0-9]+)', link)
        number = m.groups()[0]
        return number

    @staticmethod
    def get_tags(soup):
        tags = [ anchor_tag.text for anchor_tag in soup.findAll('a', {"class":"genre"})]
        return tags

    @staticmethod
    def get_picture_link(soup):
        img = soup.find('img', src=re.compile('/i/[0-9\/]+cover.jpg$'))
        if not img:
            return None
        return img['src']

    @staticmethod
    def get_picture(soup,page_link, id):
        img_link = Retriever.get_picture_link(soup)
        if not img_link:
            return None
        img_link = make_correct_link(page_link,img_link)
        return img_link

    @staticmethod
    def read_description(description_line):
        description = {}
        #Last Name;First Name;Middle Name;Title;Subtitle;Language;Year;Series;ID
        field_list = ['lastname', 'firstname', 'middlename', 'title', 'subtitle', 'language','year',' series', 'ID' ]
        line = description_line[:-1] #remove \n from the end of line
        descr_list = line.split(';')
        if len(descr_list) != len(field_list):
           descr_list = Retriever.processing_describe_list(descr_list)
        for number, field in enumerate(field_list):
           description[field] = descr_list[number]
        return description

    @staticmethod
    def processing_describe_list(descr_list):
        length = len(descr_list)
        if length >=9:
            #    0                    1               2           3      4         5             6    7       8
            #Last Name;First Name;Middle Name;Title;Subtitle;Language;Year;Series;ID
            descr_list[3] = ";".join(descr_list[3:-5])  # split all part of title togehter
            descr_list[4:] = descr_list[-5:length] # subtitle, language, year, series, ID <---
            descr_list = descr_list[0:9]     # cutting to right number of fields
        return descr_list