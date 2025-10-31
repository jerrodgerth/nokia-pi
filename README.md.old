# Welcome to the Raspberry Pi 5 from Nokia


## Basics

- DHCP & SSH are enabled for the wired Ethernet port
- Hostname:
  - raspberrpi.local 
- Credentials:
	- user = clab
	- pwd = Clab123!

  e.g. `ssh clab@raspberrypi.local`


## Pre-installed software
	
- Starship prompt
- CLI utilities
  - `eza`, `zoxide`, `lazydocker`, `fastfetch`, `btop`
- Containerlab (for labs)
- nSnake (for terminal fun)


## Containerlab notes

- Installed using the `quick setup script` from [Installation page](https://containerlab.dev/install/)
- `Labs/two-srl-pi/` directory contains `two-srl-pi.yml`
- Starting the lab
	- `cd ~/Labs/two-srl-pi/`
	- `clab deploy`
- Stoppping the lab
	- `cd ~/Labs/two-srl-pi/`
	- `clab destroy` or `clab destroy -c` (to clean all directories)

  *Reminder for Containerlab:* not all NOSs have ARM images; choose lab examples accordingly


## Pi Notes

- Hardware specs
	- Model = Raspberry Pi 5
	- RAM = 8GB
	- microSD = 32GB
- Raspberry Pi OS
	- Latest version as of October, 2025 (Debian Trixie)
    - **Raspberry Pi OS Lite** as the base for a headless server
    - [Convert Raspberry Pi OS Lite into Raspberry Pi OS Desktop](https://www.raspberrypi.com/documentation/computers/os.html#convert-raspberry-pi-os-lite-into-raspberry-pi-os-desktop)
	- WiFi & many other settings can be modified using `sudo raspi-config`
- Official Raspberry Pi Docs can be found [here](https://www.raspberrypi.com/documentation/)
