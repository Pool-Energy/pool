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


async def discord_payment(payments):
    config = load_config()
    payments = json.loads(payments.strip())
    launcher_ids = list(payments.keys())
    amount = 0

    for launcher_id in launcher_ids:
        amount += payments[launcher_id]

    async with aiohttp.request('POST', config['hook_discord_payment']['url'], json={
        'username': config['hook_discord_payment']['username'],
        'embeds': [{
            'title': '💵 Payments sent!',
            'description': f'Total amount: {amount / 10 ** 12} XCH.',
            'color': 3319634,
            'footer': {
                'text': 'Powered by pool.energy'
            },
            'timestamp': str(datetime.datetime.now(datetime.UTC))
        }]
    }) as r:
        pass


if __name__ == '__main__':
    if sys.argv[1] != 'PAYMENT':
        print('Not an PAYMENT hook')
        sys.exit(1)
    asyncio.run(discord_payment(
        *sys.argv[2:],
    ))
