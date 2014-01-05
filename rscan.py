# -*- coding: utf-8 -*- 

import sys

# # # # # # Socket Function # # # # # # # # 

import socket
import struct

# ip value to ip str
def ipint2str(ipvalue):
	return socket.inet_ntoa(struct.pack("!I",ipvalue))

# ip str to ip value
def ipstr2int(ip):
    return struct.unpack('!I', socket.inet_aton(socket.gethostbyname(ip)))[0]

# # # # # # # # Thread Func # # # # # # # # 

import threading

def thread_proc(runner):
	runner.run()

def open_threads(runner,thread_num):
	runner.still_run = True
	thread_list = []
	try:
		for i in range(thread_num):
			t = threading.Thread(target=thread_proc,args=(runner,))
			t.setDaemon(True)
			t.start()
			thread_list.append(t)
	except:
		pass

	while True:
		try:
			alive = False
			for t in thread_list:
				alive = alive or t.isAlive()
         		if not alive:
             			break
		except KeyboardInterrupt:
			if runner.still_run:
				runner.still_run = False
				sys.stdout.write ('\nAccept Ctrl+C, Quitting...\n')
				sys.stdout.flush()
		except:
			break
	runner.still_run = False

#multi-threads runner

class runner:
	still_run = False
	connector = 0

	#args: start instance in multi-threads
	def __init__(self,connector):
		self.connector = connector
		self.still_run = False

	def run(self):
		while self.still_run:
			if not self.connector():
				break

# # # # # # # # # # # # # # # # # # # # # # # # 

#portchecker: check ports

class portchecker:
	timeout = 0
	ipport_iter = 0
	result = []

	data_mutex = 0
	iter_mutex = 0
	scanned_portnum = 0
	open_portnum = 0

	def __init__(self,ipport_iter,timeout = 5):
		self.ipport_iter = ipport_iter
		self.timeout = timeout
		self.data_mutex = threading.Lock()
		self.iter_mutex = threading.Lock()
		self.result = []

	def find_a_port(self,ip,port,result):
		clean_str = '\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b'
		clean_str += clean_str
		sys.stdout.write ('%s%s                             \n' % (clean_str,result))
		sys.stdout.write ('%sOpen:%d,Scanned:%d                 ' % (clean_str,self.open_portnum,self.scanned_portnum),)
		sys.stdout.flush()
		
	def on_scanning(self,ip,port):
		clean_str = '\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b'
		clean_str += clean_str
		sys.stdout.write ('%sOpen:%d,Scanned:%d                 ' % (clean_str,self.open_portnum,self.scanned_portnum),)
		sys.stdout.flush()

	def connect(self,ip,port):
		s = socket.socket()
		s.settimeout(self.timeout)
		result = ''
		try:
			s.connect((ip,port))
			result = ('%s:%d' % (ip,port))
		except:
			pass
		s.close()
		return result

	def save_result(self,ip,port,report): 
		self.result.append(report)

	def __call__(self):
		# get ip:port from iterator			
		ip = 0
		port = 0
		try:
			self.iter_mutex.acquire()
			ip,port = self.ipport_iter.next()
		except:
			return False
		finally:	
			self.iter_mutex.release()

		self.data_mutex.acquire()
		self.on_scanning(ip,port)
		self.data_mutex.release()

		# link ip:port,get link report
		report = self.connect(ip,port)

		self.data_mutex.acquire()
		self.scanned_portnum += 1
		if report :
			self.open_portnum += 1
			self.find_a_port(ip,port,report)
			self.save_result(ip,port,report)
		self.data_mutex.release()
		return True


# # # # # # # # # # iterator # # # # # # # # # #

'''
list iterator
list of range
list_iter([[1,5],[6,9]]) -> 1 2 3 4 5 6 7 8 9
'''
class list_iter:
	list = 0
	list_iter = 0
	current = 0
	end = 0
	step = 1

	def __init__(self,list):
		self.list = list
		self.reset()

	def __iter__(self):
		return self

	def reset(self):
		self.list_iter = iter(self.list)
		self.current,self.end = self.list_iter.next()

	def next(self):
		if self.current<=self.end:
			current = self.current
			self.current = self.current + self.step
			return current
		else:
			self.current,self.end = self.list_iter.next()
			return self.next()

'''
IP+Port Iterator
Return (ip,port)
'''
class ipport_iter:
	current_ip = 0
	ip_iter = 0
	port_iter = 0

	def __init__(self,ip_iter,port_iter):
		self.ip_iter = ip_iter
		self.port_iter = port_iter
		self.reset()

	def __iter__(self):
		return self

	def reset(self):
		self.ip_iter.reset()
		self.port_iter.reset()
		self.current_ip = self.ip_iter.next()

	def next(self):
		try:
			ret = (ipint2str(self.current_ip),self.port_iter.next())
		except:
			self.current_ip = self.ip_iter.next()
			self.port_iter.reset()
			ret =  (ipint2str(self.current_ip),self.port_iter.next())
		return ret

# # # # # # # # # # # # # # # # # # # # # # 

'''

#range list
#example:

#ip
ips =	
	[
		[ipstr2int('192.168.0.0'),ipstr2int('192.168.0.255') ]
	]

#port 
ports = 
	[
		[80,80]
	]


'''

def iter_factory(ips,ports):
	ip_iter = list_iter(ips)
	port_iter = list_iter(ports)
	return ipport_iter(ip_iter,port_iter)

# # # # # # # # # # # # # # # # # # # # # # 

# use func

