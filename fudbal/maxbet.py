import aiohttp
import asyncio
import pandas as pd
from datetime import datetime
from itertools import cycle
import nest_asyncio
nest_asyncio.apply()

async def fetch_json(session, url, headers, proxy_iter):
    proxy = next(proxy_iter)
    for i in range(1):
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                return await response.json()
        except asyncio.TimeoutError:
            print(f"Maxbet timeout: {url}")
            return {}
        except aiohttp.ClientError as e:
            async with session.get(url, proxy=proxy ,headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                return await response.json()
            print(f"Greška pri zahtevu: {e}")
            return {}

async def fetch_matches_for_lige_ids(lige_ids, keys, proxy_iter):
    base_url = 'https://www.maxbet.rs/restapi/offer/sr/sport/S/league/'
    base_url_1 = '/mob?annex=3&mobileVersion=1.0.1.25&locale=sr'
    headers = {
    "sec-ch-ua-platform": '"Linux"',
    "Referer": "https://www.maxbet.rs/sr/sportsko-kladjenje/fudbal/S",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0"
     }
    async with aiohttp.ClientSession() as session:
        tasks = []
        for liga in lige_ids:
            final_url = f'{base_url}{liga}{base_url_1}'
            tasks.append(fetch_json(session, final_url, headers, proxy_iter))
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
                    }
                    match_info.update(kvote)
                    matches_info.append(match_info)

        return matches_info


async def get_lige_ids(proxy_iter):
    proxy = next(proxy_iter)
    url = 'https://www.maxbet.rs/restapi/offer/sr/categories/sport/S/l?annex=3&mobileVersion=1.0.1.25&locale=sr'
    headers = {
    "sec-ch-ua-platform": '"Linux"',
    "Referer": "https://www.maxbet.rs/sr/sportsko-kladjenje/fudbal/S",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0"
     }
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
      async with session.get(url,proxy=proxy, headers=headers) as response:
        data = await response.json()
        if 'categories' in data:
            lige_ids = [category["id"] for category in data["categories"] if "id" in category]
            if '138547' in lige_ids:
                lige_ids.remove('138547')
            return lige_ids
        return []


async def maxbet():
    print("Maxbet")
    from liste import keys, head, ucitaj_proksi
    proksi = ucitaj_proksi()
    proxy_iter = cycle(proksi)

    lige_ids = await get_lige_ids(proxy_iter)
    if lige_ids:
        matches_info = await fetch_matches_for_lige_ids(lige_ids, keys, proxy_iter)
        df = pd.DataFrame(matches_info)
        df['vreme'] = pd.to_datetime(df['vreme'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
        df = df.sort_values(by='vreme')
        df = df.replace(0, 1.0)
        df['ID'] = [f'Maxbet{i}' for i in range(len(df))]
        df.to_csv('/content/maxbet.csv', index=False, header=head)


# Pokreni asinhroni kod
if __name__ == "__main__":
    asyncio.run(maxbet())
