#!/bin/bash

BUCKET=gs://d11-logging-bucket
REGION=us-east4
ZONE=us-east4-c
GOOGLE_CLOUD_PROJECT=d11-logging
WORKER_MACHINE_TYPE=e2-standard-2

TOPIC=logs
BOOTSTRAP_SERVERS=wwoo-kafka-broker-1:9092,wwoo-kafka-broker-2:9092,wwoo-kafka-broker-3:9092,wwoo-kafka-broker-4:9092,wwoo-kafka-broker-5:9092,wwoo-kafka-broker-6:9092,wwoo-kafka-broker-7:9092,wwoo-kafka-broker-8:9092,wwoo-kafka-broker-9:9092,wwoo-kafka-broker-10:9092,wwoo-kafka-broker-11:9092,wwoo-kafka-broker-12:9092
#NUM_10K_MESSAGES=2000
NUM_10K_MESSAGES=818
INTERVAL_IN_SECONDS=1
MAX_NUM_WORKERS=250
NUM_WORKERS=20

mvn compile exec:java -e \
    -Dexec.mainClass=com.google.cloud.demo.beam.MessageFanoutProducerPipeline \
    -Dexec.args="--runner=DataflowRunner \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$REGION \
    --workerZone=$ZONE \
    --autoscalingAlgorithm=THROUGHPUT_BASED \
    --gcpTempLocation=$BUCKET/producer/temp \
    --usePublicIps=false \
    --subnetwork=regions/$REGION/subnetworks/logging-cluster-vpc-subnet \
    --topic=$TOPIC \
    --bootstrapServers=$BOOTSTRAP_SERVERS \
    --num10KMessages=$NUM_10K_MESSAGES \
    --workerMachineType=$WORKER_MACHINE_TYPE \
    --enableStreamingEngine \
    --intervalInSeconds=$INTERVAL_IN_SECONDS \
    --maxNumWorkers=$MAX_NUM_WORKERS \
    --numWorkers=$NUM_WORKERS \
    --streaming=true"

# mvn compile exec:java -e \
#     -Dexec.mainClass=com.google.cloud.demo.beam.MessageFanoutProducerPipeline \
#     -Dexec.args="--runner=DataflowRunner \
#     --project=$GOOGLE_CLOUD_PROJECT \
#     --region=$REGION \
#     --workerZone=$ZONE \
#     --autoscalingAlgorithm=THROUGHPUT_BASED \
#     --gcpTempLocation=$BUCKET/temp \
#     --usePublicIps=false \
#     --subnetwork=regions/$REGION/subnetworks/default \
#     --topic=$TOPIC \
#     --bootstrapServers=$BOOTSTRAP_SERVERS \
#     -- =$USERNAME \
#     --password=$PASSWORD \
#     --numKMessages=$NUM_K_MESSAGES \
#     --workerMachineType=$WORKER_MACHINE_TYPE \
#     --enableStreamingEngine \
#     --intervalInSeconds=$INTERVAL_IN_SECONDS \
#     --streaming=true \
#     --update \
#     --jobName=messagefanoutproducerpipeline-wwoo-0314004410-e564e67c"
