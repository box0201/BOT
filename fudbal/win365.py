import aiohttp
import asyncio
import pandas as pd
from datetime import datetime
from liste import keys, head, lige_ids
import nest_asyncio
nest_asyncio.apply()

async def fetch_json(session, url, headers,):
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
            return await response.json()
    except asyncio.TimeoutError:
        print(f"Maxbet timeout: {url}")
        return {}
    except aiohttp.ClientError as e:
        print(f"Greška pri zahtevu: {e}")
        return {}

async def fetch(lige_ids, keys):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,sr;q=0.8',
        'origin': 'https://www.365.rs',
        'referer': 'https://www.365.rs/',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    }
    async with aiohttp.ClientSession() as session:
        tasks = []
        for liga in lige_ids:
            url = f'https://ibet2.365.rs/restapi/offer/sr/sport/S/league/{liga}/mob?annex=0&null&mobileVersion=2.32.10.5&locale=sr'
            tasks.append(fetch_json(session, url, headers))
        responses = await asyncio.gather(*tasks)
        matches_info = []
        for data in responses:
            if 'esMatches' in data:
                for match in data['esMatches']:
                    match_id = match.get('id')
                    home_team = match.get('home')
                    away_team = match.get('away')
                    kick_off_time_ms = match.get('kickOffTime')
                    kick_off_time_s = kick_off_time_ms / 1000
                    kick_off_datetime = datetime.fromtimestamp(kick_off_time_s)
                    vreme = kick_off_datetime.strftime('%d-%m-%Y %H:%M:%S')
                    odds = match.get('odds', {})
                    kvote = {key: odds.get(key, 1) for key in keys}
                    match_info = {
                        'ID': match_id,
                        'vreme': vreme,
                        'domaci': home_team,
                        'gosti': away_team,
                        **kvote
                    }
                    matches_info.append(match_info)
        return matches_info


async def win365():
    print('365.rs')
    matches_info = await fetch(lige_ids, keys)
    df = pd.DataFrame(matches_info)
    df['vreme'] = pd.to_datetime(df['vreme'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
    df = df.sort_values(by='vreme')
    df['ID'] = [f'Planetwin{i}' for i in range(len(df))]
    df.to_csv('/content/365.rs.csv', index=False, header=head)

if __name__ == '__main__':
    asyncio.run(win365())
