# Open-CoNtRol, an open source web Chemical Reaction Network visualizer.

Please note pygraphviz has to be installed *beforehad*. So if you're not on unix (for some reason) meaning the bellow command doesn't work, please consult the installation guides [here](https://pygraphviz.github.io/documentation/stable/install.html).

## To run the flask web app:
```bash
git clone https://github.com/viktorashi/Open-CoNtRol.git
cd Open-CoNtRol
#this needs to be done beforehand
sudo apt-get install graphviz graphviz-dev
pip install pygraphviz
pip install -r requirements.txt
chmod +x ./run_script.sh
./run_script.sh
```
## Or simply, if you just want to run it without contributing, create a virtualenv however way you want ( [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/stable/install.html#basic-installation) recommended by yours truly) and install it there as a package with:
```bash
pip install git+https://github.com/viktorashi/Open-CoNtRol.git
flask --app open_control --debug run
```
### In the above case you can't really configure the host ip adress that the server will be running on like in the first example. In order to do that you'd need to download at least the script "run_script.sh" from the repo then give it execute permissions and run with
```bash
chmod +x ./run_script.sh
./run_script.sh
```
