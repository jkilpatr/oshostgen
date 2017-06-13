# oshostgen
A tool for generating ansible hostfiles for OpenStack TripleO Overclouds

## usage

Right now oshostgen just checks if there is an existing key in the Nova keypairs
list (by default `~/.ssh/id_rsa`) and uses that.

First we need to install oshostgen

	pip install git+https://github.com/jkilpatr/oshostgen

If you invoke oshostgen with no agruments it will generate a hosts file and
ssh_config in your current working directory. Cloud credentials are collected
from the usual environmental variables.

	source ~/home/stack/stackrc
	oshostgen

Due to it's questionable choice of authors oshostgen supports Browbeat mode
where it will generate some extra categories and insert a provided addresses
into the Ansible hosts file.

	oshostgen -b <browbeat node ip>

## TODO

1. Support for adding keys on user request
2. Getting operators to actually use it.
3. Fix all the bugs I don't know about yet.
