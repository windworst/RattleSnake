from rscan import *
import socket 


def getipaddr(ifname):
	# in linux
	import fcntl
	import struct
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(
        	s.fileno(),
	        0x8915,  # SIOCGIFADDR
        	struct.pack('256s', ifname[:15])
	)[20:24])

ip_str = socket.gethostbyname(socket.gethostname())
if '127' in ip_str >=0 :
	try:
		ip_str = getipaddr('eth0')
	except:
		try:
			ip_str = getipaddr('wlan0')
		except:
			pass

print 'Your ip:',ip_str
ipvalue = ipstr2int(ip_str)
ip1 = ipvalue - ipvalue % 256 + 1
ip2 = ip1 + 254
ipstart_str = ipint2str(ip1)
ipend_str = ipint2str(ip2)
print 'Your nat ip range is: %s - %s' % (ipstart_str,ipend_str)
print 'Start RattleSnake!!!!!'
addip(ipstart_str,ipend_str)
addport(21)
addport(23)
addport(80)
addport(135)
addport(139)
addport(1433)
addport(3389)
settimeout(5)
setthread(300)
host()
status()
scan()
current_time = time.strftime('%Y-%m-%d-%H.%M.%S',time.localtime(time.time()))
save(ip_str + '@' + current_time + '.txt')
