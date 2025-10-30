# Custom CLI Plugins for Arista EOS

The following CLI plugins are available in this repo:

> [!NOTE]
> At the time of releasing these scripts, SR Linux did not support a custom CLI path that was loaded on top of an existing native path. Due to this reason, some EOS commands start with the syntax `show eos`. This will be fixed in a future release.

| Command | Contributor |
|---|---|
| `show eos interface` | [mfzhsn](https://github.com/mfzhsn) |
| `show eos interface status` | [mfzhsn](https://github.com/mfzhsn) |
| `show arp` | [mfzhsn](https://github.com/mfzhsn) |
| `show ip bgp summary` | [sajusal](https://github.com/sajusal) |
| `show bgp evpn route-type auto-discovery` | [sajusal](https://github.com/sajusal) |
| `show bgp evpn route-type mac-ip` | [sajusal](https://github.com/sajusal) |
| `show bgp evpn route-type imet` | [sajusal](https://github.com/sajusal) |
| `show bgp evpn route-type ethernet-segment` | [sajusal](https://github.com/sajusal) |
| `show bgp evpn route-type ip-prefix` | [sajusal](https://github.com/sajusal) |
| `show bgp evpn summary` | [sajusal](https://github.com/sajusal) |

## Testing

Deploy the EVPN lab. Login to any leaf or spine node using `auser/auser` and try any of the above commands.

## Custom CLI Plugin scripts

This folder contains custom CLI python scripts for EOS commands.

The scripts are arranged in this format. The main_arista.py checks the imports in the shown path below

```
/home/auser/cli
├── bgp
│   └── bgp_evpn_report.py            # Handles BGP EVPN Route Type and summary reports
│
├── interface
│   ├── arista_arp_details.py         # Parses and formats ARP entries
│   ├── arista_interface_detail.py    # Displays detailed interface info (Arista style)
│   ├── arista_interface_status.py    # Displays brief interface status (Arista style)
│   
│
├── ip
│   └── ip_bgp_report.py              # Generates standard BGP summary reports
│
└── plugins
    ├── main_arista.py                # Loads Arista-style CLI plugins

```

### Verification commands:

**Interface Status**:
```
show eos interface status
```

**Interface Details**:
```
show eos interface {interface_name}
```
*OR, to list all interfaces*

```
show eos interface
```

**ARP Details**:
```
show eos arp
```
OR, to provide optional arguments,

```
show eos arp interface {interface_name}
```

