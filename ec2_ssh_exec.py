#!/usr/bin/env python

import argparse
import paramiko
import os
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument(
    "--instance-ip",
    dest="instance_ip",
    type=str,
    required=True,
    help="IP address of the EC2 instance to connect to",
)
parser.add_argument(
    "--key-pair",
    dest="key_pair",
    type=str,
    required=True,
    help="Name of the key pair associated with the EC2 instance",
)
parser.add_argument(
    "--ecr-registry",
    dest="ecr_registry",
    type=str,
    required=True,
    help="Name of the ECR repository to pull the Docker image from",
)
parser.add_argument(
    "--ecr-repository",
    dest="ecr_repository",
    type=str,
    required=True,
    help="Name of the Docker image to run",
)
parser.add_argument(
    "--image-tag",
    dest="image_tag",
    type=str,
    required=True,
    help="Tag of the Docker image to run",
)
parser.add_argument(
    "--private-key",
    dest="private_key",
    type=str,
    required=True,
    help="SSH private key value",
)

if __name__ == "__main__":
    args = parser.parse_args()

    # Create a temporary file and write the private key to it
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(args.private_key.encode())

    # Move the temporary file to the ~/.ssh directory with the key pair name
    key_path = os.path.expanduser(f"~/.ssh/{args.key_pair}.pem")
    os.rename(temp_file.name, key_path)
    os.chmod(key_path, 0o400)

    # Connect to the EC2 instance via SSH
    key_path = os.path.expanduser("~/.ssh/" + args.key_pair + ".pem")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=args.instance_ip,
        username="ec2-user",
        key_filename=key_path,
    )

    # Execute the ecr login command
    stdin, stdout, stderr = ssh.exec_command(
        "aws ecr get-login --no-include-email --region us-west-2"
    )
    print(stdout.read().decode("utf-8"))

    # Pull the Docker image
    stdin, stdout, stderr = ssh.exec_command(
        "docker pull {}.dkr.ecr.us-west-2.amazonaws.com/{}:{}".format(
            args.ecr_registry, args.ecr_repository, args.image_tag
        )
    )
    print(stdout.read().decode("utf-8"))

    # Run the Docker image
    stdin, stdout, stderr = ssh.exec_command(
        "docker run -d {}.dkr.ecr.us-west-2.amazonaws.com/{}:{}".format(
            args.ecr_registry, args.ecr_repository, args.image_tag
        )
    )
    print(stdout.read().decode("utf-8"))

    # Close the SSH connection
    ssh.close()
