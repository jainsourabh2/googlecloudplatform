#!/bin/bash

BUCKET=gs://d11-logging-bucket
REGION=us-east4
GOOGLE_CLOUD_PROJECT=d11-logging
REPOSITORY=d11

mvn clean package

gcloud dataflow flex-template build \
   $BUCKET/flex_templates/message_consumer.json \
   --image-gcr-path "$REGION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/$REPOSITORY/message-consumer:latest" \
   --sdk-language "JAVA" \
   --flex-template-base-image JAVA11 \
   --metadata-file "metadata.json"  \
   --jar "target/streaming-demo-bundled-1.0-SNAPSHOT.jar"  \
   --env FLEX_TEMPLATE_JAVA_MAIN_CLASS="com.google.cloud.demo.beam.MessageConsumerPipeline"