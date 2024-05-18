# Tibber Price eink display

Inspired by myself but driven by https://www.youtube.com/techpirat

## Preconditions

* Raspberry PI 2 Zero WH
* 7.5 eink display with red/black (Waveshare 7.5inch HD e-Paper HAT (B))
* HAT of the display that is on top of your Raspberry

## Steps to install

* Install Raspberian OS WITHOUT UI - **Min. Bookworm to get Python 3.11!**
* Configure the basics using HDML+Keyboard
    * Open raspi-config
        * Setting up SSH
        * Setting up Wifi
        * Enable SPI
* Install required python packages

```
apt update
apt install python3-pil python3-matplotlib python3-requests
```

* Clone this repository
* Create Tibber API key at least with `homes` and `price` scope. Additional scopes are not used!
    * Put your tibber key in the file `configuration.py`

### Optional: Disable the LED

Edit the `/boot/config.txt` file. Add to the end (if not existend) under `[all]`:
```
dtparam=act_led_trigger=none
dtparam=act_led_activelow=on
```

### Run frequently with crontab

Open the cron of the user with `crontab -e`. And add the following lines:

```
0 * * * * cd tibber-eink-display/ && python3 ./create_price_chart.py && python3 ./chart_to_display.sh
```

This updates the chart every hour and displays it on the eink display.

# Local development - Open for pull requests ;-) 

Install following:

```
pip3 install matplotlib
pip3 install requests
```

Start the `create_price_chart.py` and watch the files in the `charts/` folder

# Warranty & Licensing

* No Warranty
* Code is (still) under GPL3
* Used libraries and fonts my have other licenses!