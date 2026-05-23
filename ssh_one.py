import paramiko


def run_ssh_command(
    host,
    username,
    password=None,
    key_file=None,
    command="hostname",
    port=22,
    timeout=10
):
    """
    Connect to a remote VM over SSH and run a command.

    Args:
        host (str): VM IP or hostname
        username (str): SSH username
        password (str): SSH password (optional)
        key_file (str): Path to private key file (optional)
        command (str): Command to execute
        port (int): SSH port
        timeout (int): Connection timeout

    Returns:
        dict: {
            "host": host,
            "stdout": stdout,
            "stderr": stderr,
            "status": exit_code
        }
    """

    client = paramiko.SSHClient()

    # Auto accept unknown host keys
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Authentication
        if key_file:
            private_key = paramiko.RSAKey.from_private_key_file(key_file)

            client.connect(
                hostname=host,
                port=port,
                username=username,
                pkey=private_key,
                timeout=timeout
            )

        else:
            client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=timeout
            )

        # Run command
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode()
        error = stderr.read().decode()

        exit_code = stdout.channel.recv_exit_status()

        return {
            "host": host,
            "stdout": output.strip(),
            "stderr": error.strip(),
            "status": exit_code
        }

    except Exception as e:
        return {
            "host": host,
            "stdout": "",
            "stderr": str(e),
            "status": -1
        }

    finally:
        client.close()
