# -*- coding: utf-8 -*- 
#DONE: 2014/1/1, "tail" of "Snake" year (2013)
#It's first day I learn Python

import socket
import struct
import threading
import sys

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
			ret = (self.current_ip,self.port_iter.next())
		except:
			self.current_ip = self.ip_iter.next()
			self.port_iter.reset()
			ret =  (self.current_ip,self.port_iter.next())
		return ret

# # # # # # Socket Function # # # # # # # # 

# ip value to ip str
def ipint2str(ipvalue):
	return socket.inet_ntoa(struct.pack("!I",ipvalue))

# ip str to ip value
def ipstr2int(ip):
    return struct.unpack('!I', socket.inet_aton(socket.gethostbyname(ip)))[0]

# # # # # # # # Thread Func # # # # # # # # 

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


# # # # # # # # scanner # # # # # # # # # # 


#connector: need function connect(ip,port),return link report

class simple_connector:
	timeout = 5
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

#scanner

class scanner:
	ipport_iter = 0
	result = []
	still_run = False
	connector = 0
	
	data_mutex = threading.Lock()
	iter_mutex = threading.Lock()
	scanned_portnum = 0
	open_portnum = 0

	#args:	ipport_iter:get ip:port
	#		connector: need function connect(ip,port),return link report
	def __init__(self,ipport_iter,connector):
		self.ipport_iter = ipport_iter
		self.connector = connector

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

	def save_result(self,ip,port,report): 
		self.result.append(report)

	def run(self):
		while self.still_run:
			# get ip:port from iterator			
			try:
				self.iter_mutex.acquire()
				ip,port = self.ipport_iter.next()
				ip_str = ipint2str(ip)
			except:
				break
			finally:	
				self.iter_mutex.release()

			if not self.still_run:
				break
			
			self.data_mutex.acquire()
			self.on_scanning(ip_str,port)
			self.data_mutex.release()
			
			# link ip:port,get link report
			report = self.connector.connect(ip_str,port)

			if not self.still_run:
				break
				
			self.data_mutex.acquire()
			self.scanned_portnum += 1
			if report :
				self.open_portnum += 1
				self.find_a_port(ip_str,port,report)
				self.save_result(ip_str,port,report)
			self.data_mutex.release()

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

def scanner_factory(ips,ports,connector):
	ip_iter = list_iter(ips)
	port_iter = list_iter(ports)
	addr_iter = ipport_iter(ip_iter,port_iter)
	return scanner(addr_iter,connector)

# # # # # # # # # # # # # # # # # # # # # # 

# use func

s_ips = []
s_ports = []
s_timeout = 5
s_thread = 100
s_result = []
s_connector = simple_connector()

def addip(ipstart_str,ipend_str=''):
	global s_ips
	ipstart = ipstr2int(ipstart_str)
	if ipend_str:
		ipend = ipstr2int(ipend_str)
	else:
		ipend = ipstart
	item = [ipstart,ipend]
	s_ips.append(item)

def addport(portstart,portend=0):
	global s_ports
	if portend==0:
		portend = portstart
	item = [portstart,portend]
	s_ports.append(item)

def cleanip():
	global s_ips
	s_ips = []

def cleanport():
	global s_ports
	s_ports = []

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
	global s_ips,s_ports,s_timeout,s_thread
	print '\nStatus:'
	print ' ips:'
	for ip1,ip2 in s_ips:
		print '   [\'%s\',\'%s\']' % ( ipint2str(ip1),ipint2str(ip2) )
	print ' ports:'
	for port1,port2 in s_ports:
		print '   [\'%s\',\'%s\']' % ( port1,port2 )
	print ' Timeout:',s_timeout
	print ' Thread:',s_thread
	print ''

import time
def scan():
	global s_thread,s_timeout,s_ips,s_ports,s_result,s_connector
	s_connector.timeout = s_timeout
	try:
		s = scanner_factory(s_ips,s_ports,s_connector)
	except:
		sys.stdout.write ('IP/PORT Setting Error\n')
	s.timeout = s_timeout
	t =  time.clock()
	open_threads(s,s_thread)
	t = time.clock() - t
	s_result = s.result
	sys.stdout.write( '\nTotal Time: %.4lfs\n'%(t) )

def help():
	print '-------Rattlesnake 1.0 By Chaser---------'
	print 'I\'m a Port Scanner in Python (PC or Android)\n'
	print 'usage: python -i me.py\n'
	print '	addip(ip,[endip]): add ip range'
	print '	addport(port,[endport]): add port range\n'
	print '	cleanip(): clean ip range list'
	print '	cleanport(): clean port range list\n'
	print '	setthread(value): set thread num'
	print '	settimeout(value): set timeout value\n'
	print '	status(): watch the value you set\n'
	print '	scan(): you can start it if all setting done\n'
	print '	save(filepath): save all your scan to file\n'
	print '	help(): call this page\n'

if __name__ == '__main__':
	help()
