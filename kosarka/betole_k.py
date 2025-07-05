import aiohttp
import asyncio
import requests
import pandas as pd
import time
from datetime import timedelta
import nest_asyncio
nest_asyncio.apply()

def get_match_ids():
    url = 'https://www.betole.com/restapi/offer/sr/sport/B/mob?annex=0&desktopVersion=2.33.6.14&locale=sr'
    headers = {
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.betole.com/sport/S/calendar',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"',
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return [match.get('id') for match in data.get('esMatches', [])]

async def fetch_and_process(session, match_id, keys):
    url = f'https://www.betole.com/restapi/offer/sr/match/{match_id}?annex=0&desktopVersion=2.33.6.14&locale=sr'
    headers = {
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'Accept': 'application/json, text/plain, */*',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': '"Linux"',
    }
    timeout = aiohttp.ClientTimeout(total=20)
    try:
        async with session.get(url, headers=headers, timeout=timeout) as response:
            result = await response.json()
            match_info = {}
            if result:

                match_id = result.get('id')
                kick_off_time_ms = result.get('kickOffTime')
                formatted_time = pd.to_datetime(kick_off_time_ms, unit='ms')
                home = result.get('home')
                home = home.replace('FC', '').replace('SC', ' ')
                away = result.get('away')
                away = away.replace('FC', '').replace('SC', ' ')
                odds = result.get('odds', {})
                kvote = {key: odds.get(key, 1.0) for key in keys}
                match_info = {
                    'ID': match_id,
                    'vreme': formatted_time + timedelta(hours=2),
                    'domaci': home,
                    'gosti': away,
                }
                match_info.update(kvote)
            return match_info
    except asyncio.TimeoutError:
        print(f'Timeout Betole: {match_id}')

    except Exception as e:
        print(f'Error Betole: {e}')



async def betole():
    start_time = time.time()
    from liste_k import keys, head
    match_ids = get_match_ids()
    print("Betole: ", len(match_ids))
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_and_process(session, match_id, keys) for match_id in match_ids]
        results = await asyncio.gather(*tasks)
        results = [res for res in results if res is not None]
        if results:
            df = pd.DataFrame(results)
            df['vreme'] = pd.to_datetime(df['vreme'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
            df = df.sort_values(by='vreme')
            df['ID'] = [f'Betole{i}' for i in range(len(df))]
            df.to_csv('betole.csv', index=False, header=head)


        else:
            print("Nema validnih rezultata za kreiranje DataFrame-a.")

    end_time = time.time()  # Započni merenje vremena
    duration = end_time - start_time
    #print(f'Program je trajao {duration:.2f} sekundi')


if __name__ == '__main__':
    asyncio.run(betole())
