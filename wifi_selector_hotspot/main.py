import logging
import sys
from logging.handlers import SysLogHandler
from time import sleep

from wifi_selector_hotspot.wifi_manager import network_interface_up, network_interface_is_connected, Hotspot, \
    network_interface_set_network, network_interface_set_ip_addr, network_interface_down
from wifi_selector_hotspot.wifi_selector_server import WifiSelectorServerThread

CONNECTION_TIMEOUT = 30  # seconds


def main():
    logging.basicConfig(handlers=[SysLogHandler(address='/dev/log'), logging.StreamHandler(sys.stdout)],
                        level=logging.DEBUG, format='%(levelname)s WifiSelectorHotspot:%(module)s %(message)s')

    server = WifiSelectorServerThread()
    server.start()
    logging.info('Server running')
    hotspot = Hotspot()

    logging.debug('enabling interface')
    network_interface_up()
    logging.debug('waiting for connection')
    sleep(CONNECTION_TIMEOUT)

    while not network_interface_is_connected():
        logging.info('Could not connect to WiFi. Starting Hotspot')
        logging.debug('restarting network interface with IP for Hotspot')
        network_interface_down()
        logging.debug('restarting network interface with IP for Hotspot')
        network_interface_set_ip_addr()
        logging.debug('enabling WiFi hotspot')
        hotspot.enable()
        logging.debug('Waiting for network parameters')
        essid, password = server.wait_for_network_parameters()
        logging.info(f'received network parameters: ESSID: {essid};  Password: {password}. Connecting')
        hotspot.disable()
        network_interface_down()
        network_interface_set_network(essid, password)
        network_interface_up()
        sleep(CONNECTION_TIMEOUT)
    logging.info('Connected')


if __name__ == '__main__':
    main()
