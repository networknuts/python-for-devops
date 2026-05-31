import os
from pathlib import Path

import boto3
from paramiko.client import SSHClient, AutoAddPolicy


# =========================
# CONFIG SECTION
# =========================

REGION = "ap-south-1"

TAG_KEY = "env"
TAG_VALUE = "development"

USERNAME = "ubuntu"
COMMAND = "uptime"

USE_PRIVATE_IP = False

# =========================
# EC2 INSTANCE DISCOVERY
# =========================

def get_instances():
    ec2 = boto3.client("ec2", region_name=REGION)

    response = ec2.describe_instances(
        Filters=[
            {
                "Name": f"tag:{TAG_KEY}",
                "Values": [TAG_VALUE]
            },
            {
                "Name": "instance-state-name",
                "Values": ["running"]
            }
        ]
    )

    instances = []

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            key_name = instance.get("KeyName")

            public_ip = instance.get("PublicIpAddress")
            private_ip = instance.get("PrivateIpAddress")

            if USE_PRIVATE_IP:
                ip_address = private_ip
            else:
                ip_address = public_ip

            instances.append({
                "instance_id": instance_id,
                "ip_address": ip_address,
                "key_name": key_name
            })

    return instances


# =========================
# FIND PEM FILE
# =========================

def find_pem_file(key_name):
    pem_file = f"{key_name}.pem"
    pem_path = Path.cwd() / pem_file

    if pem_path.exists():
        return str(pem_path)

    return None


# =========================
# SSH COMMAND EXECUTION
# =========================

def run_ssh_command(host, username, pem_file, command):
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())

    try:
        print(f"\nConnecting to {host}")

        client.connect(
            hostname=host,
            username=username,
            key_filename=pem_file,
            timeout=10
        )

        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode()
        error = stderr.read().decode()

        return {
            "host": host,
            "output": output,
            "error": error
        }

    except Exception as e:
        return {
            "host": host,
            "output": "",
            "error": str(e)
        }

    finally:
        client.close()


# =========================
# MAIN PROGRAM
# =========================

instances = get_instances()

if not instances:
    print("No matching running EC2 instances found.")
    exit()

for instance in instances:
    instance_id = instance["instance_id"]
    ip_address = instance["ip_address"]
    key_name = instance["key_name"]

    print("=" * 60)
    print(f"Instance ID : {instance_id}")
    print(f"IP Address  : {ip_address}")
    print(f"Key Name    : {key_name}")

    if not ip_address:
        print("Skipping: No IP address found.")
        continue

    if not key_name:
        print("Skipping: No key name found for this instance.")
        continue

    pem_file = find_pem_file(key_name)

    if not pem_file:
        print(f"Skipping: PEM file not found: {key_name}.pem")
        continue

    result = run_ssh_command(
        host=ip_address,
        username=USERNAME,
        pem_file=pem_file,
        command=COMMAND
    )

    print("\nCommand Output:")
    print(result["output"])

    if result["error"]:
        print("\nCommand Error:")
        print(result["error"])

    print("=" * 60)
