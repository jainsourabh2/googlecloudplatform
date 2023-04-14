#!/bin/bash

BUCKET=gs://wwoo-sandbox
REGION=us-central1
ZONE=us-central1-f
GOOGLE_CLOUD_PROJECT=wwoo-sandbox
WORKER_MACHINE_TYPE=e2-standard-2

TOPIC=logs
BOOTSTRAP_SERVERS=kafka-cluster-1-kafka-0.c.wwoo-sandbox.internal:9092
# NUM_MESSAGES=19800000
NUM_MESSAGES=19800
INTERVAL_IN_SECONDS=1

# TESTING ONLY
USERNAME=user
PASSWORD=ChathacM9hth
# TESTING ONLY

# mvn compile exec:java -e \
#     -Dexec.mainClass=com.google.cloud.demo.beam.MessageProducerPipeline \
#     -Dexec.args="--runner=DataflowRunner \
#     --project=$GOOGLE_CLOUD_PROJECT \
#     --region=$REGION \
#     --workerZone=$ZONE \
#     --autoscalingAlgorithm=THROUGHPUT_BASED \
#     --maxNumWorkers=10 \
#     --gcpTempLocation=$BUCKET/temp \
#     --usePublicIps=false \
#     --subnetwork=regions/$REGION/subnetworks/default \
#     --topic=$TOPIC \
#     --bootstrapServers=$BOOTSTRAP_SERVERS \
#     --username=$USERNAME \
#     --password=$PASSWORD \
#     --numMessages=$NUM_MESSAGES \
#     --workerMachineType=$WORKER_MACHINE_TYPE \
#     --intervalInSeconds=$INTERVAL_IN_SECONDS"

mvn compile exec:java -e \
    -Dexec.mainClass=com.google.cloud.demo.beam.MessageFanoutProducerPipeline \
    -Dexec.args="--runner=DataflowRunner \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$REGION \
    --workerZone=$ZONE \
    --autoscalingAlgorithm=THROUGHPUT_BASED \
    --maxNumWorkers=20 \
    --gcpTempLocation=$BUCKET/temp \
    --usePublicIps=false \
    --subnetwork=regions/$REGION/subnetworks/default \
    --topic=$TOPIC \
    --bootstrapServers=$BOOTSTRAP_SERVERS \
    --username=$USERNAME \
    --password=$PASSWORD \
    --numMessages=$NUM_MESSAGES \
    --workerMachineType=$WORKER_MACHINE_TYPE \
    --enableStreamingEngine \
    --intervalInSeconds=$INTERVAL_IN_SECONDS"