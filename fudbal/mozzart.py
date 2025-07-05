import httpx
import aiohttp
import asyncio
import pandas as pd
from datetime import datetime
from itertools import cycle
import random
from Telegram import send
import nest_asyncio
from liste import ucitaj_proksi
nest_asyncio.apply()

proksi = ucitaj_proksi()
danas = 'three_days'
#######################################################
async def obrada(match, odd_ids):
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
        home_team = home_team
        visitor_team = match['match']['visitor']['name']
        visitor_team = visitor_team
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

###################################################3
async def get_matches(session, page, proxy):
    url = 'https://www.mozzartbet.com/betting/matches'
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "sr-RS,sr;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json",
        "medium": "WEB",
        "origin": "https://www.mozzartbet.com",
        "priority": "u=1, i",
        "referer": "https://www.mozzartbet.com/sr/kladjenje/sport/1?date=today",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }
    cookies = {
        "a_b_sft": "s%3Ac1QuJqdm6CxJzpww5TcKym.q%2BKZAlFKv0ReMj1i1K6qFQ44pzAQ9SMHEBfkVlZDGnA",
        "i18next": "sr",
        "SERVERID": "RHN2",
        "__cf_bm": "yEORU86rWsEKUt5AMOQTyFonlHbx9FBOPoySNSj6cFo-1743584675-1.0.1.1-mxSMFHdJ0SGo9YuvUdOUBGgPOzNRm2nwMMHLaMAeL5Ippo86Z3fmGn0wEN9Gp8eCpuNsMtwvUXK4hksYkyvQwkYdGyT8d4_n_c.BkwkAP7k",
        "cf_clearance": "0Im5GZcqPM6_bzKhvEQ2p7YpQaQMdnMk0whP9VNvYSY-1743584678-1.2.1.1-0Wm8MraojhmdhnoUDm86Rv2bn9NKyxM9mBUj7xjO5VaHfzgNOG_FGuftIX9dUxnkRwtotRFkU7g5qmSSe291xmrNWUK1AeHwqLgIbdDPhk9V9ZPfONz6GRnDf7HvHH.51YP6R9IK5NfMUd_cfYw4yWDgz_Y4Tn0cT3.Qa74j2R_enimYHq3uALi7N1QRJZr8fJiTbuIMvyHdiVMvWTIK8UlQAF7tRqz2N9ig3TNQDnrifLxty7tdEiuUz3.PNQoXODGVfNq.T6ST1X3fkX4flh3v5gnxDL1S.Dx6oqPwPeycV9iiS_CSAyEPbm4UNMB7R3sZR5ttMDE3AbSv9CzwBCQY6RdXBqmP6d2yxwE31Ao"
    }
    data = {
        'date': danas,
        'sort': 'bytime',
        'currentPage': page,
        'pageSize': 100,
        'sportId': 1,
        'competitionIds': [],
        'search': '',
        'matchTypeId': 0
    }
    for attempt in range(2):
        try:
            async with session.post(url, proxy=proxy,headers=headers, cookies=cookies, json=data, timeout=10) as response:
                if response.status == 200:
                    results = await response.json()
                    return [item['id'] for item in results.get('items', [])]
                else:
                    print(f"Greška kod strane {page}: Status {response.status}")
        except Exception as e:
            print(f"Greška na strani {page}, pokušaj {attempt + 1}: {e}")
            await asyncio.sleep(2)
    return []


async def main():
    proxy_iter = cycle(proksi)
    async with aiohttp.ClientSession() as session:
        tasks = [get_matches(session, page, next(proxy_iter)) for page in range(20)]
        results = await asyncio.gather(*tasks)
    ids = []
    for result in results:
        ids += result

    unique_ids = list(set(ids))
    return unique_ids

