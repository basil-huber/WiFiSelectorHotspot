import re
import subprocess

INTERFACE_DEFAULT = 'wlan0'
HOSTAPD_CONF_DEFAULT = '/etc/hostapd.conf'
IFCONFIG_IP_REGEX = re.compile(r'inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')


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


class Hotspot:
    def __init__(self, conf_path=HOSTAPD_CONF_DEFAULT):
        self._process = None
        self._conf_path = conf_path

    def enable(self):
        if not self.is_enabled():
            self._process = subprocess.Popen(['hostapd', self._conf_path])

    def disable(self):
        if self.is_enabled():
            self._process.kill()
            self._process = None

    def is_enabled(self) -> bool:
        return self._process is not None
