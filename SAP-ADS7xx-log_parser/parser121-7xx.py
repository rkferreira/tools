#!/usr/bin/python

#
# Parser for getting ADS 7XX xml request/response from defaultTrace log file
#
# Author : Rodrigo Kellermann
# Version: 1.1
# Patch:   2

# Last modification: 14-march-2013

### Changelog #

# patch 2 (1.1.2)
# - change file opens to binary, to be windows compatible.

# patch 1 (1.1.1)
# - correct error.pdf and Error_Level handling

# minor 1 (1.1.0)
# - now able to parse NW CE ADS requests
# - correction of one line requests

# major 1 (1.0.0)
# - now able to parse all versions

# patch 2 (0.0.2)
# - Added case for error.pdf and more debug information on decodeXml function

# patch 1 (0.0.1)
# - Remove carriage return from base64 string

###

import sys, string, re, os, array, base64
from xml.etree import ElementTree as ET

# If true, direct stdout to a file
debug = 0

# Write found XMLs on files
def writeFile(filename, data):
	try:
		f = open(filename, 'w+b')
	except IOError as e:
		print "I/O error({0}): {1}".format(e.errno, e.strerror)
		print 'error creating file'
	else:
		f.write(data)
		f.close
	return

def decodeXml(fname,filename,nr):
	if debug: print '#debug# Starting decodeXml ...'
	try:
		root = ET.parse(filename)
	except:
		return
	iter = root.getiterator()
	found0=0
	wfile = ''
	if debug: print '#debug# Starting for iteraction'
	for element in iter:
		if debug: print '#debug# element.tag = '+element.tag
		if element.tag == 'name' or element.tag == '{urn:com.adobe}name':
			if element.text == 'PDFDocument':
				if debug: print '#debug# Found PDFDocument'
				found0=1
				wfile = 'PDFDocument-%s.xml' % (nr)
			if element.text == 'XFD':
				if debug: print '#debug# Found XFD'
				found0=1
				wfile = 'XFD-%s.xml' % (nr)
			if (element.text == 'PDFOut') or (element.text == 'docTarget'):
				if debug: print '#debug# Found PDFOut'
				found0=1
				wfile = 'PDFOut-%s.pdf' % (nr)
			if element.text == 'PDLOut':
				if debug: print '#debug# Found PDFOut'
				found0=1
				wfile = 'PDLOut-%s.pcl' % (nr)
			if element.text == 'error.pdf':
				if debug: print '#debug# Found error.pdf'
				found0=1
				wfile = 'Error-%s.pdf' % (nr)
		if (element.tag == 'value' or element.tag == '{urn:com.adobe}value') and found0 == 1:
			try:
				result = base64.standard_b64decode(element.text)
			except:
				result = "Error decoding base64"
			if debug: print '#debug# Writing the file'
			wfile = '%s-%s' % (fname,wfile)
			file = open(wfile,'w+b')
			file.write(result)
			file.close()
			found0=0
	if debug: print '#debug# End decodeXml'
	



# Do the main task finding XML request/response
if len(sys.argv) > 1:
	fname = sys.argv[1]
	f = open(fname,'rb')
	l = '1'
	working = 0
	end = 1
	str = ''
	found = 0

	while l:
		l = f.readline()
		if end == 0:
			if not(oneline):
				if debug: print '#debug# This isnt oneline. Filling body. \n'
				t = re.search('<\/SOAP-ENV:Envelope>',l)
			else:
				if debug: print '#debug# This is oneline. I should stop. \n'
				t = re.search('<\/SOAP-ENV:Envelope>',str)
			if t:
				if not(oneline):
					if debug: print '#debug# This isnt oneline. Ending XML. \n'+l
					str = str + l
					end = 1
					working = 0
					conc = str.replace('\n','')
					conc = conc.replace('\r','')
					size = len(conc)
					conc = conc[0:size-1]
				else:
					if debug: print '#debug# This is oneline. I should get size and stop. \n'
					conc = str
					size = len(conc)
					conc = conc[0:size-2]
				if debug:
					if re.match('^<SOAP-ENV:Envelope.*.</SOAP-ENV:Envelope>$',conc):
						print '#debug# Complet XML Matched!!!'
				if re.match('.*.AdobeDocumentServices.*',conc):
					if debug:
						print '#debug# This is AdobeDocumentServices request'
					if re.match('.*PDFDocument.*',conc):
						filename = 'request'
						if debug:
							print '#debug# This is PDFDocument XML file'
					else:
						if (re.match('.*.PD[F-L]Out.*',conc)) or (re.match('.*.Response.*.docTarget.*',conc)) or (re.match('.*.Response.*.error\.pdf.*',conc)):
							filename = 'response'
							if found > 0:
								found = found-1
							if debug:
								print '#debug# This is PDFOut or PDLOut XML file'
						else:
							if (re.match('.*.Response.*.Error_Level.*',conc)):
								filename = 'error'
								if debug: print '#debug# This is Error_Level response'
							else:
								filename = 'found'
								if debug:
									print '#debug# This is not an ADS XML request (1)'
				else:
					filename = 'found'
					if debug:
						print '#debug# This is not an ADS XML request (2)'
				fname2 = '%s-%s-%s.txt' % (fname,filename,found)
				writeFile(fname2, conc)
				if filename == 'request' or filename == 'response':
					if debug:
						print '#debug# This is a request/response file. I should decodeXml'
					decodeXml(fname,fname2,found)
				found = found + 1
				str = ''
				conc = ''

				if oneline:
					working = 0
					end = 1
				else:
					l = f.readline()
			else:
				if debug: print '#debug# Adding XML body \n'+l
				str = str + l
		if working == 0:
			oner = 0
			oneline = re.match('^<SOAP-ENV:Envelope.*.</SOAP-ENV:Envelope>',l)
			if not(oneline):
				oneline = re.match('^<\?xml version=\"1\.0\" encoding=\"UTF-8\"\?><SOAP-ENV.*.</SOAP-ENV:Envelope>',l)
			if oneline:
				if debug: print '#debug# This is one line request! \n'+l
				oner = 1
				working = 1
				str = l
				end = 0
			if not(oner):
				s = re.search('^\<SOAP-ENV:Envelope',l)
				if not(s):
					s = re.search('^\<\?xml version=\"1\.0\" encoding=\"UTF-8\"\?><SOAP-ENV:Envelope',l)
				if s:
					if debug: print '#debug# Starting XML \n'+l
					working = 1
					str = l
					end = 0
	f.close()
else:
	print 'Error: please specify log file name'
	print 'Usage: ./'+sys.argv[0]+' defaulttraceXX.log\n'

