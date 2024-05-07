#!/usr/bin/env python3
import aiohttp
import asyncio
import json
import os
import sys
import yaml
import datetime


def load_config():
    with open(os.environ['CONFIG_PATH'], 'r') as f:
        return yaml.safe_load(f)


async def discord_blocks_farmed(absorbeb_coins):
    config = load_config()
    absorbeb_coins = json.loads(absorbeb_coins.strip())
    farmed_heights = []
    farmer = {}
    farmers = []

    for coin, farmer_record in absorbeb_coins:
        farmed_heights.append(
            str(int.from_bytes(bytes.fromhex(
                coin['coin']['parent_coin_info'][2:])[16:], 'big'
            ))
        )
        farmer['name'] = farmer_record['name'] or farmer_record['launcher_id']
        farmer['link'] = farmer_record['launcher_id']
        farmers.append(farmer)
        farmer.clear()

    coins_blocks = ', '.join([f'[#{i}](https://xchscan.com/blocks/{i})' for i in farmed_heights])
    farmed_by = ', '.join([f'[{f["name"]}](https://pool.energy/farmer/{f["link"]})' for f in farmers])

    async with aiohttp.request('POST', config['hook_discord_absorb']['url'], json={
        'username': config['hook_discord_absorb']['username'],
        'embeds': [{
            'title': '🏆 New block(s) farmed!',
            'description': f'New block(s) farmed! {coins_blocks}. Farmed by {farmed_by}.',
            'color': 2522040,
            'footer': {
                'text': 'Powered by pool.energy'
            },
            'timestamp': str(datetime.datetime.now(datetime.UTC))
        }]
    }) as r:
        pass


if __name__ == '__main__':
    if sys.argv[1] != 'ABSORB':
        print('Not an ABSORB hook')
        sys.exit(1)
    asyncio.run(discord_blocks_farmed(
        sys.argv[2],
    ))
