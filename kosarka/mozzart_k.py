import httpx
import aiohttp
import asyncio
import pandas as pd
from datetime import datetime
import nest_asyncio
nest_asyncio.apply()


async def get_matches(client, page):
    data = {
        "date": "all_days",
        "sort": "bytime",
        "currentPage": page,
        "pageSize": 15,
        "sportId": 2,
        "search": "",
        "matchTypeId": 0
    }
    url = 'https://www.mozzartbet.com/betting/matches'
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "sr-RS,sr;q=0.9,en-US;q=0.8,en;q=0.7,bs;q=0.6,hr;q=0.5,ru;q=0.4,zh-CN;q=0.3,zh;q=0.2",
        "content-type": "application/json",
        "cookie": "i18next=sr; _gcl_au=1.1.1500435550.1735174651; _ga=GA1.1.32261541.1735174651; _fbp=fb.1.1735174650791.572211526929542818; __ssid=5235e65f47d7af1191f517e4e94aef3; _clck=131wg59%7C2%7Cfsa%7C0%7C1821; a_b_sft=s%3AfGinFWrJWEkkknnu846E4y.wGhjKKiXsfWlveqYoMAYViwZ4cK0Ib668gQfs9%2BB6s8; SERVERID=RHN2; _sp_srt_ses.af69=*; __cf_bm=axnV_HIhUFtu9u56lrEPpvyY3A6zVJwcwOAbV3DGKQY-1735999936-1.0.1.1-zp1h4OigCpePPKxNvtrGj1uQv.xbcREIo8oRtVgY9tfOpNpiPDGT9USIH.WG3JhqfuPFQ_G0VSjHToavwxjJeQ; _clsk=1g0gzp7%7C1735999937406%7C4%7C0%7Ct.clarity.ms%2Fcollect; _sp_srt_id.af69=a782c6bb-6979-46e9-bbc7-38e09ddee794.1735174651.6.1735999948.1735985738.b0e36fe7-a409-4129-a505-60478d390f0d.5af4acc2-9023-417b-9540-6b529bc5e251...0; cf_clearance=4wEFlPb4bcrJx1eG.Qh8UGCf6RFIVF6zbs6QKfX2Fqo-1735999947-1.2.1.1-YGEpGzSZshFRLvmrBoIbvmbHDnAJ5K9yvUXRlffCYgqaihgiv7u52Qadwz_RRuy5vR8eD9aKAfz8hv_oF7CVLbaXM9aW9sn.s42lBEL63mR3kyNs0.BlemJIs5Ewb4yhAusm35cn1ZxaN7UKUd4Hj6PMyi9biD3rlsGxbndrnQvnV28MbukXf9yWv1IveupFxd2V8ZmMD5T8DV3LbFxQwKsaAhLc1TfUAM7x9MVpetog2HdowZn._wPq0zRbZX.yIrwADktDnN0x1M2jPYR10H4TPeH7LCtyDAlDAtphUHrt8vN4FDsSOjPPPwO6HDBqwSvidE5v4HdkncsId2xZj59c46F7BzJUNQb1xZImtVSJqmKnOMEqwYCGoL.gz.ai; _ga_PHMZPND8CR=GS1.1.1735998284.4.1.1735999948.48.0.0",
        "medium": "WEB",
        "origin": "https://www.mozzartbet.com",
        "priority": "u=1, i",
        "referer": "https://www.mozzartbet.com/sr/kladjenje/sport/2?date=all_days",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    try:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        results = response.json()
        return [item['id'] for item in results['items']]
    except:
        return []
async def main():
    async with httpx.AsyncClient() as client:
        tasks = [get_matches(client, page) for page in range(0, 30)]
        results = await asyncio.gather(*tasks)
    ids = set()
    for result in results:
        ids.update(result)
    return ids

