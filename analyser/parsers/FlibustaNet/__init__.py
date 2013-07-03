# -*- coding: utf-8 -*-

import re
from analyser.adds.OpenerHolder import OpenerHolder
from analyser.core.tasking.download_managers import WaitingDM

from tasks import InitialTask



class FlibustaNet:
    "site: flibusta.net"

    def __init__(self):
        self.site_link = 'http://flibusta.net/'
        self.initial_task = InitialTask()

    def get_filename(self):
        return r'flibusta_net'

    def generate_auth_data(self,user,password):
        data = {'name' : user,
                'pass' : password,
                'persistent_login' : '1',
                'form_id' : 'user_login_block'
                }
        return data


class AuthDM(WaitingDM):
    def __init__(self, site_link, auth_data):
        self.opener = OpenerHolder(auth_data,site_link)
    def get_page(self, link):
        return self.opener.urlopen(link)