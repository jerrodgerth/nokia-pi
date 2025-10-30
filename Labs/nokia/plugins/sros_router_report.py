from srlinux.location import build_path
from srlinux.mgmt.cli import CliPlugin, KeyCompleter
from srlinux.syntax import Syntax

class Plugin(CliPlugin):
    '''
        Adds SROS router show reports.
    '''

    def load(self, cli, **_kwargs):
        router = cli.show_mode.add_command(
            Syntax('router', help="show router information")
            .add_unnamed_argument('netinst', default='default', help = 'network instance name', suggestions=KeyCompleter('/network-instance[name=*]')),
            )