##############################################################################################
async def fetch_and_process(match_id, proxy, odd_ids):
    base_url = f'https://www.mozzartbet.com/match/{match_id}'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'sr-RS,sr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'medium': 'WEB',
        'origin': 'https://www.mozzartbet.com',
        'referer': 'https://www.mozzartbet.com/sr/kladjenje/sport/1?date=today',
        'sec-ch-ua': '"Chromium";v="120", "Not:A-Brand";v="24", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',  # Ako zahtev dolazi sa eksternog servera
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    cookies = {
        'i18next': 'sr',
        '_gcl_au': '1.1.1500435550.1735174651',
        '_fbp': 'fb.1.1735174650791.572211526929542818',
        '__ssid': '5235e65f47d7af1191f517e4e94aef3',
        'mp_879947a8dcd32bc336323f05afa829b3_mixpanel': '{"distinct_id":"$device:194383c89a36243-006a900d2807d2-16462c6e-100200-194383c89a36243"}',
        '_ga_98N5CRXHPC': 'GS1.1.1736288972.1.1.1736289035.0.0.0',
        '_ga': 'GA1.1.32261541.1735174651',
        '_iidt': 'ZvmwMO6vs+myM0jzQtLCKpYceWIlXtSRuXsk1y9vKkIDVc82Dj5aSt4qCGkbze0ryfHVF0nrjKpaP76sTVSLlnm8NUYDarWoDtjzRjs=',
        '_vid_t': '7dzsC+DuWwF+MYfx76XvQWjYZ0PUzcHaWfhDIAA1FPqtW3iZrpgqDTltkbxxnIG0hPXZqv8P7r7/tT4+QEn6pEfYClwUfdydHNR7fZw=',
        '_clck': '131wg59|2|fu4|0|1821',
        'a_b_sft': 's%3ApdsJUtbjyU97TH3x9Ks7qU.EUEIR%2BZ8JhbXzJUlijxrIrlHeTWGJRICVDx0jJOSxzw',
        'SERVERID': 'RHN4',
        '__cf_bm': 'fsHV.m935JhSVya20FtGgClVHQ5ijiuXvTHmK4enwRI-1741723130-1.0.1.1-Hgmn9ky.BCi5nnxjN6j3DciLXNVLhx_ZnPEbzMzcbdn54vC8BjK_.DMGc3YdZAgMdNUIh9gp9iHGKsI9pYWugUS7PJo9VORxZn3Xqp4J23g',
        'cf_clearance': 'JBDyLF0rlDRi.SJNJ0_zirfiAKtDpzw8be_NM6He0ZA-1741723131-1.2.1.1-gvf87tyb_IteWJDAEPiBthv_gWkOfJlKgJ5iat9OyMQ6yoa_TXsdaImskzPhVivd00bidz6CXIIpk5E..dLTK6OTeCjiNRboK4ztOEnzaanfBmfgR.d2IIgC_gdryXuRRmb5cqffqE.TjnSIGScCsam1KOHi0mT41Df8hrk_Bl13TmOmhC2747zadstB4xEcX8oMtl67Y6ZboUcZS0Pmql2CnwiiM0oM3vQWoyBU.N7ziLgVzOq0YQumtI97_PP5D37b6MQExV0IMcoRh97z9cQkdkb5owH_2ekLc2qZ64PSOv2d9XRnzIYDsSmi7N0ZUmJePsrd1BV2fXhOFoEGFBykC4ud4bqrujBO5ccHsSA',
    }
    json = {
        "subgameIds": []
    }
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession() as session:
        for i in range(1):
            try:
                async with session.post(base_url, proxy=None, headers=headers, json=json, timeout=timeout, cookies=cookies) as response:
                    if response.status == 200:
                        match = await response.json()
                        return await obrada(match, odd_ids)
                async with session.post(base_url, proxy=proxy, headers=headers, json=json, timeout=timeout, cookies=cookies) as response:
                    if response.status == 200:
                        match = await response.json()
                        return await obrada(match, odd_ids)
            except asyncio.TimeoutError as e:
                print(f'Mozzart timeout: {e}')
                return None
            except Exception as e:
                print(f'Mozzart error')


