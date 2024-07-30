import boto3
import os

def getPublicIP(CLUSTER_NAME,SERVICE_NAME):
# Initialize clients
    ecs_client = boto3.client('ecs')
    ec2_client = boto3.client('ec2')
    public_ip = "0.0.0.0"

    # Get the list of tasks
    tasks = ecs_client.list_tasks(cluster=CLUSTER_NAME, serviceName=SERVICE_NAME)
    task_arn = tasks['taskArns'][0] if tasks['taskArns'] else None

    if task_arn:
        # Describe the task
        task_details = ecs_client.describe_tasks(cluster=CLUSTER_NAME, tasks=[task_arn])
        attachments = task_details['tasks'][0]['attachments']

        # Find the ENI ID
        eni_id = None
        for attachment in attachments:
            for detail in attachment['details']:
                if detail['name'] == 'networkInterfaceId':
                    eni_id = detail['value']
                    break
            if eni_id:
                break

        if eni_id:
            # Describe the ENI to get the public IP address
            eni_details = ec2_client.describe_network_interfaces(NetworkInterfaceIds=[eni_id])
            public_ip = eni_details['NetworkInterfaces'][0]['Association']['PublicIp']
            print(f'Public IP: {public_ip}')
            return public_ip
        else:
            print('ENI ID not found')
    else:
        print('No running tasks found')

    return None

def updateIP(ip_address):
    route53 = boto3.client('route53')
    response = route53.change_resource_record_sets(
                HostedZoneId=os.environ['HOSTED_ZONE_ID'],
                ChangeBatch={
                    'Comment': 'Auto updating IP from ECS task',
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': os.environ['DNS_NAME'],
                                'Type': 'A',
                                'TTL': 60,
                                'ResourceRecords': [{'Value': ip_address}]
                            }
                        }
                    ]
                }
            )
    print(f"DNS update returned {response}")

ip = getPublicIP('arn:aws:ecs:eu-west-1:467134426671:cluster/FreServer','FrenchECS')
print(ip)
updateIP(ip)