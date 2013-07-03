# -*- coding: utf-8 -*-
from classifier_settings import *
from book.models import *
from classifier import *
from recommendator import *
from datetime import datetime
from django.db.models import Q


MAX_NUM = 1
MAX_DIFF = 1.1

class MyInt:
    def __init__(self):
        self.value = 0

class Tag_manager:
    '''
    Used for classification annotations from database
    '''

    def __init__(self):
        self.data = {}
        self.pairdata = {}
        self.genredata = {}
        read_stopwords()

    def get_cls(self, queryset, analyzer, dbug):
        temp = {}
        tnum = 0
        for current in queryset:
            analyzer.data = ''
            analyzer.words = []
            analyzer.read_string(current.name)
            analyzer.get_words()
            for w in analyzer.words:
                cur = temp.get(w, 0)
                temp[w] = cur + 1
            tnum += 1
            if dbug and not tnum % 1000:
                print tnum
        cls = {}
        if dbug:
            print 'creating classifiers for ', len(temp)
        tnum = 0
        for w in temp.keys():
            cl = Classifier()
            cl.set_data(temp[w], queryset.count())
            cls[w] = cl
            tnum += 1
            if dbug and not tnum % 100000:
                print tnum
        return cls

    def get_all_annotations(self, lng):
        print 'getting all annotations...'
        tempdata = Annotation.objects.filter(Q(Q(book__lang = lng) & ~Q(book__pagelink__contains="zhurnal.lib.ru")))
        print lng
        print 'number is', tempdata.count()
        TA = TextAnalyzer()
        PA = PairAnalyzer()
        print 'single words...'
        self.data[''] = self.get_cls(tempdata, TA, True)
        print 'pairs...'
        self.pairdata[''] = self.get_cls(tempdata, PA, True)

    def get_tag_annotations(self, tag, lng):
        print 'getting annotations for', tag
        tempdata = Annotation.objects.filter(Q(Q(book__lang=lng, book__tag__name=tag) & ~Q(book__pagelink__contains="zhurnal.lib.ru")))
        print 'number is', tempdata.count()
        TA = TextAnalyzer()
        PA = PairAnalyzer()
        self.data[tag] = self.get_cls(tempdata, TA, False)
        self.pairdata[tag] = self.get_cls(tempdata, PA, False)

    def get_data(self, lng):
        '''
        Obtains all necessary data
        '''
        genres = Tag.objects.filter(credit=1).order_by("name")
        self.get_all_annotations(lng)
        for tag in genres:
            self.get_tag_annotations(tag.name, lng)

    def recursive_recommend(self, curr, ids, step, num):
        print step, len(curr)
        if step != 0 and len(curr):
            print sorted(curr[curr.keys()[0]], key = curr[curr.keys()[0]].get, reverse = True)[step-1]
        stop = False
        nexts = {}
        if step == (20 - 1) or len(curr) < 100:
            stop = True
        if not stop:
            for i in ids:
                nexts[i] = {}
                for cid in curr:
                    if sorted(curr[cid], key = curr[cid].get, reverse = True)[step] == i:
                        (nexts[i])[cid] = curr[cid]
            for i in ids:
                self.recursive_recommend(nexts[i], ids, step + 1, num)
        else:
            for cid1 in curr:
                rrecs = {}
                recs = {}
                for cid2 in curr:
                    if (cid1 != cid2):
                        rrecs[cid2] = recommend(curr[cid1], curr[cid2])
                for recid in (sorted(rrecs, key = rrecs.get, reverse = True)[0:10]):
                    if rrecs[recid] > 0:
                        recs[recid] = rrecs[recid]
                a1 = Annotation.objects.get(id=cid1)
                print a1.book.id
                a1.book.similar.clear()
                for recid in recs:
                    rec = Annotation.objects.get(id=recid)
                    a1.book.similar.add(rec.book)
                a1.book.save()
                num.value += 1
