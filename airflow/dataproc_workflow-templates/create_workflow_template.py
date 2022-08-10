gcloud dataproc workflow-templates create sparkpi --region=asia-south1

gcloud dataproc workflow-templates add-job spark \
    --workflow-template=sparkpi \
    --step-id=compute \
    --class=org.apache.spark.examples.SparkPi \
    --jars=file:///usr/lib/spark/examples/jars/spark-examples.jar \
    --region=asia-south1 \
    -- 1000
      
gcloud dataproc workflow-templates set-managed-cluster sparkpi \
    --cluster-name=sparkpi \
    --single-node \
    --region=asia-south1 \
    --subnet=https://www.googleapis.com/compute/v1/projects/on-prem-project-337210/regions/asia-south1/subnetworks/on-prem-subnet-mumbai
