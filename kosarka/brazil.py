import aiohttp
import asyncio
import requests
import pandas as pd
from datetime import datetime
import time



def get_match_ids():
    url = 'https://www.brazilbet.rs/restapi/offer/sr/sport/B/mob?annex=0&desktopVersion=1.34.2.6'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "sr-RS,sr;q=0.9,en-US;q=0.8,en;q=0.7,bs;q=0.6,hr;q=0.5,ru;q=0.4,zh-CN;q=0.3,zh;q=0.2",
        "Connection": "keep-alive",
        "Cookie": "org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=sr; _ht_v=1733848336.2956903002; _ga=GA1.1.1769241303.1733848337; _fbp=fb.1.1733848336722.591661330322093736; _ht_s=1733857894.18; _ga_CM7DNEP28V=GS1.1.1733857894.2.1.1733859151.0.0.0",
        "Host": "www.brazilbet.rs",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    match_ids = [match.get('id') for match in data.get('esMatches', [])]
    return match_ids

async def fetch_and_process(session, match_id, keys):
    url = f'https://www.brazilbet.rs/restapi/offer/sr/match/{match_id}?annex=0&mobileVersion=2.32.2.10&locale=sr'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "sr-RS,sr;q=0.9,en-US;q=0.8,en;q=0.7,bs;q=0.6,hr;q=0.5,ru;q=0.4,zh-CN;q=0.3,zh;q=0.2",
        "Connection": "keep-alive",
        "Cookie": "org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=sr; _ht_v=1733848336.2956903002; _ga=GA1.1.1769241303.1733848337; _fbp=fb.1.1733848336722.591661330322093736; _ht_s=1733857894.18; _ga_CM7DNEP28V=GS1.1.1733857894.2.1.1733859151.0.0.0",
        "Host": "www.brazilbet.rs",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
    }
    timeout = aiohttp.ClientTimeout(total=20)
    retries = 1
    for attempt in range(retries):
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
                    away = result.get('away')
                    odds = result.get('odds', {})
                    kvote = {key: odds.get(key, 1.0) for key in keys}
                    match_info = {
                        'ID': match_id,
                        'vreme': formatted_time,
                        'domaci': home,
                        'gosti': away,
                    }
                    match_info.update(kvote)
                return match_info
        except asyncio.TimeoutError:
            #print(f'Timeout Merkur: {match_id}. Pokušavam ponovo... (pokušaj {attempt + 1}/{retries})')
            pass
        except Exception as e:
            #print(f'Error Merkur {match_id}: {e}')
            return None
    print(f'Svi pokušaji za {match_id} su istekli.')
    return None

async def brazil():
    start_time = time.time()
    from liste import keys, head

    match_ids = get_match_ids()
    print("Brazil bet: ", len(match_ids))
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_and_process(session, match_id, keys) for match_id in match_ids]
        results = await asyncio.gather(*tasks)
        results = [res for res in results if res is not None]
        df = pd.DataFrame(results)
        df['vreme'] = pd.to_datetime(df['vreme'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
        df = df.sort_values(by='vreme')
        df.columns = head
        df['ID'] = [f'Brazil{i}' for i in range(len(df))]
        df.to_csv('brazil.csv', index=False, header=head)

    end_time = time.time()  # Započni merenje vremena
    duration = end_time - start_time
    #print(f'Program je trajao {duration:.2f} sekundi')
if __name__ == '__main__':
    asyncio.run(brazil())



