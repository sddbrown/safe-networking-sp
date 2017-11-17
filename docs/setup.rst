Use the following instructions to download, install, configure and deploy the ElasticStack to an Ubuntu 16.04 system.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SYSTEM SETUP
============

Install supporting tools and pkgs for Ubuntu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    sudo apt-get install apt-transport-https
    sudo apt-get install sysv-rc-conf


Get the release key for the ElasticStack software
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch |sudo apt-key add -

Create the ElasticStack repository listing for apt-get
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-6.x.list

JAVA 8
------

The ElasticStack depends on Java to run, so we need to make sure that we
have the Java 8 JDK installed before we install the stack.

::

    java -version

On systems with Java 8 installed, this command produces output similar
to the following:

.. code:: java

    java version "1.8.0_65"
    Java(TM) SE Runtime Environment (build 1.8.0_65-b17)
    Java HotSpot(TM) 64-Bit Server VM (build 25.65-b01, mixed mode)

***If*** Java needs to be installed or upgraded to Java 8 (Java 9 is NOT
supported)

::

    sudo apt-get update && sudo apt-get install default-jdk

*Rerun the java -version command to verify you now have Java 8
installed*

Install Elasticsearch, Logstash & Kibana 
---------------------------------------------------

::

    sudo apt-get update && sudo apt-get install elasticsearch 
    sudo apt-get update && sudo apt-get install kibana 
    sudo apt-get update && sudo apt-get install logstash 
    

ELASTICSEARCH CONFIGURATION AND STARTUP
=======================================

Edit the network.host setting (it is commented out) elasticsearch config file /etc/elasticsearch/elasticsearch.yml 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: json

    network.host: 0.0.0.0

Configure Elasticsearch to start with the system
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    sudo /bin/systemctl daemon-reload
    sudo /bin/systemctl enable elasticsearch.service

Start Elasticsearch
^^^^^^^^^^^^^^^^^^^

::

    sudo /bin/systemctl start elasticsearch.service

Verify Elasticsearch is running by issuing this at the command prompt
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    curl 127.0.0.1:9200

You should get JSON similar to the following:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: json

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

*If you see JSON similar to the above, Elasticsearch is now up and
running* 
|
|

KIBANA CONFIGURATION AND STARTUP
================================

Edit the elasticsearch.url setting (it is commented out) in the kibana config file /etc/kibana/kibana.yml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    elasticsearch.url:"http://localhost:9200"

Configure Kibana to start with the system
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    sudo /bin/systemctl daemon-reload
    sudo /bin/systemctl enable kibana.service


Start Kibana
^^^^^^^^^^^^

::

    sudo /bin/systemctl start kibana.service

**NOTE:** The above commands provide no feedback as to whether Kibana was started successfully or not. Instead, this information will be written in the log files located in /var/log/kibana

Check to make sure Kibana is running by opening this link on the server: http://localhost:5601

*If you see the Kibana UI, Kibana is now up and running*

|
|
LOGSTASH CONFIGURATION AND STARTUP
==================================

Edit the LS_USER setting (it is logstash by default) in the logstash startup.options file /etc/logstash/startup.options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    LS_USER=root

Configure Logstash to start with the system
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

     sudo /bin/systemctl daemon-reload
     sudo /bin/systemctl enable logstash.service

Start Logstash
^^^^^^^^^^^^^^

::

     sudo /bin/systemctl start logstash.service
