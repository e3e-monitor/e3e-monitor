#e3e-vagrant


This development environment is for THE Port Hackathon participants of the E3E team.

##Usage


To start the environment

    vagrant up

To add all the tools and programs (or to update them), use the following.

    vagrant provision

Make sure to run both of these commands the first time you run the environment, otherwise you won't have any tools.

To access the machine for development,

    vagrant ssh
    
Currently, there are no volumes that are mounted out, so development must be done within the vagrant environemnt. Mounted volumes can be configured in the Vagrantfile ([docs](https://docs.vagrantup.com/v2/synced-folders/basic_usage.html))

##Verification

Once the environment is running, you can browse to [localhost:9200](http://localhost:9200) to see that elasticsearch is up and running.

You should see something like

```
{
  "status" : 200,
  "name" : "Psi-Lord",
  "cluster_name" : "elasticsearch",
  "version" : {
    "number" : "1.7.2",
    "build_hash" : "e43676b1385b8125d647f593f7202acbd816e8ec",
    "build_timestamp" : "2015-09-14T09:49:53Z",
    "build_snapshot" : false,
    "lucene_version" : "4.10.4"
  },
  "tagline" : "You Know, for Search"
}
```

You can also browse to [localhost:5601](http://localhost:5601) to see kibana. Currently, there is no data that is sent to elasticsearch, so you can't play with Kibana much. But this might be useful for at least becomig familiar with the interface.