async def mozzart():
    head = ['ID', 'vreme', 'domaci', 'gosti' ,'1', 'X', '2', '1X', '12', 'X2', 'ug 0-1', 'ug 0-2', '2-3', 'ug 3+', 'ug 4+', '4-6', 'ug 5+', 'ug 7+',
             '2+p.p.', '1+p.p.',
              '0:0', 'ug 2+', 'ug 0-3', '2-6', '2', '3', 'ug 6+', '2-4', '3-4', '1-3', '2-5', '3-5', 'ug 0-5', '1-2', '4-5', 'ug 0-4',
              '1-4', '3-6', 'par', 'nepar', '1', '4', '5', '1-5', 'ne 1', 'ne 2', 'ne 3', 'ne 4',
        #############################################
              'I 1', 'I X', 'I 2',
              '1-1','1-X', '1-2', 'X-1', 'X-X', 'X-2', '2-1', '2-X', '2-2', 'ne 1-1', 'ne X-1', 'ne X-X', 'ne X-2',
              'ne 2-2',
        ###############################################################################
              '1X-1X', '1X-12', '1X-X2', '12-1X', '12-12', '12-X2', 'X2-1X', 'X2-12', 'X2-X2'
        ######################################################################################
             , 'X', '1', '2', 'I 1+',
              'I 2+', 'I 3+', 'I 4+', 'I 0-1', 'I 2-3', 'I 0', '0', 'I 0-2', 'I 1-2', '1', '2', 'ne 1', 'ne 2',
              'II 1+', 'II 2+', 'II 3+',
              'II 4+', 'II 0-1', '2-3', 'II 0', '0', 'II 0-2', '1-2', '1', '2', 'ne 1', 'ne 2', 'prvo', 'drugo', 'jednako',
              'II 1', 'II X', 'II 2',
              '0:0', '0:1', '0:2', '0:3', '0:4', '0:5', '0:6', '0:7', '0:8', '0:9', '1:0', '1:1', '1:2',
              '1:3', '1:4', '1:5', '1:6', '1:7', '1:8', '1:9', '2:0', '2:1', '2:2', '2:3', '2:4', '2:5', '2:6', '2:7',
              '2:8', '2:9', '3:0', '3:1', '3:2', '3:3', '3:4', '3:5', '3:6', '3:7', '3:8', '3:9', '4:0', '4:1', '4:2',
              '4:3', '4:4', '4:5', '4:6', '4:7', '4:8', '4:9', '5:0', '5:1', '5:2', '5:3', '5:4', '5:5', '5:6', '5:7',
              '5:8', '5:9', '6:0', '6:1', '6:2', '6:3', '6:4', '6:5', '6:6', '6:7', '6:8', '6:9', '7:0', '7:1', '7:2',
              '7:3', '7:4', '7:5', '7:6', '7:7', '7:8', '7:9', '8:0', '8:1', '8:2', '8:3', '8:4', '8:5', '8:6', '8:7',
              '8:8', '8:9', '9:0', '9:1', '9:2', '9:3', '9:4', '9:5', '9:6', '9:7', '9:8', '9:9', 'W1', 'W2',
            #########################################################
              'D I 1+','D I 2+', 'D I 0', 'D I 0-1', 'D I 0-2', 'D I 1-2', 'D I 3+', 'G I 1+', 'G I 2+',
              'G I 0', 'G I 0-1', 'G I 0-2', 'G I 1-2', 'G I 3+',
            #######################################
              'GG', 'NG', 'GG3+',
              'I GG', 'II GG', 'ggI&ggII', 't1&t2 2+', 'ne GG3+', 'gg4+', 'I NG', 'II NG',
            ########################################
            'ING&IING', 'gg&I1+', 'GG&2+II',
              'IGG&3+', 'IIGG&3+', 'IGG&4+', 'IIGG&4+', 'GG& I1+ II1+', 'GG&2+I', '1+', '2+', '0', 'prvi', '12gg',
              '12ng', '2+&gg', '3+', '0-1', '0-2', '1', '2', 'ne 1', 'ne 2', '1-2', '1-3', '2-3', '4+', '2+I&3+',
              '2+I&2+II', '2+I&1+II', '1+I&2+', '1+I&3+', '1+I&2+II', '0-1I&0-1II', '1+', '2+', '0', 'prvi', '12gg',
              '12ng', '2+&gg', '3+', '0-1', '0-2', '1', '2', 'ne 1', 'ne 2', '1-2', '1-3', '2-3', '4+', '0-1I&0-1II',
              '1+I&2+II', '1+I&3+', '1+I&2+', '2+I&1+II', '2+I&2+II', '2+I&3+', '1', '2', '1-1', '1-X', '1-2', '2-1',
              '2-X', '2-2', '1&3+', '2&3+', '1&2+I', '2&2+I', '1-1&3+', '1-1&2+I', '1&2-3', '2&2-3', 'gg&2+I', '1&2+',
              '2& 2+', '1&4+', '2&4+', '2+I&1+II', '1+I&2+II', '2-2&3+', '1+I&1+II', '1&gg', '2&gg', '2&2+pp',
              '2-2&2+I', '1&bku>', '1&bku<', '2&bku>', '2&bku<', '1&žk>', '1&bžk<', '2&bžk>', '2&bžk<', '2+I&4+',
              '2+I&3+II', 'ggI&ngII', 'ngI&ggII', 'ngI&ngII', 'ne 1&2+', 'ne1&3+', '1&1+I', '1&0-2', '1&2-4', '1&3-5',
              '1-1&2+', '1-1&2-3', '1-1&2-4', '1-1&3-5', '1-1&gg', '1-1&ng', '1X&2+', '1X&3+', '1X&4+', '1X&2+I',
              '1X&0-2', '1X&0-3', '1X&gg', '1&vg1', '1&vgX', '1&vg2', '1X&vg1', '1X&vgX', '1X&vg2', 'X-1&2+', 'X-1&3+',
              'X-1&4+', 'X-1&0-2', 'X-1&2-3', 'X-1&2-4', 'X-1&3-5', 'X-1&gg', 'X-1&ng', 'X-X&3+', 'X-X&0-2', 'X-X&gg',
              'ne 2&2+', 'ne 2&3+', '2&1+I', '2&0-2', '2&2-4', '2&3-5', '2-2&2+', '2-2&2-3', '2-2&2-4', '2-2&3-5',
              '2-2&gg', '2-2&ng', 'X2&2+', 'X2&3+', 'X2&4+', 'X2&2+I', 'X2&0-2', 'X2&0-3', 'X2&gg', '2&vg1', '2&vgX',
              '2&vg2', 'X2&vg1', 'X2&vgX', 'X2&vg2', 'X-2&2+', 'X-2&3+', 'X-2&4+', 'X-2&0-2', 'X-2&2-3', 'X-2&2-4',
              'X-2&3-5', 'X-2&gg', 'X-2&ng', 'X&2+', 'X&0-2', 'X&4+', '2+I&2+II', '1-1&4+', '2-2&4+', 'I0-1&II0-1',
              'I0-1&II0-2', 'I0-1&II0-3', 'I0-2&II0-2', 'I1-2&II1-2', 'I1-3&II1-3', 'I1+&2+', 'I1+&3+', '1X&2-3',
              '1X&2-4', '1X&2-5', '1X&2-6', '1X&3-5', '1X&3-6', '1X&4-6', '12&0-3', '12&2+', '12&2-4', '12&2-5',
              '12&2-6', '12&3+', 'X2&2-3', 'X2&2-4', 'X2&2-5', 'X2&2-6', 'X2&3-5', 'X2&3-6', 'X2&4-6', '1&0-3', '1&2-5',
              '1&2-6', '1&3-6', '1&4-6', '2&0-3', '2&2-6', '2&3-4', '2&3-6', '2&4-6', '1-1&0-3', '1-1&2-5', '1-1&2-6',
              '1-1&3-6', '1-1&4-6', '1-1&5+', '1-1&HP1', '2-2&0-3', '2-2&2-5', '2-2&2-6', '2-2&3-6', '2-2&4-6',
              '2-2&5+', '2-2&HP2', '2&2-5', '1-2I&3+', '1-2I&4+', '2-3I&4+', '1-3I&3+', '2-3I&2-3II', '1-2I&1-3II',
              '1-3I&1-2II', '2+I&3+', '0-1I&1+II', '0-1I&2+II', '0-2I&2+II', '1-1&T1 3+', '2-2& T2 3+', '1& I1+ II 1+',
              '2& I1+ II1+', '1&T1 3+', '2&T2 3+', '1&T1 2-3', '2&T2 2-3', '1& I1+ 2+', '2&I1+ 2+', '1&I1+ 3+',
              '2&I1+ 3+', '1&I1-3 II 1-3', '2&I1-3 II 1-3',
            ###########################################################
              'D II 1+', 'D II 2+', 'D II 0', 'D II 0-1', 'D II 0-2', 'D II 1-2', 'D II 3+', 'G II 1+', 'G II 2+',
              'G II 0', 'G II 0-1', 'G II 0-2', 'G II 1-2', 'G II 3+', '1-1', '2-2',
            ########################################################################
            'ki1Vpp1', 'kiXVppX', 'ki2Vpp2', 'ki1V3+', 'ggIVggII',
              '2+IV2+II', '3+IV3+II', '1', '2', '1', '2', 'I 1X', 'I 12', 'I X2', '1', 'X', '2', 'manje', 'više', 'manje',
              '=', 'više', 'manje', '=', 'više', 'manje', '=', 'više', 'manje', '=', 'više', 'manje', '=', 'više',
              'manje', '=', 'više', 'manje', '=', 'više', 'manje', '=', 'više', 'II 1X', 'II 12', 'II X2',
            '1-1X', '1-12', '1-X2', 'X-1X', 'X-12', 'X-X2', '2-1X', '2-12',
            '2-X2', '1X-1', '1X-X', '1X-2', '12-1', '12-X', '12-2', 'X2-1', 'X2-X', 'X2-2',
            ]

    odd_ids = [1001001001, 1001001002, 1001001003, 1001002001, 1001002002, 1001002003, 1001003001, 1001003002,
               1001003003, 1001003004, 1001003005, 1001003006, 1001003007, 1001003008, 1001003009, 1001003010,
               1001003011, 1001003012, 1001003013, 1001003014, 1001003015, 1001003016, 1001003017, 1001003018,
               1001003019, 1001003020, 1001003021, 1001003022, 1001003023, 1001003024, 1001003025, 1001003026,
               1001003027, 1001003028, 1001003029, 1001003030, 1001003031, 1001003032, 1001003033, 1001003034,
               1001003035, 1001003036, 1001003037, 1001003038, 1001004001, 1001004002, 1001004003, 1001005001,
               1001005002, 1001005003, 1001005004, 1001005005, 1001005006, 1001005007, 1001005008, 1001005009,
               1001005010, 1001005011, 1001005012, 1001005013, 1001005014, 1001005015, 1001005016, 1001005017,
               1001005018, 1001005019, 1001005020, 1001005021, 1001005022, 1001005023, 1001007000, 1001007001,
               1001007002, 1001008001, 1001008002, 1001008003, 1001008004, 1001008005, 1001008006, 1001008007,
               1001008008, 1001008009, 1001008010, 1001008011, 1001008012, 1001008013, 1001008014, 1001009001,
               1001009002, 1001009003, 1001009004, 1001009005, 1001009006, 1001009007, 1001009008, 1001009009,
               1001009010, 1001009011, 1001009012, 1001009013, 1001009014, 1001016001, 1001016002, 1001016003,
               1001019001, 1001019002, 1001019003, 1001020000, 1001020001, 1001020002, 1001020003, 1001020004,
               1001020005, 1001020006, 1001020007, 1001020008, 1001020009, 1001020010, 1001020011, 1001020012,
               1001020013, 1001020014, 1001020015, 1001020016, 1001020017, 1001020018, 1001020019, 1001020020,
               1001020021, 1001020022, 1001020023, 1001020024, 1001020025, 1001020026, 1001020027, 1001020028,
               1001020029, 1001020030, 1001020031, 1001020032, 1001020033, 1001020034, 1001020035, 1001020036,
               1001020037, 1001020038, 1001020039, 1001020040, 1001020041, 1001020042, 1001020043, 1001020044,
               1001020045, 1001020046, 1001020047, 1001020048, 1001020049, 1001020050, 1001020051, 1001020052,
               1001020053, 1001020054, 1001020055, 1001020056, 1001020057, 1001020058, 1001020059, 1001020060,
               1001020061, 1001020062, 1001020063, 1001020064, 1001020065, 1001020066, 1001020067, 1001020068,
               1001020069, 1001020070, 1001020071, 1001020072, 1001020073, 1001020074, 1001020075, 1001020076,
               1001020077, 1001020078, 1001020079, 1001020080, 1001020081, 1001020082, 1001020083, 1001020084,
               1001020085, 1001020086, 1001020087, 1001020088, 1001020089, 1001020090, 1001020091, 1001020092,
               1001020093, 1001020094, 1001020095, 1001020096, 1001020097, 1001020098, 1001020099, 1001026001,
               1001026002, 1001128001, 1001128002, 1001128003, 1001128004, 1001128005, 1001128006, 1001128007,
               1001129001, 1001129002, 1001129003, 1001129004, 1001129005, 1001129006, 1001129007, 1001130001,
               1001130002, 1001130003, 1001130004, 1001130005, 1001130006, 1001130007, 1001130008, 1001130009,
               1001130010, 1001130011, 1001130012, 1001130013, 1001130014, 1001130015, 1001130016, 1001130017,
               1001130018, 1001130019, 1001130020, 1001131001, 1001131002, 1001131003, 1001131004, 1001131005,
               1001131006, 1001131007, 1001131008, 1001131009, 1001131010, 1001131011, 1001131012, 1001131013,
               1001131014, 1001131015, 1001131016, 1001131017, 1001131018, 1001131019, 1001131020, 1001131021,
               1001131022, 1001131023, 1001131024, 1001131025, 1001132001, 1001132002, 1001132003, 1001132004,
               1001132005, 1001132006, 1001132007, 1001132008, 1001132009, 1001132010, 1001132011, 1001132012,
               1001132013, 1001132014, 1001132015, 1001132016, 1001132017, 1001132018, 1001132019, 1001132020,
               1001132021, 1001132022, 1001132023, 1001132024, 1001132025, 1001139001, 1001139002, 1001140001,
               1001140002, 1001140003, 1001140004, 1001140005, 1001140006, 1001141001, 1001141002, 1001141003,
               1001141004, 1001141005, 1001141006, 1001141007, 1001141008, 1001141009, 1001141010, 1001141011,
               1001141012, 1001141013, 1001141014, 1001141015, 1001141016, 1001141017, 1001141018, 1001141019,
               1001141020, 1001141021, 1001141022, 1001141023, 1001141024, 1001141025, 1001141026, 1001141027,
               1001141028, 1001141029, 1001141030, 1001141031, 1001141032, 1001141033, 1001141034, 1001141035,
               1001141036, 1001141037, 1001141038, 1001141039, 1001141040, 1001141041, 1001141042, 1001141043,
               1001141044, 1001141045, 1001141046, 1001141047, 1001141048, 1001141049, 1001141050, 1001141051,
               1001141052, 1001141053, 1001141054, 1001141055, 1001141056, 1001141057, 1001141058, 1001141059,
               1001141060, 1001141061, 1001141062, 1001141063, 1001141064, 1001141065, 1001141066, 1001141067,
               1001141068, 1001141069, 1001141070, 1001141071, 1001141072, 1001141073, 1001141074, 1001141075,
               1001141076, 1001141077, 1001141078, 1001141079, 1001141080, 1001141081, 1001141082, 1001141083,
               1001141084, 1001141085, 1001141086, 1001141087, 1001141088, 1001141089, 1001141090, 1001141091,
               1001141092, 1001141093, 1001141094, 1001141095, 1001141096, 1001141097, 1001141098, 1001141099,
               1001141100, 1001141101, 1001141102, 1001141103, 1001141104, 1001141105, 1001141106, 1001141107,
               1001141108, 1001141109, 1001141110, 1001141111, 1001141112, 1001141113, 1001141114, 1001141115,
               1001141116, 1001141117, 1001141118, 1001141119, 1001141120, 1001141121, 1001141122, 1001141123,
               1001141124, 1001141125, 1001141126, 1001141127, 1001141128, 1001141129, 1001141130, 1001141131,
               1001141132, 1001141133, 1001141134, 1001141135, 1001141136, 1001141137, 1001141138, 1001141139,
               1001141140, 1001141141, 1001141142, 1001141143, 1001141144, 1001141145, 1001141146, 1001141147,
               1001141148, 1001141149, 1001141150, 1001141151, 1001141152, 1001141153, 1001141154, 1001141155,
               1001141156, 1001141157, 1001141158, 1001141159, 1001141160, 1001141161, 1001141162, 1001141163,
               1001141164, 1001141165, 1001141166, 1001141167, 1001141168, 1001141169, 1001141170, 1001141171,
               1001141172, 1001141173, 1001141174, 1001141175, 1001141176, 1001141177, 1001141178, 1001141179,
               1001141180, 1001141181, 1001141182, 1001141183, 1001141184, 1001141185, 1001141186, 1001141187,
               1001141188, 1001141189, 1001142001, 1001142002, 1001142003, 1001142004, 1001142005, 1001142006,
               1001142007, 1001143001, 1001143002, 1001143003, 1001143004, 1001143005, 1001143006, 1001143007,
               1001153001, 1001153002, 1001154001, 1001154002, 1001154003, 1001154004, 1001154005, 1001154006,
               1001154007, 1001179001, 1001179002, 1001180001, 1001180002, 1001297001, 1001297002, 1001297003,
               1001404001, 1001404002, 1001404003, 1001041001, 1001041002, 1001059001, 1001059002, 1001059003,
               1001060001, 1001060002, 1001060003, 1001061001, 1001061002, 1001061003, 1001062001, 1001062002,
               1001062003, 1001063001, 1001063002, 1001063003, 1001064001, 1001064002, 1001064003, 1001065001,
               1001065002, 1001065003, 1001066001, 1001066002, 1001066003]
    for i in range(3+18):
      odd_ids.append(i)
    match_ids = await main()
    if len(match_ids) < 20:
      await send(['Error Mozzart'], False)
    print("Mozzart:", len(match_ids))
    batch_size = 100
    results = []
    proxy_iter = cycle(proksi)

    for i in range(0, len(match_ids), batch_size):
      batch = match_ids[i:i+batch_size]
      tasks = [fetch_and_process(match_id, next(proxy_iter), odd_ids) for match_id in batch]
      batch_results = await asyncio.gather(*tasks)
      results.extend([r for r in batch_results if r is not None])
      await asyncio.sleep(0)
    if results:
        df = pd.DataFrame(results)
        df.columns = head
        df['vreme'] = pd.to_datetime(df['vreme'])
        df = df.sort_values(by='vreme')
        df = df.replace(0, 1.0)
        df['ID'] = [f'Mozzart{i}' for i in range(len(df))]
        df.to_csv('/content/mozzart.csv', index=False)
if __name__ == "__main__":
    asyncio.run(mozzart())
