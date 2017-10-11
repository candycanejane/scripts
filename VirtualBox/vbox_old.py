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
	from vboxapi import VirtualBoxManager
except ImportError:
	print('Unable to import VirtualBoxManager')
	sys.exit()

import sys
import os
import time
import logging

# create logger
logger = logging.getLogger('autovb.vbox')
print "Started import"

class VBoxAuto:
	def __init__(self, vm):
		self.vmname = vm
		self.ctx = {}
		self.mach = None
		self.uuid = None

	def check(self):
		vbm = VirtualBoxManager('XPCOM', None)
		
		self.ctx = {'global': vbm,
					'vb'	: vbm.vbox,
					'mgr'	: vbm.mgr,
					'const'	: vbm.constants}
		try:
			self.mach = self.ctx['vb'].findMachine(self.vmname)
			self.uuid = self.mach.id
			logger.info('Using %s (uuid: %s)', self.mach.name, self.mach.id)
			return True
		except Exception as e:
			logger.exception('Cannot find registered machine: %s. Error: %s', self.vmname, e)
			return False

	def start(self):
		vbox = self.ctx['vb']
		session = self.ctx['global'].getSessionObject(vbox)
		print "Launching new vm..."
		p = self.mach.launchVMProcess(session,'gui','')
		print "Waiting for process completion"
		p.waitForCompletion(10000)
		time.sleep(10)
		session.unlockMachine()
		print "Vm started successfully..."

	"""
    	try:
    		print "Launching new vm..."
    		p = self.mach.launchVMProcess(session,'gui','')
    		print "Waiting for process completion"
    		while not p.completed:
				p.waitForCompletion(10000)
				self.ctx['global'].waitForEvents(0)
				print "Waiting 10 seconds..."
				time.sleep(10)
    		#ph = progressHandler(self.ctx, p)
    		#if ph and int(p.resultCode) == 0:
    		print "Vm started successfully..."
    		session.unlockMachine()			
    	except Exception as e:
        	logger.exception('Cannot launch vm. Error: %s', e)
	"""
	def stop(self):
		vbox = self.ctx['vb']
		session = self.ctx['global'].getSessionObject(vbox)
		try:
			p = session.console.powerDown()
			progressHandler(self.ctx, p)
			self.ctx['global'].closeMachineSession(session)
			logger.info('VM powered down; session closed.')
		except Exception as e:
			logger.exception('Error shutting down the vm. Error: %s', e)

	def snapshot(self, name):
		vbox = self.ctx['vb']
		session = self.ctx['global'].getSessionObject(vbox)
		try:
			self.mach.lockMachine(session, self.ctx['const'].LockType_Shared)
		except Exception as e:
			logger.exception('Error locking machine for snapshot. Error: %s', e)
		
		try:
			(p,uuid) = session.machine.takeSnapshot(name,'',True)
			progressHandler(self.ctx, p)
			session.unlockMachine()
			logger.info('Offline snapshot completed.')
		except Exception as e:
			logger.exception('Error taking initial snapshot. Error: %s', e)

	def revert(self, name):
		vbox = self.ctx['vb']
		session = self.ctx['global'].getSessionObject(vbox)
		try:
			self.mach.lockMachine(session, self.ctx['const'].LockType_Shared)
		except Exception as e:
			logger.exception('Error locking machine for snapshot. Error: %s', e)
		
		try:
			snap = self.mach.findSnapshot(name)
			p = session.machine.restoreSnapshot(snap)
			progressHandler(self.ctx, p)
			session.unlockMachine()
			logger.info('VM reverted to original.')
		except Exception as e:
			logger.exception('Error restoring snapshot. Error: %s', e)	

	def addShare(self, hostshare):
		vbox = self.ctx['vb']
		session = self.ctx['global'].getSessionObject(vbox)
		try:
			self.mach.lockMachine(session, self.ctx['const'].LockType_Shared)
			#mutable = session.machine
		except Exception as e:
			logger.exception('Error locking machine for snapshot. Error: %s', e)
		
		try:
			session.console.createSharedFolder('temp', hostshare, False, True)
			logger.info('Created temporary read-only share folder.')
		except Exception as e:
			logger.exception('Error creating temporary shared folder. Error: %s', e)

	def removeShare(self):
		vbox = self.ctx['vb']
		session = self.ctx['global'].getSessionObject(vbox)
		try:
			self.mach.lockMachine(session, self.ctx['const'].LockType_Shared)
			mutable = session.machine
		except Exception as e:
			logger.exception('Error locking machine for snapshot. Error: %s', e)
		
		try:
			session.console.removeSharedFolder('temp')
			logger.info('Removed share folder.')
		except Exception as e:
			logger.exception('Error removing shared folder. Error: %s', e)
	
