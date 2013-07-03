from analyser.adds.helpers import make_correct_link

def make_correct_link_test():
    print "helper_tests: make correct link test"
    assert make_correct_link('http://ya.ru/a/', 'g.html') == 'http://ya.ru/a/g.html'
    assert make_correct_link('http://ya.ru/', 'g.html')  == 'http://ya.ru/g.html'
    assert make_correct_link('http://ya.ru/a', 'g.html')  == 'http://ya.ru/a/g.html'
    assert make_correct_link('http://ya.ru/a?set=1', 'g.html')  == 'http://ya.ru/g.html'
    assert make_correct_link('http://ya.ru/a.php', 'g.html')  == 'http://ya.ru/g.html'
    assert make_correct_link('http://ya.ru/vehicles/', 'http://www.a.ru/g.html')  == 'http://www.a.ru/g.html'
    assert make_correct_link('http://ya.ru/vehicles/', '/a.html') ==  'http://ya.ru/a.html'
    assert make_correct_link('http://ya.ru/vehicles/', 'http://www.org.ru/a.html')  == 'http://www.org.ru/a.html'
    assert make_correct_link('http://ya.ru/vehicles/','https://www.org.ru/a.html')  == 'https://www.org.ru/a.html'
    assert make_correct_link('http://www.epubbooks.ru/stanza/index.xml', 'xmllastadd.php')  == 'http://www.epubbooks.ru/stanza/xmllastadd.php'
    assert make_correct_link('http://www.stanza.epubbooks.ru/stanza/genres/0.xml', '../../tpl/download.php?npp=3376') == 'http://www.stanza.epubbooks.ru/tpl/download.php?npp=3376'
    assert make_correct_link('http://www.stanza.epubbooks.ru/stanza/genres/0.xml', '../../tpl/download.php?npp=3376') == 'http://www.stanza.epubbooks.ru/tpl/download.php?npp=3376'

def run_tests():
    make_correct_link_test()
