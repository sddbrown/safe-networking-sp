# SYSTEM SETUP 
</br>

#### Install supporting tools and pkgs for Ubuntu
```
sudo apt-get install apt-transport-https
sudo apt-get install sysv-rc-conf
```

#### Get the rlease key for the syslog-ng software
```
wget -qO - http://download.opensuse.org/repositories/home:/laszlo_budai:/syslog-ng/xUbuntu_16.04/Release.key | sudo apt-key add -
```

#### Create the syslog-ng repository listing for apt-get
```
echo "deb http://download.opensuse.org/repositories/home:/laszlo_budai:/syslog-ng/xUbuntu_16.04 ./" | sudo tee -a /etc/apt/sources.list.d/syslog-ng.list
```

#### Get the release key for the ElasticStack software
```
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch |sudo apt-key add -
```

#### Create the ElasticStack repository listing for apt-get
```
echo "deb https://artifacts.elastic.co/packages/5.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-5.x.list
```
</br>

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

## Install Elasticsearch, Logstash, Kibana & syslog-ng
 ```
 sudo apt-get update && sudo apt-get install elasticsearch 
 sudo apt-get update && sudo apt-get install kibana 
 sudo apt-get update && sudo apt-get install logstash 
 sudo apt-get update && sudo apt-get install syslog-ng-core
 ```
</br>
</br>



# ELASTICSEARCH CONFIGURATION AND STARTUP

#### Edit the elasticsearch config file network.host setting (it is commented out in the file)
/etc/elasticsearch/elasticsearch.yml </br>

<span style="color:cyan">
     network.host:
</span>
<span style="color:orange"> 
      0.0.0.0
</span>
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

#### Check to make sure Elasticsearch is running
```
curl 127.0.0.1:9200
```
#### You should get JSON similar to the following:
```
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
#### Edit the kibana config file elasticsearch.url setting (it is commented out in the file)
/etc/kibana/kibana.yml 
</br>

<span style="color:cyan">
     elasticsearch.url:
</span>
<span style="color:orange"> 
      "http://localhost:9200"
</span>
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
#### Edit the logstash startup.options file LS_USER setting (it is set to the user logstash by default)
/etc/logstash/startup.options 
</br>

<span style="color:cyan">
     LS_USER:
</span>
<span style="color:orange"> 
      root
</span>
</br>

#### Configure Kibana to start with the system
     sudo /bin/systemctl daemon-reload
     sudo /bin/systemctl enable logstash.service

#### Start Kibana
     sudo /bin/systemctl start kibana.service

