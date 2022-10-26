import os
import threading
from queue import Queue, Full
from typing import Tuple

from flask import Flask, request, redirect, url_for, render_template


class WifiSelectorServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.app = Flask(__name__)
        self.app.add_url_rule('/wifi_selector', view_func=self._select_wifi, methods=['GET', 'POST'])
        self.app.add_url_rule('/', view_func=self._select_wifi, methods=['GET', 'POST'])
        self.app.add_url_rule('/connecting/<essid>', view_func=self._connecting)

        self.network_parameter_queue = Queue()

    def _select_wifi(self):
        if request.method == 'POST':
            essid = request.form['essid']
            password = request.form['password']
            self._send_network_parameters(essid, password)
            return redirect(url_for('_connecting', essid=essid))
        else:
            return render_template('wifi_selector.html')

    def run(self) -> None:
        self.app.run(debug=True, use_reloader=False, threaded=False, port=8080, host='0.0.0.0')

    @staticmethod
    def _connecting(essid: str):
        return 'connecting to network %s' % essid

    def _send_network_parameters(self, essid: str, password: str) -> bool:
        try:
            self.network_parameter_queue.put(item=(essid, password), block=False)
            return True
        except Full:
            return False

    def wait_for_network_parameters(self) -> Tuple[str, str]:
        return self.network_parameter_queue.get()
