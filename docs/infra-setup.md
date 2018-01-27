### Use the following instructions to download, install, configure and deploy the ElasticStack 6.x to an Ubuntu 16.04 system.  


# SYSTEM SETUP 
</br>

#### Install supporting tools and pkgs for Ubuntu
```
sudo apt-get install software-properties-common python-software-properties
sudo add-apt-repository ppa:git-core/ppa
sudo apt-get update && sudo apt-get install apt-transport-https sysv-rc-conf curl git
```

#### Get the release key for the ElasticStack software
```
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch |sudo apt-key add -
```

#### Create the ElasticStack repository listing for apt-get
```
echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-6.x.list
```
</br>


## Python 3.6
SafeNetworking requires Python 3.6 to run properly.  
```
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt-get update && sudo apt-get install python3.6
```
SafeNetworking also requires the use of virtualenvs to run properly.
```
sudo apt-get install python3.6-venv
```

## JAVA 8
The ElasticStack depends on Java to run, so we need to make sure that we have the Java 8 JDK installed before we install the stack.
```
java -version
```
On systems with Java 8 installed, this command produces output similar to the following:
```java
java version "1.8.0_65"
Java(TM) SE Runtime Environment (build 1.8.0_65-b17)
Java HotSpot(TM) 64-Bit Server VM (build 25.65-b01, mixed mode)
```
***If*** Java needs to be installed or upgraded to Java 8 (Java 9 is NOT supported)
```
sudo apt-get update && sudo apt-get install default-jdk
```
*Rerun the java -version command to verify you now have Java 8 installed*
</br>
</br>

## Install Elasticsearch, Logstash & Kibana
```
sudo apt-get update && sudo apt-get install elasticsearch 
sudo apt-get update && sudo apt-get install kibana 
sudo apt-get update && sudo apt-get install logstash 
```

## Set apt to hold the versions so it doesn't inadvertently update
```
sudo apt-mark hold elasticsearch
sudo apt-mark hold kibana
sudo apt-mark hold logstash
```

</br>
</br>



# ELASTICSEARCH CONFIGURATION AND STARTUP

#### Edit the network.host setting (it is commented out) elasticsearch config file as root - sudo /etc/elasticsearch/elasticsearch.yml </br>
```json
network.host: 0.0.0.0
```
</br>

#### Configure Elasticsearch to start with the system
```
sudo /bin/systemctl daemon-reload
sudo /bin/systemctl enable elasticsearch.service
```

#### Start Elasticsearch
```
sudo /bin/systemctl start elasticsearch.service
```

#### Verify Elasticsearch is running by issuing this at the command prompt
```
curl 127.0.0.1:9200
```
#### You should get JSON similar to the following:
```json
{
  "name" : "jeXSgYs",
  "cluster_name" : "elasticsearch",
  "cluster_uuid" : "BJz9KAv0QiCxhtsayKFZcQ",
  "version" : {
    "number" : "5.6.2",
    "build_hash" : "57e20f3",
    "build_date" : "2017-09-23T13:16:45.703Z",
    "build_snapshot" : false,
    "lucene_version" : "6.6.1"
  },
  "tagline" : "You Know, for Search"
}
```
*If you see JSON similar to the above, Elasticsearch is now up and running*
</br>
</br>


# KIBANA CONFIGURATION AND STARTUP
#### Edit the elasticsearch.url setting (it is commented out) in the kibana config file as root - sudo /etc/kibana/kibana.yml 
```python
elasticsearch.url:"http://localhost:9200"
```
</br>

#### Configure Kibana to start with the system
```
sudo /bin/systemctl daemon-reload
sudo /bin/systemctl enable kibana.service
```

#### Start Kibana
```
sudo /bin/systemctl start kibana.service
```

##### NOTE: The above commands provide no feedback as to whether Kibana was started successfully or not. Instead, this information will be written in the log files located in /var/log/kibana

#### Check to make sure Kibana is running by opening this link on the server: http://localhost:5601

*If you see the Kibana UI, Kibana is now up and running*
</br>
</br>


# LOGSTASH CONFIGURATION AND STARTUP
#### Edit the LS_USER setting (it is logstash by default) in the logstash startup.options file /etc/logstash/startup.options 
```python
LS_USER=root
```

#### Create a symbolic link for the configuration for logstash (becasue, apparently, it is stupid)
```
sudo ln -s /etc/logstash /usr/share/logstash/config
```
</br>


#### Configure Logstash to start with the system
```
sudo /bin/systemctl daemon-reload
sudo /bin/systemctl enable logstash.service
```

#### Start Logstash
```
sudo /bin/systemctl start logstash.service
```

# NGINX CONFIGURATION AND STARTUP
#### Because we configured Kibana to listen on localhost, we must set up a reverse proxy to allow external access to it. We will use Nginx for this purpose.

##### Install Nginx and Apache2-utils:
```
sudo apt-get install nginx apache2-utils
```
##### Use htpasswd to create an admin user, called "sfnadmin" (or whatever you want), that can access the Kibana web interface:
```
sudo htpasswd -c /etc/nginx/htpasswd.users sfnadmin
```
##### Enter a password at the prompt. Remember this login, as you will need it to access the Kibana web interface.

##### Edit the nginx server block file /etc/nginx/sites-available/default   
##### Delete the file's contents, and paste the following code block into the file. Be sure to update the server_name to match your server's name and use whatever port you want it to listen it on:
```
    server {
        listen 80;

        server_name example.com;

        auth_basic "Restricted Access";
        auth_basic_user_file /etc/nginx/htpasswd.users;

        location / {
            proxy_pass http://localhost:5601;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;        
        }
    }
```
##### Now restart Nginx so it listens on the port:
```
sudo service nginx restart
```

##### Kibana should now be accessible via your FQDN or the public IP address of your ELK Server i.e. http://elk-server-public-ip/. If you go there in a web browser, after entering the "sfnadmin" credentials, you should see a Kibana welcome page.


#### You are now done with the infrastructure setup.  The rest of the SafeNetworking setup depends on cloning this repository.  Head back, from whence you came, and read the rest of the [README](https://github.com/PaloAltoNetworks/safe-networking-sp) to finish the install.  