##############################################################################################
async def fetch_and_process(match_id, proxy_list, odd_ids):
    base_url = f'https://www.mozzartbet.com/match/{match_id}'
    head = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'cookie': 'a_b_sft=s%3AbcMFNzQE87rVP7TagwShf8.xxctvl81EaBDWGR9qCMtmEd%2Fmd5NfP5TztGRveYCIcE; i18next=sr; SERVERID=RHN2; ...',  # Dodaj sve cookie vrednosti
        'medium': 'WEB',
        'origin': 'https://www.mozzartbet.com',
        'priority': 'u=1, i',
        'referer': f'https://www.mozzartbet.com/sr/kladjenje/sport/1/match/{match_id}?date=all_days&sort=bytime',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    json = {
        "subgameIds": []
    }
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession() as session:
        for i in range(1):
            try:
                async with session.post(base_url, headers=head, json=json, timeout=timeout) as response:
                    if response.status == 200:
                        match = await response.json()
                        odds_dict = {}
                        for i in odd_ids:
                            odds_dict[i] = 1.0
                        if match:
                            try:
                                a = match['match']['specialMatchGroupName']
                                return None
                            except:
                                pass
                            match_id = match['match']['id']
                            home_team = match['match']['home']['name']
                            visitor_team = match['match']['visitor']['name']
                            start_time = match['match']['startTime']
                            start_time_seconds = start_time / 1000
                            date_time = datetime.fromtimestamp(start_time_seconds)
                            formatted_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
                            odds_list = match['match']['odds']
                            for odd in odds_list:
                                key = odd['id']
                                if key in odd_ids:
                                    try:
                                        odds_dict[key] = odd['value']
                                    except:
                                        pass
                            match_info = {
                            'ID': match_id,
                            'vreme': formatted_time,
                            'domaci': home_team,
                            'gosti': visitor_team,
                        }
                            match_info.update(odds_dict)
                            return match_info
                    else:
                        print(f'Error: {match_id}: {response.status}')
                        return None
            except asyncio.TimeoutError as e:
                print(f'Timeout: {e}')
                return None
            except Exception as e:
                print(f'Error: {e}')

async def mozzart():
    head = ['ID', 'vreme', 'domaci', 'gosti', '1', 'X', '2', '1X', 'X2',
            'I W1', 'I W2', 'II W1', 'II W2',
            'I 1', 'I X', 'I 2', 'I 1X', 'I X2',
            'II 1', 'II X', 'II 2', 'II 1X', 'II X2',
            'W1', 'W2',
            '1/4 1', '1/4 X', '1/4 2', '1/4 1X', '1/4 X2',
            '1/4 W1', '1/4 W2',
            '2/4 1', '2/4 X', '2/4 2', '2/4 1X', '2/4 X2',
            '3/4 1', '3/4 X', '3/4 2', '3/4 1X', '3/4 X2',
            '4/4 1', '4/4 X', '4/4 2', '4/4 1X', '4/4 X2',
            '2/4 W1', '2/4 W2', '3/4 W1', '3/4 W2', '4/4 W1', '4/4 W2',
            'P1', 'P2', ]
    ids = [1002017001, 1002017002, 1002017003, 1002002001, 1002002002,
            'I W1', 'I W2', 'II W1', 'II W2',
            1002025001, 1002025002, 1002025003, 1002560001, 1002560002,
            'II 1', 'II X', 'II 2', 'II 1X', 'II X2',
            'W1', 'W2',
            '1/4 1', '1/4 X', '1/4 2', '1/4 1X', '1/4 X2',
            '1/4 W1', '1/4 W2',
            '2/4 1', '2/4 X', '2/4 2', '2/4 1X', '2/4 X2',
            '3/4 1', '3/4 X', '3/4 2', '3/4 1X', '3/4 X2',
            '4/4 1', '4/4 X', '4/4 2', '4/4 1X', '4/4 X2',
            '2/4 W1', '2/4 W2', '3/4 W1', '3/4 W2', '4/4 W1', '4/4 W2',
            1002196001, 1002196003, ]

    brojac = -1
    nova_lista = []
    for x in ids:
        if isinstance(x, str):
            nova_lista.append(brojac)
            brojac -= 1
        else:
            nova_lista.append(x)
    match_ids = await main()
    odd_ids = nova_lista
    proxy_list = []
    print("Mozzart:", len(match_ids))
    tasks = [fetch_and_process(match_id, proxy_list, odd_ids) for match_id in match_ids]
    results = await asyncio.gather(*tasks)
    results = [result for result in results if result is not None]
    if results:

        df = pd.DataFrame(results)
        df.columns = head
        df['vreme'] = pd.to_datetime(df['vreme'])
        df = df.sort_values(by='vreme')
        df['ID'] = [f'Mozzart{i}' for i in range(len(df))]
        df.to_csv('mozzart.csv', index=False)
if __name__ == "__main__":
    asyncio.run(mozzart())
