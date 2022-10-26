import logging
from time import sleep

from wifi_selector_hotspot.wifi_manager import network_interface_up, network_interface_is_connected, Hotspot, \
    network_interface_set_network, network_interface_set_ip_addr, network_interface_down
from wifi_selector_hotspot.wifi_selector_server import WifiSelectorServerThread

CONNECTION_TIMEOUT = 30  # seconds


def main():
    server = WifiSelectorServerThread()
    server.start()
    hotspot = Hotspot()

    network_interface_up()
    sleep(CONNECTION_TIMEOUT)

    while not network_interface_is_connected():
        network_interface_set_ip_addr()
        hotspot.enable()
        logging.info('enabling WiFi Hotspot. Waiting for network parameters')
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
