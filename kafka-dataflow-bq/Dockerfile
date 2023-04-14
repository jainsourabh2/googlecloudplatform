# Copyright 2023 Google. This software is provided as-is, without warranty or representation
# for any use or purpose. Your use of it is subject to your agreement with Google.

FROM gcr.io/dataflow-templates-base/java11-template-launcher-base

ARG WORKDIR=/dataflow/template
RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}

COPY pom.xml .
COPY src .

ENV FLEX_TEMPLATE_JAVA_MAIN_CLASS="com.google.cloud.demo.beam.MessageConsumerPipeline"
ENV FLEX_TEMPLATE_JAVA_CLASSPATH="${WORKDIR}/src/main/java/com/google/cloud/demo/beam/MessageConsumerPipeline.java"

ENTRYPOINT ["/opt/google/dataflow/java_template_launcher"]