# Read the Setup Instructions if you do not have an ElasticStack cluster (i.e. ElasticCloud or a local install)
[Infrastructure Setup Instructions](docs/infra-setup.md)


# Install & start the SafeNetworking Application
### 1. Clone repo
```git clone git@github.com:sdndude/safe-networking-sp.git```

### 2. Change into repo directory
```$ cd safe-networking-sp```

### 3. Create python 3.6 virtualenv
```$ python3.6 -m venv env```

### 4. Active virtualenv
```$ source env/bin/activate```

### 5. Download required libraries
```$ pip install -r requirements.txt```

### 6. Configure the .panrc for your installation
[Configuring SafeNetworking](docs/sfn-config.md) - this link is currently under construction. 

### 7. Copy the SafeNetworking logstash configuration files to the logstash config directory
```
sudo cp install/logstash/sfn-dns.conf /etc/logstash/conf.d/
```
### 8. Edit the /etc/logstash/conf.d/sfn-dns.conf file and replace the IP address(es) of your logstash listener and elasticsearch server where appropriate (3 places)
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

### 9. Install the index mappings into ElasticSearch
NOTE: Change localhost below to the IP address you bound ES to, if you did that in the Infrastructure Setup steps
```
curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/af-details/' -d @install/elasticsearch/af-details.json
```
```
curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/sfn-dns-event/' -d @install/elasticsearch/sfn-dns-event.json
```
```
curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/sfn-domain-details/' -d @install/elasticsearch/sfn-domain-details.json
```
```
curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/sfn-tag-details/' -d @install/elasticsearch/sfn-tag-details.json
```

###
### Start the portal
$ python ./sfn
