#!/usr/bin/python

__description__ = "Test VirtualBox VM."
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

try:
	import vboxapi
except ImportError:
	print('Unable to import VirtualBoxManager')
	sys.exit()

import sys
import os
import time

vbm = VirtualBoxManager('XPCOM', None)
vbox = vbm.vbox
machine = vbox.findMachine('MLVM')
session = vbm.getSessionObject(vbox)
err = IVirtualBoxErrorInfo()
try:
	p = machine.launchVMProcess(session,'gui','')

	while not p.completed:
		p.waitForCompletion(10000)
		vbm.waitForEvents(0)
		print "Wating 10 seconds..."
		time.sleep(10)
	
	session.unlockMachine()
except Exception as e:
	print "Error starting vm: %s" % e
	print "Testing error code: %s" % err.resultCode
	print "Testing error message: %s" % err.text