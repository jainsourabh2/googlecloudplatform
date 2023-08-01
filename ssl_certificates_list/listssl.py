from pprint import pprint
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from google.oauth2 import service_account
import json
import csv

f = open('./ssl_certificates.csv', 'w')
writer = csv.writer(f)

# Uncomment to use Application Default Credentials (ADC)
credentials = GoogleCredentials.get_application_default()
service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
service_compute = discovery.build('compute', 'v1', credentials=credentials)

request = service.projects().list()

ignore_projects = ['ai-dev-preview-external','data-analytics-golden-v1-share','gm-test-337806']

while request is not None:
    response = request.execute()
    print(response)
    for project in response.get('projects', []):
        project_id = project['projectId']
        if project_id not in ignore_projects :
            request_ssl = service_compute.sslCertificates().list(project=project_id)
            while request_ssl is not None:
                response_ssl = request_ssl.execute()
                if 'items' in response.keys():
                    for ssl_certificate in response['items']:
                        pprint("projectid: " + project_id)
                        pprint("name: " + ssl_certificate["name"])
                        pprint("creationTimestamp: " + ssl_certificate["creationTimestamp"])
                        pprint("expireTime: " + ssl_certificate["expireTime"])
                        writer.writerow(project_id + "," + ssl_certificate["name"] + "," + ssl_certificate["creationTimestamp"] + "," + ssl_certificate["expireTime"] + "\n")
                        pprint("----------------------------------------------")
                request_ssl = service_compute.sslCertificates().list_next(previous_request=request_ssl, previous_response=response_ssl)

    request = service.projects().list_next(previous_request=request, previous_response=response)
    
