# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import re


def browbeat_specific_ansible_categories(lines, browbeat_host):
    custom_lines = []
    custom_categories = ["browbeat",
                         "graphite",
                         "grafana",
                         "elk",
                         "elk-client"]

    for category in custom_categories:
        custom_lines += "{}\n".format(category)
        if 'browbeat' in category:
            custom_lines += "{}\n".format(browbeat_host)
        else:
            custom_lines += "## example host entry\n"
            custom_lines += "#host-01\n\n"

    return custom_lines + lines


def build_ansible_host_file(conn, args):
    entries = {}
    entries['undercloud'] = ["undercloud\n"]
    for server in conn.compute.servers():
        category = name_to_category(server.name)
        if category not in entries:
            entries[category] = ["{}\n".format(server.name)]
        else:
            entries[category] += "{}\n".format(server.name)
    lines = []
    for category in entries:
        lines += "[{}]\n".format(category)
        lines.extend(entries[category])
        lines += "\n"

    # Add overcloud metacategory
    lines += "[overcloud:children]\n"
    for category in entries:
        if 'undercloud' in category:
            continue
        lines += "{}\n".format(category)

    if args.browbeat is not None:
        lines = browbeat_specific_ansible_categories(lines,
                                                     args.browbeat)

    return lines


def build_ssh_config(conn, args):
    lines = []
    lines = build_ssh_config_undercloud_entries(lines)
    for server in conn.compute.servers():
        lines += build_ssh_config_entry(server)
    return lines


def name_to_category(name):
    parts = name.split('-')
    if 'novacompute' in parts[1]:
        return "compute"
    else:
        return parts[1]


def build_ssh_config_undercloud_entries(lines):
    ssh_key_path = "/home/stack/.ssh/id_rsa"
    line = "Host undercloud\n"
    line += "\tHostname localhost\n"
    line += "\tIdentityFile {}\n".format(ssh_key_path)
    line += "\tStrictHostKeyChecking no\n"
    line += "\tUserKnownHostsFile=/dev/null\n\n"
    lines += line
    line = "Host undercloud-root\n"
    line += "\tHostname localhost\n"
    line += "\tUser root\n"
    line += "\tIdentityFile {}\n".format(ssh_key_path)
    line += "\tStrictHostKeyChecking no\n"
    line += "\tUserKnownHostsFile=/dev/null\n\n"
    lines += line
    line = "Host undercloud-stack\n"
    line += "\tHostname localhost\n"
    line += "\tUser stack\n"
    line += "\tIdentityFile {}\n".format(ssh_key_path)
    line += "\tStrictHostKeyChecking no\n"
    line += "\tUserKnownHostsFile=/dev/null\n\n"
    lines += line
    return lines


def build_ssh_config_entry(server):
    undercloud_ip = re.findall('(?:\d{1,3}\.){3}\d{1,3}',
                               os.environ['OS_AUTH_URL'])[0]
    ssh_cfg_path = "ssh-config"
    ssh_key_path = "/home/stack/.ssh/id_rsa"
    server_ip = server.addresses['ctlplane'][0]['addr']
    entry = "Host {}\n".format(server.name)
    entry += "\tProxyCommand ssh -F {} ".format(ssh_cfg_path)
    entry += "-o UserKnownHostsFile=/dev/null "
    entry += "-o StrictHostKeyChecking=no "
    entry += "-o ConnectTimeout=60 "
    entry += "-i {} ".format(ssh_key_path)
    entry += "{}@{} ".format("stack", undercloud_ip)
    entry += "-W {}:{}\n".format(server_ip, "22")
    entry += "\tUser heat-admin\n"
    entry += "\tIdentityFile {}\n".format(ssh_key_path)
    entry += "\tStrictHostKeyChecking no\n"
    entry += "\tUserKnownHostsFile=/dev/null\n\n"
    return entry


def add_key(keypair, conn):

    # Check if the given key is already in nova
    for key in conn.compute.keypairs():
        return True
    return False
