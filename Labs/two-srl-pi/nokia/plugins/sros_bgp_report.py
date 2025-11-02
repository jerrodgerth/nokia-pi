from modulefinder import Module
from srlinux.location import build_path
from srlinux.mgmt.cli import CliPlugin, RequiredPlugin, KeyCompleter
from srlinux.syntax import Syntax

################################################################################
# Importing BgpSummaryFilter class
import sys
import os
# Dynamically find the correct module directory
# Need to add the paths explicitly as the env that script runs is somewhere else
potential_paths = [
    os.path.expanduser('~/cli'),
    '/etc/opt/srlinux/cli'
]
# Find the first valid path
import_base = None
for path in potential_paths:
    if os.path.exists(path):
        import_base = path
        break
if import_base is None:
    raise ImportError("Could not find a valid CLI plugin base directory")
import_path = os.path.join(import_base, "bgp")
# Add to Python path if not already present
if import_path not in sys.path:
    sys.path.insert(0, import_path)
# Import your subcodes
from sros_bgpsummary import BgpSummaryFilter
################################################################################

class Plugin(CliPlugin):
    '''
        Adds bgp routes ipv4 summary show reports.
    '''

    def get_required_plugins(self):

        return [
            # bgp_reports adds 'show network-instance' so it must be loaded first
            # to add our new plugin beneath it.
            RequiredPlugin(module='srlinux', plugin='sros_router_report')
        ]
    
    def load(self, cli, **_kwargs):
        router = cli.show_mode.root.get_command('router')

        bgp = router.add_command(
            Syntax('bgp', help='show bgp information for a network instance'),
            update_location=True
            )
        bgp.add_command(
            BgpSummaryFilter().get_syntax(),
            update_location=False,
            callback=BgpSummaryFilter().print,
            schema=BgpSummaryFilter().get_data_schema(),
        )
