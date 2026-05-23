from ssh_client import run_ssh_command


# LIST OF VMs
VMS = [
    {
        "host": "192.168.1.10",
        "username": "root",
        "password": "redhat"
    },
    {
        "host": "192.168.1.11",
        "username": "root",
        "password": "redhat"
    },
    {
        "host": "192.168.1.12",
        "username": "root",
        "password": "redhat"
    }
]


COMMAND = "hostnamectl"


for vm in VMS:

    result = run_ssh_command(
        host=vm["host"],
        username=vm["username"],
        password=vm["password"],
        command=COMMAND
    )

    print("=" * 60)
    print(f"HOST: {result['host']}")
    print(f"STATUS: {result['status']}")

    if result["stdout"]:
        print("\nSTDOUT:")
        print(result["stdout"])

    if result["stderr"]:
        print("\nSTDERR:")
        print(result["stderr"])
