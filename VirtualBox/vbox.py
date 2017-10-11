#!/usr/bin/python

__description__ = "Class to support VirtualBox functionality"
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"

"""

Code excerpts provided by VirtualBox:
download.virtualbox.org/virtualbox/SDKRef.pdf

Other material referenced:
https://github.com/cuckoosandbox/cuckoo

"""

try:
	import vboxapi
except ImportError:
	print('Unable to import VirtualBoxManager')
	sys.exit()

import sys
import os
import time
import logging

#create logger
logger = logging.getLogger('autovb.vbox')

#TODO: fix documentation
#TODO: add separate logger for events logging

class VBoxAuto:
	def __init__(self, vm):
		self.vmname = vm
		self.ctx = {}
		self.mach = None
		self.uuid = None
	
	def init(self):
		vbm = vboxapi.VirtualBoxManager('XPCOM', None)
		
		self.ctx = {'global': vbm,
					'vb'	: vbm.vbox,
					'mgr'	: vbm.mgr,
					'const'	: vbm.constants,
					'guest'	: None} # console.guest unavailable until VM started
		try:
			self.mach = self.ctx['vb'].findMachine(self.vmname)
			self.uuid = self.mach.id
			logger.info('Using %s (uuid: %s)', self.vmname, self.uuid)
			return True
		except Exception as e:
			logger.exception('Cannot find registered machine: %s. Error: %s', self.vmname, e)
			return False
	
	def start(self):
		session = self.ctx['global'].getSessionObject(self.ctx['vb'])
		try:
			print "Launching new vm..."
			p = self.mach.launchVMProcess(session, 'gui', '')
			print "Waiting for process completion"
			ph = progressHandler(self.ctx, p)
			if ph and int(p.resultCode) == 0:
				print "Vm started successfully..."
				self.ctx['guest'] = session.console.guest
				# now that we have active "console", deploy passive, aggregate listener for the following events
				listen(ctx,[OnMachineStateChanged,OnStateChanged,OnSnapshotRestored,OnSnapshotTaken,OnSharedFolderChanged,OnGuestSessionRegistered,
				OnGuestSessionStateChanged,OnGuestProcessRegistered,OnGuestProcessStateChanged,OnGuestUserStateChanged,OnGuestFileRegistered,
				OnGuestFileStateChanged,OnGuestFileRead,OnGuestFileWrite,OnGuestProcessOutput,OnRuntimeError])
		except Exception as e:
			logger.exception('Cannot launch vm. Error: %s', e)
		
		session.unlockMachine()

	def stop(self):
		session = self.ctx['global'].getSessionObject(self.ctx['vb'])
		try:
			p = session.console.powerDown()
			progressHandler(self.ctx, p)
			self.ctx['global'].closeMachineSession(session)
			logger.info('VM powered down; session closed.')
		except Exception as e:
			logger.exception('Error shutting down the vm. Error: %s', e)

	def snapshot(self, name):
		session = self.ctx['global'].getSessionObject(self.ctx['vb'])
		try:
			self.mach.lockMachine(session, self.ctx['const'].LockType_Shared)
		except Exception as e:
			logger.exception('Error locking machine for snapshot. Error: %s', e)
		
		try:
			(p,uuid) = session.machine.takeSnapshot(name,'',True)
			progressHandler(self.ctx, p)
			logger.info('Offline snapshot completed.')
		except Exception as e:
			logger.exception('Error taking initial snapshot. Error: %s', e)
		
		session.unlockMachine()
	
	def revert(self, name):
		session = self.ctx['global'].getSessionObject(self.ctx['vb'])
		logger.info('Restoring clean image.')
		try:
			self.mach.lockMachine(session, self.ctx['const'].LockType_Shared)
		except Exception as e:
			logger.exception('Error locking machine to revert. Error: %s', e)
		
		try:
			snap = self.mach.findSnapshot(name)
			p = session.machine.restoreSnapshot(snap)
			ph = progressHandler(self.ctx, p, 5000)
			if ph and int(p.resultCode) == 0:
				logger.info('VM reverted to "%s".', name)
		except Exception as e:
			logger.exception('Error restoring snapshot. Error: %s', e)
		
		session.unlockMachine()
		
	# add read-only share named 'temp' to VM
	def addShare(self, hostshare):
		session = self.ctx['global'].getSessionObject(self.ctx['vb'])
		
		try:
			self.mach.lockMachine(session, self.ctx['const'].LockType_Shared)
		except Exception as e:
			logger.exception('Error locking machine to add share. Error: %s', e)
		
		try:
			# creates share, but on CentOS automount not working; must manually mount via
			# sudo mount -t vboxsf -o ro temp /media/sf_temp
			# creates share on Windows under \\VBOXSVR\temp
			session.console.createSharedFolder('temp', hostshare, False, True)
			logger.info('Created temporary read-only share folder.')
		except Exception as e:
			logger.exception('Error creating temporary share folder. Error: %s', e)
		
		session.unlockMachine()
	
	def removeShare(self):
		session = self.ctx['global'].getSessionObject(self.ctx['vb'])
		
		try:
			self.mach.lockMachine(session, self.ctx['const'].LockType_Shared)
		except Exception as e:
			logger.exception('Error locking machine to remove share. Error: %s', e)
		
		try:
			# removes share, but on CentOS must manually unmount via
			# sudo umount /media/sf_temp
			session.console.removeSharedFolder('temp')
			logger.info('Removed share folder.')
		except Exception as e:
			logger.exception('Error removing share folder. Error: %s', e)
		
		session.unlockMachine()

	def execInGuest(self, exe, args):
		session = self.ctx['global'].getSessionObject(self.ctx['vb'])
		try:
			self.mach.lockMachine(session, self.ctx['const'].LockType_Shared)
		except Exception as e:
			logger.exception('Error locking machine for guest process. Error: %s', e)
			
		try:
			guestSession = self.ctx['guest'].createSession('user','pass','','internal_exec')
			guestSession.waitFor(self.ctx['const'].GuestSessionWaitForFlag_Start,0)
			logger.info('Session %s started w/ id %s. Session status: %s', guestSession.name, guestSession.id, getEnumValue(self.ctx, "GuestSessionStatus", guestSession.status))
			logger.info('Executing %s with args %s',exe,' '.join(args))
			process = guestSession.processCreate(exe,args,[],[self.ctx['const'].ProcessCreateFlag_None],0)
			logger.info('Executed with pid %d', process.PID)
			process.waitFor(self.ctx['const'].ProcessWaitForFlag_Terminate, 5000)
			# GET OUTPUT FROM STDERR
		except Exception as e:
			logger.exception('Error executing process: %s', exe)
			
		guestSession.close()
		session.unlockMachine()
	
	# TODO: fix this; not working even w/ drag/drop	turned on/tested successfully; session stuff looks good; not sure why; not working via vboxmanage either	
	def fileCopyTo(self, src, dest):
		session = self.ctx['global'].getSessionObject(self.ctx['vb'])
		try:
			self.mach.lockMachine(session, self.ctx['const'].LockType_Shared)
		except Exception as e:
			logger.exception('Error locking machine to copy file. Error: %s', e)
			
		try:
			guestSession = self.ctx['guest'].createSession('user','pass','','test_session2')
			gh = guestSession.waitFor(self.ctx['const'].GuestSessionWaitForFlag_Start,0)
			logger.info('Session %s started w/ id %s. Session status: %s', guestSession.name, guestSession.id, getEnumValue(self.ctx, "GuestSessionStatus", guestSession.status))
			logger.info('Session result: %s', gh)
		except Exception as e:
			logger.exception('Error starting guest session for file copy. Error: %s', e)
		
		try:
			time.sleep(7)
			# if guest session successfully started
			if gh == 1:
				#logger.info('Guest Additions status: %s', self.ctx['guest'].getAdditionsStatus(self.ctx['const'].AdditionsRunLevelType_Desktop))
				p = guestSession.fileCopyToGuest(src,dest,[self.ctx['const'].FileCopyFlag_None])
				ph = progressHandler(self.ctx, p, 5000)
				if ph and int(p.resultCode) == 0:
					logger.info('File %s copied to VM as %s.', src, dest)
		except Exception as e:
			logger.exception('Error copying file to VM. Error: %s', e)
		
		guestSession.close()
		session.unlockMachine()
		
