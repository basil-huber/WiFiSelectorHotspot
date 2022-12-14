import re
import subprocess

INTERFACE_DEFAULT = 'wlan0'
HOSTAPD_CONF_DEFAULT = '/etc/hostapd.conf'
DHCPD_CONF_DEFAULT = '/etc/udhcpd.conf'
HOST_IP_DEFAULT = '192.168.2.1'
NETMASK_DEFAULT = '255.255.255.0'
IFCONFIG_IP_REGEX = re.compile(r'inet addr:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')


def network_interface_up(interface_name=INTERFACE_DEFAULT):
    subprocess.check_output(['ifup', interface_name])


def network_interface_down(interface_name=INTERFACE_DEFAULT):
    subprocess.check_output(['ifdown', interface_name])


def network_interface_is_connected(interface_name=INTERFACE_DEFAULT):
    output = subprocess.check_output(['ifconfig', interface_name]).decode()
    return IFCONFIG_IP_REGEX.search(output) is not None


def network_interface_set_network(essid, password):
    with open('/etc/wpa_supplicant.conf', 'w') as output_file:
         subprocess.check_call(['wpa_passphrase', essid, password], stdout=output_file)


def network_interface_set_ip_addr(interface_name=INTERFACE_DEFAULT, ip_addr=HOST_IP_DEFAULT, netmask=NETMASK_DEFAULT):
    subprocess.check_output(['ifconfig', interface_name, 'up', ip_addr, 'netmask', netmask])


class Hotspot:
    def __init__(self, hostapd_conf_path=HOSTAPD_CONF_DEFAULT, dhcpd_conf_path=DHCPD_CONF_DEFAULT):
        self._hostapd_process = None
        self._dhcpd_process = None
        self._hostapd_conf_path = hostapd_conf_path
        self._dhcpd_conf_path = dhcpd_conf_path

    def enable(self):
        if not self.is_enabled():
            self._dhcpd_process = subprocess.Popen(['udhcpd', '-S', '-f', self._dhcpd_conf_path])
            self._hostapd_process = subprocess.Popen(['hostapd', '-s', self._hostapd_conf_path])

    def disable(self):
        if self.is_enabled():
            self._hostapd_process.kill()
            self._hostapd_process = None
            self._dhcpd_process.kill()
            self._dhcpd_process = None

    def is_enabled(self) -> bool:
        return self._hostapd_process is not None
