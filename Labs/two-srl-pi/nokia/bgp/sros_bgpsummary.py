#!/usr/bin/python
###########################################################################
# Description:
#
# Copyright (c) 2020 Nokia
###########################################################################

from os import name
from srlinux import data
from srlinux.data import Border, ColumnFormatter, TagValueFormatter, Data, Borders, Formatter, TagValuePrinter, Indent
from srlinux.location import build_path
from srlinux.schema import FixedSchemaRoot
from srlinux.syntax import Syntax
from datetime import datetime, timezone


class BgpSummaryFilter(object):

    def __init__(self):
        # dictionary for BGP stats
        
        self._netinst = None
        self._router_id = None
        self._asn = None
        self._local_as = None
        self._admin_state = None
        self._oper_state = None
        self._groups = 0
        self._neighbors = 0
        self._path_memory = None
        self._neighbor_data = {}
        self._stats = {
            'total_ipv4_remote_rts' : 0,
            'total_ipv6_remote_rts' : 0,
            'total_ipv4_backup_rts' : 0,
            'total_lblipv4_rem_rts' : 0,
            'total_lblipv6_rem_rts' : 0,
            'total_lblipv4_bkp_rts' : 0,
            'total_supressed_rts' : 0,
            'total_decay_rts' : 0,
            'total_ipv4_rem_active_rts' : 0,
            'total_ipv6_rem_active_rts' : 0,
            'total_ipv6_backup_rts' : 0,
            'total_lblipv4_rem_act_rts' : 0,
            'total_lblipv6_rem_act_rts' : 0,
            'total_lblipv6_bkp_rts' : 0,
            'total_hist_rts' : 0,
            'total_vpn_ipv4_rem_rts' : 0,
            'total_vpn_ipv6_rem_rts' : 0,
            'total_vpn_ipv4_bkup_rts' : 0,
            'total_vpn_local_rts' : 0,
            'total_vpn_hist_rts' : 0,
            'total_vpn_ipv4_rem_act_rts' : 0,
            'total_vpn_ipv6_rem_act_rts' : 0,
            'total_vpn_ipv6_bkup_rts' : 0,
            'total_vpn_supp_rts' : 0,
            'total_vpn_decay_rts' : 0,
            'total_evpn_rem_rts' : 0,
            'total_evpn_rem_act_rts' : 0,
        }  

    def get_syntax(self):
        """Returns the Syntax for the show router bgp summary SR-OS command

        Args:
            self (BgpSummaryFilter): main class

        Returns:
            Syntax: summary with help for SR-OS command
        """
        
        result = Syntax('summary', help='show bgp summary information for a network instance')
        return result

    def get_data_schema(self):
        """Returns the Schema describing the data-model of the show routine. 

        Args:
            self (BgpSummaryFilter): main class

        Returns:
            FixedSchemaRoot: object following with following the data-model:
            list bgp {
                key 'router_id';
                leaf 'asn';
                leaf 'local_as';
                leaf 'admin_state';
                leaf 'oper_state';
                leaf 'groups';
                leaf 'neighbors';
                leaf 'stats';
                leaf 'path_memory';
                list neighbor {
                    key 'peer_address';
                    leaf 'ip';
                    leaf 'asn';
                    leaf 'pkts_received';
                    leaf 'pkts_sent';
                    leaf 'session_state';
                    leaf 'uptime';
                    leaf 'routes_received';
                    leaf 'routes_active';
                    leaf 'routes_sent';
                    list 'afi_safi' {
                        key 'afi_safi_name';
                        leaf 'name';
                        leaf 'received_routes';
                        leaf 'active_routes';
                        leaf 'sent_routes';
                    }
                }
            }
                
        """
        
        root = FixedSchemaRoot()
        bgp = root.add_child(
            'bgp',
            key = 'router_id',
            fields=[
                'asn',
                'local_as',
                'admin_state',
                'oper_state',
                'groups',
                'neighbors',
                'stats',
                'path_memory'
            ]
        )
        neighbor = bgp.add_child(
            'neighbor',
            key = 'peer_address',
            fields=[
                'ip',
                'asn',
                'pkts_received',
                'pkts_sent',
                'session_state',
                'uptime',
                'routes_received',
                'routes_active',
                'routes_sent'
            ]
        )
        neighbor.add_child(
            'afi_safi',
            key = 'afi_safi_name',
            fields=[
                'name',
                'received_routes',
                'active_routes',
                'sent_routes'
            ]
        )
        
        return root

    def print(self, state, arguments, output, **_kwargs):
        """Prints all information for SR-OS command show router bgp summary
        
        Args:
            self (BgpSummaryFilter): main class
            state (CliState): data state from the node
            arguments (CommandNodeWithArguments): arguments ingressed via CLI
            output (CliOutput): output CLI

        Returns:
            Prints output for command

        """
        
        # Getting BGP information and assigning it to Class variables
        self._getBgpSummary_(state, arguments)
        self._getBgpNeighborList_(state, arguments)

        # populating data Class and formatting for CLI output
        result = self._populate_data(arguments, state)
        self._set_formatters(result, state)
        output.print_data(result)
        print(f'\nTry SR Linux command: show network-instance {self._netinst} protocols bgp summary\n')

    # Dumping information into Data object based on CLI schema
    def _populate_data(self, arguments, state):
        """Takes information in attributes in self class and dumps them into a Data object that follows the data schema defined
        
        Args:
            self (BgpSummaryFilter): main class
            arguments (CommandNodeWithArguments): arguments ingressed via CLI

        Returns:
            Data: result that follows the schema previously defined in get_data_schema() taking attributes from self class as input for the data model

        """
        
        result = Data(arguments.schema)

        # Dumping BGP information 
        bgp = result.bgp.create(self._router_id)
        bgp.asn = self._asn
        bgp.local_as = self._local_as
        bgp.admin_state = self._admin_state
        bgp.oper_state = self._oper_state
        bgp.groups = self._groups
        bgp.neighbors = self._neighbors
        bgp.stats = self._stats
        bgp.path_memory = self._path_memory
        
        # Dumping neighbor information through self._neighbor_data filled in self_getBgpNeighborList_()
        for neighbor_temp in self._neighbor_data:
            neighbor = bgp.neighbor.create(self._neighbor_data[neighbor_temp]['ip'])
            neighbor.ip = self._neighbor_data[neighbor_temp]['ip']
            neighbor.asn = self._neighbor_data[neighbor_temp]['asn']
            neighbor.pkts_received = self._neighbor_data[neighbor_temp]['pkts_received']
            neighbor.pkts_sent = self._neighbor_data[neighbor_temp]['pkts_sent'] 
            neighbor.session_state = self._neighbor_data[neighbor_temp]['session_state']
            neighbor.uptime = self._neighbor_data[neighbor_temp]['uptime']
            neighbor.routes_received = self._neighbor_data[neighbor_temp]['routes_received']
            neighbor.routes_active = self._neighbor_data[neighbor_temp]['routes_active']
            neighbor.routes_sent = self._neighbor_data[neighbor_temp]['routes_sent']                             

            # Dumping afi_safi information iterating through the neighbor dictionary:
            counter = 0
            for afi_safi_temp in self._neighbor_data[neighbor_temp]: 
                try:
                    if self._neighbor_data[neighbor_temp][f'afi_safi_{counter}']['admin_state'] == "enable":
                        afi_safi = neighbor.afi_safi.create(f'afi_safi_{counter}')
                        afi_safi.name = self._neighbor_data[neighbor_temp][f'afi_safi_{counter}']['name']
                        afi_safi.received_routes = self._neighbor_data[neighbor_temp][f'afi_safi_{counter}']['received_routes']
                        afi_safi.active_routes = self._neighbor_data[neighbor_temp][f'afi_safi_{counter}']['active_routes']
                        afi_safi.sent_routes = self._neighbor_data[neighbor_temp][f'afi_safi_{counter}']['sent_routes']
                        counter += 1
                except KeyError:
                    break
                except Exception as e:
                    break
                
        return result

    def _getBgpSummary_(self, state, arguments):
        """Retrieves main BGP information from the path defined and assigns them to the self class attributes

        Args:
            self (BgpSummaryFilter): main class
            state (CliState): data state from the node
            arguments (CommandNodeWithArguments): arguments ingressed via CLI

        Returns:
            None

        """
        
        self._netinst = arguments.get('router','netinst')

        # building path using network-instance value entered via CLI
        path = build_path('/network-instance[name={name}]/protocols/bgp',name=self._netinst)
        data = state.server_data_store.get_data(path, recursive=True)
        
        self._router_id = data.network_instance.get().protocols.get().bgp.get().router_id
        self._asn = data.network_instance.get().protocols.get().bgp.get().autonomous_system
        self._local_as = data.network_instance.get().protocols.get().bgp.get().autonomous_system
        self._admin_state = data.network_instance.get().protocols.get().bgp.get().admin_state
        self._oper_state = data.network_instance.get().protocols.get().bgp.get().oper_state

        self._groups = 0
        for group in data.network_instance.get().protocols.get().bgp.get().group.items():
            self._groups += 1

        self._neighbors = 0
        for group in data.network_instance.get().protocols.get().bgp.get().neighbor.items():
            self._neighbors += 1

        self._path_memory = data.network_instance.get().protocols.get().bgp.get().statistics.get().path_memory

    def _getBgpNeighborList_(self, state, arguments):
        """Retrieves BGP neighbor state iterating through all neighbors and afi-safi. It then assigns them to the self class attributes.

        Args:
            self (BgpSummaryFilter): main class
            state (CliState): data state from the node
            arguments (CommandNodeWithArguments): arguments ingressed via CLI

        Returns:
            None

        """
        
        self._netinst = arguments.get('router','netinst')
        
        # building path using network-instance value entered via CLI for all BGP Neighbors
        path = build_path('/network-instance[name={name}]/protocols/bgp/neighbor[peer-address=*]',name=self._netinst)
        data: Data = state.server_data_store.get_data(path, recursive=False)

        # getting peer-address from state datastore
        neighbor_list = []
        for neighbor_path in data.network_instance.get().protocols.get().bgp.get().neighbor.items():
            neighbor_list.append(neighbor_path.peer_address)
        
        # geting information per BGP Neighbor on a dictionary
        neighbor_data = {}
        for neighbor_ip in neighbor_list:
            neighbor_data[neighbor_ip] = {}

            path = build_path('/network-instance[name={name}]/protocols/bgp/neighbor[peer-address={ip}]',name=self._netinst,ip=neighbor_ip)
            data = state.server_data_store.get_data(path, recursive=True)

            neighbor_data[neighbor_ip]['ip'] = data.network_instance.get().protocols.get().bgp.get().neighbor.get().peer_address
            neighbor_data[neighbor_ip]['asn'] = data.network_instance.get().protocols.get().bgp.get().neighbor.get().peer_as
            neighbor_data[neighbor_ip]['pkts_received'] = data.network_instance.get().protocols.get().bgp.get().neighbor.get().received_messages.get().total_messages
            neighbor_data[neighbor_ip]['pkts_sent'] = data.network_instance.get().protocols.get().bgp.get().neighbor.get().sent_messages.get().total_messages
            
            # information available only if BGP Session is Established
            neighbor_data[neighbor_ip]['session_state'] = data.network_instance.get().protocols.get().bgp.get().neighbor.get().session_state
            if neighbor_data[neighbor_ip]['session_state'] == 'established':
                neighbor_data[neighbor_ip]['uptime'] = data.network_instance.get().protocols.get().bgp.get().neighbor.get().last_established
                neighbor_data[neighbor_ip]['routes_received'] = data.network_instance.get().protocols.get().bgp.get().neighbor.get().afi_safi.get().received_routes
                neighbor_data[neighbor_ip]['routes_active'] = data.network_instance.get().protocols.get().bgp.get().neighbor.get().afi_safi.get().active_routes
                neighbor_data[neighbor_ip]['routes_sent'] = data.network_instance.get().protocols.get().bgp.get().neighbor.get().afi_safi.get().sent_routes
            
                # geting all afi_safi information per BGP neighbor only for Enabled afi_safi
                counter = 0
                for afi_safi in data.network_instance.get().protocols.get().bgp.get().neighbor.get().afi_safi.items():
                    if afi_safi.admin_state == "enable":
                        neighbor_data[neighbor_ip][f'afi_safi_{counter}'] = {}
                        neighbor_data[neighbor_ip][f'afi_safi_{counter}']['admin_state'] = afi_safi.admin_state
                        neighbor_data[neighbor_ip][f'afi_safi_{counter}']['name'] = afi_safi.afi_safi_name
                        neighbor_data[neighbor_ip][f'afi_safi_{counter}']['received_routes'] = afi_safi.received_routes
                        neighbor_data[neighbor_ip][f'afi_safi_{counter}']['active_routes'] = afi_safi.active_routes
                        neighbor_data[neighbor_ip][f'afi_safi_{counter}']['sent_routes'] = afi_safi.sent_routes
                        counter += 1
            
                        # getting total BGP stats
                        if afi_safi.afi_safi_name == 'ipv4-unicast':
                            self._stats['total_ipv4_remote_rts'] += afi_safi.received_routes
                            self._stats['total_ipv4_backup_rts'] += 0
                            self._stats['total_ipv4_rem_active_rts'] += afi_safi.active_routes
                        elif afi_safi.afi_safi_name == 'ipv6-unicast':
                            self._stats['total_ipv6_remote_rts'] += afi_safi.received_routes
                            self._stats['total_ipv6_backup_rts'] += 0
                            self._stats['total_ipv6_rem_active_rts'] += afi_safi.active_routes
                        elif afi_safi.afi_safi_name == 'evpn':
                            self._stats['total_evpn_rem_rts'] += afi_safi.received_routes
                            self._stats['total_evpn_rem_act_rts'] += afi_safi.active_routes
                        elif afi_safi.afi_safi_name == 'ipv4-labeled-unicast':
                            self._stats['total_lblipv4_rem_rts'] += afi_safi.received_routes
                            self._stats['total_lblipv4_bkp_rts'] += 0
                            self._stats['total_lblipv4_rem_act_rts'] += afi_safi.active_routes
                        elif afi_safi.afi_safi_name == 'ipv6-labeled-unicast':
                            self._stats['total_lblipv6_rem_rts'] += afi_safi.received_routes
                            self._stats['total_lblipv6_bkp_rts'] += 0
                            self._stats['total_lblipv6_rem_act_rts'] += afi_safi.active_routes
                        elif afi_safi.afi_safi_name == 'l3vpn-ipv4-unicast':
                            self._stats['total_vpn_ipv4_rem_rts'] += afi_safi.received_routes
                            self._stats['total_vpn_ipv4_bkup_rts'] += 0
                            self._stats['total_vpn_ipv4_rem_act_rts'] += afi_safi.active_routes
                        elif afi_safi.afi_safi_name == 'l3vpn-ipv6-unicast':
                            self._stats['total_vpn_ipv6_rem_rts'] += afi_safi.received_routes
                            self._stats['total_vpn_ipv6_bkup_rts'] += 0
                            self._stats['total_vpn_ipv6_rem_act_rts'] += afi_safi.active_routes

            # if BGP Session is not Established, empty values
            else:
                neighbor_data[neighbor_ip]['uptime'] = 0
                neighbor_data[neighbor_ip]['routes_received'] = 0
                neighbor_data[neighbor_ip]['routes_active'] = 0
                neighbor_data[neighbor_ip]['routes_sent'] = 0
                neighbor_data[neighbor_ip]['afi_safi_0'] = {}

            

        # Assigning obtained information to a Class variable
        self._neighbor_data = neighbor_data

    # formatting based on Key:Value for Debugging
    # not required but used for initial debugging
    def _printKeyValue (self, data:Data, state):
        data.set_formatter('/bgp', ColumnFormatter(ancestor_keys=False, print_on_data=True))
        print("\n***********************\nDEBUG: Print Formatter\n***********************")
        data.set_formatter('/bgp', Indent(TagValueFormatter(ancestor_keys=False),indentation=0))
        print(f'-----------------------------------------')
        data.set_formatter('/bgp/neighbor', Indent(TagValueFormatter(ancestor_keys=False),indentation=4))
        print(f'-----------------------------------------')
        data.set_formatter('/bgp/neighbor/afi_safi', Indent(TagValueFormatter(ancestor_keys=False),indentation=8))

    # formatting based on data schema provided in self._get_data_schema()
    def _set_formatters(self, data:Data, state):
        data.set_formatter('/bgp', SrosBgpHeaderFormatter())
        data.set_formatter('/bgp/neighbor', SrosBgpNeighborFormatter())
        data.set_formatter('/bgp/neighbor/afi_safi', SrosBgpAfiSafiFormatter(self.get_data_schema()))