# enum must be a string - "GuestSessionStatus"
def getEnumValue(ctx, enum, element):
	enumVals = ctx['const'].all_values(enum)
	for e in enumVals.keys():
		if str(element) == str(enumVals[e]):
			return e
	return element
		
def progressHandler(ctx, progress, wait=10000):
	try:
		while not progress.completed:
			#logger.info('Processing: %s%%', progress.percent)
			progress.waitForCompletion(wait)
			ctx['global'].waitForEvents(0)
			logger.info('Waiting %d seconds for process...', wait/1000)
			time.sleep(wait/1000)
		# report IProgress add'l error info
		if int(progress.resultCode) != 0 and progress.errorInfo:
			logger.error('Error in module "%s": %s', progress.errorInfo.component, progress.errorInfo.text)
		return 1
	except Exception as e:
		logger.exception('Error completing task. Error: %s', e)
		return 0

# create aggregate listener for multiple event types
def listen(ctx, events, active=False, dur=100000):
	session = ctx['global'].getSessionObject(ctx['vb'])
	es = session.console.eventSource
	listener = es.createListener()
	agg = es.createAggregator(events)
	agg.registerListener(listener, events, active)
	registered = True
	end = time.time() + dur
	while time.time() < end:
		ev = agg.getEvent(listener, 1000)
		processEvent(ctx, ev)
		agg.eventProcessed(listener, ev)
	agg.unregisterListener(listener)

