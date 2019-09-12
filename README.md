# pyZodiacTri
Python scripts for running a webserver directly controlling a Zodiac Tri connected by RS485.

!!! Use at your own risk !!!

These codes are based on various sources on the internet, but mostly:
https://github.com/sfeakes/AquapureD
https://github.com/ericbuehl/pyaqualink

Scripts are tested on a raspberry pi 3B+ running Stretch and a low cost Sertronics USB - RS485 Converter.
The RS485 converter is connected to the Zodiac PSU board using the Zodiac Comms section pins A B.
The stabilized 5V power supply that feeds the RPI is also connected to the Zodiac Comms section, pins POS and 0V.
https://nl.farnell.com/mean-well/hdr-30-5/power-supply-ac-dc-5v-3a/dp/2815640?CMP=i-ddd7-00001003

Sertronics RS485 A	-------		Zodiac Tri A
Sertronics RS485 B	------- 	Zodiac Tri B
PSU RPI		 5v	-------		Zodiac Tri POS
PSU RPI		 0v	-------		Zodiac Tri 0V

- On the Zodiac Tri, select Jandy Rev L/M as remote controller

- Check if the USB RS485 converter is recognized:
	Open a LXTerminal and run ls /dev/tty* to find the device name, and edit webserver.py 
	and zodiactest.py accordingly	
	Mine showed up as /dev/ttyUSB0

- Run python2 zodiactest.py, there should be communication going on.

- Run python2 webserver.py from within the HTML directory:
	cd /ZodiacScripts/HTML
	/usr/bin/python2 /ZodiacScripts/V1.1/webserver.py
	open a webbrowser and go to http://ip.of.raspberry:8081

- When 'Talk To Zodiac' is enabled, the script will continiously send messages to the Zodiac Tri to keep it alive and have those settings applied. When it's disabled, the Zodiac Tri will shut off after half a minute.

- If 'Status' is not showing 'connected', then there is not response from the Zodiac and the settings won't be applied.

- When connected the little connection icon changes in the right upper corner of the Zodiac Tri's display

- Data is not pushed from the webserver to the webclient, so manual webclient refresh is needed to have the last status.

- To test without python scripts, run these commands repeatedly. if 'od' output is nothing more than 00000000 this indicates the RS485 adapter is not reading anything back from the Zodiac Tri:
	echo -n -e '\x10\x02\x50\x00\x62\x10\x03' > /dev/ttyUSB0
	od -x < /dev/ttyUSB0




