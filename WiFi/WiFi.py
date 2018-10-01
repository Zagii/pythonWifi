import machine
import ujson
import network
import utime


class WiFi:
    CHECK_RECONNECT = 10000
    confFile = "/wifi.json"
    lastConnTime = 0
    sta_if = network.WLAN(network.STA_IF)  # station-> connection to router
    ap_if = network.WLAN(network.AP_IF)  # accessPoint-> ESP=router

    def __init__(self, conf):
        if conf is None:
            self.confFile = "/wifi.json"
        else:
            self.confFile = conf

    # def config
    CONFIG = {"myssid":
            [{"ssid": "open.t-mobile.pl", "pwd": ""},
                   {"ssid": "DOrangeFreeDom", "pwd": "KZagaw01_ruter_key"}],
              "AP": {"ssid": "esp8266_test", "pwd": "1234567"}}  # str(machine.unique_id())

    def load_config(self):
        try:
            with open(self.confFile) as f:
                config = ujson.loads(f.read())
        except (OSError, ValueError):
            print("Couldn't load " + self.confFile)
            self.save_config()
        else:
            self.CONFIG.update(config)
            self.sta_if.active(False)
            print("Loaded config from " + self.confFile)
            self.ap_if.config(essid=self.CONFIG['AP']['ssid'])
         #   self.ap_if.config(password=self.CONFIG['AP']['pwd'])

    def save_config(self):
        try:
            with open(self.confFile, "w") as f:
                f.write(ujson.dumps(self.CONFIG))
        except OSError:
            print("Couldn't save " + self.confFile)

    def begin(self):
        self.load_config()
        self.lastConnTime = - self.CHECK_RECONNECT

    def getBestWifi(self):
        s = self.sta_if.scan()
        print('## przed ##')
        print(str(s[0][0]) + " " + str(s[0][3]))
        print(str(s[1][0]) + " " + str(s[1][3]))
        print("##")
        s.sort(key=lambda x: x[3], reverse=True)

        # print([item[0] for item in s])
        # print("@@\n")
        # print([item[3] for item in s])

        print('## po ##')
        print(str(s[0][0]) + " " + str(s[0][3]))
        print(str(s[1][0]) + " " + str(s[1][3]))
        print("##")

       # for i, member in enumerate(s):
      #      ss = str(s[i][0])[2:-1]
       #     print('i: ' + i + 'ssid:'+ss)
            #  if(ss in self.CONFIG['myssid'])
        return 1

    def do_connect(self):
            print(self.sta_if.active())
            print(self.ap_if.active())
            if self.sta_if.isconnected():
                return
            self.sta_if.active(True)
            # scan best network
            i = self.getBestWifi()
            if i >= 0:
                sid = self.CONFIG['myssid'][i]['ssid']
                pwd = self.CONFIG['myssid'][i]['pwd']
                sid = 'DOrangeFreeDom'
                pwd = 'KZagaw01_ruter_key'
                print('connecting to network: '+sid+' / '+pwd)
                self.sta_if.connect(sid, pwd)
                utime.sleep_ms(1000)
                if not self.sta_if.isconnected():
                    print('..not connected..')
                else:
                    print('network config:', self.sta_if.ifconfig())


    def loop(self):
        now = utime.ticks_ms()
        if utime.ticks_diff(now, self.lastConnTime) > self.CHECK_RECONNECT:
            self.do_connect()
            self.lastConnTime = now


