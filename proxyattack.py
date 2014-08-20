import rscan

readfile = 'proxylist.txt'
port = 5555

if __name__ == '__main__':
  if rscan.readaddrlist(readfile):
    print 'Waiting data on port',port
    rscan.senddata(rscan.loadport(port))
