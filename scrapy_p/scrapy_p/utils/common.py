# -*- coding: utf-8 -*-
__author__ = "kisan"
import hashlib

def get_md5(url):
    """
    need to encode unicode to utf-8
    :param url:
    :return:
    """
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()
