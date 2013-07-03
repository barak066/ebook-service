from analyser.tests import helpers_tests
from analyser.tests import OPDS_tests
from analyser.tests import LibRu_tests

def main(argv, **kwargs):
    print 'running tests. If no exception raised, then tests passed right.'
    print
    helpers_tests.run_tests()
    OPDS_tests.run_tests()
    LibRu_tests.run_tests()
    pass