import osimport subprocessfrom flask import Flaskapp = Flask(__name__, template_folder='templates')import open_control.viewsprint('now working in the app: ')print(__name__)app.secret_key = os.urandom(24)#create the needed  files for storing the reactionsopen_control_folder = "open_control"templates = "templates"methode_lucru = "metode_lucru"crn = "crn.txt"folder_to_create = os.path.join(open_control_folder, templates, methode_lucru)file_path = os.path.join(folder_to_create , crn)try:    # Create the folder if it doesn't exist    os.makedirs(folder_to_create)    # Create and write to the file inside the folder    with open(file_path, "w") as file:        file.write("")    print(f"Folder '{folder_to_create}' and file '{file_path}' created successfully.")except FileExistsError:    print(f"Folder '{folder_to_create}' already exists.")    if not os.path.exists(file_path):        with open(file_path, "w") as file:            file.write("")            print(f"File '{file_path}' created successfully.")    else:        print(f"File '{file_path}' already exists as well.")if __name__ == 'open_control':    passif __name__ == '__main__':    pass# ---------------------------------------# US ip     10.0.0.50, port:5000# campus ip 172.30.5.50, port:5000# Ro ip     192.168.1.50, port:5000