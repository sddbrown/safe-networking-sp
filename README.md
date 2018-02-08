# Read the Setup Instructions if you do not have an ElasticStack cluster (i.e. ElasticCloud or a local install)
[Infrastructure Setup Instructions](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki/Infrastructure-Setup)


# Install & start the SafeNetworking Application
### 1. Clone repo
```git clone https://www.github.com/PaloAltoNetworks/safe-networking-sp.git```
<br/><br/>
### 2. Change into repo directory
```cd safe-networking-sp```
<br/><br/>
### 3. Create python 3.6 virtualenv
```python3.6 -m venv env```
<br/><br/>
### 4. Activate virtualenv
```source env/bin/activate```
<br/><br/>
### 5. Download required libraries
```pip install -r requirements.txt```
<br/><br/>
### 6. Deactivate the virutalenv (we will return to it later)
```deactivate```
<br/><br/>
### 7. Configure the .panrc for your installation
[Configuring SafeNetworking](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki/Default-.panrc-configuration-file)
<br/><br/>
### 8. Copy the SafeNetworking logstash configuration files to the logstash config directory
```
sudo cp install/logstash/sfn-dns.conf /etc/logstash/conf.d/
```
<br/><br/>
### 9. Edit the /etc/logstash/conf.d/sfn-dns.conf file and replace the "CHANGEME" with your logstash listener and elasticsearch server where appropriate (3 places)
Example Input and Output stanzas.  Do not delete any of the lines. The filter stanza has been omitted and only sections of the input and output stanzas are show for clarity.

```
input {
  http {
    host => "10.10.10.10"
    port => '9563'
...

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
...
```
<br/><br/>
### 10. Install the index mappings into ElasticSearch
NOTE: The setup script runs against localhost. If ES is bound to a particular IP address, you will need to edit the file and change it to reflect that.
```
cd install
bash ./setup.sh
```
<br/><br/>

### 11. Configure the Firewall to send events
[NGFW Configuration](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki/NGFW-Configuration)
<br/><br/>
### 12. Start the portal  (make sure you are in the safe-networking-sp directory)
```
source env/bin/activate
python ./sfn >log/console-"$(date +"%Y-%d-%m %H:%M:%S").log" 2>&1
```
#### NOTE: The above two commands is how you will start it from now on.
<br/><br/>
### 13. Kibana setup
SafeNetworking is now running and processing events.  You will need to perfrom some minor post install setup in Kibana for the visualizations and dashboards.
[Kibana setup for SafeNetworking](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki/Kibana-post-install-setup)

<br/><br/>
## Best Practices and Optional Configuration
You should be all set.  For even more ideas on what you can do with the system and other things that you can download and install to get the most out of SafeNetworking, checkout the [Wiki](https://github.com/PaloAltoNetworks/safe-networking-sp/wiki)!!
