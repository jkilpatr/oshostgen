import argparse
import lib.Tools
import threading
import sys
import openstack
import os
import json
from collections import deque

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

parser = MyParser(description=' \
                               large OpenStack deployments')

parser.add_argument('-n', '--no-touch', dest='no_touch', action="store_true",
                    help="Don't load a key")

parser.add_argument('-k', '--keyfile', dest='keyfile', type=str,
                    default = "$HOME/id_rsa", help="Keyfile to load")

args = parser.parse_args()

if 'OS_AUTH_URL' not in os.environ:
    print("Please source a cloud rc file")
    exit(1)


auth_args = {
    'auth_url': os.environ['OS_AUTH_URL'],
    'project_name': 'admin',
    'username': os.environ['OS_USERNAME'],
    'password': os.environ['OS_PASSWORD'],
}



def main():
        conn = openstack.connection.Connection(**auth_args)
        # Issue one thread for each node
        if not no_touch:
            lib.Tools.add_key(keypair, conn)

        threads = []
        nodes = deque()
        for server in conn.compute.servers():
            thread = threading.Thread(target=lib.Tools.identify_node, args=(server, conn))
            threads.append(thread)
            thread.start()
            for thread in threads:
                thread.join()

        #come back from the threads, take the deque they built and make a hosts/ssh-config with it
