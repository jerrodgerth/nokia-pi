"""
CLI Plugin for SR Linux for Cisco-style IP Route Command
Provides alternate command syntax for route information
Author: Alperen Akpinar
Email: alperen.akpinar@nokia.com
"""
from srlinux.syntax import Syntax
from srlinux.location import build_path
from srlinux.mgmt.cli import KeyCompleter
import datetime
import ipaddress
from srlinux.schema import FixedSchemaRoot

class IpRouteReport:
    """Handles the 'ip route' command functionality."""
    
    # Class level constants
    ROUTE_CODES = {
        'aggregate': 'Ag',
        'arp-nd': 'Ar',
        'bgp': 'B',
        'bgp-label': 'BL',
        'bgp-evpn': 'BE', 
        'bgp-vpn': 'BV',
        'dhcp': 'D',
        'gribi': 'G',
        'host': 'H',
        'isis': 'IS',
        'linux': 'Li',
        'ndk1': 'N1',
        'ndk2': 'N2',
        'ospfv2': 'O',
        'ospfv3': 'O',
        'static': 'S',
    }

    PATH_TEMPLATES = {
        'routes': '/network-instance[name={network_instance}]/route-table/ipv4-unicast/route',
        'next_hop_group': '/network-instance[name={network_instance}]/route-table/next-hop-group[index={nhg_id}]',
        'next_hop': '/network-instance[name={network_instance}]/route-table/next-hop[index={nh_id}]',
        'route_detail': '/network-instance[name={network_instance}]/route-table/ipv4-unicast/route[ipv4-prefix={ip_prefix}][route-type={route_type}][route-owner={route_owner}]'
    }

    def _show_routes(self, state, output, network_instance):
        """Main function to display routes"""
        self._print_header()

        if network_instance != 'default':
            print(f'Routing Table: VRF {network_instance}\n')

        # Get all routes
        routes_data = self._get_routes_data(state, network_instance)
        if not routes_data:
            self._print_not_found_message(network_instance)
            return

        route_entries = self._process_routes(state, network_instance, routes_data)
        self._display_routes(route_entries, network_instance)

    def _print_header(self):
        """Print command header and legend"""
        print('''Codes: C - connected, L - local, S - static, B - BGP, O - OSPF, IS - IS-IS,
       Ag - aggregate, Ar - arp-nd, BL - bgp-label, BE - bgp-evpn, BV - bgp-vpn
       D - dhcp, G - gribi, H - host, Li - linux, N1/N2 - ndk\n''')

    def _print_not_found_message(self, network_instance):
        """Print error message when VRF/routes not found"""
        print(f"Error: VRF '{network_instance}' not found or no routes present.")

    def _get_routes_data(self, state, network_instance):
        """Get routes with proper error handling"""
        try:
            routes_path = build_path(self.PATH_TEMPLATES['routes'].format(network_instance=network_instance))
            return state.server_data_store.get_data(routes_path, recursive=True)
        except Exception as e:
            return None

    def _process_routes(self, state, network_instance, routes_data):
        """Process all routes and return sorted entries"""
        all_routes = []
        
        for ni in routes_data.network_instance.items():
            route_table = ni.route_table.get()
            ipv4_unicast = route_table.ipv4_unicast.get()

            for route in ipv4_unicast.route.items():
                route_entry = self._create_route_entry(route)
                
                if route.route_type in ['local', 'connected']:
                    self._process_connected_route(state, network_instance, route, route_entry)
                else:
                    self._process_regular_route(state, network_instance, route, route_entry)
                
                all_routes.append(route_entry)

        return sorted(all_routes, key=lambda x: int(ipaddress.ip_network(x['prefix']).network_address))

    def _create_route_entry(self, route):
        """Create basic route entry with standard fields"""
        return {
            'prefix': route.ipv4_prefix,
            'code': self._get_route_code(route.route_type, route.route_owner),
            'type': route.route_type,
            'owner': route.route_owner,
            'next_hops': [],
            'uptime': self._format_uptime(route),
            'interface': None,
            'preference': route.preference,
            'metric': route.metric
        }

    def _process_connected_route(self, state, network_instance, route, route_entry):
        """Process connected/local route types"""
        next_hop_group = getattr(route, 'next_hop_group', None)
        if next_hop_group:
            try:
                next_hops = self._get_next_hops(state, network_instance, next_hop_group)
                for nh in next_hops:
                    if nh.get('interface'):
                        route_entry['interface'] = nh['interface']
                        break
            except Exception as e:
                pass

    def _process_regular_route(self, state, network_instance, route, route_entry):
        """Process non-connected route types"""
        next_hop_group = getattr(route, 'next_hop_group', None)
        if next_hop_group:
            try:
                route_entry['next_hops'] = self._get_next_hops(state, network_instance, next_hop_group)
            except Exception as e:
                pass

    def _get_next_hops(self, state, network_instance, next_hop_group):
        """Get next-hop information for a route"""
        next_hops = []
        try:
            nhg_path = build_path(self.PATH_TEMPLATES['next_hop_group'].format(
                network_instance=network_instance, 
                nhg_id=next_hop_group
            ))
            nhg_data = state.server_data_store.get_data(nhg_path, recursive=True)

            for ni in nhg_data.network_instance.items():
                nhg = ni.route_table.get().next_hop_group.get()
                for nh in nhg.next_hop.items():
                    if hasattr(nh, 'next_hop') and getattr(nh, 'resolved', False):
                        next_hop_info = self._get_next_hop_info(state, network_instance, nh.next_hop)
                        if next_hop_info:
                            next_hops.append(next_hop_info)
        except Exception as e:
            pass

        return next_hops

    def _get_next_hop_info(self, state, network_instance, next_hop_id):
        """Get detailed next-hop information"""
        try:
            nh_path = build_path(self.PATH_TEMPLATES['next_hop'].format(
                network_instance=network_instance,
                nh_id=next_hop_id
            ))
            nh_data = state.server_data_store.get_data(nh_path, recursive=True)
            next_hop = nh_data.network_instance.get().route_table.get().next_hop.get()

            subinterface = None
            if getattr(next_hop, 'type', '') == 'indirect' and hasattr(next_hop, 'resolving_route'):
                subinterface = self._get_resolving_route_interface(state, network_instance, next_hop.resolving_route)
            else:
                subinterface = getattr(next_hop, 'subinterface', None)

            if hasattr(next_hop, 'ip_address'):
                return {
                    'ip': next_hop.ip_address,
                    'interface': subinterface or ''
                }
        except Exception as e:
            pass
        return None

    def _get_resolving_route_interface(self, state, network_instance, resolving_route):
        """Follow next-hop chain recursively until finding the interface"""
        try:
            resolving_route_data = resolving_route.get()
            route_path = build_path(self.PATH_TEMPLATES['route_detail'].format(
                network_instance=network_instance,
                ip_prefix=resolving_route_data.ip_prefix,
                route_type=resolving_route_data.route_type,
                route_owner=resolving_route_data.route_owner
            ))
            
            route_data = state.server_data_store.get_data(route_path, recursive=True)
            nhg_id = route_data.network_instance.get().route_table.get().ipv4_unicast.get().route.get().next_hop_group

            next_hops = self._get_next_hops(state, network_instance, nhg_id)
            for nh in next_hops:
                if nh.get('interface'):
                    return nh['interface']

        except Exception:
            pass
        return None

    def _format_uptime(self, route):
        """Extract and format uptime for a route"""
        try:
            if not getattr(route, 'active', False):
                return ""

            if route.route_type == 'bgp':
                try:
                    last_update_str = route.last_app_update
                    if last_update_str:
                        timestamp = last_update_str.split(' (')[0]
                        last_update_time = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        current_time = datetime.datetime.now(datetime.timezone.utc)
                        uptime = current_time - last_update_time
                        days, seconds = uptime.days, uptime.seconds
                        hours = seconds // 3600
                        if days > 0:
                            return f"{days}d{hours:02d}h"
                        else:
                            minutes, seconds = divmod(seconds % 3600, 60)
                            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                except Exception:
                    pass
            return ""
        except Exception:
            return ""

    def _get_route_code(self, route_type, route_owner):
        """Get single character code for route type"""
        if route_type == 'host':
            return 'L'
        if route_type == 'local':
            return 'C'
        return self.ROUTE_CODES.get(route_type.lower(), '?')

    def _display_routes(self, routes, network_instance):
        """Display formatted routes"""
        # Check for default route
        default_route_exists = any(route['prefix'] == '0.0.0.0/0' for route in routes)
        if not default_route_exists:
            print("Gateway of last resort is not set")

        for route in routes:
            self._display_route(route)

    def _display_route(self, route):
        """Display a single route entry"""
        if route['interface']:
            print(f"{route['code']}    {route['prefix']} is directly connected, {route['interface']}")
        elif route['code'] == 'L':
            print(f"{route['code']}    {route['prefix']} is directly connected")
        elif not route['next_hops']:
            print(f"{route['code']}    {route['prefix']}")
        else:
            self._display_route_with_next_hops(route)

    def _display_route_with_next_hops(self, route):
        """Display route with its next-hops"""
        if len(route['next_hops']) > 1:
            # First next-hop
            first_hop = route['next_hops'][0]
            self._print_next_hop(route, first_hop, is_first=True)
            
            # Additional next-hops
            for next_hop in route['next_hops'][1:]:
                self._print_next_hop(route, next_hop, is_first=False)
        else:
            # Single next-hop
            self._print_next_hop(route, route['next_hops'][0], is_first=True)

    def _print_next_hop(self, route, next_hop, is_first):
        """Print a single next-hop entry"""
        if is_first:
            line = f"{route['code']}    {route['prefix']} [{route['preference']}/{route['metric']}] via {next_hop['ip']}"
        else:
            line = f"           [{route['preference']}/{route['metric']}] via {next_hop['ip']}"
            
        if route['uptime']:
            line += f", {route['uptime']}"
        if next_hop['interface']:
            line += f", {next_hop['interface']}"
            
        print(line)