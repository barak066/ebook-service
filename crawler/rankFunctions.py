import Stemmer, re
from ContentExtractor import extract_raw_text
from crawler.KeyWords import KeyWords
stemmer = Stemmer.Stemmer('russian')

def page_useful_link_koef(links, threshold):
    """
    Get the percentage of good links in <links> list.
    Good links - links with weight >= threshold
    <links> is [(link, weight)]
    <threshold> is int
    return type is float
    """
    good_count = float(0)
    for link, weight in links:
        if weight >= threshold:
            good_count += 1
    return good_count / len(links)

def compare_pages(page1, page2):
    """
    Get the similarity coefficient of two pages.
    """
    pattern = re.compile(u'\W+', re.UNICODE)
    words1 = {}
    words2 = {}
    raw_text1 = extract_raw_text(page1)
    raw_text2 = extract_raw_text(page2)
    total_w_count1 = 0
    total_w_count2 = 0
    for w in re.split(pattern, raw_text1):
        if len(w) > 3 and w in KeyWords.words:
            w = w.encode('utf8')
            w = stemmer.stemWord(w.lower())
            words1[w] = words1.get(w, float(0)) + 1
            total_w_count1 += 1
    for w in re.split(pattern, raw_text2):
        if len(w) > 3 and w in KeyWords.words:
            w = w.encode('utf8')
            w = stemmer.stemWord(w.lower())
            words2[w] = words2.get(w, float(0)) + 1
            total_w_count2 +=1
    similarity = float(0)
    for word1, count1 in words1.items():
        count1 /= total_w_count1
        count2 = words2.get(word1, 0) / total_w_count2
        avg_count = (count1 + count2) / 2
        similarity += avg_count - abs(count1 - count2)
    return similarity