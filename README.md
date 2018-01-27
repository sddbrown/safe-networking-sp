# Read the Setup Instructions if you do not have an ElasticStack cluster (i.e. ElasticCloud or a local install)
[Infrastructure Setup Instructions](docs/infra-setup.md)


# Install & start the SafeNetworking Application
### 1. Clone repo
```git clone https://www.github.com/PaloAltoNetworks/safe-networking-sp.git```

### 2. Change into repo directory
```cd safe-networking-sp```

### 3. Create python 3.6 virtualenv
```python3.6 -m venv env```

### 4. Activate virtualenv
```source env/bin/activate```

### 5. Download required libraries
```pip install -r requirements.txt```

### 6. Deactivate the virutalenv (we will return to it later)
```deactivate```

### 7. Configure the .panrc for your installation
[Configuring SafeNetworking](docs/sfn-config.md)

### 8. Copy the SafeNetworking logstash configuration files to the logstash config directory
```
sudo cp install/logstash/sfn-dns.conf /etc/logstash/conf.d/
```
### 9. Edit the /etc/logstash/conf.d/sfn-dns.conf file and replace the "CHANGEME" with your logstash listener and elasticsearch server where appropriate (3 places)
Example Input and Output stanzas (the Filter stanza has been omitted for clarity)

```
input {
  http {
    host => "10.10.10.10"
    port => '9563'
    response_headers => {
      "Access-Control-Allow-Origin" => "*"
      "Content-Type" => "text/plain"
      "Access-Control-Allow-Headers" => "Origin, X-Requested-With, Content-Type, Accept"
     }
   }
 }

output {
  if "SFN-DNS" in [tags] {
    elasticsearch { 
      hosts => ["10.10.10.10:9200"]
      index => ["sfn-dns-event"]
    }
    stdout { codec => rubydebug }
  }
  else if "_grokparsefailure" in [tags] {
    elasticsearch { 
      hosts => ["10.10.10.10:9200"]
      index => ["sfn-dns-unknown"]
    }
    stdout { codec => rubydebug }
  }
  stdout { codec => rubydebug }
}
```

### 10. Install the index mappings into ElasticSearch
NOTE: The setup script runs against localhost. If ES is bound to a particular IP address, you will need to edit the file and change it to reflect that.
```
cd install
bash ./setup.sh
```
<br/><br/>

### 11. Configure the Firewall to send events
[NGFW Configuration](docs/NGFW/ngfw-configuration.md)

### 12. Start the portal  (make sure yoyu are in the safe-networking-sp directory)
```
source env/bin/activate
python ./sfn > log/console-\`date '%Y-%m-%d %H:%M:%S'\`.log 2>&1
```

### 13. Kibana setup
SafeNetworking is now running and processing events.  You will need to perfrom some minor post install setup in Kibana for the visualizations and dashboards.
[Kibana setup for SafeNetworking](docs/kibana-setup.md)

<br/><br/>
## Best Practices and Optional Configuration
You should be all set.  For even more ideas on what you can do with the system and other things that you can download and install to get the most out of SafeNetworking, checkout the [Wiki](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki)!!

