import asyncio
import aiohttp
import itertools
import pandas as pd
from datetime import datetime, timedelta
import requests
import nest_asyncio
nest_asyncio.apply()

razlika = ['ID', 'vreme', 'domaci', 'gosti', '1', 'X', '2', 'GG', 'NG', 'GG3+', 'ne GG3+',
        'ug 0-1', 'ug 2+', 'ug 0-2', 'ug 3+', 'ug 0-3', 'ug 4+', 'ug 0-4', 'ug 5+', '1&3+', 'ne1&3+',
        '1-1', 'ne 1-1', 'W1', 'W2',
        'D I 0-1', 'D I 2+', 'G I 0-1', 'G I 2+', 'D II 0-1', 'D II 2+', 'G II 0-1', 'G II 2+',
        'I GG', 'I NG', 'II GG', 'II NG',
        '1X', '12', 'X2',
        'I 1', 'I X', 'I 2', 'I 1X', 'I 12', 'I X2', 'II 1', 'II X', 'II 2', 'II 1X', 'II 12', 'II X2',
        'I 0', 'I 0-1', 'I 0-2', 'I 1+', 'I 2+', 'I 3+', 'II 0', 'II 0-1', 'II 0-2', 'II 1+', 'II 2+', 'II 3+',
        '1X-1X', '1X-12', '1X-X2', '12-1X', '12-12', '12-X2', 'X2-1X', 'X2-12', 'X2-X2',
        '1-1X', '1-12', '1-X2', 'X-1X', 'X-12', 'X-X2', '2-1X', '2-12',
        '2-X2', '1X-1', '1X-X', '1X-2', '12-1', '12-X', '12-2', 'X2-1', 'X2-X', 'X2-2',
        ]

async def get_matches():
    url = "https://sportdataproviderv3-volcanors.xtreme.bet/api/public/offer/GetFixtures"
    params = {
        'lang': 'en',
        'dp': '2ce6ccb8-29af-4535-82b3-8e21685e04d5-V3',
        'clientType': 'WebConsumer',
        't': 'c3edd3df-2450-4dd7-a200-6f78b897fb0b',
        'v': '1.1.2764'
    }
    headers = {
        'Referer': 'https://www.volcanobet.rs/',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0'
    }
    async with aiohttp.ClientSession() as session:
      async with session.get(url, proxy=None, headers=headers, params=params) as response:
        data = await response.json()
        ids = []
        matches_info = []
        for item in data["f"]:
          if item["si"] == "1":
              if item['s'] == "NSY":
                  id = item['ai']
                  ids.append(id)
              else:
                  continue
          else:
              continue
          ai = item.get("ai")
          sd = item.get("sd")
          sd = datetime.strptime(sd, "%Y-%m-%dT%H:%M:%SZ")
          teams = [team.get("n") for team in item.get("p", [])]
          domaci = teams[0]
          gosti = teams[1]
          matches_info.append({
              "ID": ai,
              "vreme": sd,
              'domaci': domaci,
              'gosti': gosti
          })
      return ids, matches_info

async def fetch_and_process(session, match_id):
    url = "https://sportdataproviderv3-volcanors.xtreme.bet/api/public/Offer/GetEventMarkets"
    params = {
        "eventIds": match_id,
        "clientType": "WebConsumer",
        "dpId": "2ce6ccb8-29af-4535-82b3-8e21685e04d5-V3",
        "lang": "en",
        "t": "c3edd3df-2450-4dd7-a200-6f78b897fb0b",
        "v": "1.1.2764"
    }
    headers = {
        "sec-ch-ua-platform": '"Linux"',
        "Referer": "https://www.volcanobet.rs/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0"
    }
    timeout = aiohttp.ClientTimeout(total=20)
    try:
        async with session.get(url, headers=headers, params=params, timeout=timeout) as response:
            data = await response.json()
            keys = ['1', '10', '11', 'M1']
            lista = ['1/1', '1/x', '1/2', '10/1x', '10/x2', '10/12', '11/1', '11/2', 'M1/GG', 'M1/NG', 'M1/GG3+']
            a = ['1', 'X', '2', '1X', 'X2', '12', 'W1', 'W2', 'GG', 'NG', 'GG3+']
            match_info = dict.fromkeys(lista, 1.0)
            if data:
                e_value = data[0]["e"]
                match_info = {'ID': e_value}
                for item in data[0]['m']:
                    sp = item['id']
                    for j in item.get('b', []):
                        un = j['id']
                        key = f'{sp}/{un}'
                        if key in lista:
                            match_info.update({key: j['od']})

            mapa = dict(zip(lista, a))
            match_info_1 = {mapa.get(k, k): v for k, v in match_info.items()}
            return match_info_1
    except asyncio.TimeoutError:
        print(f'Timeout error for match_id: {match_id}')
        return None
    except Exception as e:
        print(f'Error fetching match_id {match_id}: {e}')
        return None

async def volcano():
    async with aiohttp.ClientSession() as session:
        match_ids, df_info = await get_matches()
        print("Volcano:", len(match_ids))
        tasks = [fetch_and_process(session, match_id) for match_id in match_ids]
        results = await asyncio.gather(*tasks)
        results = [result for result in results if result is not None]
        df_1 = pd.DataFrame(df_info)
        head = ['ID', 'vreme', 'domaci', 'gosti', '1', 'X', '2', '1X', 'X2', '12', 'W1', 'W2', 'GG', 'NG', 'GG3+']
        rezultat = [x for x in razlika if x not in head]

        if results:
            df_2 = pd.DataFrame(results)
            df = pd.merge(df_1, df_2, on='ID')
            df['ID'] = [f'Volcano{i}' for i in range(len(df))]
            for header in rezultat:
                df[header] = 1.0
            df.fillna(1, inplace=True)
            df = df.replace(0, 1.0)
            df = df.sort_values(by='vreme')
            df.to_csv('/content/volcano.csv', index=False)

if __name__ == "__main__":
    asyncio.run(volcano())
