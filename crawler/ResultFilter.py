# -*- coding: UTF-8 -*-
__author__ = 'pxanych'

from crawler.Worker import Worker
from crawler.WorkerTask import WorkerTask
from crawler.linkFunctions import is_html_url, URLParser

class ResultFilter(object):

    def __init__(self, results_class):
        self._rf_worker = Worker()
        self._results_class = results_class
        self.thresholds = [20,1,1]

    def ready_to_shutdown(self):
        return self._rf_worker.ready_to_shutdown()

    def submit_ranker_result(self, rank_result):
        """
        This function is used by Ranker.
        Takes [page_url, page_weight, [(link_soup,weight)]] and passes it to rf_worker
        as
        [page_url, page_weight, [(link_soup,weight)], self.thresholds, self._results_class]
        """
        args = list(rank_result) + [self.thresholds, self._results_class]
        rfw_task = WorkerTask(args, result_filter_routine, args[0])
        self._rf_worker.add_task(rfw_task)

    def get_result(self, filter_match = (lambda x: True)):
        """
        Returns [page_url, page_weight, [(link,weight)]]
        """
        completed_rfw_task = self._rf_worker.get_completed_task(filter_match)
        if completed_rfw_task is None:
            return None
        return completed_rfw_task.result
    
    def purge_tasks(self, filter_not_match):
        """
        Removes all tasks, for which <filter_not_match> returns False.
        """
        self._rf_worker.purge_tasks(filter_not_match)



def result_filter_routine(self, args):
    """
    Searches links/pages with big weight and returns them.
    Also increases weight of page if there is link to book.
    Appends [(url, weight)] to task.result
    """
    file_types = set(['fb2', 'epub'])
    page_url, page_weight, weighted_links, thresholds, result_class = args
    page_threshold, link_threshold, book_link_cnt = thresholds

    ret_links = {}
    for link, weight in weighted_links:
        link_href = link.get('href', None)
        if not link_href:
            continue
        link_tgt_type = link_href.split('.')[-1]
        if link_tgt_type in file_types:
            page_weight += page_threshold / book_link_cnt
            link_url = extract_url_from_link(link_href,page_url)
            result_class.submit_book_link(link_url,page_url)
            continue
        if link.get('rel', None) == 'nofollow':
            continue
        if weight >= link_threshold:
            link_url = extract_url_from_link(link_href,page_url)
            if is_html_url( link_url ):
                old_weight = ret_links.get(link_url, 0)
                ret_links[link_url] = max(old_weight,weight)
    if page_weight >= page_threshold:
        result_class.submit_site(page_url)
    self.result = [page_url, page_weight, ret_links.items()]
    self.complete = True

    
def extract_url_from_link(link_href, page_url):
    return URLParser(link_href).build_url(page_url, True)