class SrosBgpHeaderFormatter(Formatter):
    def iter_format(self, entry, max_width):
        yield from self._format_header_line(max_width)
        yield f' BGP Router ID:{entry.router_id:<20} AS:{entry.asn:<10} Local AS:{entry.local_as:<10}'
        yield from self._format_header_line(max_width)
        # Print "Up" if entry.router_id is "enable", otherwise print "Down"
        admin_state = "Up" if entry.admin_state == "enable" else "Down"
        oper_state = "Up" if entry.oper_state == "up" else "Down"
        yield f'BGP Admin State         : {admin_state:<11} BGP Oper State              : {oper_state:<10}'
        yield f'Total Peer Groups       : {entry.groups:<3}         Total Peers                 : {entry.neighbors:<4}      '
        yield f'Total VPN Peer Groups   : 0           Total VPN Peers             : 0         '
        yield f'Current Internal Groups : 1           Max Internal Groups         : 1         '
        yield f'Total BGP Paths         : 52          Total Path Memory           : {entry.path_memory:<6}'
        yield f' '
        yield f"Total IPv4 Remote Rts   : {entry.stats['total_ipv4_remote_rts']:<10}  Total IPv4 Rem. Active Rts  : {entry.stats['total_ipv4_rem_active_rts']:<10}"
        yield f"Total IPv6 Remote Rts   : {entry.stats['total_ipv6_remote_rts']:<10}  Total IPv6 Rem. Active Rts  : {entry.stats['total_ipv6_rem_active_rts']:<10}"
        yield f"Total IPv4 Backup Rts   : {entry.stats['total_ipv4_backup_rts']:<10}  Total IPv6 Backup Rts       : {entry.stats['total_ipv6_backup_rts']:<10}"
        yield f"Total LblIpv4 Rem Rts   : {entry.stats['total_lblipv4_rem_rts']:<10}  Total LblIpv4 Rem. Act Rts  : {entry.stats['total_lblipv4_rem_act_rts']:<10}"
        yield f"Total LblIpv6 Rem Rts   : {entry.stats['total_lblipv6_rem_rts']:<10}  Total LblIpv6 Rem. Act Rts  : {entry.stats['total_lblipv6_rem_act_rts']:<10}"
        yield f"Total LblIpv4 Bkp Rts   : {entry.stats['total_lblipv4_bkp_rts']:<10}  Total LblIpv6 Bkp Rts       : {entry.stats['total_lblipv6_bkp_rts']:<10}"
        yield f"Total Supressed Rts     : {entry.stats['total_supressed_rts']:<10}  Total Hist. Rts             : {entry.stats['total_hist_rts']:<10}"
        yield f"Total Decay Rts         : {entry.stats['total_decay_rts']:<10}"
        yield f' '
        yield f"Total VPN-IPv4 Rem. Rts : {entry.stats['total_vpn_ipv4_rem_rts']:<10}  Total VPN-IPv4 Rem. Act. Rts: {entry.stats['total_vpn_ipv4_rem_act_rts']:<10}"
        yield f"Total VPN-IPv6 Rem. Rts : {entry.stats['total_vpn_ipv6_rem_rts']:<10}  Total VPN-IPv6 Rem. Act. Rts: {entry.stats['total_vpn_ipv6_rem_act_rts']:<10}"
        yield f"Total VPN-IPv4 Bkup Rts : {entry.stats['total_vpn_ipv4_bkup_rts']:<10}  Total VPN-IPv6 Bkup Rts     : {entry.stats['total_vpn_ipv6_bkup_rts']:<10}"
        yield f"Total VPN Local Rts     : {entry.stats['total_vpn_local_rts']:<10}  Total VPN Supp. Rts         : {entry.stats['total_vpn_supp_rts']:<10}"
        yield f"Total VPN Hist. Rts     : {entry.stats['total_vpn_hist_rts']:<10}  Total VPN Decay Rts         : {entry.stats['total_vpn_decay_rts']:<10}"
        yield f' '
        yield f'Total MVPN-IPv4 Rem Rts : 0           Total MVPN-IPv4 Rem Act Rts : 0         '
        yield f'Total MVPN-IPv6 Rem Rts : 0           Total MVPN-IPv6 Rem Act Rts : 0         '
        yield f'Total MDT-SAFI Rem Rts  : 0           Total MDT-SAFI Rem Act Rts  : 0         '
        yield f'Total McIPv4 Remote Rts : 0           Total McIPv4 Rem. Active Rts: 0         '
        yield f'Total McIPv6 Remote Rts : 0           Total McIPv6 Rem. Active Rts: 0         '
        yield f'Total McVpnIPv4 Rem Rts : 0           Total McVpnIPv4 Rem Act Rts : 0         '
        yield f'Total McVpnIPv6 Rem Rts : 0           Total McVpnIPv6 Rem Act Rts : 0         '
        yield f' '
        yield f"Total EVPN Rem Rts      : {entry.stats['total_evpn_rem_rts']:<10}  Total EVPN Rem Act Rts      : {entry.stats['total_evpn_rem_act_rts']:<10}"
        yield f'Total L2-VPN Rem. Rts   : 0           Total L2VPN Rem. Act. Rts   : 0         '
        yield f'Total MSPW Rem Rts      : 0           Total MSPW Rem Act Rts      : 0         '
        yield f'Total RouteTgt Rem Rts  : 0           Total RouteTgt Rem Act Rts  : 0         '
        yield f'Total FlowIpv4 Rem Rts  : 0           Total FlowIpv4 Rem Act Rts  : 0         '
        yield f'Total FlowIpv6 Rem Rts  : 0           Total FlowIpv6 Rem Act Rts  : 0         '
        yield f'Total FlowVpnv4 Rem Rts : 0           Total FlowVpnv4 Rem Act Rts : 0         '
        yield f'Total FlowVpnv6 Rem Rts : 0           Total FlowVpnv6 Rem Act Rts : 0         '
        yield f'Total Link State Rem Rts: 0           Total Link State Rem Act Rts: 0         '
        yield f'Total SrPlcyIpv4 Rem Rts: 0           Total SrPlcyIpv4 Rem Act Rts: 0         '
        yield f'Total SrPlcyIpv6 Rem Rts: 0           Total SrPlcyIpv6 Rem Act Rts: 0         '

        if entry.neighbor.exists():
            yield from self._format_header(max_width)
            yield from entry.neighbor.iter_format(max_width)

        yield from self._format_footer(max_width)
            
    def _format_header_line(self, width):
        return (
            '===============================================================================',
        )

    def _format_header(self, width):
        return (
            '',
            '===============================================================================',
            'BGP Summary',
            '===============================================================================',
            'Legend : D - Dynamic Neighbor',
            '===============================================================================',
            'Neighbor',
            'Description',
            '                   AS PktRcvd InQ  Up/Down   State|Rcv/Act/Sent (Addr Family)',
            '                      PktSent OutQ',
            '-------------------------------------------------------------------------------',
        )

    def _format_footer(self, width):
        return (
            '-------------------------------------------------------------------------------',
        )

