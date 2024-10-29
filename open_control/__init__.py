import os
import subprocess
from flask import Flask

app = Flask(__name__, template_folder='templates')

import open_control.views

print('aplicatia in care mergem acm:')
print(__name__)

if __name__ == 'open_control':
    ip = 0
    try:
        ip = subprocess.check_output(["ifconfig en0 | grep 'inet'| awk '{print$2}'"], shell=True, text=True).split("\n")[1].strip()
        #ca nu exista index 1 daca nu ai interfete pornite
    except IndexError:
        try:
            ip = subprocess.check_output(["ifconfig ens33 | grep 'inet'| awk '{print$2}'"], shell=True, text=True).split("\n")[1].strip()
        except IndexError:
            try:
                ip = subprocess.check_output(["ifconfig ens37 | grep 'inet'| awk '{print$2}'"], shell=True, text=True).split("\n")[1].strip()
            except IndexError:
                ip = '127.0.0.1'
                print('nu cred ca ai netu pornit da-i ca ok dam pe localhost')

    app.secret_key = os.urandom(24)
    '''
    indented because of 
    * Ignoring a call to 'app.run()' that would block the current 'flask' CLI command.
   Only call 'app.run()' in an 'if __name__ == "__main__"' guard.
    '''
    port = 5000
    app.run(host=ip, port=port, debug=True)

# ---------------------------------------

# US ip     10.0.0.50, port:5000
# campus ip 172.30.5.50, port:5000
# Ro ip     192.168.1.50, port:5000
