#!/bin/bash

BUCKET=gs://d11-logging-bucket
REGION=us-east4
ZONE=us-east4-c
GOOGLE_CLOUD_PROJECT=d11-logging
REPOSITORY=d11
WORKER_MACHINE_TYPE=n1-standard-2
NUM_WORKERS=500
MAX_WORKERS=500
MIN_WORKERS=350

TOPIC=logs
CONSUMER_GROUP_ID=message-consumer-pipeline
# OUTPUT_TABLE is in `project:dataset.table` format
OUTPUT_TABLE=wwoo-sandbox:test.logs_json
BOOTSTRAP_SERVERS=wwoo-kafka-broker-1:9092,wwoo-kafka-broker-2:9092,wwoo-kafka-broker-3:9092,wwoo-kafka-broker-4:9092,wwoo-kafka-broker-5:9092,wwoo-kafka-broker-6:9092
SINK_TYPE=bigquery

# Only for Reshuffle test
NUM_RESHUFFLE_BUCKETS=2000

# Only for Storage Write API
BIGQUERY_WRITE_METHOD="load_job"
BIGQUERY_USE_AUTO_SHARDING=false
BIGQUERY_NUM_WRITE_STREAMS=50
BIGQUERY_WRITE_TRIGGER_SECONDS=5

gcloud dataflow flex-template run "message-consumer-`date +%Y%m%d-%H%M%S`" \
   --template-file-gcs-location "$BUCKET/flex_templates/message_consumer.json" \
   --parameters "topic=$TOPIC" \
   --parameters "groupId=$CONSUMER_GROUP_ID" \
   --parameters "outputTable=$OUTPUT_TABLE" \
   --parameters "^|^bootstrapServers=$BOOTSTRAP_SERVERS" \
   --parameters "bigQueryWriteMethod=$BIGQUERY_WRITE_METHOD" \
   --parameters "bigQueryWriteTriggerSeconds=$BIGQUERY_WRITE_TRIGGER_SECONDS" \
   --parameters "bigQueryNumWriteStreams=$BIGQUERY_NUM_WRITE_STREAMS" \
   --parameters "bigQueryUseAutoSharding=$BIGQUERY_USE_AUTO_SHARDING" \
   --parameters "sinkType=$SINK_TYPE" \
   --parameters "autoscalingAlgorithm=THROUGHPUT_BASED" \
   --worker-machine-type $WORKER_MACHINE_TYPE \
   --enable-streaming-engine \
   --worker-zone $ZONE \
   --temp-location $BUCKET/consumer/temp \
   --disable-public-ips \
   --project $GOOGLE_CLOUD_PROJECT \
   --region $REGION \
   --num-workers $NUM_WORKERS \
   --max-workers $MAX_WORKERS \
   --subnetwork=regions/$REGION/subnetworks/logging-cluster-vpc-subnet
