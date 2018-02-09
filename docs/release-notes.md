# Version 2.0.2
Release Date: 09 Feb 2018
<br/>
### New Features
New Kibana visualizations and Dashboards added for malware viewed by time <br/>
- import install/kibana/export.json via Kibana if you already have an install<br/>

Safenetworking now processes all threat categories with dns in the name (dns, dns-wildfire, etc.)

### Issues resolved
[Concurrency issue with af-details](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/30)<br/>
[SFN2.0.1 not populating sfn-domain-details index docs](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/62)<br/>
[Change "Not Available" verbage](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/60)<br/>
[Runner processDNS() search should be descending](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/64)<br/>
[Move documentation to the Wiki](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/36)<br/>
[sfn linting score](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/58)<br/>
[runner linting score](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/49)<br/>
[dnsutils linting score](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/48)<br/>
[dns linting score](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/47)<br/>
[views linting score](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/46)<br/>
[init linting score](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/45)<br/>
[instance empty directory](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/52)<br/>
[public = empty directory](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/51)<br/>
[cleanup unused directory](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/50)<br/>
[Unassigned shards error](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/32)<br/>
[Add new viz to 2.0.2](https://github.com/PaloAltoNetworks/safe-networking-sp/issues/70)<br/>

### Known issues
- Intermittently, there is a domain document concurrency error that will show up in the sfn.log as an ERROR and it will create subsequent ERROR messages as the system cannot work with the domain details document correctly.  To remedy this, as it *could* slow down performance, delete the domain document in question. Contact the account team or SP-Solutions with help on this matter.

<br/><br/><br/><br/>


# Version 2.0
Release Date: 17 Jan 2018

### New Features
Moved to ElasticStack (ELK) as the underlying architecture<br/>
New processing engine for DNS event<br/>
Ability to sync directly from Github with no VM download<br/>
Issue tracking via Github<br/>
Full documentation on install, startup and (some) troubleshooting<br/>

### Issues Resolved


### Known issues
- Intermittently, there is a concurrency error that will show up in the sfn.log as an ERROR and it will create subsequent ERROR messages as the system cannot work with the domain details document correctly.  To remedy this, as it *could* slow down performance, delete the domain document in question. Contact the account team or SP-Solutions with help on this matter.
