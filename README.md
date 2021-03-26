# Binance Real time Crypto Ticker
A Binance socket real time cryptocurrency ticker for Raspberry Pi using a 64x32 LED Matrix

Inspired from https://github.com/Howchoo/crypto-ticker.

> Attention: This is `only the software part` that drives the LED Matrix. Once you have all the hardware assembled, use this software to display real time crypto data from Binance. Check out this [Guide](https://howchoo.com/pi/raspberry-pi-cryptocurrency-ticker) for assembling the hardware.

### Requires:

- Adafruit 64x32 LED Matrix Panel
- Raspberry Pi

### Before installation
software needs to have access to LED Matrix hardware using root previledge to function properly. you can use `sudo` to run this script as well.
 - ssh to your pi
 - `su` to switch to root user

### Prerequisites
- `sudo apt-get update  && sudo apt-get install -y git python3-dev python3-pillow`
- `git clone https://github.com/hzeller/rpi-rgb-led-matrix.git`
- `cd rpi-rgb-led-matrix`

```
cd rpi-rgb-led-matrix
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
```

### Installation
- clone this repo
```
git clone https://github.com/hyp3rs0nik/binance-socket-led-matrix
cd binance-socket-led-matrix
```
- create a file called `.env` in the root folder (sample env file provided `env-sample`)
- install dependencies

```
pip install asyncio websockets
pip install -U python-dotenv
```
- we will use pm2 to manage this python script
```
wget -qO- https://getpm2.com/install.sh | bash
pm2 start socket-multiple.py --name cryptosocket --interpreter python3
```

more info about `pm2` here [pm2](https://www.npmjs.com/package/pm2)

### How it look like 

https://photos.app.goo.gl/KcyuNqKQi8aMfj1s8