s_ips = []
s_ports = []
s_addrlist = []
s_timeout = 5
s_thread = 100
s_result = []

def addip(ipstart_str,ipend_str=''):
	global s_ips
	ipstart = ipstr2int(ipstart_str)
	if ipend_str:
		ipend = ipstr2int(ipend_str)
	else:
		ipend = ipstart
	item = [ipstart,ipend]
	s_ips.append(item)

def readiplist(listfile):
	print 'File',listfile,
	try:
		f = open(listfile,'r')
		print 'Read Success',
	except:
		print 'Read Failed'
		return
	total = 0
	for line in f.readlines():
		if line[-1] == '\n':
			line = line[0:-1]		
		ip1 = 0
		ip2 = 0
		ips_iter = iter(line.split(' '))
		try:
			ip1 = ips_iter.next()
			ip2 = ips_iter.next()
		except:
			ip2 = ip1

		if ip2:
			total += 1
			addip(ip1,ip2)
		else:
			break
	print 'Add',total,'ip range'

def addport(portstart,portend=0):
	global s_ports
	if portend==0:
		portend = portstart
	item = [portstart,portend]
	s_ports.append(item)

import string
def readportlist(listfile):
	print 'File',listfile,
	try:
		f = open(listfile,'r')
		print 'Read Success',
	except:
		print 'Read Failed'
		return
	total = 0
	for line in f.readlines():
		if line[-1] == '\n':
			line = line[0:-1]
		port1 = 0
		port2 = 0
		ports_iter = iter(line.split(' '))
		try:
			port1 = ports_iter.next()
			port2 = ports_iter.next()
		except:
			port2 = port1

		if port2:
			total += 1
			port1 = string.atoi(port1)
			port2 = string.atoi(port2)
			addport(port1,port2)
		else:
			break
	print 'Add',total,'port range'

def addaddr(ip,port):
	global s_addrlist
	item = [ip,port]
	s_addrlist.append(item)

def readaddrlist(listfile):
	print 'File',listfile,
	try:
		f = open(listfile,'r')
		print 'Read Success',
	except:
		print 'Read Failed'
		return
	total = 0
	for line in f.readlines():
		if line[-1] == '\n':
			line = line[0:-1]
		ip = 0
		port = 0
		addr_iter = iter(line.split(':'))
		try:
			ip = addr_iter.next()
			port = addr_iter.next()
		except:
			break

		total += 1
		port = string.atoi(port)
		addaddr(ip,port)
	print 'Add',total,'addr'

def cleanip():
	global s_ips
	s_ips = []

def cleanport():
	global s_ports
	s_ports = []

def cleanaddr():
	global s_addrlist
	s_addrlist = []

def settimeout(value):
	global s_timeout
	s_timeout = value

def setthread(value):
	global s_thread
	s_thread = value

def save(path):
	global s_result
	try:
		print 'File',path,
		output = open(path,'w')
		for s in s_result:
			output.write(s+'\n')
		print 'Save Success'
	except:
		print 'Save Failed'

def status():
	global s_ips,s_ports,s_timeout,s_thread,s_addrlist
	print '\nStatus:'
	print ' ips:'
	for ip1,ip2 in s_ips:
		print '   [\'%s\',\'%s\']' % ( ipint2str(ip1),ipint2str(ip2) )
	print ' ports:'
	for port1,port2 in s_ports:
		print '   [\'%s\',\'%s\']' % ( port1,port2 )
	print ' addrs:'
	for ip,port in s_addrlist:
		print '   [\'%s\':%d]' % ( ip,port )
	print ' Timeout:',s_timeout
	print ' Thread:',s_thread
	print ''

import time
def scan():
	global s_thread,s_timeout,s_ips,s_ports,s_addrlist,s_result

	if (len(s_ips)==0 or len(s_ports)==0) and len(s_addrlist)==0 :
		sys.stdout.write ('You Scan Nothing\n')
		return

	conn1 = 0
	conn2 = 0
	try:
		ipport_iter = iter_factory(s_ips,s_ports)
		conn1 = portchecker(ipport_iter,s_timeout)
	except:
		pass

	if len(s_addrlist):
		conn2 = portchecker(iter(s_addrlist),s_timeout)

	s_result = []

	t =  time.clock()
	if conn1:
		r1 = runner(conn1)
		open_threads(r1,s_thread)
		s_result.extend(conn1.result)
	if conn2:
		r2 = runner(conn2)
		open_threads(r2,s_thread)
		s_result.extend(conn2.result)
	t = time.clock() - t

	sys.stdout.write( '\nTotal Time: %.4lfs\n'%(t) )

def help():
	print '-------Rattlesnake 1.1 By Chaser---------'
	print 'I\'m a Port Scanner in Python (PC or Android)\n'
	print 'usage: python -i me.py\n'
	print '	addip(ip,[endip]): add ip range'
	print '	addport(port,[endport]): add port range'
	print '	addaddr(ip,port): add addr (ip,port)\n'
	print '	readiplist(listfile): read ip list from file'
	print '	readportlist(listfile): read port list from file'
	print '	readaddrlist(listfile): read addr list from file\n'
	print '	cleanip(): clean ip range list'
	print '	cleanport(): clean port range list'
	print '	cleanaddr(): clean addr list\n'
	print '	setthread(value): set thread num'
	print '	settimeout(value): set timeout value\n'
	print '	status(): watch the value you set\n'
	print '	scan(): you can start it if all setting done\n'
	print '	save(filepath): save all your scan to file\n'
	print '	help(): call this page\n'

if __name__ == '__main__':
	help()
