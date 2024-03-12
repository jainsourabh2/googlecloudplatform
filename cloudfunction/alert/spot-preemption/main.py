from __future__ import annotations
from collections.abc import Iterable
from google.cloud import compute_v1
import functions_framework

@functions_framework.http
def hello_http(request):

    request_json = request.get_json(silent=True)

    # fetch instance details
    instance = list_instances(request_json['incident']['resource']['labels']['project_id'],request_json['incident']['resource']['labels']['zone'],request_json['incident']['resource']['labels']['instance_id'])

    # Print the values needed for logging
    print(request_json['incident']['resource']['labels']['instance_id'])
    print(request_json['incident']['resource']['labels']['project_id'])
    print(request_json['incident']['resource']['labels']['zone'])
    print(instance.machine_type)
    print(instance.name)

    return 'Success'

def list_instances(project_id: str, zone: str, instance: str) -> Iterable[compute_v1.Instance]:

    instance_client = compute_v1.InstancesClient()

    # Initialize request argument(s)
    request = compute_v1.GetInstanceRequest(
        instance=instance,
        project=project_id,
        zone=zone,
    )

    # Make the request
    response = instance_client.get(request=request)

    return response
