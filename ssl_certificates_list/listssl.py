from pprint import pprint
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from google.oauth2 import service_account
import json
import csv

filter='parent.type="folders" AND parent.id="{}"'.format('435911974745')

f = open('./ssl_certificates.csv', 'w')
writer = csv.writer(f,delimiter=',',lineterminator='\r\n',quotechar = "'")
writer.writerow(['projectid','name','creationtimestamp','expiretime'])
# Uncomment to use Application Default Credentials (ADC)
credentials = GoogleCredentials.get_application_default()
service = discovery.build('cloudresourcemanager', 'v3', credentials=credentials)

service_compute = discovery.build('compute', 'v1', credentials=credentials)


# If you want at org level replace the value below as organizations/org-number
hierarchy = 'folders/<<folder-number>>'
request = service.projects().list(parent=hierarchy)

ignore_projects = ['','','']
while request is not None:
    response = request.execute()
    for project in response.get('projects', []):
        project_id = project['projectId']

        if project_id not in ignore_projects :
            request_ssl = service_compute.sslCertificates().list(project=project_id)
            while request_ssl is not None:
                response_ssl = request_ssl.execute()
                print(response_ssl)
                if 'items' in response_ssl.keys():
                    for ssl_certificate in response_ssl['items']:
                        pprint("projectid: " + project_id)
                        pprint("name: " + ssl_certificate["name"])
                        pprint("creationTimestamp: " + ssl_certificate["creationTimestamp"])
                        pprint("expireTime: " + ssl_certificate["expireTime"])
                        writer.writerow([project_id + "," + ssl_certificate["name"] + "," + ssl_certificate["creationTimestamp"] + "," + ssl_certificate["expireTime"]])
                        pprint("----------------------------------------------")
                request_ssl = service_compute.sslCertificates().list_next(previous_request=request_ssl, previous_response=response_ssl)

    request = service.projects().list_next(previous_request=request, previous_response=response)
