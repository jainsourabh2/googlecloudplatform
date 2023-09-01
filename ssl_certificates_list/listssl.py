from pprint import pprint
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from google.oauth2 import service_account
import json
import csv

from googleapiclient.discovery import build
import google.auth

ORGANIZATION_ID = '641067203402'

def listAllProjects():
    # Start by listing all the projects under the organization
    filter='parent.type="organization" AND parent.id="{}" AND lifecycleState="ACTIVE"'.format(ORGANIZATION_ID)
    projects_under_org = rm_v1_client.projects().list(filter=filter).execute()

    all_projects=[]

    if len(projects_under_org) > 0:
        # Get all the project IDs
        all_projects = [p['projectId'] for p in projects_under_org['projects']]

    # Now retrieve all the folders under the organization
    parent="organizations/"+ORGANIZATION_ID
    folders_under_org = rm_v2_client.folders().list(parent=parent).execute()

    # Make sure that there are actually folders under the org
    if not folders_under_org:
        return all_projects

    # Now sabe the Folder IDs
    folder_ids = [f['name'].split('/')[1] for f in folders_under_org['folders']]

    # Start iterating over the folders
    while folder_ids:
        # Get the last folder of the list
        current_id = folder_ids.pop()
        
        # Get subfolders and add them to the list of folders
        subfolders = rm_v2_client.folders().list(parent="folders/"+current_id).execute()
        
        if subfolders:
            folder_ids.extend([f['name'].split('/')[1] for f in subfolders['folders']])
        
        # Now, get the projects under that folder
        filter='parent.type="folder" AND parent.id="{}" AND lifecycleState="ACTIVE"'.format(current_id)
        projects_under_folder = rm_v1_client.projects().list(filter=filter).execute()
        
        # Add projects if there are any
        if projects_under_folder:
            all_projects.extend([p['projectId'] for p in projects_under_folder['projects']])

    # Finally, return all the projects
    return all_projects

credentials, _ = google.auth.default()

# V1 is needed to call all methods except for the ones related to folders
rm_v1_client = build('cloudresourcemanager', 'v1', credentials=credentials, cache_discovery=False) 

# V2 is needed to call folder-related methods
rm_v2_client = build('cloudresourcemanager', 'v2', credentials=credentials, cache_discovery=False) 

filter='parent.type="folders" AND parent.id="{}" AND lifecycleState="ACTIVE"'.format(ORGANIZATION_ID)

f = open('./ssl_certificates.csv', 'w')
writer = csv.writer(f,delimiter=',',lineterminator='\r\n',quotechar = "'")
writer.writerow(['projectid','name','creationtimestamp','expiretime'])

service = discovery.build('cloudresourcemanager', 'v3', credentials=credentials)

service_compute = discovery.build('compute', 'v1', credentials=credentials)

projects = listAllProjects()

ignore_projects = ['euphoric-stone-394707','protean-fabric-394522','delivr-394508']

for project_id in projects:
    if project_id not in ignore_projects :
        request_ssl = service_compute.sslCertificates().list(project=project_id)
        while request_ssl is not None:
            response_ssl = request_ssl.execute()
            if 'items' in response_ssl.keys():
                for ssl_certificate in response_ssl['items']:

                    pprint("projectid: " + project_id)
                    pprint("name: " + ssl_certificate["name"])
                    pprint("creationTimestamp: " + ssl_certificate["creationTimestamp"])
                    if "expireTime" in ssl_certificate:
                        pprint("expireTime: " + ssl_certificate["expireTime"])
                        writer.writerow([project_id + "," + ssl_certificate["name"] + "," + ssl_certificate["creationTimestamp"] + "," + ssl_certificate["expireTime"]])
                    else:
                        pprint("expireTime: Not Available")
                        writer.writerow([project_id + "," + ssl_certificate["name"] + "," + ssl_certificate["creationTimestamp"] + ",'not Available'" ])
                    pprint("----------------------------------------------")
            request_ssl = service_compute.sslCertificates().list_next(previous_request=request_ssl, previous_response=response_ssl)
