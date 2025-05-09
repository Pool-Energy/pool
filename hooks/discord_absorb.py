#!/usr/bin/env python3

import aiohttp
import asyncio
import json
import os
import sys
import yaml
import datetime
import logging

logger = logging.getLogger('hooks.discord_absorb')


def load_config():
    with open(os.environ['CONFIG_PATH'], 'r') as f:
        return yaml.safe_load(f)


async def main(absorbeb_coins):
    config = load_config()
    absorbeb_coins = json.loads(absorbeb_coins.strip())
    farmed_heights = []
    farmers = []

    for coin, farmer_record in absorbeb_coins:
        farmed_heights.append(
            str(int.from_bytes(bytes.fromhex(
                coin['coin']['parent_coin_info'][2:])[16:], 'big'
            ))
        )
        farmers.append(farmer_record)

    coins_blocks = ", ".join([f"[#{i}](https://xchscan.com/blocks/{i})" for i in farmed_heights])
    farmed_by = ", ".join([f"[{f['name'] or f['launcher_id']}](https://pool.energy/farmer/{f['launcher_id'].split('x')[1]})" for f in farmers])

    logger.info(f'New block(s) farmed! {coins_blocks}. Farmed by {farmed_by}.')

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
    asyncio.run(main(sys.argv[2]))
