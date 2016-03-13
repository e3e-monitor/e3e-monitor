import serial
from json import JSONEncoder
import string

import requests

import time

serialDevice = '/dev/ttyUSB0'
host = 'http://52.29.7.137:5000/reading'






ser = serial.Serial(serialDevice, 9600, timeout = 0.1)

x = 0

MAX_BUF = 100;


b = ['\x00'] * MAX_BUF


while 1:
	x = ser.inWaiting()
	if (x > 20):
		size = 0
		frametype = 0
		source_64 = '' 
		source_16 = ''
		data = ''

		ser.readinto(b)
		
		if (b[0] != '\x7E'):
			continue
		
		size = ((int(b[1].encode('hex'),16) & 0xFF) << 8) | (int(b[2].encode('hex'),16) & 0xFF)
		datasize = size - 12  

		frametype = b[3]

		if (frametype != '\x90'):
			continue
	
		for i in range(0,8):
			source_64 += b[4+i].encode('hex')		
		
		#for i in range(0,2):
		#	source_16 += b[12+i].encode('hex')
		
		#print b

		for i in range(0,datasize):
			#print i
			data += b[15+i].encode('utf-8')
	
		jsonString = JSONEncoder().encode({
 			"timestamp": time.time(),
			"source": source_64,
			"payload": data
		})

		#print data
		#print jsonString

		try:
			r = requests.post(host, json=jsonString)
			print jsonString
			print r.status_code
		except Exception, e:
			print e	
