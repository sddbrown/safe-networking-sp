# Read the Setup Instructions if you do not have an ElasticStack cluster (i.e. ElasticCloud or a local install)
[Infrastructure Setup Instructions](docs/infra-setup.md)

# If this is a demo system, there are a couple more steps needed so that the infrastructure has data to work with
### NOTE: This is only needed for demos.  PoCs and Test/Production will not need this step
[Demo Setup](docs/demo-setup.md)


# Install & start the SafeNetworking Application
###### 1. Clone repo
```git clone git@github.com:sdndude/safe-networking-sp.git```

###### 2. Change into repo directory
```$ cd safe-networking-sp```

###### 3. Create python 3.6 virtualenv
```$ python3.6 -m venv env```

###### 4. Active virtualenv
```$ source env/bin/activate```

###### 5. Download required libraries
```$ pip install -r requirements.txt```

###### 6. Edit instance/sfn.cfg for your installation
[Configuring SafeNetworking](docs/sfn-config.md) - this link is currently under construction. 


###### 7. Start the portal
$ python ./sfn
