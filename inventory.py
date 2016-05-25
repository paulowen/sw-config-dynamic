#!/usr/bin/env python

import argparse
import json
import paramiko
import subprocess
import csv
import sys
import pprint
import xlrd
import re

from itertools import ifilterfalse
from collections import defaultdict

class Inventory(object):

    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()

    def triggerUpdate(self, host, vlans, switchports):
        host.update({"vlans": vlans})
        host.update({"switchports": switchports})
        return host

    def Excel2CSV(this, ExcelFile, SheetName, CSVFile):
        workbook = xlrd.open_workbook(ExcelFile)
        worksheet = workbook.sheet_by_name(SheetName)
        csvfile = open(CSVFile, 'wb')
        wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

        for rownum in xrange(worksheet.nrows):
            # wr.writerow(
            #     list(x.encode('utf-8') if type(x) == type(u'') else x
            #         for x in worksheet.row_values(rownum)))
            rowValues = worksheet.row_values(rownum)

            newValues = []
            for s in rowValues:
                if isinstance(s, unicode):
                    strValue = (str(s.encode("utf-8")))
                else:
                    strValue = (str(s))

                isInt = bool(re.match("^([0-9]+)\.0$", strValue))

                if isInt:
                    strValue = int(float(strValue))
                else:
                    isFloat = bool(re.match("^([0-9]+)\.([0-9]+)$", strValue))
                    isLong  = bool(re.match("^([0-9]+)\.([0-9]+)e\+([0-9]+)$", strValue))

                    if isFloat:
                        strValue = float(strValue)

                    if isLong:
                        strValue = int(float(strValue))

                newValues.append(strValue)

            wr.writerow(newValues)

        csvfile.close()

    def host_list(self):

        # Define list of hosts and skip header
        meta_dict = {}
        host_dict = {}
        vlan_dict = {}
        port_dict = {}

        self.Excel2CSV('inventory.xlsx', "Sheet1", "inventory.csv")

        file = open('inventory.csv')
        file_dict = csv.DictReader(file)

        for row in file_dict:

            if len(row["Device"]) >> 0:

                # Trigger update on detection of new device, but only if values exist indicating a host is parsed already
                if len(host_dict) >> 0:
                    # Update meta dictionary with collated host values, using hostname as key to distinguish for now
                    meta_dict.update({host: self.triggerUpdate(host_dict, vlan_dict, port_dict)})

                # Set a host variable to remember the last known device
                host = row["Device"]

                # Reset dictionaries now a new device is detected
                host_dict = {}
                vlan_dict = {}
                port_dict = {}

            if len(row["Username"]) >> 0:
                host_dict.update({'username': row["Username"]})

            if len(row["Password"]) >> 0:
                host_dict.update({'password': row["Password"]})

            if len(row["Domain Name"]) >> 0:
                host_dict.update({'domainname': row["Domain Name"]})

            if len(row["VLANs"]) >> 0:
                if len(row["VLAN Name"]) >> 0:
                    vlan_dict.update({row["VLANs"]: row["VLAN Name"]})

            switchports = {}
            if len(row["Switchports"]) >> 0:
                if "TRUNK" in row["Mode"]:
                    switchports.update({'mode': 'trunk'})
                    if len(row["Allowed VLANs"]) >> 0:
                        switchports.update({'allowedvlans': row["Allowed VLANs"]})
                    if len(row["Native VLAN"]) >> 0:
                        switchports.update({'nativevlan': row["Native VLAN"]})
                elif "ROUTED" in row["Mode"]:
                    switchports.update({'mode': 'routed'})
                else:
                    switchports.update({'mode': 'access'})
                    switchports.update({'vlan': row["VLAN"]})

                if len(row["Description"]) >> 0:
                    switchports.update({'desc': row["Description"]})

                if "1" in row["Shutdown"]:
                    switchports.update({'shutdown': 'true'})

                port_dict.update({row["Switchports"]: switchports})

        # Update dictionaries again due to end of file - new host detection won't pick it up - still using hostname as key to distinguish
        meta_dict.update({host: self.triggerUpdate(host_dict, vlan_dict, port_dict)})

        # Prepare returned dictionary into right format for ansible-playbook using switchname key as distinguisher
        result = {}
        for key in meta_dict:
            result.update({key: {
               "hosts": [key],
               "vars" : meta_dict[key]
               }
            })

        file.close()

        return result

    # Empty inventory for testing.
    def empty_inventory(self):
        return {}

    def __init__(self):
        self.read_cli_args()

        inventory = {}
        # Called with `--list`.
        if self.args.list:
            inventory = self.host_list()
            json.dump(inventory, sys.stdout)

        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            inventory = self.empty_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            inventory = self.empty_inventory()


if __name__ == '__main__':
    Inventory()
