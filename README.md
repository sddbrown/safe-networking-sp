# Read the Setup Instructions if you do not have an ElasticStack cluster (i.e. ElasticCloud or a local install)
[Setup Instructions](docs/setup.md)
# Start the SafeNetworking Application
###### 1. Clone repo
git clone git@github.com:sdndude/safe-networking-sp.git

###### 2. Change into repo directory
$ cd safe-networking-sp

###### 3. Create python 3.6 virtualenv (install python 3.6 if you do not have it)
$ python3.6 -m venv env

###### 4. Active virtualenv
$ source env/bin/activate

###### 5. Download required libraries
$ pip install -r requirements.txt

###### 6. Edit instance/sfn.cfg for your installation
[Configuring SafeNetworking](docs/sfn-config.rst)

###### 7. Start the portal
$ python ./sfn
