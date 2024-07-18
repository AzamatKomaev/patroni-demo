# patroni-demo

This repository contains everything to run PostgreSQL main-replica cluster via docker compose. Be free to explore docker compose and PostgreSQL configuration!

## How to start
Optionally run containers for monitoring:
```shell
$ docker compose -f ./monitoring-docker-compose.yml up -d
 ✔ Container prometheus                  Started                                                                                           1.3s 
 ✔ Container postgres-exporter           Started                                                                                           1.2s 
 ✔ Container postgres-exporter-replica1  Started                                                                                           1.3s 
 ✔ Container grafana                     Started 
```
After that you can navigate to http://localhost:3000, add Prometheus data source and import dashboards to monitor PostgreSQL instances.

### Running main + replicas (Without Patroni)
![PostgreSQLReplication](https://github.com/user-attachments/assets/1653df3c-f3dd-424b-bea9-5f542935945c)
Run main docker-compose.yml:
```shell
$ git checkout async-and-sync-replicas-replication
Switched to branch 'async-and-sync-replicas-replication'
$ docker compose up -d
 ✔ Container main      Started                                                                                                             0.9s 
 ✔ Container replica1  Started                                                                                                             0.9s 
 ✔ Container replica2  Started                                                                                                             1.0s 
 ✔ Container app       Started 
```
At this point main is ready to accept connections, but replicas are not configured. Each of PostgreSQL containers has own mount point from data/* 
directory to /var/lib/postgresql/data inside container. 

We need to create replication user, that will be used for connections by replicas:
```shell
$ PGPASSWORD=1234 psql \
    --host=localhost \
    --port=5432 \
    --username=user \
    db -c "CREATE USER replication REPLICATION LOGIN ENCRYPTED PASSWORD '1234';"
```
Look at the config/pg_hba.conf file. It has line, that allow replicas to connect to main via replication user:
```conf
host    replication     replication     172.16.0.0/12           scram-sha-256
```
Now we need to create base backup and restore the replicas with that backup:
```shell
$ docker compose exec -it replica1 su postgres
$ cd /var/lib/postgresql/
$ PGPASSWORD=1234 pg_basebackup --host=main --username=replication --pgdata=./main-backup --wal-method=stream --write-recovery-conf
$ rm -rf ./data/* && mv ./main-backup/* ./data
```
Repeat these commands for replica2. After removing data folder your container will be restarted. Delete postgresql.auto.conf because it contains 
configuration to connect to main that we already have in config/replica1.conf. After that restart container manually:
```shell
$ docker compose exec -it replica1 rm -rf /var/lib/postgresql/data/postgresql.auto.conf
$ docker compose restart replica1
```
Now check replication status by connection to main and executing command below:
```shell
$ PGPASSWORD=1234 psql \
        --host=localhost \
        --port=5432 \
        --username=user \
        db -c "SELECT usename, application_name, sync_state FROM pg_stat_replication;" 
   usename   | application_name | sync_state 
-------------+------------------+------------
 replication | replica1         | potential
 replication | replica2         | sync
(2 rows)
```

## Branches
| Branch Name | Components |  Description |
|-------------|-------------|-------------|
| one-async-replica-replication | main, replica1 (async) | Runs cluster with one synchronous replica |
| async-and-sync-replicas-replication | main, replica1 (async), replica2 (sync) | Runs cluster with two replicas one of which is asynchronous |
