from pysnmp.hlapi import *
import sys,os,time
import argparse
import logging

parser  = argparse.ArgumentParser(description='A tool to power cycle a system.', usage='%(prog)s [options]')

parser.add_argument('pdu', help='The hostname/IP of the pdu.')
parser.add_argument('vendor_name', help='Vendor name for this Pdu. e.g. IBM/Eaton.')
parser.add_argument('system', help='The hostname/IP of the BMC/FSP to be power cycled.')
<<<<<<< HEAD
parser.add_argument('-o', '--outlet_numbers', type=lambda s: [int(item) for item in s.split(',')], required=True, help='The outlets to which the system is connected to. Multiple outlets can also be specified. e.g. p_cycle.py coral-pdu ibm f19a -outlet_numbers 10,11')
=======
parser.add_argument('-outlet_numbers', nargs='+', required=True, help='The outlets to which the system is connected to. Multiple outlets can also be specified. '
                     'p_cycle.py coral-pdu 10 11 f19a')
>>>>>>> 19c303ad77b5918c2b4864e910192bf5521a31f4
parser.add_argument('-snmp_version', required=False, default="v1", help='The SNMP version to be used. Default is v1') 
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p %Z', level=logging.DEBUG)
args = parser.parse_args()
session_args = {}
vendor_list = ['ibm', 'eaton']

def get_pdu_outlet_count(**kwargs):
    # Get the details
<<<<<<< HEAD
    logging.info("\tGetting outlet count.")
=======
    logging.info("\tGetting outlet count..")
