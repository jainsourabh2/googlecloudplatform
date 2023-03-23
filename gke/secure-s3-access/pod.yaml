apiVersion: v1
kind: Pod
metadata:
  labels:
    run: my-pod
  name: my-pod
  namespace: dev
spec:
  initContainers:
  - image: gcr.io/gke-s3-secure-poc/secure-s3
    name: secure-s3
    command: ['node', 'app.js']
    env:
    - name: AWS_REGION
      value: "us-west-2"
    - name: AWS_ACCESS_KEY_ID
      value: ""
    - name: AWS_SECRET_ACCESS_KEY
      value: ""
  containers:
  - image: nginx
    name: my-pod
    ports:
    - containerPort: 80
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
