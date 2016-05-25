# sw-config-dynamic
Ansible dynamic inventory from spreadsheet used to build basic Cisco IOS switch configurations.

The basic concept is that a spreadsheet can be distributed to a customer, nicely formatted, all of that. They fill in the necessary details required for the switch including basic attributes, VLAN list, layer 2 switchport information, etc. The script will then convert the spreadsheet into a CSV, parse the CSV as a dynamic inventory list then build host vars from the parsed information using them to build configurations per device.

There is brief experimentation in the spreadsheet using Data Validation and lists of entries to force what values are supported.

Additional configuration items will be supported as the script evolves. As of yet it is a PoC, nothing is optimised, nothing is really tested. The logic is dense and repetitive and needs to be improved upon.

Launch playbook with `ansible-playbook site.yml -i inventory.py`.
