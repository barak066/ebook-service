"Checks request type, requester IP, etc"

from settings import ANALYZER_IP

from spec.exception import RequestServerException


def check_ip(request):
    """Checks requester IP, valide IPs are defined in settings.py
    Raises exception if IP is not valide"""
    if ANALYZER_IP and request.META['REMOTE_ADDR'] != ANALYZER_IP:
        raise RequestServerException('Bad IP adress. Your IP is %s' %
                                        (request.META['REMOTE_ADDR']))


def get_xml_request(request):
    "Checks request type. Returns xml_request or raises exception if error."
    if request.method != 'POST':
        raise RequestServerException('Use POST method in request')
    if not 'xml' in request.POST:
        raise RequestServerException("Not found xml field in POST request")

    return request.POST['xml']
