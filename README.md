# Desk Server
A simple server to provide a rest api to raise and lower as desk. This projects configures an esp8266 chip 
with wifi and implements a simple rest api.  This code coonnects two pins from the esp8266 to a relay in 
order to move a desk up or down from a browser or a curl command. The projects uses micropython to implement
the simple server.  The esp8266 can be configured to run a remote repl to test python code.  Using mpfshell
files may be copied to the device.  A main.py copied to the root of the filesystem will run automatically
when the esp8266 chip boots up.  Additionally the esp8266 has a builtin led connected to pin0 for testing
and feedback.

## General esp8266 setup
A really usable version of the esp8266 chip maybe purchased here for < $20.  This version is easily powered
by a microusb connection:
https://www.adafruit.com/product/2821

## Prerequisites
The esp8266 on osx requires installing a usb to uart driver:
https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers

## Setup environment

To configure the esp8266 first setup an environment in python 2.7 for example using virtualenv.  Install
the mpfshell and esptool packages.

```bash
virtualenv env
source ./env/bin/activate
pip install -r requirements.txt
```

## Install micropython
Micropython can be installed on the chip by connecting a micro to your computer.  Verify a directory appears
as /dev/tty.SLAB_USBtoUART.  First erase the esp8266 then install micropython.  Download the latest esp8266
micropython binary here:
http://micropython.org/download#esp8266
For example for 1.9.3:
http://micropython.org/resources/firmware/esp8266-20171220-v1.9.3-203-gd8d633f1.bin

```bash
esptool.py -p /dev/tty.SLAB_USBtoUART erase_flash
esptool.py -p /dev/tty.SLAB_USBtoUART write_flash 0x000000 esp8266-*.bin
```

## Connect and configure esp8266
Now connect to the esp8266 micropython and configure wifi.

```bash
mpfshell
open tty.SLAB_USBtoUART
repl
print 'hello'
import network
wlan=network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("<ssid>","<password>")
wlan.ifconfig()
('10.10.4.69', '255.255.248.0', '10.10.0.1', '8.8.8.8')
import webrepl
E (for enable)
set a password
```

## Connect by wifi install server
After the esp8266 is configured on wifi restart the esp8266.  You can press the reset button.

```bash
cp deskserver.py main.py
mpfshell
open ws:10.10.4.69
put main.py
```

## General usage
Now from a browser of curl you may query the esp8266 server.

```bash
curl http://10.10.4.69/ping
pong  # tests connectivity
curl http://10.10.4.69/uptime
10m30s # shows how many minutes has been up
curl http://10.10.4.69/state
up # shows up or down the show the state of the desk
curl http://10.10.4.69/up
# goes up
curl http://10.10.4.69/down
# goes down
curl http://10.10.4.69/up
# goes up
```
