# Welcome to the Raspberry Pi 5 from Nokia


## Basics

- DHCP, SSH & VNC are enabled for the wired ethernet port
- Initial login credentials:
	- user = clab
	- pwd = Clab123$
- Pre-installed software
	- Containerlab (for labs)
	- nSnake (for terminal fun)

## Containerlab notes

- Installed using the `quick setup script` from [Installation page](https://containerlab.dev/install/)
- `clab-quickstart` directory contains .yml for [Two SR Linux nodes](https://containerlab.dev/lab-examples/two-srls/) lab
	- Starting the lab
		- `cd ~/clab-quickstart`
		- `clab deploy`
	- Stoppping the lab
		- `cd ~/clab-quickstart`
		- `clab destroy` or `clab destroy -c` (to clean all directories)
- *Reminder for Containerlab:* not all NOSs have ARM images; choose lab examples accordingly


## Pi Notes

- Hardware specs
	- Model = Raspberry Pi 5
	- RAM = 8GB
	- microSD = 32GB
- Raspberry Pi OS
	- Latest version as of June, 2025
	- WiFi & many other settings can be modified using `sudo raspi-config`
- Official Raspberry Pi can be found [here](https://www.raspberrypi.com/documentation/)
