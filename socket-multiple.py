#!/usr/bin/env python3

import asyncio
import websockets
import json
import sys
import os
from decimal import Decimal
from dotenv import load_dotenv
from itertools import cycle
from frame import Frame
from setinterval import SetInterval
from rgbmatrix import graphics
from millify import millify

class BinanceSocket(Frame):

    def __init__(self, *args, **kwargs):
        load_dotenv()

        self.symbols = os.getenv('SYMBOLS').split(',')
        self.refresh = int(os.getenv('TOGGLE_RATE', 3))
        self.data = {}
        self.ctr = 0
        self.idx = 0
        self.wssurl =  "wss://stream.binance.com:9443/ws/" + self.symbols[0].replace('-', '') + "@ticker"
        self.meta = {}
        self.cycle_symbols = cycle(self.symbols)
        self.current_symbol = self.symbols[0]

        font_symbol = graphics.Font()
        font_symbol.LoadFont('fonts/7x14B.bdf')

        font_price = graphics.Font()
        font_price.LoadFont('fonts/6x12.bdf')

        font_change = graphics.Font()
        font_change.LoadFont('fonts/6x10.bdf')

        font_vol = graphics.Font()
        font_vol.LoadFont('fonts/5x7.bdf')


        self.fonts = {
            'symbol': font_symbol,
            'price': font_price,
            'change': font_change,
            'vol': font_vol
        }

        self.canvas = None

        super().__init__(*args, **kwargs)
    
    def get_pairs_payload(self):
        count = len(self.symbols[1:])
        if count == 0:
            return '{"method": "SUBSCRIBE", "params": ["'+ self.symbols[0].replace('-', '') + '@ticker"], "id": 1}'
        
        symbols = self.symbols[1:]
        str_symbol = ''
        for symbol in symbols:
            str_symbol = str_symbol + '"' + symbol.replace('-', '') + '@ticker",'
        
        str_symbol = str_symbol[:-1]
        return '{"method": "SUBSCRIBE", "params": ['+ str_symbol + '], "id": 1}'        

    async def fetchTickerData(self):
        async with websockets.connect(self.wssurl) as sock:
            pairs = self.get_pairs_payload()
            print(pairs)
            await sock.send(pairs)
        
            while True:
                k = json.loads(await sock.recv())
                if not 'id' in k:
                    self.data[k['s']] = {
                        'change': '{0:.4f}'.format(Decimal(k['P'])),
                        'price': k['c'],
                        'vol': k['v'],
                        's': k['s'],
                        'qoute': k['q']
                    }
    

    def insertBefore(self, s, ss, ns):
        idx = s.index(ss)
        return s[:idx] + ns + s[idx:]
    
    def render_ticker_canvas(self, symbol):
        key = symbol.replace('-','').upper()
        if not key in self.data:
            return
        data = self.data[key]

        if not self.canvas:
            self.canvas = self.matrix.CreateFrameCanvas()

        self.canvas.Clear()

        priceChangePercent = float(data["change"])
        price = float(data["price"])

        prefix = '' if data['change'].startswith('-') else '+'

        change_width = sum(
            [self.fonts['change'].CharacterWidth(ord(c))
             for c in f'{prefix}{priceChangePercent:.2f}']
        )

        change_x = 64 - change_width

        change_color = (
            graphics.Color(220, 47, 2)
            if data['change'].startswith('-')
            else graphics.Color(0, 255, 0)
        )

        prefixes = ['K', 'M', 'B']
        
        self.ctr += 1

        n = self.refresh / 2

        if self.ctr >= n:
            vol_txt = 'B:' + millify(data['vol'], precision=3, prefixes=prefixes)
        if self.ctr < n:
            vol_txt = 'Q:' + millify(data['qoute'], precision=3, prefixes=prefixes)

        if self.ctr == self.refresh:
            self.ctr = 0

        graphics.DrawText(
            self.canvas, self.fonts['change'], change_x, 9, change_color, f'{prefix}{priceChangePercent:.2f}'
        )
        graphics.DrawText(self.canvas, self.fonts['price'], 3, 20, graphics.Color(203, 243, 240), vol_txt)

        graphics.DrawText(self.canvas, self.fonts['symbol'], 3, 11, graphics.Color(255, 209, 102), symbol[0:3].upper())

        graphics.DrawText(self.canvas, self.fonts['price'], 3, 30, change_color, f'{price:,.5f}')

        self.matrix.SwapOnVSync(self.canvas)

    def toggle_idx(self):
        self.current_symbol = next(self.cycle_symbols)
        self.ctr = 0

    def run_ticker(self):
        self.render_ticker_canvas(self.current_symbol)
        
    def run(self):
        SetInterval(self.refresh, self.toggle_idx)
        SetInterval(1, self.run_ticker)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.fetchTickerData())


if __name__ == '__main__':
    BinanceSocket().initMatrix()
    BinanceSocket().run()
