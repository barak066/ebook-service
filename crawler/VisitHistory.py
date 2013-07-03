# -*- coding: UTF-8 -*-

"""
This module contains classes, that provide access to crawler page visits history.
"""


__author__ = 'pxanych'

import time, globalcrawersettings
from crawler.linkFunctions import get_netlock

class VisitHistory(object):
    """
    This class used as interface to crawler page visits history
    """
    def __init__(self, s_file = 'visit_history'):
        """
        Loads last state.
        """
        settings = globalcrawersettings.load_settings('visit_history')
        self._visited_sites = settings.get('_visited_sites', {})

    def save_state(self):
        """
        Dumps current VisitHistory's state to disk.
        """
        settings = dict()
        settings['_visited_sites'] = self._visited_sites
        globalcrawersettings.dump_settings(settings, 'visit_history')

    def set_visited(self, url, weight = 0, timestamp = None ):
        """
        add <url> to page visit history
        """
        if not timestamp:
            timestamp = time.time()
        site_url = get_netlock(url)
        if site_url not in self._visited_sites:
            site_visit_info = SiteVisitInfo()
            self._visited_sites[site_url] = site_visit_info
        else:
            site_visit_info = self._visited_sites[site_url]
        site_visit_info.submit_url(url, weight, timestamp)


    def is_visited_site(self, url):
        return self._visited_sites.get(get_netlock(url), None)

    def is_visited(self, url):
        """
        Check whether visit history contains <url>
        """
        site_url = get_netlock(url)
        if not self._visited_sites.has_key(site_url):
            return None
        siteVisitInfo = self._visited_sites[site_url]
        if siteVisitInfo:
            return  siteVisitInfo.visited_urls.get(url)

    def get_url_timestamp(self, url):
        """
        Get timestamp of last <url> visit
        """
        site_visit_info = self._visited_sites.get(get_netlock(url), None)
        if not site_visit_info:
            return -1
        return site_visit_info.visited_urls.get(url, -1)


class SiteVisitInfo(object):
    """
    Contains information (weights, timestamps) about site visits
    """
    def __init__(self):
        self.avg_weight = 0
        self.visited_urls = {}
        self.last_visit = -1

    def submit_url(self, url, weight, timestamp):
        self.last_visit = timestamp
        prev_avg_weight = len(self.visited_urls) * self.avg_weight
        self.visited_urls[url] = weight, timestamp
        self.avg_weight = (prev_avg_weight + weight) / len(self.visited_urls)











