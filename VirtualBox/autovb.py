#!/usr/bin/python

__description__ = "Automation tool for running unknown files inside VirtualBox vm."
__author__ = "candycanejane"
__copyright__ = "Copyright 2016"
__email__ = "bumbleb33tuna@gmail.com"
	
import os
import sys
import time
import shutil
import argparse
import logging
import subprocess
import zipfile
import hashlib
import ZSI
import vbox


"""
This script will automate malware analysis in VirtualBox vms. Relies on Python 2.7 functionality.

"""
# TODO: find way to pass around filenames for log; what is best return value?
# TODO: logfile for individual file...make this global handle?
# TODO: figure out how to send stderr and stdout to logging utility!!
# TODO: get output of guest processes

## DEFAULTS ##
timestr = time.strftime("%Y%m%d-%H%M%S")
_RESULTS = '~/Documents/LAB/VM/testing'
_LOGFILE = 'autovb_{0}.log'.format(timestr)
hostshare = '~/Documents/LAB/VM/vmshare'
guestshare = '/media/sf_temp'

## LOGGING UTILITY ##
logger = logging.getLogger('autovb')
logger.setLevel(logging.DEBUG)
# create file handler
fh = logging.FileHandler(_LOGFILE)
fh.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s, %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
fh.setFormatter(formatter)
# add handler to logger
logger.addHandler(fh)
add = {'function': '%(funcName)s', 'lineno': '%(lineno)d'}

# preps file for transmission -> zip, add password
def prep(file, result_path):
	try:
		root,ext = os.path.splitext(file)
		fname = os.path.basename(root)
		zname = os.path.join(result_path, '{0}.zip'.format(fname))
		logger.info('Zipping file: %s',os.path.basename(file))
		# call to zip function, -j discards the folder information, -P provides the password 'virus'
		subprocess.check_call(['zip', '-j', '-P', 'virus', zname, file])
		logger.info('File zipped: %s','{0}.zip'.format(fname))
	except subprocess.CalledProcessError as e:
		logger.exception('Call to zip utility failed. Command %s returned: %s'.format(e.cmd, e.returncode))
	
	# hash the new zip file for future validation 	
	try:
		with open(zname, 'rb') as f:
			data = f.read()
			h = hashlib.md5()
			h.update(data)
			hash = h.hexdigest()
		f.close()
	except OSError as e:
		logger.exception('Hash of {0} failed. Error: {1}, {2}'.format(zname, e.errno, e.strerror))
	
	# save hash of zip file to hash.txt
	try:
		hashfile = os.path.join(result_path, '{0}.txt'.format(hash))
		with open(hashfile, 'w') as outfile:
			outfile.write(hash)
		outfile.close()
		logger.info('Hash saved: %s', hashfile)
	except OSError as e:
		logger.exception('Writing hash failed: {0}. Error: {1}, {2}'.format(hashfile, e.errno, e.strerror))
		
	return [zname,hashfile]

# copy zip file to host share folder
def copy_mal(list_of_files, share):
	if not os.path.isdir(share):
		logger.warning('Share folder not found')
		logger.info('Creating share folder: %s', share)
		os.makedirs(share)

	try:
		for f in list_of_files:
			shutil.copy(f, share)
		return True
	except Error as e:
		logger.exception('Unable to transfer malware to share: %s', e)
		return False


def main(argv):
	"""
	Usage: python autovb.py <path_to_file> -l <path_to_logfile> -r <path_to_results> -d
	
	"""
	args = argparse.ArgumentParser(description='Automate unknown file analysis.')
	args.add_argument('file', metavar='/path/to/file.xyz', help='Filename to pass to vm')
	args.add_argument('-l', '--log', default=_LOGFILE, metavar='/path/to/log.log', help='Location to store logfile')
	args.add_argument('-r', '--results', default=_RESULTS, metavar='/path/to/results', help='Location of results folder')
	args.add_argument('-d', '--debug', default=False, action='store_true', help='Prints additional status info')
	p_args = args.parse_args()
	
	# args
	file = p_args.file
	result_path = p_args.results
	
	# check file
	logger.info('Processing new file: %s', file)
	if not os.path.isfile(file):
		logger.error('Filename provided is not valid: %s', file)
		logger.debug('Something is wrong with the source file', extra=add)
		sys.exit()
		
	# check for results directory
	if not os.path.isdir(result_path):
		logger.warning('Results folder not found')
		logger.info('Creating results folder: %s',result_path)
		os.makedirs(result_path)
	
	# process file
	files = prep(file, result_path) 
	
	# copy zip/hash file to share folder
	if not copy_mal(files, hostshare):
		logger.error('Error copying zip file to share folder.')
		sys.exit()

	# initialize vm 
	vm = vbox.VBoxAuto('MLVM')
	if not vm.init():
		logger.error('Error initializing vm.')
		sys.exit()
	
	vm.revert('clean_img2')
	vm.start()
	vm.addShare(hostshare)
	time.sleep(5)
	vm.execInGuest('root','/bin/mount',['-t','vboxsf','-o','ro','temp',guestshare])
	print "CHECK FOR SHARE FOLDER"
	time.sleep(120)
	print "REMOVING SHARE"
	vm.execInGuest('root','/bin/umount',[guestshare])
	vm.removeShare()
	print "Manually shut down VM during testing..."
	#time.sleep(60)
	#vm.stop()
	#logger.info('Test successful')
	
	# shutdown vm handler??
	
	# shutdown logger
	logging.shutdown()
	
		
if __name__ == "__main__":
	main(sys.argv)
	