#                if num.value % 5 == 0:
#                    print num.value


    def check_all(self, lng, change):
        '''
        Checks all annotations from database
        '''
        print 'checking...'
        annotations = Annotation.objects.filter(Q(Q(book__lang = lng) & ~Q(book__pagelink__contains="zhurnal.lib.ru")))
        now = datetime.now()
        outp = open('output.txt','w')
        changelog = open('changes.log','a')
        cantlog = open('fail.log','a')
        outp.write('\n******************\n')
        outp.write(str(now))
        outp.write('\n******************\n')
        changelog.write('\n******************\n')
        changelog.write(str(now))
        changelog.write('\n******************\n')
        cantlog.write('\n******************\n')
        cantlog.write(str(now))
        cantlog.write('\n******************\n')
        num = 0
        rightnum = 0
        self.genredata = {}
        for a in annotations:
            tags = {}
            pre_tags = {}
            if len(a.name) > 80:
                pre_tags = self.find_tags(a.name, lng)
            temptags = {}
            for tag in (sorted(pre_tags, key = pre_tags.get, reverse = True))[0:20]:
                if ((pre_tags[tag] * MAX_DIFF) >= pre_tags[sorted(pre_tags, key = pre_tags.get, reverse = True)[0]]):
                    tags[tag] = pre_tags[tag]
                temptags[tag] = pre_tags[tag]
            if len(tags) > MAX_NUM:
                tags = {}
            if len(temptags):
                self.genredata[a.id] = temptags
            name = a.book.title
            authors = a.book.author.all()
            genres = a.book.tag.all()
            for author in authors:
                outp.write(author.name.encode('UTF-8'))
                outp.write(', ')
            outp.write('- ')
            outp.write(name.encode('UTF-8'))
            outp.write(' ')
            outp.write(str(a.book.id))
            outp.write(':')
            outp.write('\n')
            for genre in genres:
                outp.write(genre.name.encode('UTF-8'))
                outp.write('\n')
            for tag in sorted(tags, key = tags.get, reverse = True):
                prob = tags[tag]
                outp.write(str(prob))
                outp.write(' - ')
                outp.write(tag.encode('UTF-8'))
                outp.write('\n')
            if tags != {}:
                for tag in tags:
                    current_tag = Tag.objects.get(name=tag)
                    if current_tag not in genres:
                        if change:
                            a.book.tag.add(current_tag)
                            a.save()
                        changelog.write('''Added tag "''')
                        changelog.write(tag.encode('UTF-8'))
                        changelog.write('''" for book: ''')
                        for author in authors:
                            changelog.write(author.name.encode('UTF-8'))
                            changelog.write(''', ''')
                        changelog.write(name.encode('UTF-8'))
                        changelog.write('''\n''')
                        changelog.flush()
            else:
                cantlog.write('failed to classify ')
                cantlog.write(name.encode('UTF-8'))
                cantlog.write('''\n''')
                cantlog.flush()
            num += 1
            outp.write('\n')
            if num % 10 == 0:
                outp.flush()
                print num
        outp.close()
        changelog.close()
        cantlog.close()
        ids = sorted(self.data.keys())
        self.data = {}
        self.pairdata = {}
        num = MyInt()
        self.recursive_recommend(self.genredata, ids, 0, num)

    def find_tags(self, text, lng):
        '''
        Obtains tag list for annotation
        '''
        TA = TextAnalyzer()
        TA.read_string(text)
        TA.lang = lng
        TA.get_words()
        PA = PairAnalyzer()
        PA.read_string(text)
        PA.lang = lng
        PA.get_words()
        wordstats = TA.words
        pairstats = PA.words
        sumweights = {}
        sumprobs = {}
        psumweights = {}
        psumprobs = {}
        tags = []
        RESULT = {}
        for tag in self.data:
            if (tag != '') and (len(self.data[tag]) > 5):
                tags.append(tag)
                sumweights[tag] = 0.0
                sumprobs[tag] = 0.0
                psumweights[tag] = 0.0
                psumprobs[tag] = 0.0

        for w in wordstats:
            temp = self.check_tags_word(tags, w)
            for tag in tags:
                tagresult = temp[tag]
                sumweights[tag] += tagresult[1]
                sumprobs[tag] += tagresult[0] * tagresult[1]

        for w in pairstats:
            temp = self.check_tags_pair(tags, w)
            for tag in tags:
                tagresult = temp[tag]
                psumweights[tag] += tagresult[1]
                psumprobs[tag] += tagresult[0] * tagresult[1]

        for tag in tags:
            if psumweights[tag] == 0:
                if sumweights[tag] == 0:
                    RESULT[tag] = -1
                else:
                    RESULT[tag] = (sumprobs[tag] / sumweights[tag])
            else:
                RESULT[tag] = ((sumprobs[tag] / sumweights[tag])*len(wordstats) + (psumprobs[tag] / psumweights[tag])*len(pairstats)) / (len(wordstats) + len(pairstats))
        return RESULT

    def check_tags_word(self, tags, word):
        '''
        Something here
        '''
        alldata = self.data['']
        allcl = alldata.get(word, None)
        data = {}
        for tag in tags:
            tagdata = self.data[tag]
            tagcl = tagdata.get(word, None)
            data[tag] = getProbability(tagcl, allcl)
        return data

    def check_tags_pair(self, tags, pair):
        '''
        Something here
        '''
        alldata = self.pairdata['']
        allcl = alldata.get(pair, None)
        data = {}
        for tag in tags:
            tagdata = self.pairdata[tag]
            tagcl = tagdata.get(pair, None)
            data[tag] = getProbability(tagcl, allcl)
        return data


