# -*- coding: UTF-8 -*-
__author__ = 'Павел'


from crawler import PageLoader, Ranker, Scheduler, ResultFilter, Results, VisitHistory
from time import sleep
from KeyWords import KeyWords


def run_crawler(duration = 120):
    KeyWords.load_link_kw()
    pl = PageLoader.PageLoader_v2()
    #pl.add_task(PageLoader.PageLoaderTask('http://bookz.ru/'))
    res = Results.Results()
    rf = ResultFilter.ResultFilter(res)
    rank = Ranker.Ranker(pl, rf)
    visitHistory = VisitHistory.VisitHistory()
    sched = Scheduler.Scheduler(pl, rf, rank, visitHistory, 40)
    rank.active = True
    sched.active = True
    print 'all initialized. Addint start page to PageLoader in 3 seconds'
    #pl.add_task(PageLoaderTask('http://bookz.ru'))
    #print 'added start page'
    print 'now running for %i seconds' % duration
    sleep(duration)
    pl.enter_sleep_mode()
    waited_for = 0
    while (not sched.ready_to_shutdown()) and waited_for < 60:
        waited_for += 1
        sleep(1)
    sched.active = False
    rank.active = False
    sched.save_state()
    pl.save_state()
    res.save_state()
    visitHistory.save_state()
    res.list_sites()

if __name__ == '__main__':
    run_crawler(240)
    print 'profiling stopped'
