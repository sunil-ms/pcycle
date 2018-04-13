from pysnmp.hlapi import *
from pysnmp.error import PySnmpError
from p_cycle_exceptions import *
import sys
import os
import time
import argparse
import logging

parser = argparse.ArgumentParser(
    description='A tool to power cycle a system.', usage='%(prog)s [options]')

parser.add_argument('pdu_hosts', type=lambda s: [pdu for pdu in s.split(':')], help='The hostname/IP of the pdu. Multiple pdus can be specified as a colon separated string.')
parser.add_argument('pdu_vendors' , type=lambda s: [vendor for vendor in s.split(':')], help='Vendor name for the Pdus. e.g. IBM/Eaton.  Multiple names can be specified as a colon separated string.')
parser.add_argument(
    'system', help='The hostname/IP of the BMC/FSP to be power cycled.')
parser.add_argument('-o', '--outlet_numbers', type=lambda s: [[int(item) for item in outlets.split(
    ',')] for outlets in s.split(':')], required=True, help='The outlets to which the system is connected to. Multiple outlets can be specified as a comma separated string. e.g. p_cycle.py coral-pdu ibm f19a -outlet_numbers 10,11. Delimit each set of outlets with a colon for multiple pdus. e.g. p_cycle.py coral-pdu:coral-pdu1 ibm:ibm 1,2:3,4')
parser.add_argument('-snmp_version', required=False, default="v1",
                    help='The SNMP version to be used. Default is v1.')
parser.add_argument('--power_off_timeout', default=30, type=int,
                    help="Timeout value for 'power off' operation in seconds. Default is 30.")
parser.add_argument('--power_on_timeout', default=30, type=int,
                    help="Timeout value for 'power on' operation in seconds. Default is 30.")
parser.add_argument('--ping_timeout', default=300, type=int,
                    help="Timeout value for ping operation in seconds. Default is 300.")
parser.add_argument('--log', required=False, default="debug",
                    help="Set the log level. Values can be info,debug,warning etc.")
args = parser.parse_args()
numeric_level = getattr(logging, args.log.upper(), None)
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='#(%Z) %m/%d/%Y %I:%M:%S %p - ', level=numeric_level)
session_args = {}
if not (len(args.pdu_hosts) == len(args.pdu_vendors) == len(args.outlet_numbers)):
    logging.critical("Wrong arguments passed. Number of colon delimited values for PDU hostname, PDU vendor, outlets must match.")
    exit(1)