def progressHandler(ctx, progress, wait=10000):
	try:
		while not progress.completed:
			progress.waitForCompletion(wait)
			ctx['global'].waitForEvents(0)
			logger.info('Waiting 10 seconds...')
			time.sleep(10)
		return 1
	except Exception as e:
		logger.exception('Error during task completion. Error: %s', e)
		return 0

print "Imported vbox"

#def winexec
"""
def cmdExistingVm(ctx, mach, cmd, args):
    session = None
    try:
        vbox = ctx['vb']
        session = ctx['global'].getSessionObject(vbox)
        mach.lockMachine(session, ctx['global'].constants.LockType_Shared)
    except Exception, e:
        printErr(ctx, "Session to '%s' not open: %s" % (mach.name, str(e)))
        if g_fVerbose:
            traceback.print_exc()
        return
    if session.state != ctx['const'].SessionState_Locked:
        print "Session to '%s' in wrong state: %s" % (mach.name, session.state)
        session.unlockMachine()
        return
    # this could be an example how to handle local only (i.e. unavailable
    # in Webservices) functionality
    if ctx['remote'] and cmd == 'some_local_only_command':
        print 'Trying to use local only functionality, ignored'
        session.unlockMachine()
        return
    console = session.console
    ops = {'pause':           lambda: console.pause(),
           'resume':          lambda: console.resume(),
           'powerdown':       lambda: console.powerDown(),
           'powerbutton':     lambda: console.powerButton(),
           'guest':           lambda: guestExec(ctx, mach, console, args),
           'ginfo':           lambda: ginfo(ctx, console, args),
           'guestlambda':     lambda: args[0](ctx, mach, console, args[1:]),
           'save':            lambda: progressBar(ctx, session.machine.saveState()),
           'screenshot':      lambda: takeScreenshot(ctx, console, args),
           'gueststats':      lambda: guestStats(ctx, console, args),
           'mountiso':        lambda: mountIso(ctx, session.machine, session, args),
           }
    try:
        ops[cmd]()
    except KeyboardInterrupt:
        ctx['interrupt'] = True
    except Exception, e:
        printErr(ctx, e)
        if g_fVerbose:
            traceback.print_exc()

    session.unlockMachine()

def cmdClosedVm(ctx, mach, cmd, args=[], save=True):
    session = ctx['global'].openMachineSession(mach, True)
    mach = session.machine
    try:
        cmd(ctx, mach, args)
    except Exception, e:
        save = False
        printErr(ctx, e)
        if g_fVerbose:
            traceback.print_exc()
    if save:
        try:
            mach.saveSettings()
        except Exception, e:
            printErr(ctx, e)
            if g_fVerbose:
                traceback.print_exc()
    ctx['global'].closeMachineSession(session)


def cmdAnyVm(ctx, mach, cmd, args=[], save=False):
    session = ctx['global'].openMachineSession(mach)
    mach = session.machine
    try:
        cmd(ctx, mach, session.console, args)
    except Exception, e:
        save = False
        printErr(ctx, e)
        if g_fVerbose:
            traceback.print_exc()
    if save:
        mach.saveSettings()
    ctx['global'].closeMachineSession(session)
    
def copyToGuest(ctx, console, args, user, passwd):
    src = args[0]
    dst = args[1]
    flags = 0
    print "Copying host %s to guest %s" % (src, dst)
    progress = console.guest.copyToGuest(src, dst, user, passwd, flags)
    progressBar(ctx, progress)

def execInGuest(ctx, console, args, env, user, passwd, tmo, inputPipe=None, outputPipe=None):
    if len(args) < 1:
        print "exec in guest needs at least program name"
        return
    guest = console.guest
    guestSession = guest.createSession(user, passwd, "", "vboxshell guest exec")
    # shall contain program name as argv[0]
    gargs = args
    print "executing %s with args %s as %s" % (args[0], gargs, user)
    flags = 0
    if inputPipe is not None:
        flags = 1 # set WaitForProcessStartOnly
    print args[0]
    process = guestSession.processCreate(args[0], gargs, env, [], tmo)
    print "executed with pid %d" % (process.PID)
    if pid != 0:
        try:
            while True:
                if inputPipe is not None:
                    indata = inputPipe(ctx)
                    if indata is not None:
                        write = len(indata)
                        off = 0
                        while write > 0:
                            w = guest.setProcessInput(pid, 0, 10*1000, indata[off:])
                            off = off + w
                            write = write - w
                    else:
                        # EOF
                        try:
                            guest.setProcessInput(pid, 1, 10*1000, " ")
                        except:
                            pass
                data = guest.getProcessOutput(pid, 0, 10000, 4096)
                if data and len(data) > 0:
                    sys.stdout.write(data)
                    continue
                progress.waitForCompletion(100)
                ctx['global'].waitForEvents(0)
                data = guest.getProcessOutput(pid, 0, 0, 4096)
                if data and len(data) > 0:
                    if outputPipe is not None:
                        outputPipe(ctx, data)
                    else:
                        sys.stdout.write(data)
                    continue
                if progress.completed:
                    break

        except KeyboardInterrupt:
            print "Interrupted."
            ctx['interrupt'] = True
            if progress.cancelable:
                progress.cancel()
        (_reason, code, _flags) = guest.getProcessStatus(pid)
        print "Exit code: %d" % (code)
        return 0
    else:
        reportError(ctx, progress)

def asEnumElem(ctx, enum, elem):
    enumVals = ctx['const'].all_values(enum)
    for e in enumVals.keys():
        if str(elem) == str(enumVals[e]):
            return colored(e, 'green')
    return colored("<unknown>", 'green')

def enumFromString(ctx, enum, strg):
    enumVals = ctx['const'].all_values(enum)
    return enumVals.get(strg, None)

def monitorSource(ctx, eventSource, active, dur):
    def handleEventImpl(event):
        evtype = event.type
        print "got event: %s %s" % (str(evtype), asEnumElem(ctx, 'VBoxEventType', evtype))
        if evtype == ctx['global'].constants.VBoxEventType_OnMachineStateChanged:
            scev = ctx['global'].queryInterface(event, 'IMachineStateChangedEvent')
            if scev:
                print "machine state event: mach=%s state=%s" % (scev.machineId, scev.state)
        elif  evtype == ctx['global'].constants.VBoxEventType_OnSnapshotTaken:
            stev = ctx['global'].queryInterface(event, 'ISnapshotTakenEvent')
            if stev:
                print "snapshot taken event: mach=%s snap=%s" % (stev.machineId, stev.snapshotId)
        elif  evtype == ctx['global'].constants.VBoxEventType_OnGuestPropertyChanged:
            gpcev = ctx['global'].queryInterface(event, 'IGuestPropertyChangedEvent')
            if gpcev:
                print "guest property change: name=%s value=%s" % (gpcev.name, gpcev.value)
        elif  evtype == ctx['global'].constants.VBoxEventType_OnMousePointerShapeChanged:
            psev = ctx['global'].queryInterface(event, 'IMousePointerShapeChangedEvent')
            if psev:
                shape = ctx['global'].getArray(psev, 'shape')
                if shape is None:
                    print "pointer shape event - empty shape"
                else:
                    print "pointer shape event: w=%d h=%d shape len=%d" % (psev.width, psev.height, len(shape))
        elif evtype == ctx['global'].constants.VBoxEventType_OnGuestMouse:
            mev = ctx['global'].queryInterface(event, 'IGuestMouseEvent')
            if mev:
                printMouseEvent(ctx, mev)
        elif evtype == ctx['global'].constants.VBoxEventType_OnGuestKeyboard:
            kev = ctx['global'].queryInterface(event, 'IGuestKeyboardEvent')
            if kev:
                printKbdEvent(ctx, kev)
        elif evtype == ctx['global'].constants.VBoxEventType_OnGuestMultiTouch:
            mtev = ctx['global'].queryInterface(event, 'IGuestMultiTouchEvent')
            if mtev:
                printMultiTouchEvent(ctx, mtev)

    class EventListener(object):
        def __init__(self, arg):
            pass

        def handleEvent(self, event):
            try:
                # a bit convoluted QI to make it work with MS COM
                handleEventImpl(ctx['global'].queryInterface(event, 'IEvent'))
            except:
                traceback.print_exc()
            pass

    if active:
        listener = ctx['global'].createListener(EventListener)
    else:
        listener = eventSource.createListener()
    registered = False
    if dur == -1:
        # not infinity, but close enough
        dur = 100000
    try:
        eventSource.registerListener(listener, [ctx['global'].constants.VBoxEventType_Any], active)
        registered = True
        end = time.time() + dur
        while  time.time() < end:
            if active:
                ctx['global'].waitForEvents(500)
            else:
                event = eventSource.getEvent(listener, 500)
                if event:
                    handleEventImpl(event)
                    # otherwise waitable events will leak (active listeners ACK automatically)
                    eventSource.eventProcessed(listener, event)
    # We need to catch all exceptions here, otherwise listener will never be unregistered
    except:
        traceback.print_exc()
        pass
    if listener and registered:
        eventSource.unregisterListener(listener)       
    oVBoxMgr.deinit()
    del oVBoxMgr"""
