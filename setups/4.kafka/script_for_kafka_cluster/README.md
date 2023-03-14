Pre-requisite:
- Zookeeper is setup
- Kafka image is available.

Steps for creating the cluster

1. Copy the 3 files locally i.e. in cloud shell of the respective project.
2. Modify the export.sh variables appropriately.
3. Change the permission of create_kafka_cluster.sh by running chmod +x create_kafka_cluster.sh
4. Modify the server_base.properties appropriately for any kafka config changes. Do not modify any line that has <<variable>>
5. Run ./create_kafka_cluster.sh
