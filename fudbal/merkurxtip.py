import aiohttp
import asyncio
import requests
import pandas as pd
from datetime import datetime
import time



def get_match_ids():
    url = 'https://www.merkurxtip.rs/restapi/offer/sr/sport/S/mob?annex=0&desktopVersion=1.34.2.6'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_gcl_au=1.1.1353040940.1722521383; _sp_srt_ses.b653=*; _gcl_aw=GCL.1722521385.EAIaIQobChMI8KaMlvzThwMVXJNoCR24VwBXEAAYAiAAEgIRJfD_BwE; _gid=GA1.2.67312855.1722521385; _gac_UA-186718919-2=1.1722521385.EAIaIQobChMI8KaMlvzThwMVXJNoCR24VwBXEAAYAiAAEgIRJfD_BwE; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=sr; _hjSessionUser_2552826=eyJpZCI6ImFhYmYxNmFmLTVlMTAtNTEzZS04Zjc1LTRkMzcyYjY0YTMyNiIsImNyZWF0ZWQiOjE3MjI1MjE0NDY0NTAsImV4aXN0aW5nIjpmYWxzZX0=; _hjSession_2552826=eyJpZCI6IjRhYTJiZGNkLTU3NjMtNDY4Yi1iMWI5LTg3MDAyN2Y0NWEyZCIsImMiOjE3MjI1MjE0NDY0NTIsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=; _hjHasCachedUserAttributes=true; _fbp=fb.1.1722521446905.606103513421401764; _gat_UA-186718919-2=1; _ga=GA1.1.1604690935.1722521385; _ga_HXB5PRRKV1=GS1.1.1722521385.1.1.1722522907.54.0.0; _sp_srt_id.b653=9789ac46-5624-41b4-99bc-bf92dda15c90.1722521384.1.1722522908..21144f6a-ec00-4001-9381-a6d2427f0793..dca77802-b777-448e-bedc-f84152c2ad56.1722521575411.2',
        'priority': 'u=1, i',
        'referer': 'https://www.merkurxtip.rs/desk/sr/sportsko-kladjenje/fudbal/S/bundesliga/2313709/special/mgladbach-v-leverkusen/128992811',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    match_ids = [match.get('id') for match in data.get('esMatches', [])]
    return match_ids

async def fetch_and_process(session, match_id, keys):
    url = f'https://www.merkurxtip.rs/restapi/offer/sr/match/{match_id}?annex=0&mobileVersion=2.32.2.10&locale=sr'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_gcl_au=1.1.1353040940.1722521383; _sp_srt_ses.b653=*; _gcl_aw=GCL.1722521385.EAIaIQobChMI8KaMlvzThwMVXJNoCR24VwBXEAAYAiAAEgIRJfD_BwE; _gid=GA1.2.67312855.1722521385; _gac_UA-186718919-2=1.1722521385.EAIaIQobChMI8KaMlvzThwMVXJNoCR24VwBXEAAYAiAAEgIRJfD_BwE; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=sr; _hjSessionUser_2552826=eyJpZCI6ImFhYmYxNmFmLTVlMTAtNTEzZS04Zjc1LTRkMzcyYjY0YTMyNiIsImNyZWF0ZWQiOjE3MjI1MjE0NDY0NTAsImV4aXN0aW5nIjpmYWxzZX0=; _hjSession_2552826=eyJpZCI6IjRhYTJiZGNkLTU3NjMtNDY4Yi1iMWI5LTg3MDAyN2Y0NWEyZCIsImMiOjE3MjI1MjE0NDY0NTIsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=; _hjHasCachedUserAttributes=true; _fbp=fb.1.1722521446905.606103513421401764; _gat_UA-186718919-2=1; _ga=GA1.1.1604690935.1722521385; _ga_HXB5PRRKV1=GS1.1.1722521385.1.1.1722522907.54.0.0; _sp_srt_id.b653=9789ac46-5624-41b4-99bc-bf92dda15c90.1722521384.1.1722522908..21144f6a-ec00-4001-9381-a6d2427f0793..dca77802-b777-448e-bedc-f84152c2ad56.1722521575411.2',
        'priority': 'u=1, i',
        'referer': 'https://www.merkurxtip.rs/desk/sr/sportsko-kladjenje/fudbal/S/bundesliga/2313709/special/mgladbach-v-leverkusen/128992811',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    timeout = aiohttp.ClientTimeout(total=20)
    for attempt in range(1):
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
                    #home = home.replace('FC', '').replace('SC', ' ')
                    away = result.get('away')
                    #away = away.replace('FC', '').replace('SC', ' ')
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
    return None

async def merkur():
    start_time = time.time()
    from liste import keys, head

    match_ids = get_match_ids()
    print("Merkur: ", len(match_ids))
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_and_process(session, match_id, keys) for match_id in match_ids]
        results = await asyncio.gather(*tasks)
        results = [res for res in results if res is not None]
        df = pd.DataFrame(results)
        df['vreme'] = pd.to_datetime(df['vreme'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
        df = df.sort_values(by='vreme')
        df = df.replace(0, 1.0)
        df.columns = head
        
        df['ID'] = [f'Merkur{i}' for i in range(len(df))]
        df.to_csv('/content/merkurxtip.csv', index=False, header=head)

    end_time = time.time()  # Započni merenje vremena
    duration = end_time - start_time
    #print(f'Program je trajao {duration:.2f} sekundi')
if __name__ == '__main__':
    asyncio.run(merkur())
