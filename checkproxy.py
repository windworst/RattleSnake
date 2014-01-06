import rscan
import socket

def checkproxy(ip,port):
	result = ''
	get = 'GET http://www.baidu.com/ HTTP/1.1\n\n'
	try:
		s = socket.socket()
		s.settimeout(5)
		s.connect((ip,port))
		s.send(get)
		data = s.recv(8192)
		if 'baidu.com' in data:
			result = '%s:%d' % (ip,port)
	except:
		pass
	return result

def proxyscan():
	host_iter = rscan.host_iterator()
	if not host_iter:
		print 'None Proxy Host'
		return
	conn = rscan.portchecker(host_iter,rscan.s_timeout)
	conn.connect = checkproxy
	rscan.rscanner(conn)

import os
if rscan.readaddrlist('proxylist.txt'):
	proxyscan()
	savepath = 'usableproxy.txt'
	try:
		os.remove(savepath)
	except:
		pass
	rscan.save(savepath)
