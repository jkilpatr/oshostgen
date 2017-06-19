import argparse
import lib.Tools
import sys
from openstack import connection
import os


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def main():
    parser = MyParser(description='A Ansible hostfile generator for \
                                   large OpenStack deployments')

    parser.add_argument('-n', '--no-touch', dest='no_touch',
                        action="store_true", help="Don't load a key")

    parser.add_argument('-k', '--keyfile', dest='keyfile', type=str,
                        default="$HOME/.ssh/id_rsa", help="Keyfile to load")

    parser.add_argument('-b', '--browbeat', dest='browbeat',
                        type=str, default=None,
                        help="Browbeat mode. Usage: -b <browbeat machine ip>")

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

    conn = connection.Connection(**auth_args)
    if not lib.Tools.add_key(args.keyfile, conn):
        print("There are no keys in Nova, please add one")
        exit(1)

    with open("ssh-config", 'w') as ssh_conf:
        lines = lib.Tools.build_ssh_config(conn, args)
        for line in lines:
            ssh_conf.write(line)

    with open("hosts", 'w') as hosts_file:
        lines = lib.Tools.build_ansible_host_file(conn, args)
        for line in lines:
            hosts_file.write(line)
