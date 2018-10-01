import utime
from machine import Pin
from WiFi import WiFi

# only pins 0, 2, 4, 5, 12, 13, 14, 15, and 16
# pin 2 to BUILTINLED
wifi = WiFi.WiFi("/wifi.json")


def setup():
    wifi.begin()
    led = Pin(2, Pin.OUT)


def loop1():
    enabled = False
    while True:
        if enabled:
            led.off()
            utime.sleep_ms(1000)
            print("OFF")
        else:
            led.on()
            print("ON")
        utime.sleep_ms(300)
        enabled = not enabled


def loop():
    wifi.loop()


# ############################################### main
def main():
    while True:
        loop()


if __name__ == '__main__':
    setup()
    main()
