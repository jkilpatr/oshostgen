import collections
import subprocess
import json
import openstack
import paramiko
import os

# Run command, return stdout as result
def run_cmd(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode > 0:
        print("The command " + cmd + " returned with errors!")
        print("Printing stderr and continuing")
        print(stderr)

    return stdout.strip()

def identify_node(server, conn):
    print str(server)


def add_key(keypair, conn):
    file_name = os.path.abspath(os.path.expandvars(keypair))
    user_key = paramiko.pkey.PKey.from_private_key_file(file_name)

    # Check if the given key is already in nova
    for key in conn.compute.keypairs():
        if user_key.get_fingerprint() == key.fingerprint:
            return True
    # Key Not already uploaded, or paramiko / openstack diverge fingerprint
    # formats, so we have to upload a key.

    conn.compute.create_keypair(private_key=user_key)
