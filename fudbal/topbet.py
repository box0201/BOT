import aiohttp
import asyncio
from datetime import datetime, timedelta
import pandas as pd
from pytz import timezone
import nest_asyncio
nest_asyncio.apply()


lista = []
async def fetch_event(session, match_id, ids):
    if match_id:
        try:
            base_url = 'https://sports-sm-distribution-api.de-2.nsoftcdn.com/api/v1/events/'
            params = {
                'companyUuid': '4dd61a16-9691-4277-9027-8cd05a647844',
                'id': match_id,
                'language': '{"default":"en-Latn","events":"en-Latn","sport":"en-Latn","category":"en-Latn","tournament":"en-Latn","team":"en-Latn","market":"en-Latn"}',
                'timezone': 'Europe/Belgrade',
                'dataFormat': '{"default":"array","markets":"array","events":"array"}'
            }
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9',
                'origin': 'https://sports-sm-web.7platform.net',
                'priority': 'u=1, i',
                'referer': 'https://sports-sm-web.7platform.net/',
                'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
            }
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.get(base_url + str(match_id), headers=headers, params=params,
                                   timeout=timeout) as response:
                if response.status != 200:
                    print(f"Failed to fetch event {match_id}, Status code: {response.status}")
                    return None

                data = await response.json()
                timovi = data['data']['name'].split(' - ')
                domaci = timovi[0]
                gosti = timovi[1]
                id = data['data']['id']
                vreme = data['data']['startsAt']
                vreme = datetime.strptime(vreme, "%Y-%m-%dT%H:%M:%S.%fZ")
                vreme = vreme
                odds_data = {
                    'ID': id,
                    'vreme': vreme,
                    'domaci': domaci,
                    'gosti': gosti,
                }
                for outcome_id in ids:
                    odds_data[outcome_id] = 1.0
                for market in data['data']['markets']:
                    for outcome in market['outcomes']:
                        if outcome['outcomeId'] in ids:
                            odds_data[outcome['outcomeId']] = outcome['odd']

                return odds_data
        except Exception as e:
            print(f"Topbet timeout {match_id}:")
            return None


async def fetch_events(session):
    sada = datetime.now()
    formatirani_datum_vreme = sada.strftime('%Y-%m-%dT%H:%M:%S')
    url = f'https://sports-sm-distribution-api.de-2.nsoftcdn.com/api/v1/events?deliveryPlatformId=3&dataFormat=%7B%22default%22:%22object%22,%22events%22:%22array%22,%22outcomes%22:%22array%22%7D&language=%7B%22default%22:%22sr-Latn%22,%22events%22:%22sr-Latn%22,%22sport%22:%22sr-Latn%22,%22category%22:%22sr-Latn%22,%22tournament%22:%22sr-Latn%22,%22team%22:%22sr-Latn%22,%22market%22:%22sr-Latn%22%7D&timezone=Europe%2FBelgrade&company=%7B%7D&companyUuid=4dd61a16-9691-4277-9027-8cd05a647844&filter[sportId]=3&filter[from]={formatirani_datum_vreme}&sort=categoryPosition,categoryName,tournamentPosition,tournamentName,startsAt&offerTemplate=WEB_OVERVIEW&shortProps=1'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://sports-sm-web.7platform.net',
        'priority': 'u=1, i',
        'referer': 'https://sports-sm-web.7platform.net/',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            print(f"Error fetching events: Status code {response.status}")
            return []
        data = await response.json()
        events = data['data']['events']
        return [event['a'] for event in events]


