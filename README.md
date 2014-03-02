JellyControl
============

Home automation for RaspberryPi using Python.

With this software your house can be controlled & programmed through your webbrowser.


INSTALLATION INSTRUCTIONS
-------------------------
Install git, python-setuptools, python, python-tz

Install pymodbus if you need the modbus components, otherwise remove them from the source;
git clone git://github.com/bashwork/pymodbus.git
cd pymodbus

remove "'twisted >= 12.2.0'," from setup.py:
python setup.py install


