# pyZodiacTri
Run python scripts as a webserver for controlling a Zodiac Tri connected by RS485


These scripts are tested on a raspberry pi 3B+ running Stretch and a low cost Sertronics USB - RS485 Converter.
The converter is connected to the Zodiac PSU board using the Comms section pins 0V POS A B.

Sertronics RS485 A	-------		Zodiac Tri A
Sertronics RS485 B	------- 	Zodiac Tri B
Raspberry pi 3B+ 5v	-------		Zodiac Tri POS
Raspberry pi 3B+ 0v	-------		Zodiac Tri 0V

- Check if the USB RS485 converter is recognized:
	Open a LXTerminal and run ls /dev/tty* to find the device name, and edit webserver.py 
	and zodiactest.py accordingly	
	Mine showed up as /dev/ttyUSB0

- Run python2 zodiactest.py, there should be communication going on.

- Run python2 webserver.py from within the HTML directory:
	cd /ZodiacScripts/HTML
	/usr/bin/python2 /ZodiacScripts/V1.1/webserver.py
	open a webbrowser and go to http://ip.of.raspberry:8081



