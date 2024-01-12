# Tibber Price eink display

Inspired by myself but driven by https://www.youtube.com/techpirat

## Preconditions

* Raspberry PI 2 Zero WH
* einkl Header to control the eink display
* 7.5 eink display with red/black

## Steps to install

* Install Raspberian OS WITHOUT UI
* Configure the basics using HDML+Keyboard
    * Open raspi-config
        * Setting up SSH
        * Enable SPI
* Install required python packages

```
apt update
apt install python3-pil python3-tk python3-matplotlib python3-requests python3-numpy
```

* Clone this repository
* Create Tibber API key at least with `homes` and `price` scope. Additional scopes are not used!
    * Put your tibber key in the file `api_key.py`

Beide Skripte manuell starten oder per crontab

Mit " -e" könnt ihr einen Job anlegen. Hier ein Beispiel:

0 * * * * python3 /home/joerg/Desktop/e-paper/speicher_chart_heute.py >/dev/null 2>&1
3 * * * * python3 /home/joerg/Desktop/e-paper/examples/epd_7in5_V2_anzeigen.py >/dev/null 2>&1

Damit wird das eine Skript immer zur vollen und das zweite 3 Minuten nach jeder vollen Stunde gestartet.

Nach dem Starten wird das Display alle 60 Minuten aktualisiert.

Besucht mich auf YouTube: https://www.youtube.com/techpirat

# Warranty & Licensinf

* No Warranty
* Code is (still) under GPL3
* Used libraries my have other licenses!