#active listener implementation
class EventListener(object):
	def handleEvent(self, event):
		processEvent(ctx, cts['global'].queryInterface(event, 'IEvent'))

def listen(ctx, events, active=False, dur=100000):
	session = ctx['global'].getSessionObject(ctx['vb'])
	if active:
		listener = ctx['global'].createListener(EventListener)
		es.registerListener(listener, events, True)
		for ev in events:
			listener.handleEvent(ev)
		es.unregisterListener(listener)
	
	# create single listener
	if len(events) == 1:
		es = session.console.eventSource
		listener = es.createListener()
		es.registerListener(listener, events, active)
		ev = es.getEvent(listener, 1000)
		if ev != null:
			processEvent(ctx, ev)
			es.eventProcessed(listener, ev)
		es.unregisterListener(listener)
[ctx['const'].VBoxEventType_Any]
										c.VBoxEventType_MachineEvent,
										c.VBoxEventType_SnapshotEvent,
										c.VBoxEventType_OnMachineStateChanged,
										c.VBoxEventType_OnStateChanged,
										c.VBoxEventType_OnSnapshotRestored,
										c.VBoxEventType_OnSnapshotTaken,
										c.VBoxEventType_OnSharedFolderChanged,
										c.VBoxEventType_OnGuestSessionRegistered,
										c.VBoxEventType_OnGuestSessionStateChanged,
										c.VBoxEventType_OnGuestProcessRegistered,
										c.VBoxEventType_OnGuestProcessStateChanged,
										c.VBoxEventType_OnGuestUserStateChanged,
										c.VBoxEventType_OnGuestFileRegistered,
										c.VBoxEventType_OnGuestFileStateChanged,
										c.VBoxEventType_OnGuestFileRead,
										c.VBoxEventType_OnGuestFileWrite,
										c.VBoxEventType_OnGuestProcessOutput,
										c.VBoxEventType_OnRuntimeError
OnEventSourceChanged
OnGuestPropertyChanged
