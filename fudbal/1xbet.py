import aiohttp
import asyncio
import pandas as pd
from datetime import datetime
import requests
import urllib.parse
from itertools import cycle
from liste import ucitaj_proksi
import nest_asyncio
nest_asyncio.apply()

proksi = ucitaj_proksi()

async def fetch_matches_for_lige_ids(lige_ids, proxy_iter):
    proxy = next(proxy_iter)
    async with aiohttp.ClientSession() as session:
        for liga in lige_ids:
            url = "https://1xbet.rs/service-api/LineFeed/Get1x2_VZip?"
            params = {
                "sports": "1",
                "champs": liga,
                "count": "10",
                "lng": "en",
                "mode": "4",
                "country": "168",
                "partner": "321",
                "getEmpty": "true",
                "virtualSports": "true"
            }
            headers = {
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-US,en;q=0.9,sr;q=0.8",
                "content-type": "application/json",
                "if-modified-since": "Sun, 01 Jun 2025 10:42:55 GMT",
                "is-srv": "false",
                "priority": "u=1, i",
                "referer": "https://1xbet.rs/en/line/football",
                "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Linux"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
                "x-app-n": "__BETTING_APP__",
                "x-hd": "'x-hd: eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJndWlkIjoib09xb29zVFlUN2xKWlZ4VVU1SmkwR0o4czl6eWF6eXZOK1ZFNGVwNDJ4bHFQMFgwcVJTUGJHc2pHQnQ3VFF6cEtxZ21wNVR5bk01OUJGWk5PalVrdEJ1eWJPNmtOOUNqWFRRZnYwUUk0cDBjcXJuZUZlMkxFWWlqOWNSMXRxWkg1aFdTZzRXa3V1eXRPNGYvTlM4R3plN2pEdTQwYWRPTEkrS2lCVVdBZ3hXQ2ZWRUxUYXlWemloZGFnRG5zN0xqUE1CaXRBT0tIdGFCQ0ltM2g0S29WNXlTanhRRVUwNVZDcXBkRkp2NkxDWWsxZTZEc1ZMT0h0TERacC9zcFVEbjRLVnhXZk5ncldDa0lheDQ1UFgxQmFxNkZCNU82S2tXVVJZUE5nWUdlVUpMMFM5bzFSRGNVbzZsTjJ6Unl3TGVUT2tiWHhuSlN3MFZEaWJoTmM4ZlAwYjc3cUhOMXRybU9PVEt4OWNET1c2Y0xteUxCb1M0cjF0QnRUVTBDQXpjQXdQaDk3ak11TFE9IiwiZXhwIjoxNzQ4Nzg4MzkwLCJpYXQiOjE3NDg3NzM5OTB9.YfaswNYUUACVJ_lsiOR7AtD10RE6rySaGn5NO8wrbpy1Bm191FydcVqc8PD1dFLBtoPPggMnD1ijdUuOuADZJw'",
                "x-requested-with": "XMLHttpRequest",
                "x-svc-source": "__BETTING_APP__"
            }
            cookies = {
                "platform_type": "desktop",
                "auid": "CsgTC2g8K6RA9xAFA8nGAg==",
                "lng": "en",
                "tzo": "2",
                "is12h": "0",
                "referral_values": urllib.parse.quote(
                    '{"type":"reflinkid","val":"e_3882345m_96329c_sb_google-search_all_brand_Eng~168605490701~749643525582~1xbet","additional":{"name_tag":"tag"}}'
                ), "reflinkid": "e_3882345m_96329c_sb_google-search_all_brand_Eng~168605490701~749643525582~1xbet",
                "SESSION": "6674ce1689b8a7e2ce8609372fcc79c1",
                "che_g": "a65007a4-56cf-92ad-1e9c-d41c29591581",
                "sh.session.id": "edd648f5-896e-4784-874a-776eff47ce18",
                "cookies_agree_type": "3",
                "application_locale": "en",
                "PAY_SESSION": "eff86aec5c1a742c4900ccdeb002c0fe",
                "_gcl_gs": "2.1.k1$i1748773968$u179606692",
                "_gcl_au": "1.1.1901237137.1748773981",
                "_ga": "GA1.1.1202900648.1748773982",
                "_fbp": "fb.1.1748773982050.453936093732582956",
                "_gcl_aw": "GCL.1748773983.Cj0KCQjw9O_BBhCUARIsAHQMjS5bx2GBaj88MMpYoQON1sLHfoiSdVR8zRjgxvxQqbQII7cUUThHwiQaAv_2EALw_wcB",
                "_cq_duid": "1.1748773983.uVcrvbZCD2ZOUCzu",
                "_cq_suid": "1.1748773983.GqBFBt9Mmkn5jEN4",
                "window_width": "1366",
                "_ga_K6MKCGPW4P": "GS2.1.s1748773981$o1$g1$t1748774582$j3$l0$h0",
                "_ga_C3NHDZS119": "GS2.1.s1748773982$o1$g1$t1748774582$j3$l0$h0"
            }
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.get(url, proxy=None, headers=headers, cookies=cookies, params=params,timeout=timeout) as response:
                if response.status != 200:
                    print(response.status)
                    continue
                print('----vvvvvvvvv')
                data = await response.json()
                for match in data["Value"]:
                    liga = match.get("L", "Nepoznata liga")
                    pocetak = match.get("S", 0)
                    vreme = datetime.fromtimestamp(pocetak)
                    domacin = match.get("O1", "Nepoznato")
                    gost = match.get("O2", "Nepoznato")
                    continue
                    print(f"🏆 Liga: {liga}")
                    print(f"🕒 Početak: {vreme}")
                    print(f"⚽ Meč: {domacin} vs {gost}")
                    kvote = {1: None, 2: None, 3: None}
                    for e in match.get("E", []):
                        if e.get("G") == 1 and e.get("T") in [1, 2, 3]:
                            kvote[e["T"]] = e["C"]

                    print("📈 Kvote:")
                    print(f"  ➤ 1: {kvote[1]}")
                    print(f"  ➤ X: {kvote[2]}")
                    print(f"  ➤ 2: {kvote[3]}")
                    print("-" * 40)
    return None