>>>>>>> 19c303ad77b5918c2b4864e910192bf5521a31f4
    g = getCmd(kwargs['snmp_engine'],
           kwargs['community_data'],
           kwargs['transport_target'],
           kwargs['context_data'],
           ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises',2,6,223,8,2,1,0)))
    # Returns a generator object, so invoke next() to get the actual data
    errorIndication, errorStatus, errorIndex, varBinds = g.next()
    if errorIndication:
        logging.info(errorIndication)
        exit(5)
    elif errorStatus:
        logging.info("{} at {}".format(errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            var_string = ' = '.join(list(x.prettyPrint() for x in varBind))
            status = var_string.split('=')[1]
            logging.info('\t\t'+var_string)
            return int(status)

def get_pdu_outlet_state(outlet_number, **kwargs):

    # Get the details
<<<<<<< HEAD
    logging.info("\tGetting outlet state for outlet number {}.".format(outlet_number))
=======
    logging.info("\tGetting outlet state for outlet number {}...".format(outlet_number))
>>>>>>> 19c303ad77b5918c2b4864e910192bf5521a31f4
    g = getCmd(kwargs['snmp_engine'],
           kwargs['community_data'],
           kwargs['transport_target'],
           kwargs['context_data'],
           ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises',2,6,223,8,2,2,1,11,outlet_number)))
    # Returns a generator object, so invoke next() to get the actual data
    errorIndication, errorStatus, errorIndex, varBinds = g.next()
    if errorIndication:
        logging.info(errorIndication)
        exit(5)
    elif errorStatus:
        logging.info("{} at {}".format(errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            var_string = ' = '.join(list(x.prettyPrint() for x in varBind))
            status = var_string.split('=')[1]
            logging.info('\t\t'+var_string)
            return int(status)

def set_pdu_outlet_state(outlet_number, state, **kwargs):

    # Set the value
<<<<<<< HEAD
    logging.info("\tSetting outlet state to {} for outlet number {}.".format(state, outlet_number))
=======
    logging.info("\tSetting outlet state to {} for outlet number {}..".format(state, outlet_number))
>>>>>>> 19c303ad77b5918c2b4864e910192bf5521a31f4
    g = setCmd(kwargs['snmp_engine'],
           kwargs['community_data'],
           kwargs['transport_target'],
           kwargs['context_data'],
           ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises',2,6,223,8,2,2,1,11,outlet_number), Integer32(state)))

     # Returns a generator object, so invoke next() to get the actual data
    errorIndication, errorStatus, errorIndex, varBinds = g.next()
    if errorIndication:
        logging.info(errorIndication)
        exit(5)
    elif errorStatus:
        logging.info("{} at {}".format(errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            logging.info('\t\t'+' = '.join(list(x.prettyPrint() for x in varBind)))


def do_power_cycle_on_ibm_pdu():
    power_off_timeout = 15
    power_on_timeout = 15
    ping_timeout = 300
    session_args['snmp_engine'] = SnmpEngine()
    session_args['transport_target'] = UdpTransportTarget((args.pdu, 161))
    session_args['context_data'] = ContextData()
    if args.snmp_version=="v1" or args.snmp_version=="v2":
           session_args['community_data'] = CommunityData('public', mpModel=0)
    outlet_count = get_pdu_outlet_count(**session_args)
    for outlet in args.outlet_numbers:
        if not 1 <= int(outlet) <= int(outlet_count):
<<<<<<< HEAD
            logging.info('Invalid outlet number {}. Valid outlet range is (1,{}), both inclusive.'.format(outlet,outlet_count))
            exit(10)
        #get_pdu_outlet_state(args.outlet_number, **session_args)
        logging.info("Initiating 'power off' on outlet {}.".format(outlet))
=======
            logging.info('Invalid outlet number {}. Valid outlet range (1,{}).'.format(outlet,outlet_count))
            exit(10)
        #get_pdu_outlet_state(args.outlet_number, **session_args)
        logging.info("Initiating 'power off' on outlet {}..".format(outlet))
>>>>>>> 19c303ad77b5918c2b4864e910192bf5521a31f4
        set_pdu_outlet_state(outlet, 0, **session_args)        
        while((get_pdu_outlet_state(outlet, **session_args) != 0) and power_off_timeout >= 0):
           time.sleep(5)
           power_off_timeout -= 5
        if power_off_timeout < 0:
           logging.info("Power off on outlet {} failed. Please re-try.".format(outlet))
           exit(1)
<<<<<<< HEAD
    logging.info("All outlets powered off. Checking system status.")
    time.sleep(5)
    if( not os.system("ping -c 1 -w2 " + args.system + " > /dev/null 2>&1")):
        logging.info("System pingable after power off.")
        exit(2)
    logging.info('{} is not reachable. Power Off successful'.format(args.system))

    time.sleep(30)
    for outlet in args.outlet_numbers:
        logging.info("Initiating 'power on' on outlet {}.".format(outlet))
=======
    logging.info("All outlets powered off. Checking system status..")
    time.sleep(5)
    if( not os.system("ping -c 1 -w2 " + args.system + " > /dev/null 2>&1")):
        logging.info("System pingable after power off")
        exit(2)
    logging.info('{} is not reachable. Power Off successful'.format(args.system))
    time.sleep(30)
    for outlet in args.outlet_numbers:
        logging.info("Initiating 'power on' on outlet {}..".format(outlet))
>>>>>>> 19c303ad77b5918c2b4864e910192bf5521a31f4
        set_pdu_outlet_state(outlet, 1, **session_args)
        while((get_pdu_outlet_state(outlet, **session_args) != 1) and power_on_timeout >= 0):
            time.sleep(5)
            power_on_timeout -= 5
        if power_on_timeout < 0:
            logging.info("'Power on' on outlet {} failed. Please re-try.".format(outlet))
            exit(3)
<<<<<<< HEAD
    logging.info("All outlets powered on. Checking system status.")
=======
    logging.info("All outlets powered on. Checking system status..")
>>>>>>> 19c303ad77b5918c2b4864e910192bf5521a31f4
    time.sleep(30)
    while(os.system("ping -c 1 -w2 " + args.system + " > /dev/null 2>&1") and ping_timeout >= 0):
        time.sleep(2)
        ping_timeout -= 2
    if(ping_timeout < 0):    
        logging.info("System not reachable after Power cycle. Please contact lab support team")
        exit(4)
    else:
<<<<<<< HEAD
        pre_red_text = "\x1B[31;40m"
        suf_red_text = "\x1B[0m"
        logging.info("{0} is ".format(args.system) + pre_red_text+ "pingable " + suf_red_text+ "after power" + pre_red_text+" on."+suf_red_text)
=======
        logging.info('{} is up and running. Power Off successful'.format(args.system))
        logging.info("\n\nSUCCESS : {} was power cycled successfully.".format(args.system))
>>>>>>> 19c303ad77b5918c2b4864e910192bf5521a31f4

def main():
    if args.vendor_name.lower() not in vendor_list:
        logging.info("Currently we don't support pdu cycling on {}.".format(args.vendor_name))
        exit(6)
    elif args.vendor_name.lower() == 'ibm':
        do_power_cycle_on_ibm_pdu()
        
main()
