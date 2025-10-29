# Autonomes Fahren

Dieses Repo enthält den Code für [JetBot](https://jetbot.org/master/software_setup/sd_card.html).

![jetbot](assets/jetbot.jpg)

## Setup

[Dieses Image runterladen und auf eine mindestens 64Gb Sd Karte flashen](https://nvidia.box.com/shared/static/mhtefkijy2c267rbuux6mhelj7ynjohz.zip) ~13,6GB

Als nächtes den Jetson booten (jetbot/jetbot) und via `nmtui` eine WLAN verbindung herstellen.

```sh
ssh jetbot@192.168.3.199
sudo nvpmodel -m1 # set to 5w limit
sudo nvpmodel -q # check if config applied
sudo apt update
sudo apt install nano
```

grow partition:

```sh
sudo apt install cloud-guest-utils
sudo growpart /dev/mmcblk0 1
sudo resize2fs /dev/mmcblk0p1
df -h
```

set passwordless sudo:

```sh
# sudo visudo -f /etc/sudoers.d/jetbot

jetbot ALL=(ALL) NOPASSWD:ALL
```

setup the env:

```sh
cd jetbot
git pull
sudo apt install -y python3-pip python3-setuptools python3-distutils python3-dev python3-venv build-essential python3-opencv libopencv-dev
scripts/configure_jetson.sh
scripts/enable_swap.sh
sudo reboot
```

install uv:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Mit uv das Projekt bauen bzw. Skripte starten:

```sh
git clone github.com/dav354/autonomes_fahren.git
cd autonomes_fahren
uv sync --extra jetbot
uv run python -m autonomes_fahren.camera_calibration
```

## No Jupyter
