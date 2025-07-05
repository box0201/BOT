import requests
from datetime import datetime, timedelta
import asyncio
import aiohttp
import pandas as pd
import nest_asyncio
nest_asyncio.apply()

async def get_matches():
    vreme = datetime.now() - timedelta(hours=2)
    url = 'https://production-superbet-offer-rs.freetls.fastly.net/sb-rs/api/v2/sr-Latn-RS/events/by-date'
    params = {
        'offerState': 'prematch',
        'startDate': vreme,
        'endDate': '2026-06-08 08:00:00',
        'sportId': '5'
    }
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'sr-RS,sr;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://superbet.rs',
        'priority': 'u=1, i',
        'referer': 'https://superbet.rs/',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print('Superbet greška get_matches()')
    response = response.json()
    event_ids = [item['eventId'] for item in response['data']]
    return event_ids

async def fetch_and_process(session, match_id, keys, head):
    url = f'https://production-superbet-offer-rs.freetls.fastly.net/sb-rs/api/v2/sr-Latn-RS/events/{match_id}'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'sr-RS,sr;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://superbet.rs',
        'priority': 'u=1, i',
        'referer': 'https://superbet.rs/',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }
    timeout = aiohttp.ClientTimeout(total=20)
    try:
        async with session.get(url, headers=headers, timeout=timeout) as response:
            match = await response.json()
            odds = {kljuc: 1 for kljuc in keys}
            if match:
                for item in match['data']:
                    timovi = item['matchName'].split('·')
                    vreme = item['matchDate']
                    domaci = timovi[0].replace('(Ž)', '(W)')
                    gosti = timovi[1].replace('(Ž)', '(W)')

                    for odd in item['odds']:
                        a = odd['marketId']
                        b = odd['outcomeId']
                        name = odd['name']
                        key = f'{a}/{b}'
                        if key in keys:
                            odds[key] = odd['price']
                    match_info = {
                        'ID': match_id,
                        'vreme': vreme,
                        'domaci': domaci,
                        'gosti': gosti,
                        **odds
                    }
                    return match_info
        return {}
    except asyncio.TimeoutError:
        print(f'Superbet timeout: {match_id}')

    except Exception as e:
        pass


async def superbet():
    match_ids = await get_matches()
    head = ['ID', 'vreme', 'domaci', 'gosti', '1', 'X', '2', '1X', '12', 'X2', 'W1', 'W2', 'GG', 'NG', 'GG3+', 'ne GG3+',
               'ug 0-1', 'ug 2+', 'ug 0-2', 'ug 3+', 'ug 0-3', 'ug 4+', 'ug 0-4', 'ug 5+', '1&3+', 'ne1&3+',
               '1-1', 'ne 1-1',
               'D I 0-1', 'D I 2+', 'G I 0-1', 'G I 2+', 'D II 0-1', 'D II 2+', 'G II 0-1', 'G II 2+',
               'I GG', 'I NG', 'II GG', 'II NG',
               'I 1', 'I X', 'I 2', 'I 1X', 'I 12', 'I X2', 'II 1', 'II X', 'II 2', 'II 1X', 'II 12', 'II X2',
               'I 0', 'I 0-1', 'I 0-2', 'I 1+', 'I 2+', 'I 3+', 'II 0', 'II 0-1', 'II 0-2', 'II 1+', 'II 2+', 'II 3+',
               '1X-1X', '1X-12', '1X-X2', '12-1X', '12-12', '12-X2', 'X2-1X', 'X2-12', 'X2-X2',
               '1-1X', '1-12', '1-X2', 'X-1X', 'X-12', 'X-X2', '2-1X', '2-12',
               '2-X2', '1X-1', '1X-X', '1X-2', '12-1', '12-X', '12-2', 'X2-1', 'X2-X', 'X2-2',
               ]
    keys = ['547/1470', '547/1471', '547/1472', '531/1363', '531/1364', '531/1365', '555/1494', '555/1495',
            '539/1440', '539/1441', '201503/153194', '201503/153195'
            ]
    #head = ['ID', 'vreme', 'domaci', 'gosti', '1', 'X', '2', '1X', '12', 'X2', 'W1', 'W2', 'GG', 'NG', 'GG3+', 'ne GG3+']
    print("Superbet: ", len(match_ids))
    for i in range(75):
        keys.append(f'{-i}')
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_and_process(session, match_id, keys, head) for match_id in match_ids]
        results = await asyncio.gather(*tasks)
        results = [res for res in results if res is not None]

        if results:
            df = pd.DataFrame(results)
            df = df.sort_values(by='vreme')
            df['ID'] = [f'Superbet{i}' for i in range(len(df))]
            df.to_csv('/content/superbet.csv', index=False, header=head)
        else:
            print("Nema validnih rezultata za kreiranje DataFrame-a.")

if __name__ == '__main__':
    asyncio.run(superbet())

