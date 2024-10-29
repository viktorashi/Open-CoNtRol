import os
import subprocess
from flask import Flask

app = Flask(__name__, template_folder='templates')

import open_control.views

print('aplicatia in care mergem acm:')
print(__name__)

if __name__ == 'open_control':
    app.secret_key = os.urandom(24)

# ---------------------------------------

# US ip     10.0.0.50, port:5000
# campus ip 172.30.5.50, port:5000
# Ro ip     192.168.1.50, port:5000