class SrosBgpNeighborFormatter(Formatter):
    def iter_format(self, entry: Data, max_width):

        # Print uptime if session is established, otherwise print session_state
        if entry.session_state == "established":
            uptime = self._get_time(entry.uptime)
        else:
            uptime = entry.session_state

        yield f'{entry.ip}'
        line0 = f'                {entry.asn:<7}    {entry.pkts_received:<7}0 {uptime:<10} '
        line1 = f'                           {entry.pkts_sent:<7}0           '

        # print afi_safi information
        if entry.afi_safi.exists(): 
            afi_safi_info = entry.afi_safi.iter_format(max_width)
            
            counter = entry.afi_safi.get().afi_safi_name # need to be fixed to iterate for each afi_safi entry
            if counter == 'afi_safi_0': prefix = line0
            elif counter == 'afi_safi_1': prefix = line1
            else: prefix = f'                                             '

            # line = prefix.join(afi_safi_info)
            line = ''.join(afi_safi_info) # temp
        else:
            line = ''

        yield line0 # temp
        yield line1 # temp

        yield line

    def _get_time(self, time_value):
        
        if time_value != 0:
            # Given time value in ISO 8601 format "2025-03-08T23:29:45.900Z"
            # Parse the given time value to a datetime object
            given_time = datetime.strptime(time_value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

            # Get the current time in UTC
            current_time = datetime.now(timezone.utc)

            # Calculate the difference between the current time and the given time
            time_difference = current_time - given_time

            # Extract hours, minutes, and seconds from the time difference
            total_seconds = int(time_difference.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Format the output as 00h04m10s
            formatted_output = f"{hours:02}h{minutes:02}m{seconds:02}s"

        elif time_value == 0:
            formatted_output = ""

        return formatted_output


class SrosBgpAfiSafiFormatter(TagValueFormatter):

    def __init__(self, schema):
        TagValueFormatter.__init__(self)
        self._schema = schema

    def iter_format(self, entry, max_width):
        
        sros_afisafi = {
            'l3vpn-ipv4-unicast' : 'VpnIPv4',
            'l3vpn-ipv6-unicast' : 'VpnIPv4',
            'evpn' : 'Evpn',
            'ipv4-unicast' : 'IPv4',
            'ipv6-unicast' : 'IPv6',
            'ipv4-labeled-unicast' : 'Lbl-IPv4',
            'ipv6-labeled-unicast' : 'Lbl-IPv6',

        }

        yield f'                                             {entry.received_routes}/{entry.active_routes}/{entry.sent_routes} ({sros_afisafi[entry.name]})\n'
  
        