async def get_lige_ids():
    url = "https://1xbet.rs/service-api/LineFeed/GetSportsShortZip?"
    params = {
        "sports": "1",
        "lng": "en",
        "country": "168",
        "partner": "321",
        "virtualSports": "True",
        "gr": "1039",
        "groupChamps": "True"
    }
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9,sr;q=0.8",
        "content-type": "application/json",
        "if-modified-since": "Sun, 01 Jun 2025 10:42:55 GMT",
        "is-srv": "false",
        "priority": "u=1, i",
        "referer": "https://1xbet.rs/en/line/football",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "x-app-n": "__BETTING_APP__",
        "x-hd": "'x-hd: eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJndWlkIjoib09xb29zVFlUN2xKWlZ4VVU1SmkwR0o4czl6eWF6eXZOK1ZFNGVwNDJ4bHFQMFgwcVJTUGJHc2pHQnQ3VFF6cEtxZ21wNVR5bk01OUJGWk5PalVrdEJ1eWJPNmtOOUNqWFRRZnYwUUk0cDBjcXJuZUZlMkxFWWlqOWNSMXRxWkg1aFdTZzRXa3V1eXRPNGYvTlM4R3plN2pEdTQwYWRPTEkrS2lCVVdBZ3hXQ2ZWRUxUYXlWemloZGFnRG5zN0xqUE1CaXRBT0tIdGFCQ0ltM2g0S29WNXlTanhRRVUwNVZDcXBkRkp2NkxDWWsxZTZEc1ZMT0h0TERacC9zcFVEbjRLVnhXZk5ncldDa0lheDQ1UFgxQmFxNkZCNU82S2tXVVJZUE5nWUdlVUpMMFM5bzFSRGNVbzZsTjJ6Unl3TGVUT2tiWHhuSlN3MFZEaWJoTmM4ZlAwYjc3cUhOMXRybU9PVEt4OWNET1c2Y0xteUxCb1M0cjF0QnRUVTBDQXpjQXdQaDk3ak11TFE9IiwiZXhwIjoxNzQ4Nzg4MzkwLCJpYXQiOjE3NDg3NzM5OTB9.YfaswNYUUACVJ_lsiOR7AtD10RE6rySaGn5NO8wrbpy1Bm191FydcVqc8PD1dFLBtoPPggMnD1ijdUuOuADZJw'",
        "x-requested-with": "XMLHttpRequest",
        "x-svc-source": "__BETTING_APP__"
    }
    cookies = {
        "platform_type": "desktop",
        "auid": "CsgTC2g8K6RA9xAFA8nGAg==",
        "lng": "en",
        "tzo": "2",
        "is12h": "0",
        "referral_values": urllib.parse.quote(
            '{"type":"reflinkid","val":"e_3882345m_96329c_sb_google-search_all_brand_Eng~168605490701~749643525582~1xbet","additional":{"name_tag":"tag"}}'
        ), "reflinkid": "e_3882345m_96329c_sb_google-search_all_brand_Eng~168605490701~749643525582~1xbet",
        "SESSION": "6674ce1689b8a7e2ce8609372fcc79c1",
        "che_g": "a65007a4-56cf-92ad-1e9c-d41c29591581",
        "sh.session.id": "edd648f5-896e-4784-874a-776eff47ce18",
        "cookies_agree_type": "3",
        "application_locale": "en",
        "PAY_SESSION": "eff86aec5c1a742c4900ccdeb002c0fe",
        "_gcl_gs": "2.1.k1$i1748773968$u179606692",
        "_gcl_au": "1.1.1901237137.1748773981",
        "_ga": "GA1.1.1202900648.1748773982",
        "_fbp": "fb.1.1748773982050.453936093732582956",
        "_gcl_aw": "GCL.1748773983.Cj0KCQjw9O_BBhCUARIsAHQMjS5bx2GBaj88MMpYoQON1sLHfoiSdVR8zRjgxvxQqbQII7cUUThHwiQaAv_2EALw_wcB",
        "_cq_duid": "1.1748773983.uVcrvbZCD2ZOUCzu",
        "_cq_suid": "1.1748773983.GqBFBt9Mmkn5jEN4",
        "window_width": "1366",
        "_ga_K6MKCGPW4P": "GS2.1.s1748773981$o1$g1$t1748774582$j3$l0$h0",
        "_ga_C3NHDZS119": "GS2.1.s1748773982$o1$g1$t1748774582$j3$l0$h0"
    }
    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                print(f"Error status: {response.status}")
                exit()
            data = await response.json()

    def extract_all_li(obj):
        li_values = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "LI":
                    li_values.append(v)
                else:
                    li_values.extend(extract_all_li(v))
        elif isinstance(obj, list):
            for item in obj:
                li_values.extend(extract_all_li(item))
        return li_values
    lista = extract_all_li(data)
    for item_to_remove in ['1413697', '2819162']:
        try:
            lista.remove(item_to_remove)
        except ValueError:
            pass

    return lista

async def maxbet():
    print("1Xbet")
    lige_ids = await get_lige_ids()
    proxy_iter = cycle(proksi)
    print('ff')
    if lige_ids:
        matches_info = await fetch_matches_for_lige_ids(lige_ids, proxy_iter)
        df = pd.DataFrame(matches_info)
        df['vreme'] = pd.to_datetime(df['vreme'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
        df = df.sort_values(by='vreme')
        df['ID'] = [f'Maxbet{i}' for i in range(len(df))]
        df.to_csv('maxbet.csv', index=False, header=head)


# Pokreni asinhroni kod
if __name__ == "__main__":
    asyncio.run(maxbet())

