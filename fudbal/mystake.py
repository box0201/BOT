import requests
import pandas as pd
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta



def matches():
    url = 'https://analytics-sp.googleserv.tech/api/sport/getheader/en'
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,sr;q=0.8',
        'origin': 'https://mystake.com',
        'priority': 'u=1, i',
        'referer': 'https://mystake.com/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    data = json.loads(data)
    games_list = []
    ids = []
    sports = data['EN']['Sports']
    for sport_id, sport_data in sports.items():
        regions = sport_data.get('Regions', {})
        for region_id, region_data in regions.items():
            champs = region_data.get('Champs', {})
            for champ_id, champ_data in champs.items():
                games = champ_data.get('GameSmallItems', {})
                for game_id, game in games.items():
                    game_info = {
                        'SportID': sport_id,
                        'SportName': sport_data['Name'],
                        'RegionID': region_id,
                        'RegionName': region_data['Name'],
                        'ChampID': champ_id,
                        'ChampName': champ_data['Name'],
                        'GameID': game['ID'],
                        'Team1': game.get('t1'),
                        'Team2': game.get('t2'),
                        'StartTime': game.get('StartTime'),
                        'IsTop': champ_data.get('IsTop', False),
                        'Neutral': game.get('neut'),
                        'Plng': game.get('plng'),
                    }
                    if game_info['SportID'] == '1':
                        games_list.append(game_info)
                        ids.append(game_info['GameID'])
    all_ids = []
    for i in ids:
        if i > 0:
            all_ids.append(i)
    return all_ids
async def kvote(session, id, headers, timeout):
    url = f'https://analytics-sp.googleserv.tech/api/prematch/getprematchgamefull/28/{id}'
    market_ids = ['448', '476', '463', '481']  # redosled po kome želiš da ideš
    head = ['1', 'X', '2', '1X', '12', 'X2', 'GG', 'NG', 'W1', 'W2', 'GG3+',
            'ne GG3+',
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
    kvote = ['448/1', '448/2', '448/3', '476/57', '476/58', '476/59', '463/44', '463/45', '481/60', '481/61']
    try:
        async with session.get(url, headers=headers, timeout=timeout) as response:
            if response.status == 200:
                data = await response.json()
                game_str = data.get("game")
                game = json.loads(game_str)
                vreme = datetime.fromisoformat(game['st']) + timedelta(hours=0)
                for market_id in market_ids:
                    odds_dict = game["ev"].get(market_id)
                    if odds_dict is None:
                        continue
                    for odd_id, odd_info in odds_dict.items():
                        pos = odd_info.get("pos")
                        coef = odd_info.get("coef")
                        if isinstance(coef, (int, float)):
                            pass
                        else:
                            coef = 1.0
                        index = kvote.index(f"{market_id}/{pos}")
                        kvote[index] = coef
                for i in range(len(head)-len(kvote)):
                    kvote.append(1)
                odds = dict(zip(head, kvote))
                for key in odds:
                    if isinstance(odds[key], str):
                        odds[key] = 1
                return odds, vreme
            else:
                print(response.status)
                return None
    except Exception as e:
        print(f'GREŠKA U kvote(): {e}')
        return None

async def fetch_and_process(session, match_id):
    url = f'https://analytics-sp.googleserv.tech/api/prematch/getprematchgameall/en/28/?games=,{match_id}'
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,sr;q=0.8',
        'origin': 'https://mystake.com',
        'priority': 'u=1, i',
        'referer': 'https://mystake.com/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    }
    timeout = aiohttp.ClientTimeout(total=20)
    try:
        async with session.get(url, headers=headers, timeout=timeout) as response:
            if response.status == 200:
                data = await response.json()
                data = json.loads(data)
                teams = data.get('teams')
                teams = json.loads(teams)
                team_names = [team['Name'] for team in teams]
                odds, vreme = await kvote(session, match_id, headers, timeout)
                match_info = {
                    'ID': match_id,
                    'vreme': vreme,
                    'domaci': team_names[0].replace('FC', '').replace('SC', ' '),
                    'gosti': team_names[1].replace('FC', '').replace('SC', ' '),
                }
                match_info.update(odds)
                return match_info

            else:
                print(response.status)
                return None
    except Exception as e:
        print('GREŠKA FETCH', e)
        return None

async def mystake():
    async with aiohttp.ClientSession() as session:
        match_ids = matches()
        #match_ids = match_ids[:10]
        print("Mystake:", len(match_ids))
        tasks = [fetch_and_process(session, match_id) for match_id in match_ids]
        results = await asyncio.gather(*tasks)
        results = [result for result in results if result is not None]
        if results:
            df = pd.DataFrame(results)
            df['ID'] = [f'Mystake{i}' for i in range(len(df))]
            df = df.sort_values(by='vreme')
            df = df.replace(0, 1.0)
            df.to_csv('/content/mystake.csv', index=False)

if __name__ == "__main__":
    asyncio.run(mystake())
