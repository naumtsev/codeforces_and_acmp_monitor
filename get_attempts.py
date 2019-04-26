#!/usr/bin/python
# -*- coding: utf-8 -*-
from requests import get
import bs4


def get_attempts_from_acmp(user_id):
    # Раскоментить, когда будете ставить на свой хостинг

    url = 'http://acmp.ru/index.asp?main=user&id={}'.format(user_id)
    res = get(url).text.encode().decode('ascii', errors='ignore')
    solved = []

    dom = bs4.BeautifulSoup(res, 'lxml').find_all(class_='text')[0].find_all('a')
    for ex in dom:
        solved.append(ex.next_element)
    return solved

    return []


def get_attempts_from_codeforces(handle):

    map_request = 'http://codeforces.com/api/user.status?handle={}'.format(handle)
    attempts = []
    request = get(map_request).json()
    if request['status'] != 'OK':
        return attempts
    for i in request['result']:
        attempt = i['problem']
        contestId = attempt['contestId']
        index = attempt['index']
        if(i['verdict'] == 'OK'):
            attempts.append(str(contestId) + index)
    return attempts


get_attempts_from_acmp(211586)