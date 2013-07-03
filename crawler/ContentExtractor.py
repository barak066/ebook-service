#!/usr/bin/python

from lib.BeautifulSoup import BeautifulSoup

def replace_chars( string, from_chars, to_char ):
    return reduce( lambda s,c: (c in from_chars) and (s + to_char) or (s + c), string, '' )


def extract_mapped_content_list( body_soup ):
    if type(body_soup) != BeautifulSoup.Tag:
        raise TypeError
    return _extract_mapped_content_list(body_soup, 0, [''], [])[1:]


def _extract_mapped_content_list( body_soup, counter, cl, l ):
    for element in body_soup.contents:
        if type(element) == BeautifulSoup.NavigableString:
            if type(cl[-1]) == int:
                cl[-1] = str(cl[-1])
            cl[-1] += replace_chars(element, '\n\t-:,.?!()', ' ')
        if type(element) == BeautifulSoup.Tag:
            if element.name == 'a':
                cl.append(counter)
                cl.append('')
                l.append(element)
                counter += 1
            counter = _extract_mapped_content_list( element, counter, cl, l )[0]
    return counter, cl, l

def extract_raw_text( soup ):
    text = ''
    for element in soup.contents:
        if type(element) == BeautifulSoup.NavigableString:
            text += element
        if type(element) == BeautifulSoup.Tag:
            text += extract_raw_text(element)
    return text

