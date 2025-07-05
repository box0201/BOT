import requests
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime
import nest_asyncio
nest_asyncio.apply()




def get_matches():
    base_url = 'https://www.soccerbet.rs/restapi/offer/sr/sport/B/mob'
    params = {
        'annex': 0,
        'desktopVersion': '2.34.3.22',
        'locale': 'sr'
    }
    headers = {
        'X-INSTANA-T': '6c5bb6a9ecb7d4a8',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'X-INSTANA-L': '1,correlationType=web;correlationId=6c5bb6a9ecb7d4a8',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.soccerbet.rs/sr/sportsko-kladjenje/fudbal/S',
        'X-INSTANA-S': '6c5bb6a9ecb7d4a8',
        'sec-ch-ua-platform': '"Linux"'
    }
    response = requests.get(base_url, headers=headers, params=params)
    lista = []
    if response.status_code == 200:
        data = response.json()  # Ako je odgovor u JSON formatu
        for i in data['esMatches']:
            lista.append(i['id'])
    else:
        print(f'Error: {response.status_code}')

    return lista

async def fetch_and_process(session, match_id, keys):
    url = f'https://www.soccerbet.rs/restapi/offer/sr/match/{match_id}'
    params = {
        'annex': 0,
        'desktopVersion': '2.34.3.22',
        'locale': 'sr'
    }
    headers = {
        'X-INSTANA-T': 'd268882d0407a85',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'X-INSTANA-L': '1,correlationType=web;correlationId=d268882d0407a85',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'X-INSTANA-S': 'd268882d0407a85',
        'sec-ch-ua-platform': '"Linux"'
    }
    timeout = aiohttp.ClientTimeout(total=20)

    try:
        async with session.get(url, headers=headers, params=params, timeout=timeout) as response:
            result = await response.json()

            if result:
                match_id = result.get('id')
                start_time = result.get('kickOffTime')
                start_time_seconds = start_time / 1000
                date_time = datetime.fromtimestamp(start_time_seconds)
                formatted_time = date_time.strftime('%Y-%m-%d %H:%M:%S')

                home = result.get('home')
                home = home.replace('FC', '').replace('SC', ' ')
                away = result.get('away')
                away = away.replace('FC', '').replace('SC', ' ')
                odds = result.get('betMap', {})
                kvote = {key: odds.get(key, {}).get('NULL', {}).get('ov', 1) for key in keys}
                match_info = {
                    'ID': match_id,
                    'vreme': formatted_time,
                    'domaci': home,
                    'gosti': away,
                }
                match_info.update(kvote)
                return match_info
    except asyncio.TimeoutError:
        print(f'Timeout error for match_id: {match_id}')
        return None
    except Exception as e:
        print(f'Error fetching match_id {match_id}: {e}')
        return None

async def soccer():
    async with aiohttp.ClientSession() as session:
        match_ids = get_matches()
        print("Soccer:", len(match_ids))
        from liste_k import keys, head
        tasks = [fetch_and_process(session, match_id, keys) for match_id in match_ids]
        results = await asyncio.gather(*tasks)
        results = [result for result in results if result is not None]
        if results:
            df = pd.DataFrame(results)
            df.columns = head
            df['ID'] = [f'Soccer{i}' for i in range(len(df))]
            df.to_csv('soccer.csv', index=False)


if __name__ == "__main__":
    asyncio.run(soccer())
