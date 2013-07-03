import re
import urlparse

def make_correct_link(base, link):
    """
    makes links correct:
        http://... -- pass
        /...       -- adding link to site before
        www. ...   -- adding http:// before
        smth.html  -- adding full path before

        it's planned to be a wrapper over urlparse's functions
        done in order to handle all possible cases of url presentation

        handles absolute url and relative url
        clean up all 'fragments' in url (like http://site.ru/1.html#4 -> http://site.ru/1.html)
    """

    defrag_link, _ = urlparse.urldefrag(link)
    defrag_base, _ = urlparse.urldefrag(base)
    # case 'g.html  on http://ya.ru/a   ==>  http://ya.ru/a/g.html
    # (added slash after a if it's a unslashed folder
    # defining unslashed folder: empty query (like 'a.php?set=1'),
    #                        no  dots
    #                       no closing slash
    scheme, netloc, url, params, query, fragment = urlparse.urlparse(defrag_base)
    if url and not query and not re.search("/$", url) and not re.search("\.", url ):
        url += '/'
        defrag_base = urlparse.urlunparse( (scheme, netloc, url, params, query, fragment) )
    #just  rejoining all parts
    return_link = urlparse.urljoin(defrag_base, defrag_link)
    return return_link

def get_site_root_link(link):
    """
    returns link to site root
    example: http://www.feedbooks.com/catalog.atom => http://www.feedbooks.com
    """
    scheme, netloc, url, params, query, fragment = urlparse.urlparse(link)
    site_link =  scheme + '://' + netloc
    return site_link

def get_url_from_link(link):
    "http://lib.ru/POEZIQ --> POEZIQ"
    scheme, netloc, url, params, query, fragment = urlparse.urlparse(link)
    return url

def check_local_link(site_link, link):
    link_parse = urlparse.urlparse(link.lower())
    sitelink_parse = urlparse.urlparse(site_link.lower())
    return (not link_parse.netloc and not link_parse.scheme) or  link_parse.netloc == sitelink_parse.netloc