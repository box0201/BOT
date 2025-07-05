import aiohttp
import asyncio
import requests
import pandas as pd
from datetime import datetime
import itertools
import nest_asyncio
nest_asyncio.apply()


url = 'https://www.oktagonbet.com/restapi/offer/sr/sport/B/mob'
headerss = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,bs;q=0.8',
    'cookie': 'org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=sr',
    'priority': 'u=1, i',
    'referer': 'https://www.oktagonbet.com/mob/sr/sportsko-kladjenje/fudbal/S',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}
params = {
    'annex': '1',
    'hours': '72',
    'mobileVersion': '2.33',
    'locale': 'sr'
}

def fetch_match_ids():
    response = requests.get(url, headers=headerss)
    data = response.json()
    return [match.get('id') for match in data.get('esMatches', [])]

async def fetch_and_process(session, match_id, keys):
    url = f'https://www.oktagonbet.com/restapi/offer/sr/match/{match_id}?annex=1&mobileVersion=2.33.5.4&locale=sr'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,bs;q=0.8,sr;q=0.7',
        'cookie': 'org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=sr',
        'priority': 'u=1, i',
        'referer': 'https://www.oktagonbet.com/mob/sr/sportsko-kladjenje/fudbal/S/argentina-1/2239121/special/godoy-cruz-v-sarmiento/39310367',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    timeout = aiohttp.ClientTimeout(total=20)

    try:
        async with session.get(url, headers=headers, timeout=timeout) as response:
            result = await response.json()
            match_info = {}
            if result:
                match_id = result.get('id')
                kick_off_time_ms = result.get('kickOffTime')
                kick_off_time_s = kick_off_time_ms / 1000
                kick_off_datetime = datetime.fromtimestamp(kick_off_time_s)
                formatted_time = kick_off_datetime.strftime('%d-%m-%Y %H:%M:%S')
                home = result.get('home')
                home = home.replace('FC', '').replace('SC', ' ')
                away = result.get('away')
                away = away.replace('FC', '').replace('SC', ' ')
                odds = result.get('odds', {})
                kvote = {key: odds.get(key, 1) for key in keys}
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
        return None  # Vraća prazan rečnik u slučaju timeout-a
    except Exception as e:
        print(f'Error fetching match_id {match_id}: {e}')
        return None# Vraća prazan rečnik u slučaju bilo koje druge greške

async def oktagon():
    async with aiohttp.ClientSession() as session:
        from liste_k import keys, head

        match_ids = fetch_match_ids()
        print("Oktagon:", len(match_ids))
        tasks = [fetch_and_process(session, match_id, keys) for match_id in match_ids]
        results = await asyncio.gather(*tasks)
        results = [result for result in results if result is not None]
        df = pd.DataFrame(results)  # results je lista rečnika
        # Ako vam je potrebna neka obrada, možete je dodati ovde
        df['vreme'] = pd.to_datetime(df['vreme'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
        df = df.sort_values(by='vreme')
        df.columns = head
        df['ID'] = [f'Oktagon{i}' for i in range(len(df))]
        df.to_csv('oktagon.csv', index=False, header=head)

if __name__ == "__main__":
    asyncio.run(oktagon())
