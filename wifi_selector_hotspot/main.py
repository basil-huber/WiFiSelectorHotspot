import logging
import sys
import threading
import time
from logging.handlers import SysLogHandler
from time import sleep
import RPi.GPIO as GPIO

from wifi_selector_hotspot.wifi_manager import network_interface_up, network_interface_is_connected, Hotspot, \
    network_interface_set_network, network_interface_set_ip_addr, network_interface_down, WifiManager
from wifi_selector_hotspot.wifi_selector_server import WifiSelectorServerThread

CONNECTION_TIMEOUT = 30  # seconds
WIFI_RESET_BUTTON_CHANNEL = 18


class WifiResetButton:
    """ Thread to detect button pressing

    Using a dedicated polling thread to avoid problems with debounce """
    LONG_PRESS_TIME = 10

    def __init__(self, button_gpio_channel, long_press_callback):
        self._press_timestamp = None
        self._long_press_callback = long_press_callback
        self._gpio_channel = button_gpio_channel
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(button_gpio_channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        threading.Thread(target=self.main_loop).start()

    def main_loop(self):
        while True:
            if GPIO.input(self._gpio_channel) == GPIO.HIGH:
                if not self._press_timestamp:
                    self._press_timestamp = time.time()
                    logging.debug('Button pressed')
                elif time.time() - self._press_timestamp > self.LONG_PRESS_TIME:
                    logging.debug('Long press')
                    self._press_timestamp = None
                    if self._long_press_callback:
                        self._long_press_callback()
            else:
                self._press_timestamp = None
            time.sleep(1)


def main():
    logging.basicConfig(handlers=[SysLogHandler(address='/dev/log'), logging.StreamHandler(sys.stdout)],
                        level=logging.DEBUG, format='%(levelname)s WifiSelectorHotspot:%(module)s %(message)s')

    server = WifiSelectorServerThread()
    server.start()
    logging.info('Server running')
    wifi_manager = WifiManager()
    WifiResetButton(WIFI_RESET_BUTTON_CHANNEL, wifi_manager.enable_hotspot)

    while True:
        logging.debug('Waiting for network parameters')
        essid, password = server.wait_for_network_parameters()
        logging.info(f'received network parameters: ESSID: {essid}. Connecting...')
        network_interface_set_network(essid, password)
        wifi_manager.disable_hotspot()


if __name__ == '__main__':
    main()