vendor_list = ['ibm', 'eaton']
print(args)
def process_command_output(errorIndication, errorStatus, errorIndex, varBinds):
    r"""Analyze the output returned by a SNMP request and return
        output back to the caller."""

    # Process the output returned from a SNMP request.
    if errorIndication:
        logging.critical(errorIndication)
    elif errorStatus:
        logging.critical("{} at {}".format(errorStatus.prettyPrint(
        ), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            var_string = ' = '.join(list(x.prettyPrint() for x in varBind))
            output = var_string.split('=')[1]
            logging.debug('\t\t' + var_string)
            return int(output)


def get_pdu_outlet_count(**kwargs):
    r"""Return the outlet count for a ePDU."""

    # Get the outlet count.
    logging.debug("\tGetting outlet count.")
    g = getCmd(kwargs['snmp_engine'],
               kwargs['community_data'],
               kwargs['transport_target'],
               kwargs['context_data'],
               ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', 2, 6, 223, 8, 2, 1, 0)))

    # getCmd() returns a generator object, so invoke next() to perform the actual query.
    errorIndication, errorStatus, errorIndex, varBinds = g.next()

    # Process the output returned.
    return process_command_output(errorIndication, errorStatus, errorIndex, varBinds)


def get_pdu_outlet_state(outlet_number, **kwargs):
    r"""Return the outlet/relay state on a ePDU."""

    # Get the outlet state
    logging.debug(
        "\tGetting outlet state for outlet number {}.".format(outlet_number))
    g = getCmd(kwargs['snmp_engine'],
               kwargs['community_data'],
               kwargs['transport_target'],
               kwargs['context_data'],
               ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', 2, 6, 223, 8, 2, 2, 1, 11, outlet_number)))

    # getCmd() returns a generator object, so invoke next() to perform the actual query.
    errorIndication, errorStatus, errorIndex, varBinds = g.next()

    # Process the output returned.
    return process_command_output(errorIndication, errorStatus, errorIndex, varBinds)


def set_pdu_outlet_state(outlet_number, state, **kwargs):
    r"""Set the outlet/relay state on a ePDU to either ON(1) or OFF(0)."""

    # Set the outlet state.
    logging.debug("\tSetting outlet state to {} for outlet number {}.".format(
        state, outlet_number))
    g = setCmd(kwargs['snmp_engine'],
               kwargs['community_data'],
               kwargs['transport_target'],
               kwargs['context_data'],
               ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', 2, 6, 223, 8, 2, 2, 1, 11, outlet_number), Integer32(state)))

    # setCmd() returns a generator object, so invoke next() to perform the actual query.
    errorIndication, errorStatus, errorIndex, varBinds = g.next()

    # Process the output returned.
    return process_command_output(errorIndication, errorStatus, errorIndex, varBinds)


def do_power_cycle_on_ibm_pdu(pdu_host, outlets, power_off_timeout, power_on_timeout, ping_timeout):
    r"""Inititate all session variables and do a power cycle."""

    session_args = {}
    session_args['snmp_engine'] = SnmpEngine()
    session_args['transport_target'] = UdpTransportTarget((pdu_host, 161))
    session_args['context_data'] = ContextData()

    # Currently, we don't handle SNMP v3.
    if args.snmp_version == "v1" or args.snmp_version == "v2":
        session_args['community_data'] = CommunityData('public', mpModel=0)
    outlet_count = get_pdu_outlet_count(**session_args)
    for outlet in outlets:
        try:
            if not 1 <= int(outlet) <= int(outlet_count):
                raise InvalidOutletNumberException(outlet, outlet_count)
        except InvalidOutletNumberException as e:
            logging.critical(e)
            exit(1)

        # Start a 'power off', 'power on' sequence.
        logging.info("Initiating 'power off' on outlet {}.".format(outlet))
        try:
            set_pdu_outlet_state(outlet, 0, **session_args)
        except PySnmpError as e:
            logging.critical(e)
            exit(1)
        while((get_pdu_outlet_state(outlet, **session_args) != 0) and power_off_timeout >= 0):
            time.sleep(5)
            power_off_timeout -= 5
        try:
            if power_off_timeout < 0:
                raise PowerOffTimeoutException(outlet)
        except PowerOffTimeoutException as e:
            logging.critical(e)
            exit(1)
    logging.info("All outlets powered off. Checking system status.")
    time.sleep(5)
    try:
        if(not os.system("ping -c 1 -w2 " + args.system + " > /dev/null 2>&1")):
            raise PowerOffPingException
    except PowerOffPingException as e:
        logging.critical(e)
        exit(1)
    logging.info(
        '{} is not reachable. Power Off successful'.format(args.system))

    logging.info("Waiting for 10 seconds before powering on.")
    time.sleep(10)
    for outlet in outlets:
        logging.info("Initiating 'power on' on outlet {}.".format(outlet))
        try:
            set_pdu_outlet_state(outlet, 1, **session_args)
        except PySnmpError as e:
            logging.critical(e)
            exit(1)
        while((get_pdu_outlet_state(outlet, **session_args) != 1) and power_on_timeout >= 0):
            time.sleep(5)
            power_on_timeout -= 5
        try:
            if power_on_timeout < 0:
                raise PowerOnTimeoutException(outlet)
        except PowerOnTimeoutException as e:
            logging.critical(e)
            exit(1)
    logging.info("All outlets powered on. Checking system status.")

    # sleep for 30 seconds.
    logging.info("Waiting for 30 seconds before checking the system state.")
    while(os.system("ping -c 1 -w2 " + args.system + " > /dev/null 2>&1") and ping_timeout >= 0):
        time.sleep(2)
        ping_timeout -= 2
    try:
        if(ping_timeout < 0):
            raise PowerOnPingException()
    except PowerOnPingException as e:
        logging.critical(
            "System not reachable after Power cycle. Please contact lab support team")
        exit(1)
    pre_red_text = "\x1B[31;40m"
    suf_red_text = "\x1B[0m"
    logging.info("{0} is ".format(args.system) + pre_red_text + "pingable " +
                 suf_red_text + "after power" + pre_red_text+" on."+suf_red_text)
    return True


def main():
    r""" main function for the power cycle operation."""
    
    for i in range(len(args.pdu_hosts)):
        if args.pdu_vendors[i].lower() not in vendor_list:
            logging.error(
                "Currently we don't support pdu cycling on {}.".format(args.vendor_name))
            exit(6)
        elif args.pdu_vendors[i].lower() == 'ibm':
            do_power_cycle_on_ibm_pdu(
                args.pdu_hosts[i], args.outlet_numbers[i], args.power_off_timeout, args.power_on_timeout, args.ping_timeout)
        elif args.pdu_vendors[i].lower() == 'eaton':
            outlet_nums = ''.join(str(i) for i in args.outlet_numbers[i])
            # Invoke existing script for Eaton ePDU.
            os.system("/afs/rch/projects/esw/dvt/autoipl/apollotest/bin/pcycle --ipc_host={} --outlet_nums={}".format(args.pdu, outlet_nums))


main()
