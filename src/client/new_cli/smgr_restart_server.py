#!/usr/bin/python

# vim: tabstop=4 shiftwidth=4 softtabstop=4
"""
   Name : smgr_restart_server.py
   Author : Abhay Joshi
   Description : This program is a simple cli interface that
   provides restarting server(s) via server manager. The program
   takes an optional parameter (netboot), if set the server is
   enabled for booting from net, else a local boot is performed.
"""
import argparse
import pdb
import sys
import pycurl
from StringIO import StringIO
import json

_DEF_SMGR_IP_ADDR = '127.0.0.1'
_DEF_SMGR_PORT = 8090


def parse_arguments(args_str=None):
    if not args_str:
        args_str = sys.argv[1:]
    # Process the arguments
    parser = argparse.ArgumentParser(
        description='''Reboot given server(s)'''
    )
    parser.add_argument("--smgr_ip", "-i",
                        help="IP address of the server manager.")
    parser.add_argument("--smgr_port", "-p",
                        help="server manager listening port number")
    parser.add_argument("server_list",
                        help=("match condition identifying server(s)"
                              "should be one of following:"
                              " server_id=SERVER_ID,"
                              " mac=SERVER_MAC,"
                              " cluster_id=CLUSTER_ID,"
                              " rack_id=RACK_ID,"
                              " pod_id=POD_ID,"
                              " vns_id=VNS_ID"))
    parser.add_argument("--net_boot", "-n", action="store_true",
                        help=("optional parameter to indicate"
                             " if server should be netbooted."))
    args = parser.parse_args()
    return args


def send_REST_request(ip, port, payload):
    try:
        response = StringIO()
        headers = ["Content-Type:application/json"]
        url = "http://%s:%s/server/restart" %(
            ip, port)
        conn = pycurl.Curl()
        conn.setopt(pycurl.URL, url)
        conn.setopt(pycurl.HTTPHEADER, headers)
        conn.setopt(pycurl.POST, 1)
        conn.setopt(pycurl.POSTFIELDS, '%s'%json.dumps(payload))
        conn.setopt(pycurl.WRITEFUNCTION, response.write)
        conn.perform()
        return response.getvalue()
    except:
        return None

def restart_server(args_str=None):
    serverMgrCfg = {
        'smgr_ip_addr': _DEF_SMGR_IP_ADDR,
        'smgr_port': _DEF_SMGR_PORT
    }
    args = parse_arguments(args_str)
    if args.smgr_ip:
        serverMgrCfg['smgr_ip_addr'] = args.smgr_ip
    if args.smgr_port:
        serverMgrCfg['smgr_port'] = args.smgr_port
    server_list = args.server_list
    if (server_list.startswith("server_id=") or
        server_list.startswith("mac=") or
        server_list.startswith("cluster_id=") or
        server_list.startswith("rack_id=") or
        server_list.startswith("pod_id=") or
        server_list.startswith("vns_id=")):
        pass
    else:
        sys.exit("Error : Invalid server selection criteria.")

    x = server_list.split("=", 2)
    match_key = x[0]
    match_value = x[1]
    
    payload = {}
    if (args.net_boot):
        payload['net_boot'] = "y"
    payload[match_key] = match_value
 
    resp = send_REST_request(serverMgrCfg['smgr_ip_addr'],
                      serverMgrCfg['smgr_port'],
                      payload)
    print resp
# End of restart_server

if __name__ == "__main__":
    import cgitb
    cgitb.enable(format='text')

    restart_server(sys.argv[1:])
# End if __name__