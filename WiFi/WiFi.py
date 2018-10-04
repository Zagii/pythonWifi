import machine
import ujson
import network
import utime


class WiFi:
    CHECK_RECONNECT = 5000
    confFile = "/wifi.json"
    lastConnTime = 0
    confail=0
    maxconfail=10
    ap_if = network.WLAN(network.AP_IF)  # accessPoint-> ESP=router
    sta_if = network.WLAN(network.STA_IF)  # station-> connection to router

    def __init__(self, conf):
        if conf is None:
            self.confFile = "/wifi.json"
        else:
            self.confFile = conf

    # def config
    CONFIG = {'myssid':
                [{'ssid': 'open.t-mobile.pl', 'pwd': ''},
                {'ssid': 'InstalujWirusa', 'pwd': 'BlaBlaBla123'},
                {'ssid': 'DOrangeFreeDom', 'pwd': 'KZagaw01_ruter_key'}],
              'AP': {'ssid': 'esp8266_test', 'pwd': '1234567'}}  # str(machine.unique_id())
    CONFIG_SSID_ID = 0

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
            self.sta_if.active(True)
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
        self.getBestWifi()

    def getBestWifi(self):
        s = self.sta_if.scan()
        # print('## przed ##')
        # print(str(s[0][0]) + " " + str(s[0][3]))
        # print(str(s[1][0]) + " " + str(s[1][3]))
        # print("##")
        s.sort(key=lambda x: x[3], reverse=True)

        # print([item[0] for item in s])
        # print("@@\n")
        # print([item[3] for item in s])

        # print('## po ##')
        # print(str(s[0][0]) + " " + str(s[0][3]))
        # print(str(s[1][0]) + " " + str(s[1][3]))
        # print("##")
        print("#### Lista WiFi ###")
        for i, member in enumerate(s):
            ss = str(s[i][0])[2:-1]
            print('i: ' + str(i) + ', ssid: '+ss)
        return s

    def getWiFiID(self):
        return self.CONFIG_SSID_ID

    def do_connect(self):
            status = self.sta_if.status()
            # print('status: ' + str(status) + '; confID: ' + str(self.CONFIG_SSID_ID))
            # STAT_IDLE – no connection and no activity,
            # STAT_CONNECTING – connecting in progress,
            # STAT_WRONG_PASSWORD – failed due to  incorrect password,
            # STAT_NO_AP_FOUND – failed because no access point replied,
            # STAT_CONNECT_FAIL – failed due to other problems,
            # STAT_GOT_IP – connection successful.

            if status == network.STAT_CONNECTING:
                print("...connecting...status=> "+str(status))
                utime.sleep_ms(500)
                return
            if status == network.STAT_GOT_IP:
                # print('network config:',  self.sta_if.ifconfig(),  " => "+str(status))
                return
            if status == network.STAT_CONNECT_FAIL:
                print("connect fail, reconnecting... ["+str(self.confail)+" / "+str(self.maxconfail)+"] status => "+str(status))

            if status == network.STAT_WRONG_PASSWORD:
                print("wrong password=> "+str(status))
            if status == network.STAT_NO_AP_FOUND:
                print("no_ap_found=> "+str(status))
                # print(self.getBestWifi())
                # utime.sleep_ms(10000)
                print('#############\n###################')

            if status in (network.STAT_WRONG_PASSWORD, network.STAT_CONNECT_FAIL, network.STAT_NO_AP_FOUND):
                self.CONFIG_SSID_ID = self.CONFIG_SSID_ID+1
                self.sta_if.disconnect()
                self.sta_if.active(False)
                self.sta_if.active(True)
                if self.CONFIG_SSID_ID >= len(self.CONFIG['myssid']):
                    self.CONFIG_SSID_ID = 0;
                return

            if status == network.STAT_IDLE:
                # print(self.sta_if.active())
                # print(self.ap_if.active())
                # scan best network
                i = self.getWiFiID()
                if i >= 0:
                    sid = self.CONFIG['myssid'][i]['ssid']
                    pwd = self.CONFIG['myssid'][i]['pwd']
                    print('connecting to network: "'+str(sid)+'" / "'+str(pwd)+'"')
                    self.sta_if.connect(sid, pwd)
                    # while not self.sta_if.isconnected():
                      #  tmpstat = self.sta_if.status()
                       # print(tmpstat)
                       # if tmpstat != network.STAT_CONNECTING:
                       #     break
                       # utime.sleep_ms(500)
                    # utime.sleep_ms(1000)
                    if not self.sta_if.isconnected():
                        print('..not connected..')
                    else:
                        print('network config:', self.sta_if.ifconfig())

    def loop(self):
        now = utime.ticks_ms()
        utime.sleep_ms(10)
        if utime.ticks_diff(now, self.lastConnTime) > self.CHECK_RECONNECT:
            self.do_connect()
            self.lastConnTime = now


