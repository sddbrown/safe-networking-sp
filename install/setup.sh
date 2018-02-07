curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/af-details/' -d @elasticsearch/af-details.json

curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/sfn-dns-event/' -d @elasticsearch/sfn-dns-event.json

curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/sfn-domain-details/' -d @elasticsearch/sfn-domain-details.json

curl -XPUT -H'Content-Type: application/json' 'http://localhost:9200/sfn-tag-details/' -d @elasticsearch/sfn-tag-details.json

curl -XPUT -H'Content-Type: application/json' 'localhost:9200/_settings' -d '{"index" : {"number_of_replicas" : 0}}'
