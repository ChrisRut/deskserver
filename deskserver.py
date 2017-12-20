import machine
import network
import ntptime
import socket
import sys
import time


class DeskServer():
    def __init__(self):
        # time difference hack to show time zone
        self.tzdiff = 5 * 60 * 60
        # listen port for http
        self.port = 80
        # time for desk to fully down up and down
        self.sleep_time_full = 12
        # when going down go fully down then go up small amount
        self.sleep_time_afterdown = 1
        self.test_pin = machine.Pin(0, machine.Pin.OUT)   # connect to red led, is switched
        self.up_pin = machine.Pin(14, machine.Pin.OUT)    # connected to UP relay, send low to connect
        self.down_pin = machine.Pin(12, machine.Pin.OUT)  # connected to DOWN relay, send low to connect
        # verify up and down pins are in the disengaged state
        self.up_pin.on()
        self.down_pin.on()

        # provide a list of ip addresses to respond to
        self.valid_ips = [
        ]
        self.state = "down"
        self.wlan = None  # initialize network in start_network
        # the template html page, use format to replace {} with message
        self.HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Desk Server</title>
</head>
<body>
<hr>
<h2>Desk</h2>
{}
</body>
</html>
        """

    def run(self):
        self.reset_time()
        self.test_pin.on()
        time.sleep(.5)
        for i in range(8):
            print("init: {}".format(self.toggle('test')))
            time.sleep(.5)
        self.test_pin.on()
        print("running server on {}".format(self.wlan.ifconfig()[0]))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', self.port))
        sock.listen(5)
        result = ""
        while result != "exiting":
            conn, addr = sock.accept()
            ipaddr = addr[0]
            if ipaddr not in self.valid_ips:
                print("got unauthorized connection from {}".format(ipaddr))
                conn.close()
                continue
            print("got a connection from {}".format(ipaddr))
            request = conn.recv(1024)
            data = str(request)
            print("request: {}".format(data))
            result = self.process(data)
            if result == 'test':
                result = "{} {}".format(result, self.toggle("test"))
            elif result == 'up':
                self.up()
            elif result == 'down':
                self.down()
            if result != "close":
                conn.send(self.HTML.format(result))
                conn.close()
        time.sleep(5)
        sock.close()

    def reset_time(self):
        self.wlan = network.WLAN(network.STA_IF)
        if not self.wlan.active():
            wlan.active(True)
        try:
            ntptime.settime()
        except:
            print("error calling ntptime")
        self.start_time = time.time()

    def get_time(self):
        ts = time.localtime(time.time() - self.tzdiff)
        secs = str(ts[5])
        if len(secs) == 1:
            secs = "0" + secs
        mins = str(ts[4])
        if len(mins) == 1:
            mins = "0" + mins
        date_str = "{}:{}:{} {}/{}".format(ts[3], mins, secs, ts[1], ts[2])
        return date_str

    def process(self, data):
        try:
            data = data.split(" ")[1][1:]
        except:
            data = "ping"
        if data == "favicon.ico":
            return "close"
        if data == "ping":
            return "pong"
        elif data in ['up', 'down', 'test']:
            return data
        elif data == 'state':
            return self.state
        elif data == 'uptime':
            uptimesec = time.time() - self.start_time
            days = int(uptimesec / (60 * 60 * 24))
            uptimesec = uptimesec % (60 * 60 * 24)
            hours = int(uptimesec / (60 * 60))
            uptimesec = uptimesec % (60 * 60)
            mins = int(uptimesec / 60)
            secs = int(uptimesec % 60)
            return '{}d{}h{}m{}s'.format(days, hours, mins, secs)
        elif data == 'upstate':
            self.state = 'up'
            return self.state
        elif data == 'downstate':
            self.state = 'down'
            return self.state
        elif data == 'resettime':
            self.reset_time()
            return "reset time"
        elif data == 'time':
            return "server time {}".format(self.get_time())
#        elif data == "exit":
#            return "exiting..."
        return "unknown command '{}' valid commands are ping,test,up,down,time,uptime,upstate,downstate,state".format(data)

    def up(self):
        if self.state == 'up':
            return
        self.test_pin.off()
        self.up_pin.off()
        time.sleep(self.sleep_time_full)
        self.up_pin.on()
        self.test_pin.on()
        self.state = 'up'

    def down(self):
        if self.state == 'down':
            return
        self.test_pin.off()
        self.down_pin.off()
        time.sleep(self.sleep_time_full)
        self.down_pin.on()
        self.up_pin.off()
        time.sleep(self.sleep_time_afterdown)
        self.up_pin.on()
        self.test_pin.on()
        self.state = 'down'

    def toggle(self, name):
        result = 'unknown'
        pin = self.test_pin
        if name == 'up':
            pin = self.up_pin
        elif name == 'down':
            pin = self.down_pin
        if pin.value() == 1:
            pin.off()
            result = 'off'
        else:
            pin.on()
            result = 'on'
        return result


if __name__ == '__main__':
    deskserver = DeskServer()
    try:
        deskserver.run()
    except:
        print(sys.exc_info())
        raise
