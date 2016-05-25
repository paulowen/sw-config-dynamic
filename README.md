# sw-config-dynamic
Ansible dynamic inventory from spreadsheet used to build basic Cisco IOS switch configurations.

The basic concept is that a spreadsheet can be distributed to a customer, nicely formatted, all of that. They fill in the necessary details required for the switch including basic attributes, VLAN list, layer 2 switchport information, and the script will convert it into a CSV, parse the CSV as a dynamic inventory pull host vars from the CSV and build configurations per device.

Additional configuration items will be supported as the script evolves. As of yet it is a PoC, nothing is optiimised, nothing is really tested.

Launch playbook with `ansible-playbook site.yml -i inventory.py`.