def processEvent(ctx, ev):
	evtype = ev.type
	# monitor machine-level events
	if evtype == ctx['const'].VBoxEventType_OnMachineStateChanged:
		msce = ctx['global'].queryInterface(ev, 'IMachineStateChangedEvent')
		if msce:
			logger.info('Machine state event: mach=%s state=%s', msce.machineId, msce.state)
	elif evtype == ctx['const'].VBoxEventType_OnStateChanged:
		sc = ctx['global'].queryInterface(ev, 'IStateChangedEvent')
		if sc:
			logger.info('Machine execution state event: state=%s', getEnumValue(ctx, 'MachineState', sc.state))
	elif evtype == ctx['const'].VBoxEventType_OnSnapshotRestored:
		sr = ctx['global'].queryInterface(ev, 'ISnapshotRestoredEvent')
		if sr:
			logger.info('Snapshot restored: id=%s', sr.snapshotId)
	elif evtype == ctx['const'].VBoxEventType_OnSnapshotTaken:
		st = ctx['global'].queryInterface(ev, 'ISnapshotTakenEvent')
		if st:
			logger.info('Snapshot taken: id=%s', st.snapshotId)
	elif evtype == ctx['const'].VBoxEventType_OnSharedFolderChanged:
		sfc = ctx['global'].queryInterface(ev, 'ISharedFolderChangedEvent')
		if sfc:
			logger.info('Shared folder event: type=%s', getEnumValue(ctx, 'Scope', sfc.scope))
	# monitor guest-level events
	elif evtype == ctx['const'].VBoxEventType_OnGuestSessionRegistered:
		gsr = ctx['global'].queryInterface(ev, 'IGuestSessionRegisteredEvent')
		if gsr:
			logger.info('Guest session registered: session=%s registered=%s', gsr.session.name, gsr.registered)
	elif evtype == ctx['const'].VBoxEventType_OnGuestSessionStateChanged:
		gssc = ctx['global'].queryInterface(ev, 'IGuestSessionStateChangedEvent')
		if gssc:
			logger.info('Guest session changed: session=%s status=%s', gssc.session.name, getEnumValue(ctx, 'GuestSessionStatus', gssc.status))
		if gssc.error:
			logger.error('Guest session change generated errors: code=%s, detail=%s, component=%s, text=%s', gssc.error.resultCode, gssc.error.resultDetail, gssc.error.component, gssc.error.text)
	elif evtype == ctx['const'].VBoxEventType_OnGuestProcessRegistered:
		gpr = ctx['global'].queryInterface(ev, 'IGuestProcessRegisteredEvent')
		if gpr:
			logger.info('Guest process registered: PID=%s process=%s registered=%s', gpr.pid, gpr.process.name, gpr.registered)
	elif evtype == ctx['const'].VBoxEventType_OnGuestProcessStateChanged:
		gpsc = ctx['global'].queryInterface(ev, 'IGuestProcessStateChangedEvent')
		if gpsc:
			logger.info('Guest process changed: PID=%s process=% status=%s', gpsc.pid, gpsc.process.name, getEnumValue(ctx, 'ProcessStatus', gpsc.status))
		if gpsc.error:
			logger.error('Guest process change generated errors: code=%s, detail=%s, component=%s, text=%s', gpsc.error.resultCode, gpsc.error.resultDetail, gpsc.error.component, gpsc.error.text)
	elif evtype == ctx['const'].VBoxEventType_OnGuestUserStateChanged:
		gusc = ctx['global'].queryInterface(ev, 'IGuestUserStateChangedEvent')
		if gusc:
			logger.info('Guest user state changed: user=%s', gusc.name)
	elif evtype == ctx['const'].VBoxEventType_OnGuestFileRegistered:
		gfre = ctx['global'].queryInterface(ev, 'IGuestFileRegisteredEvent')
		if gfre:
			logger.info('Guest file registered: file=%s registered=%s', gfre.file.fileName, gfre.registered)
	elif evtype == ctx['const'].VBoxEventType_OnGuestFileStateChanged:
		gfsc = ctx['global'].queryInterface(ev, 'IGuestFileStateChangedEvent')
		if gfsc:
			logger.info('Guest file changed: file=%s registered=%s', gfre.file.fileName, getEnumValue(ctx, 'FileStatus', gfsc.status))
		if gfsc.error:
			logger.error('Guest file change generated errors: code=%s, detail=%s, component=%s, text=%s', gfsc.error.resultCode, gfsc.error.resultDetail, gfsc.error.component, gfsc.error.text)
	elif evtype == ctx['const'].VBoxEventType_OnGuestFileRead:
		gfr = ctx['global'].queryInterface(ev, 'IGuestFileReadEvent')
		if gfr:
			logger.info('Guest file read: file=%s bytes=%s', gfr.file.fileName, gfr.processed)
	elif evtype == ctx['const'].VBoxEventType_OnGuestFileWrite:
		gfw = ctx['global'].queryInterface(ev, 'IGuestFileWriteEvent')
		if gfw:
			logger.info('Guest file written: file=%s bytes=%s', gfw.file.fileName, gfw.processed)
	elif evtype == ctx['const'].VBoxEventType_OnGuestProcessOutput:
		gpo = ctx['global'].queryInterface(ev, 'IGuestProcessOutputEvent')
		if gpo:
			for d in gpo.data:
				logger.info('Guest process output: %s', d)
	# monitor other-level events
	elif evtype == ctx['const'].VBoxEventType_OnRuntimeError:
		re = ctx['global'].queryInterface(ev, 'IRuntimeErrorEvent')
		if re:
			logger.error('Runtime error: fatal=%s id=%s message=%s', re.fatal, re.id, re.message)