GET sfn-dns-event


GET sfn-dns-unknown/_search 
{
  "query": {
    "match_all": {}
  }
}

GET _search
{
  "query":{
    "bool": {
      "must": [
        {"match": {"threat_category": "dns"}},
        {"match": {"processed":"17"}}
     ]
    }
  },
  "sort": [
    {
      "received_at": {
        "order": "desc"
      }
    }
  ]
}

GET sfn-dns-event/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "threat_category": "wildfire"
          }
        },
        {
          "match": {
            "processed": "0"
          }
        }
      ]
    }
  },
  "sort": [
    {
      "received_at": {
        "order": "desc"
      }
    }
  ]
}
GET sfn-details
GET sfn-dns-unknown/_search
{
  "query": {
    "match_all": {}
  }
}

DELETE sfn-dns-event
DELETE sfn-dns
DELETE sfn-details

GET sfn-details/_search
{
  "query": {
    "match_all":{}
  }
}
GET sfn-details/_search
{
  "query": {
    "match": {"domain_name": "mkconsulting.com.tr"}
  }
}

POST sfn-details/domain-doc
{
  "domain_name": "mudsk.ddns.net",
  "last_updated": "2017/12/15 22:02:47",
  "processed": 0
}
PUT sfn-details
{
  "mappings": {
    "domain-doc": {
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "@version": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "domain_name": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "last_updated": {
          "type": "date",
          "format": "yyyy/MM/dd HH:mm:ss||yyyy/MM/dd||epoch_millis"
        },
        "processed": {
          "type": "byte",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        }
      }
    }
  }
}

PUT sfn-dns-event
{
  "mappings": {
    "doc": {
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "@version": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "device_name": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 128
            }
          }
        },
        "domain_name": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "dst_ip": {
          "type": "ip",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "host": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "msg_gen_time": {
          "type": "date",
          "format": "yyyy/MM/dd HH:mm:ss||yyyy/MM/dd||epoch_millis"
        },
        "sig_num": {
          "type": "integer",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "processed": {
          "type": "byte",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "received_at": {
          "type": "date"
        },
        "rule": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "src_ip": {
          "type": "ip",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "geoip": {
          "dynamic": true,
          "properties": {
            "ip": {
              "type": "ip"
            },
            "location": {
              "type": "geo_point"
            },
            "latitude": {
              "type": "half_float"
            },
            "longitude": {
              "type": "half_float"
            }
          }
        },
        "tags": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "threat_category": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "threat_id": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "threat_name": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        }
      }
    }
  }
}
}