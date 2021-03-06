import numpy
import ardustat_library_simple as ard
import time

import subprocess
import os
import glob
import sys

##Guess a serial port
port = ""
if os.name == "posix":
	#try os x
	if len(glob.glob("/dev/tty.u*")) > 0:
		port = glob.glob("/dev/tty.u*")[0]
	elif len(glob.glob("/dev/ttyUSB*")) > 0:
		port = glob.glob("/dev/ttyUSB*")[0]
	else:
		print "can't see any ardustats.  PEACE."
		sys.exit()
	print port
	

#start a serial forwarder
p = subprocess.Popen(("python tcp_serial_redirect.py "+port+" 57600").split())
print "waiting"
time.sleep(5)
print "going"

#set parameters
read_delay = .5 #second
ardustat_id = 21
file_name = "galvanostat_test"
ardustat_socket = 7777
debug = False
pulse_time = 60*60*10



#Below here no touchy
#connect to to ardustat and setup resistance table
a = ard.ardustat()
a.connect(ardustat_socket)
a.debug = debug
a.load_resistance_table(ardustat_id)
a.ocv()
a.groundvalue = 4
a.moveground()
time.sleep(.2)
a.ocv()


#create arrays + a function for logging data
times = []
potential = []
current = []
time_start = time.time()
cycle = 0
file_name = file_name+"_"+str(int(time_start))+".dat"
def appender(reading):
	if reading['valid']:
		print reading['cell_ADC'],read['current']
		tdiff = str(time.time()-time_start)
		out = tdiff+","+str(reading['cell_ADC'])+","+str(read['current'])+","+str(cycle)+"\n"
		open(file_name,"a").write(out)
	else:
		print "bad read"


#Step through values
output = 0
a.ocv()
for i in range(0,20):
	time.sleep(.1)
	read = a.parsedread()
	appender(read)


start_pulse = time.time()
a.galvanostat(-0.001)
while (time.time()- start_pulse) < pulse_time:
	time.sleep(read_delay)
	read = a.parsedread()
	appender(read)		
		
start_pulse = time.time()
a.ocv()
while (time.time()- start_pulse) < 600:
	time.sleep(read_delay)
	read = a.parsedread()
	appender(read)
	


p.kill()