async def topbet():
    ids = [12, 15, 18, 21, 24, 27, 363, 366, 369, 372, 375, 378, 381, 384, 387, 390, 393, 396, 399, 402, 405, 126, 135,
           276, 279, 282, 288, 291, 294, 297, 300, 303, 306, 309, 312, 315, 318, 321, 324, 327, 330, 333, 336, 339, 342,
           345, 348, 351, 354, 357, 360, 2763, 2766, 2769, 2772, 2775, 2778, 2781, 2784, 2787, 2790, 2793, 2796, 1665,
           1671, 1677, 1680, 1695, 1698, 1701, 1704, 1707, 1710, 1713, 1716, 1719, 1722, 1725, 1728, 1731, 1734, 1737,
           1740, 1743, 744, 747, 750, 753, 756, 759, 762, 765, 768, 771, 774, 777, 780, 783, 786, 789, 792, 186, 189,
           192, 201, 207, 210, 213, 216, 219, 222, 228, 231, 234, 237, 240, 243, 246, 249, 252, 255, 258, 261, 264, 267,
           270, 273, 1938, 1941, 1944, 1947, 1950, 2307, 2310, 2313, 2316, 2319, 2331, 2334, 2337, 2340, 2343, 2346,
           2349, 2352, 2355, 2358, 2361, 2364, 2367, 2370, 2373, 2376, 2379, 2382, 2385, 2388, 2391, 2394, 3363, 3366,
           3369, 3372, 3375, 3378, 1152, 1155, 1158, 1161, 1164, 1167, 1170, 1173, 1176, 1179, 1182, 1185, 1188, 1191,
           1194, 1197, 1200, 1203, 1209, 1212, 1236, 1239, 1242, 1245, 1251, 1254, 1257, 1260, 1263, 1266, 1269, 1272,
           1275, 1278, 1287, 1290, 1293, 1296, 1299, 1302, 1305, 1308, 1311, 1314, 1317, 1320, 1323, 1326, 1329, 1332,
           1356, 1359, 1362, 1365, 1368, 1371, 1374, 1377, 1380, 1383, 1386, 1389, 1392, 1395, 1398, 1401, 1404, 1407,
           1410, 1416, 1419, 4852, 3381, 3384, 3387, 3390, 3393, 3396, 3399, 3402, 3405, 3408, 3282, 3285, 3288, 3291,
           3294, 3297, 3315, 3318, 3321, 3324, 3327, 3330, 408, 411, 414, 417, 420, 423, 426, 429, 432, 435, 438, 441,
           444, 447, 450, 453, 456, 459, 462, 465, 468, 471, 474, 477, 480, 483, 486, 2799, 2802, 2805, 2808, 2811,
           2814, 2817, 2820, 2823, 2826, 3333, 3336, 3339, 3342, 3345, 3348, 3351, 3354, 3357, 3360, 3828, 3834, 3837,
           3843, 3849, 3852, 3855, 3861, 3867, 3873, 3876, 3879, 3885, 3888, 3891, 3894, 3897, 3900, 3903, 3906, 3909,
           3915, 3918, 3921, 3927, 3930, 3933, 3945, 3948, 3954, 3957, 3960, 3963, 3966, 3969, 4840, 4843, 4846, 4849,
           3795, 3801, 3804, 3687, 3690, 3693, 3696, 3708, 3711, 3714, 3720, 3723, 3726, 3729, 3735, 528, 531, 534, 537,
           540, 543, 546, 549, 552, 555, 558, 561, 1746, 1749, 1752, 1755, 1758, 1761, 1764, 1767, 1770, 1773, 1776,
           564, 567, 570, 573, 576, 579, 582, 585, 588, 591, 594, 597, 1779, 1782, 1785, 1788, 1791, 1794, 1797, 1800,
           1803, 1806, 1809, 600, 603, 606, 609, 612, 615, 618, 645, 648, 651, 654, 657, 660, 663, 621, 624, 627, 633,
           636, 639, 642, 666, 669, 672, 675, 678, 681, 684, 1632, 1635, 1638, 1611, 1614, 693, 696, 1554, 1557, 1560,
           1563, 1566, 1569, 1572, 1575, 1578, 1581, 519, 522, 5347, 5350, 5353, 1977, 1980, 1983, 1986, 1989, 1992,
           2964, 2967, 2970, 2973, 5362, 5365, 2976, 2982, 2985, 2988, 2991, 2994, 2997, 3003, 3006, 3009, 5117, 5120,
           5123, 5126, 5129, 5132, 5135, 5138, 5141, 5329, 5332, 5335, 5338, 5341, 5344, 5356, 5359, 1473, 1476, 1479,
           1482, 1485, 1488, 1491, 1494, 1497, 1500, 1503, 1506, 1509, 1512, 1515, 1518, 1521, 1527, 1530, 1533, 1536,
           1539, 1542, 1545, 1548, 1551, 489, 492, 495, 498, 501, 504, 507, 510, 513, 516, 1443, 1446, 1449, 1452, 1455,
           1458, 1461, 1464, 1467, 1470, 4332, 4335, 4338, -1, -2, -3]
    head = ['ID', 'vreme', 'domaci', 'gosti', '1', 'X', '2', '1X', '12', 'X2', 'I 1', 'I X', 'I 2',
            'II 1', 'II X', 'II 2',
            '1-1', '1-X', '1-2', 'X-1', 'X-X', 'X-2', '2-1', '2-X', '2-2', 'ug 0-2', 'ug 3+', 'ug 0-1', 'ug 2+',
            'ug 1+', '1', '2', '3', '4', '5', 'ug 0-3', 'ug 4+', 'ug 0-4', 'ug 5+', '6+', '7+', '1-2', '1-3', '1-4',
            '1-5', '1-6', '2-3', '2-4', '2-5', '2-6',
            '3-4',
            '3-5', '3-6', '4-5', '4-6', 'GG', 'NG', '2GG', '2NG', 'I GG', 'I NG', 'II GG', 'II NG', 'ING&IING',
            'ING&IIGG',
            'IGG&IING', 'IGG&IIGG', 'I0-1&II0-1', 'I0-2&II0-2', 'I1+&II1+', 'I2+&II2+', 'I0-1&II0-2', 'I0-1&II0-3',
            'I0-2&II0-1', 'I0-2&II0-3', 'I1+&II2+', 'I1+&II3+', 'I1-2&II1-2', 'I1-3&II1-3', 'I2-3&II2-3', 'I2+&II1+',
            'I2+&II3+', 'I1+&2+', 'I1+&3+', 'I1-2&3+', 'I1-2&4+', 'I2+&3+', 'I2+&4+', 'GG3+', 'GG&4+', 'GG&2-3',
            'GG&I1+', 'GG&I1-2', 'GG&I2+', 'GG&II1+', 'GG&II2+', 'GG&I1+II1+', 'GG&D2+', 'GG&G2+', 'IGG&3+', 'IGG&4+',
            'IGG&I3+', 'IIGG&3+', 'IIGG&4+', 'IIGG&II3+',
            'I 0', 'I 0-1', 'I 0-2', 'I 1+', 'I 2+', 'I 1-2', 'I 1-3', 'I 2-3', 'I 1', 'I 2', 'I 3+', 'I 3', 'I 4+',
            'II 0', 'II 1', 'II 2+', 'II 0-1', 'II 1+', 'II 0-2', 'II 1-2', 'II 1-3', 'II 2', 'II 2-3', 'II 3',
            'II 3+', 'II 4+',
            '1&3+',
            '1&4+', '2&3+', '2&4+', '1&2-3', '1&0-2', '1&0-3', '1&2+', '1&2-4', '1&2-5', '1&2-6', '1&3-4', '1&3-5',
            '1&3-6', '1&4-5', '1&4-6', '1&5+', 'X&0-2', 'X&2+', '2&0-2', '2&0-3', '2&2+', '2&2-3', '2&2-4', '2&2-5',
            '2&2-6', '2&3-4', '2&3-5', '2&3-6', '2&4-5', '2&4-6', '2&5+', '1&D2-3', '1&D3+', '1&I1+II1+', '2&G2-3',
            '2&G3+', '2&I1+II1+', '1-1&0-2', '1-1&0-3', '1-1&2+', '1-1&2-3', '1-1&2-4', '1-1&2-5', '1-1&2-6',
            '1-1&3+',
            '1-1&3-4', '1-1&3-5', '1-1&3-6', '1-1&4+', '1-1&4-5', '1-1&4-6', '1-1&5+', '1-1&II1+', '1-1&I2+',
            '1-1&II2+',
            '1-1&D2-3', '1-1&D3+', '1-2&5+', 'X-1&0-2', 'X-1&0-3', 'X-1&2+', 'X-1&2-4', 'X-1&2-5', 'X-1&2-6',
            'X-1&3+',
            'X-1&3-4', 'X-1&3-5', 'X-1&3-6', 'X-1&4+', 'X-1&I2+', 'X-1&II2+', 'X-X&0-2', 'X-X&2+', 'X-2&0-2',
            'X-2&0-3',
            'X-2&2+', 'X-2&2-3', 'X-2&2-4', 'X-2&2-5', 'X-2&2-6', 'X-2&3+', 'X-2&3-4', 'X-2&3-5', 'X-2&3-6', 'X-2&4+',
            'X-2&I2+', 'X-2&II2+', '2-1&5+', '2-2&0-2', '2-2&0-3', '2-2&2+', '2-2&2-3', '2-2&2-4', '2-2&2-5',
            '2-2&2-6',
            '2-2&3+', '2-2&3-4', '2-2&3-5', '2-2&3-6', '2-2&4+', '2-2&4-5', '2-2&4-6', '2-2&5+', '2-2&II1+',
            '2-2&I2+',
            '2-2&II2+', '2-2&G2-3', '2-2&G3+', 'X-1&2-3', '1&I1-2', '1&I1+', '1&I2+', '2&I1-2', '2&I1+', '2&I2+',
            '1&II1+', '1&II2+', '2&II1+', '2&II2+', '1&GG', '1&IGG', '1&IIGG', '2&GG', '2&IGG', '2&IIGG', '1&I<II',
            '1&I=II', '1&I>II', '2&I<II', '2&I=II', '2&I>II',
            '1X-1X', '1X-12', '1X-X2', '12-1X', '12-12', '12-X2', 'X2-1X', 'X2-12', 'X2-X2', '1X-1', '1X-X',
            '1X-2', '12-1', '12-X', '12-2', 'X2-1', 'X2-X', 'X2-2', '1-1X', '1-12', '1-X2', 'X-1X',
            'X-12', 'X-X2', '2-1X', '2-12', '2-X2',
            '1-1&NG', '1-1&GG', '1-1&IGG', '1-1&IIGG',
            'X-1&GG', 'X-2&GG', '2-2&NG', '2-2&GG', '2-2&IGG', '2-2&IIGG', '1-1&I<II', '1-1&I=II', '1-1&I>II',
            '2-2&I<II',
            '2-2&I=II', '2-2&I>II', '1-1&HP1', 'X-1&HP1', 'X-2&HP2', '2-2&HP2', '1X&0-2', '1X&0-3', '1X&2+', '1X&2-3',
            '1X&2-4', '1X&2-5', '1X&2-6', '1X&3+', '1X&3-5', '1X&3-6', '1X&4+', '1X&4-6', '1X&I1+II1+', 'X2&0-2',
            'X2&0-3', 'X2&2+', 'X2&2-3', 'X2&2-4', 'X2&2-5', 'X2&2-6', 'X2&3+', 'X2&3-5', 'X2&3-6', 'X2&4+', 'X2&4-6',
            'X2&I1+II1+', '12&3+', '12&4+', '12&2-4', '12&2-5', '12&2-6', '12&3-5', '12&3-6', '12&4-6', '12&I1+II1+',
            '12&0-2', '12&0-3', '12&2+', '12&2-3', '12&GG', '1X&GG', 'X2&GG', '12&I0-1', '12&I1-2', '12&I1+',
            '12&I2+',
            '1X&I0-1', '1X&I1-2', '1X&I1+', '1X&I2+', 'X2&I0-1', 'X2&I1-2', 'X2&I1+', 'X2&I2+', '0', '0-1', '0-2',
            '0-3',
            '1+', '2+', '3+', '4+', '1-2', '1-3', '2-3', '2-4', 'I0-1&II0-1', 'I0-1&II0-2', 'I0-2&II0-1',
            'I0-2&II0-2',
            'I1+&II1+', 'I1+&II2+', 'I2+&II1+', 'I2+&II2+', 'I1+&2+', 'I1+&3+', 'I2+&3+', '0', '0-1', '0-2', '0-3',
            '1+',
            '2+', '3+', '4+', '1-2', '1-3', '2-3', '2-4', 'I0-1&II0-1', 'I0-1&II0-2', 'I0-2&II0-1', 'I0-2&II0-2',
            'I1+&II1+', 'I1+&II2+', 'I2+&II1+', 'I2+&II2+', 'I1+&2+', 'I1+&3+', 'I2+&3+',
            ######################################################################################
            'D I 0', 'D I 0-1', 'D I 1+', 'D I 2+', 'D I 3+', 'D I 1', 'D I 1-2',
            'D II 0', 'D II 0-1', 'D II 1+', 'D II 2+', 'D II 3+', 'D II 1', 'D II 1-2',
            'G I 0', 'G I 0-1', 'G I 1+', 'G I 2+', 'G I 3+', 'G I 1', 'G I 1-2',
            'G II 0', 'G II 0-1', 'G II 1+', 'G II 2+', 'G II 3+', 'G II 1', 'G II 1-2',
            ##############################################################################
            'I>II', 'I=II', 'I<II', '1', '2', '1', '2', 'I1v1', 'IXvX', 'I2v2', '1v3+',
            'Xv3+', '2v3+', 'I2+vII2+', 'I2+v4+', 'GGv3+', 'IGGvIIGG', 'W1', 'W2', '1', 'X', '2', '1&PG1', '1&PG2',
            'X&PG1',
            'X&PG2', '2&PG1', '2&PG2', '1', '2', 'Ipol 1', 'Ipol 2', '1', '2', 'PG1&2+', 'PG1&3+', 'PG1&4+', 'PG1&GG',
            'PG1&D2+', 'PG2&2+', 'PG2&3+', 'PG2&4+', 'PG2&GG', 'PG2&G2+', '1-10', '11-20', '21-30', '31-40', '41-50',
            '51-60', '61-70', '71-80', '81-90', '1-15', '16-30', '31-45', '46-60', '61-75', '76-90', 'Nepar', 'Par',
            '1:0', '0:0', '2:0', '3:0', '4:0', '0:1', '1:1', '2:1', '3:1', '4:1', '0:2', '1:2', '2:2', '3:2', '4:2',
            '0:3', '1:3', '2:3', '3:3', '4:3', '0:4', '1:4', '2:4', '3:4', '4:4', 'Ostali', '0:0', '1:1', '2:2',
            '1:0',
            '2:0', '2:1', '0:1', '0:2', '1:2', 'Ostali', '0:0', '1:1', '2:2', '1:0', '2:0', '2:1', '0:1', '0:2',
            '1:2',
            'Ostali', '1', 'X', '2', 'ne GG3+', 'ne1&3+', 'ne 1-1',
            'I 1X', 'I 12', 'I X2', 'II 1X', 'II 12', 'II X2', ]

    index = ids.index(186)

    for i in range(6):
        ids.append(i)

    async with aiohttp.ClientSession() as session:
        match_ids = await fetch_events(session)
        print(f'Top bet: {len(match_ids)}')
        if match_ids:
            tasks = [fetch_event(session, match_id, ids) for match_id in match_ids]
            results = await asyncio.gather(*tasks)
            results = [result for result in results if result is not None]
            if results:
                df = pd.DataFrame(results)
                df.columns = head
                df['ID'] = [f'Topbet{i}' for i in range(len(df))]
                df = df.replace(0, 1.0)
                df.to_csv('/content/topbet.csv', index=False)
              
            else:
                print("No valid results to save.")
        else:
            print("No match IDs found.")


if __name__ == '__main__':
    asyncio.run(topbet())


