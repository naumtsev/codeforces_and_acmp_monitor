from requests import get
from xml.etree import ElementTree





def get_attempts_from_acmp(user_id):
    url = 'http://acmp.ru/index.asp?main=user&id={}'.format(user_id)
    import urllib.request
    res = urllib.request.urlopen(url).read().decode(errors='ignore')
    text = res.split('<b class=btext>')
    #for i in range(len(text)):
    #    print(i, text[i])
    parse = text[4].replace('href=?main=task&id_task=', '').replace('<p class=text>', '').replace('</p>', '').split('</a>')
    solved = []
    for tt in parse:
        numb = ''
        for j in range(len(tt) - 1, -1, -1):
            if tt[j].isdigit():
                numb += tt[j]
            else:
                break
        solved.append(numb[::-1])
    del solved[-1]
    return solved


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