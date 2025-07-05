
import aiohttp
import asyncio
from datetime import datetime
import pandas as pd
from pytz import timezone
from datetime import timedelta


async def fetch_event(session, match_id, ids):
    if match_id:

        try:
            base_url = 'https://sports-sm-distribution-api.de-2.nsoftcdn.com/api/v1/events/'
            params = {
                'companyUuid': '4f54c6aa-82a9-475d-bf0e-dc02ded89225',
                'id': match_id,
                'language': '{"default":"sr-Latn","events":"sr-Latn","sport":"sr-Latn","category":"sr-Latn","tournament":"sr-Latn","team":"sr-Latn","market":"sr-Latn"}',
                'timezone': 'Europe/Belgrade',
                'dataFormat': '{"default":"array","markets":"array","events":"array"}'
            }
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'sr-RS,sr;q=0.9,en-US;q=0.8,en;q=0.7,bs;q=0.6,hr;q=0.5,ru;q=0.4,zh-CN;q=0.3,zh;q=0.2',
                'If-None-Match': 'W/"212ce-bQW7cB3AhhqdBzQIbPRCdA"',
                'Origin': 'https://sports-sm-web.7platform.net',
                'Priority': 'u=1, i',
                'Referer': 'https://sports-sm-web.7platform.net/',
                'Sec-Ch-Ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Linux"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
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
            print(f"Topbet {match_id}: {e}")
            return None


async def fetch_events(session):
    sada = datetime.now()
    formatirani_datum_vreme = sada.strftime('%Y-%m-%dT%H:%M:%S')
    url = 'https://sports-sm-distribution-api.de-2.nsoftcdn.com/api/v1/events'
    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    params = {
        'deliveryPlatformId': '3',
        'dataFormat': '{"default":"object","events":"array","outcomes":"array"}',
        'language': '{"default":"sr-Latn","events":"sr-Latn","sport":"sr-Latn","category":"sr-Latn","tournament":"sr-Latn","team":"sr-Latn","market":"sr-Latn"}',
        'timezone': 'Europe/Belgrade',
        'company': '{}',
        'companyUuid': '4f54c6aa-82a9-475d-bf0e-dc02ded89225',
        'filter[sportId]': '18',
        'filter[from]': current_time,
        'sort': 'categoryPosition,categoryName,tournamentPosition,tournamentName,startsAt',
        'offerTemplate': 'WEB_OVERVIEW',
        'shortProps': '1'
    }
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'sr-RS,sr;q=0.9,en-US;q=0.8,en;q=0.7,bs;q=0.6,hr;q=0.5,ru;q=0.4,zh-CN;q=0.3,zh;q=0.2',
        'Origin': 'https://sports-sm-web.7platform.net',
        'Priority': 'u=1, i',
        'Referer': 'https://sports-sm-web.7platform.net/',
        'Sec-Ch-Ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Linux"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    async with session.get(url, headers=headers, params=params) as response:
        if response.status != 200:
            print(f"Error fetching events: Status code {response.status}")
            return []
        data = await response.json()
        events = data['data']['events']
        return [event['a'] for event in events]


async def balkan():
    ids = [6, 9, 12, 1004, 1007, 1013, 1016, 1019, 1022, 1031, 1034, 1037, 1040, 1043, 1046, 1058, 1061, 1064, 1067,
           1070, 1073, 1076, 1079, 1082, 1085, 1088, 1091, 1094, 1097, 1100, 1103, 1106, 1109, 1112, 1115, 1127, 1130,
           1133, 1136, 1139, 1142, 1145, 1148, 1151, 1154, 1157, 1160, 1163, 1166, 1169, 1172, 1175, 1178, 1181, 1184,
           1187, 1190, 1193, 1196, 1199, 1202, 1205, 1208, 1211, 1214, 1217, 1220, 1223, 1226, 1229, 1232, 1235, 1238,
           1241, 1244, 1247, 1250, 1253, 1256, 1259, 1262, 1265, 1268, 1271, 1274, 1277, 1280, 1283, 1286, 1289, 1292,
           1295, 1298, 1301, 1304, 1307, 1310, 1313, 1316, 1319, 1322, 1325, 1328, 1331, 1334, 1337, 1340, 1343, 1346,
           1349, 1352, 1355, 1358, 1361, 1364, 1367, 1370, 1373, 1376, 1379, 1382, 1385, 1388, 1391, 1394, 1397, 1400,
           1403, 1406, 1409, 1412, 1415, 1418, 1421, 1424, 1427, 1430, 1433, 1436, 1439, 1442, 1445, 1448, 1451, 1454,
           1457, 1460, 1463, 1466, 1544, 1547, 1550, 1553, 1556, 1559, 1562, 1565, 1568, 1571, 1574, 1577, 1580, 1583,
           1586, 1589, 1592, 1595, 1598, 1601, 1604, 1607, 1613, 1616, 1619, 1622, 1625, 1628, 1631, 1634, 1637, 1640,
           1643, 1646, 1652, 1655, 1658, 1661, 1664, 1667, 1670, 1673, 1676, 1679, 1682, 1685, 1688, 1691, 1694, 1697,
           1700, 1703, 1706, 1709, 1712, 1715, 1718, 1721, 1724, 1727, 1730, 1733, 1736, 1739, 1742, 1745, 1748, 1751,
           1754, 1757, 1760, 1763, 1766, 1769, 1772, 1775, 1778, 1781, 1784, 1787, 1790, 1793, 1796, 1799, 1802, 1805,
           1808, 1811, 1814, 1817, 1820, 1823, 1826, 1829, 1832, 1835, 1838, 1841, 1844, 1847, 1853, 1856, 1859, 1862,
           1865, 1868, 1871, 1874, 1877, 1880, 1886, 1889, 1892, 1895, 1898, 1901, 1904, 1907, 1910, 1913, 1916, 1922,
           1925, 1928, 1931, 1934, 1937, 1940, 1943, 1946, 1949, 1952, 1955, 1958, 1961, 1964, 1967, 1970, 1973, 1976,
           1979, 1982, 1985, 1988, 1991, 1994, 1997, 2000, 2003, 2006, 2009, 2012, 2015, 2018, 2021, 2024, 2027, 2030,
           2033, 2036, 2039, 2042, 2045, 2048, 2051, 2054, 2057, 2060, 2063, 2066, 2069, 2072, 2075, 2078, 2081, 2453,
           2456, 2459, 2462, 2465, 2480, 2483, 2489, 2492, 2495, 2498, 2501, 2504, 2507, 2510, 2534, 2537, 2540, 2543,
           2546, 2549, 2552, 2555, 2558, 2561, 2564, 2567, 2570, 2573, 2576, 2579, 2582, 2585, 2588, 2591, 2594, 2597,
           2600, 2603, 2606, 2627, 2630, 2633, 2636, 2639, 2642, 2645, 2648, 2651, 2654, 2657, 2675, 2678, 2681, 2684,
           2687, 2690, 2693, 2696, 2858, 2861, 2864, 2867, 2870, 4829, 4832, 4835, 5525, 5528, 5531, 5534, 5537, 5540,
           5543, 5546, 5549, 5552, 5555, 5558, 5561, 7319, 7322, 7325, 7328, 7331, 7334, 7337, 7340, 7343, 7346, 7349,
           7352, 7355, 7358, 7361, 7364, 7367, 7370, 7373, 7379, 7382, 7385, 7388, 7391, 7394, 7397, 7400, 7403, 7406,
           7409, 7412, 7415, 7418, 7421, 7424, 7427, 7430, 7433, 7436, 7439, 7442, 7445, 7448, 7451, 7454, 7466, 7469,
           7472, 7475, 7478, 7481, 7484, 7487, 7490, 7493, 7496, 7499, 7511, 7514, 7517, 7520, 7523, 7526, 7529, 7532,
           7535, 7538, 7541, 7544, 7547, 7550, 7553, 7556, 7559, 7562, 7565, 7568, 7571, 7580, 7586, 7589, 7592, 7595,
           7598, 7601, 7604, 7607, 7610, 7613, 7616, 7619, 7622, 7625, 7628, 7631, 7634, 7637, 7640, 7643, 7646, 7658,
           7661, 7664, 7667, 7670, 7673, 7676, 7679, 7682, 7685, 7688, 7691, 7694, 7697, 7700, 7703, 7706, 7709, 7712,
           7715, 7718, 7721, 7724, 7727, 7730, 7733, 7736, 7739, 7742, 7745, 7748, 7751, 7754, 7856, 7859, 7862, 7865,
           7868, 7871, 7874, 7877, 7880, 7883, 8075, 8078, 8084, 8088, 8090, 9427, 9430, 9433, 9436, 9439, 9442, 9445,
           9840, 9843, 9846, 9849, 9852, 9855, 9858, 9861, 9864, 9867, 9870, 9873, 9993, 9996, 9999, 10002, 10005,
           10008, 10011, 10014, 10017, 10020, 10023, 10026, 10029, 10032, 10035, 10038, 10041, 10044, 10047, 10050,
           10053, 10056, 10059, 10062, 10065, 10068, 10071, 10074, 10077, 10080, 10083, 10086, 10089, 10092, 10095,
           10098, 10101, 10104, 10107, 10110, 10113, 10116, 10119, 10122, 10125, 10128, 10131, 10134, 10137, 10140,
           10374, 10377, 10380, 10383, 10386, 10389, 10392, 10395, 10398, 10401, 10404, 10407, 10440, 10443, 10446,
           10551, 10554, 10557, 10560, 10563, 10566, 10569, 10572, 10575, 10578, 10581, 10584, 10587, 10590, 10593,
           10596, 10599, 10602, 10605, 10608, 10611, 10617, 10620, 10623, 10626, 10629, 10632, 10635, 10638, 10665,
           10668, 10671, 10674, 10677, 10680, 10683, 10686, 10689, -1, -2]
    head = ['ID', 'vreme', 'domaci', 'gosti', '1', 'X', '2', '1X', '12', 'X2',
            'I 1', 'I X', 'I 2', 'I 1X', 'I 12',
            'I X2', 'II 1', 'II X', 'II 2', 'W1', 'W2', 'DUPLAP1', 'DUPLAP2',
            'SP1', 'SP2', '1-1', '1-X', '1-2', 'X-1', 'X-X',
            'X-2', '2-1', '2-X', '2-2', 'ne 1-1', 'ne 2-2', 'I 1v1', 'I XvX',
            'I 2v2', 'D I 0', 'D I 1+', 'D I 2+',
            'D II 0', 'D II 1+', 'D II 2+', 'G I 0', 'G I 1+', 'G I 2+', 'G II 0',
            'G II 1+', 'G II 2+', 'D 0', 'D 1+',
            'D 0-1',
            'D 2+', 'D 3+', 'DI1+&DII1+', 'G 0', 'G 1+', 'G 0-1', 'G 2+', 'G3+',
            'GI1+&GII1+', 'I GG', 'II GG', 'GG', 'NG',
            'IGG&II GG', 'IGG&II NG', 'I NG&II GG', 'IGGvII GG', 'NE I GG', 'NE II GG',
            'GG&D2+', 'GG&G2+', 'D2+&G2+',
            'GG3+', 'GG&4+', 'I 0', 'I 0-1', 'I 1+', 'I 1 gol', 'I 1-2', 'I 2+',
            'I 2 gol.', 'I 2-3', 'I 3+', 'I 4+',
            'II 0', 'II 0-1', 'II 1+', 'II 1 gol', 'II 1-2', 'II 2+', 'II 2 gol.',
            'II 2-3', 'II 3+', 'II 4+',
            'I1+&II1+', 'I1+&II2+', 'I2+&II1+', 'I2+&II2+', 'NE(I1+&II1+)',
            'NE(I1+&II2+)', 'NE(I2+&II1+)',
            'I0-1&II0-1', 'I0-1&II0-2', 'I0-2&II0-1', 'I0-2&II0-2',
            'I1+&2+', 'I1+&3+', 'I2+&4+', 'I2+ vII2+',
            'I2+ v4+', 'I >', 'I = II', 'II >', 'ug 0-1', 'ug 0-2',
            '1 gol', '2 gol.', 'ug 2+', 'ug 2-5',
            'ug 2-4', 'ug 2-3', 'ug 0-3',
            'ug 0-4', 'ug 1-2', 'ug 1-3', 'ug 1-4', 'ug 1-5', 'ug 1-6',
            '3 gol.', '4 gol.', '5 gol.',
            'ug 3+', 'ug 3-4', 'ug 3-5', 'ug 3-6', 'ug 4+',
            'ug 4-5', 'ug 4-6', 'ug 5+', 'ug 6+', 'ug 7+', 'NE 1-2', 'NE 1-3',
            'NE 2-3', 'NE 2-4', 'NE 2-5', 'NE 3-4', 'NE 3-5',
            'NE 4-6', '1&I1+', '1&I2+', '1&I2-3', '2&I1+', '2&I2+', '2&I2-3', '1&II1+',
            '1&II2+', '2&II1+', '2&II2+',
            '1&0-2', '1&0-3', '1&2+', '1&3+', '1&4+', '1&2-3', '1&2-4', '1&2-5', '1&3-4',
            '1&3-5', '1&4-6', '1&5+',
            '2&0-2', '2&0-3', '2&2+', '2&3+', '2&4+', '2&2-3', '2&2-4', '2&2-5', '2&3-4',
            '2&3-5', '2&4-6', '2&5+',
            '1v3+', '2v3+', '1v4+', '2v4+', 'I 1 &1X', 'I 1 &12', 'I 1 &X2', 'I X &1X',
            'I X &12', 'I X &X2', 'I 2 &1X',
            'I 2 &12', 'I 2 &X2', 'I 1X&1', 'I 1X&X', 'I 1X&2', 'I 12&1', 'I 12&X',
            'I 12&2', 'I X2&1', 'I X2&X',
            'I X2&2', 'I 1X&1X', 'I 1X&12', 'I 1X&X2', 'I 12&1X', 'I 12&12', 'I 12&X2',
            'I X2&1X', 'I X2&12', 'I X2&X2',
            '1X&I1+', '1X&I2+', '1X&I2-3', '12&I1+', '12&I2+', '12&I2-3', 'X2&I1+',
            'X2&I2+', 'X2&I2-3', '1X&II1+',
            '1X&II2+', '12&II1+', '12&II2+', 'X2&II1+', 'X2&II2+', '1X& I >',
            '1X& I = II', '1X& II >', 'X2& I >',
            'X2& I = II', 'X2& II >', '12& I >', '12& I = II', '12& II >', '1X&2+',
            '1X&3+', '1X&0-2', '1X&0-3',
            '1X&2-3', '1X&2-4', '1X&2-5', '1X&3-4', '1X&3-5', '1X&4+', '1X&4-6', '12&2+',
            '12&3+', '12&0-2', '12&0-3',
            '12&2-4', '12&2-5', '12&3-4', '12&3-5', '12&4+', '12&4-6', 'X2&2+', 'X2&3+',
            'X2&0-2', 'X2&0-3', 'X2&2-3',
            'X2&2-4', 'X2&2-5', 'X2&3-4', 'X2&3-5', 'X2&4+', 'X2&4-6', '1-1&I2+', 'X-1&I2+',
            '2-2&I2+', 'X-2&I2+',
            '1-1&II2+', 'X-1&II2+', '2-2&II2+', 'X-2&II2+', '1-1&0-2', '1-1&0-3', '1-1&2+',
            '1-1&2-3', '1-1&2-4',
            '1-1&2-5', '1-1&3+', '1-1&3-4', '1-1&3-5', '1-1&4+', 'X-1&0-2', 'X-1&0-3',
            'X-1&2+', 'X-1&2-3', 'X-1&2-4',
            'X-1&2-5', 'X-1&3+', 'X-1&3-4', 'X-1&3-5', 'X-1&4+', '2-2&0-2', '2-2&0-3',
            '2-2&2+', '2-2&2-3', '2-2&2-4',
            '2-2&2-5', '2-2&3+', '2-2&3-4', '2-2&3-5', '2-2&4+', 'X-2&0-2', 'X-2&0-3',
            'X-2&2+', 'X-2&2-3', 'X-2&2-4',
            'X-2&2-5', 'X-2&3+', 'X-2&3-4', 'X-2&3-5', 'X-2&4+', '1& I >', '1& I = II',
            '1& II >', '2& I >',
            '2& I = II', '2& II >', 'POG 1', 'POG Niko', 'POG 2', 'Nepar', 'Par',
            'I Nepar', 'I Par', '1:1', '2:2',
            '1:0', '2:0', '2:1', '0:1', '0:2', '1:2', '0:0', '1:0', '2:0', '3:0', '4:0', '0:1', '1:1', '2:1', '3:1',
            '4:1', '0:2', '1:2', '2:2', '3:2', '4:2', '0:3', '1:3', '2:3', '3:3', '4:3', '0:4', '1:4', '2:4', '3:4',
            '4:4', 'II Nepar', 'II Par', '0:0', '0:1', '0:2', '1:0', '1:1', '1:2', '2:0', '2:1', '2:2',
            '1:0, 2:0 ili 3:0', '0:1, 0:2 ili 0:3', '4:0, 5:0 ili 6:0', '0:4, 0:5 ili 0:6', '2:1, 3:1 ili 4:1',
            '1:2, 1:3 ili 1:4', '3:2, 4:2, 4:3 ili 5:1', '2:3, 2:4, 3:4 ili 1:5',
            'AH1', 'AH2', 'EH1', 'EHX', 'EH2',
            'P10M 1', 'P10M X', 'P10M 2', 'PDG 1 I', 'PDG Niko I', 'PDG 2 I', 'PDG 1',
            'PDG Niko', 'PDG 2', 'PDG1 & 1',
            'PDG1 & X', 'PDG1 & 2', 'PDG2 & 1', 'PDG2 & X', 'PDG2 & 2', 'Nema gola',
            '1&I GG', 'X&I GG', '2&I GG',
            '1&II GG', 'X&II GG', '2&II GG', '1&I NG', 'X&I NG', '2&I NG', '1&II NG',
            'X&II NG', '2&II NG', 'I 1 &I GG',
            'I X &I GG', 'I 2 &I GG', 'I 1 &II GG', 'I X &II GG', 'I 2 &II GG',
            'I 1 &I NG', 'I 2 &I NG', 'I 1 &II NG',
            'I X &II NG', 'I 2 &II NG', '1X&I GG', '12&I GG', 'X2&I GG', '1X&II GG',
            '12&II GG', 'X2&II GG', '1X&I NG',
            '12&I NG', 'X2&I NG', '1X&II NG', '12&II NG', 'X2&II NG', 'D0-2', 'D1-2', 'D1-3', 'D2-3', 'D4+', 'D1g.',
            'D2g.', 'DI1+&DII2+', 'DI2+&DII1+', 'DI2+&DII2+', 'DI1+&D2+', 'DI1+&D3+', 'G0-2', 'G1-2', 'G1-3', 'G2-3',
            'G4+', 'G1g.', 'G2g.', 'GI1+&GII2+', 'GI2+&GII1+', 'GI2+&GII2+', 'GI1+&G2+', 'GI1+&G3+', 'DI 1g.', 'DI 3+',
            'D I 0-1', 'D I 1-2', 'DII 1g.', 'D II 0-1', 'D II 1-2', 'D II 3+', 'GI 1g.',
            'G I 0-1', 'G I 1-2', 'G I 3+',
            'G II 1g.', 'G II 0-1', 'G II 1-2', 'G II 3+', 'GG&D3+', 'GG&G3+', 'GG&2-3', 'GG v3+', 'D3+ vG3+', '1&D3+',
            '2&G3+', 'NE 1&2+', 'NE 2&2+', 'NE 1&3+', 'NE 2&3+', 'I1+&II3+', 'I2+&II3+', 'I1+&II2-3', 'I2+&II2-3',
            'I2-3&II1+', 'I2-3&II2-3', 'I2-3&4+', 'I2-3 vII2-3', 'I3+ vII3+', 'NE X-1', 'NE X-2', 'NE X-X', 'Xv3+',
            'Xv4+', '1v I2+', 'Xv I2+', '2v I2+', '1-1&GG', '2-2&GG', '1-1&NG', '2-2&NG', 'X-1&GG', 'X-2&GG', 'X-1&NG',
            'X-2&NG', '1-1v IGG', '2-2v IGG', '1-1v IIGG', '2-2v IIGG', '1-1v GG4+', '2-2v GG4+', 'X-1v GG4+',
            'X-2v GG4+', 'X-1v IGG', 'X-2v IGG', 'X-1v IIGG', 'X-2v IIGG', '1-1v I2+', '2-2v I2+', '1-1v II2+',
            '2-2v II2+', 'X-1v I2+', 'X-2v I2+', 'X-1v II2+', 'X-2v II2+', 'X-Xv IGG', 'X-Xv IIGG', '1-10', '11-20',
            '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', 'Nema gola', '1&GG', '2&GG', '1X&GG',
            '12&GG', 'X2&GG', '1-15', '16-30', '31-45', '46-60', '61-75', '76-90', 'Nema gola', 'I 0-2', 'I 1-3',
            'I 3 gol.', 'II 0-2', 'II 1-3', 'II 3 gol.', 'I0-2&II0-3', 'I1-2&II1-2', 'I1-3&II1-3', 'I1-2&3+', 'I1-2&4+',
            'I2+&3+', '1-15 0 gol.', '1-15 1 gol.', '1-15 1+', '1-15 2+', '1-30 0 gol.', '1-30 0-1', '1-30 1 gol.',
            '1-30 1+', '1-30 2+', '0&1+', '0&2+', '1+&0', '1+&1+', '1+&2+', '0&1+', '1+&0', '1+&1+', '2+&0', '2+&1+',
            '0g&II 1+', '0g&II 0-1', '0g&II 2+', '1+&II 1+', '1+&II 0-1', '1+&II 2+', '0g&II 0-1', '0g&II 1+',
            '0g&II 1-2', '0g&II 2+', '0g&II 2-3', '0-1&II 0-1', '0-1&II 1+', '0-1&II 1-2', '0-1&II 2+', '0-1&II 2-3',
            '1g&II 0-1', '1g&II 1+', '1g&II 1-2', '1g&II 2+', '1g&II 2-3', '1+&II 0-1', '1+&II 1+', '1+&II 1-2',
            '1+&II 2+', '1+&II 2-3', '2+&II 0-1', '2+&II 1+', '2+&II 1-2', '2+&II 2+', '2+&II 2-3', '1&(I1+&II1+)',
            '2&(I1+&II1+)', '1&(I1+&2+)', '2&(I1+&2+)', '1&(I1+&3+)', '2&(I1+&3+)', '1X&(I1+&II1+)', '12&(I1+&II1+)',
            'X2&(I1+&II1+)', '1X&(I1+&2+)', '12&(I1+&2+)', 'X2&(I1+&2+)', '1X&(I1+&3+)', '12&(I1+&3+)', 'X2&(I1+&3+)',
            'I0-1&II1+', 'I0-1&II2+', 'I0-1&II1-2', 'I0-1&II1-3', 'I0-1&II0-3', 'I0-1&II2-3', 'I1+&II0-1', 'I1+&II0-2',
            'I1+&II1-2', 'I1+&II1-3', 'I1-2&II1+', 'I1-2&II1-3', 'I1-2&II2+', 'I1-2&II2-3', 'I1-2&II0-1', 'I1-2&II0-2',
            'I1-2&II0-3', 'I1-3&II1-2', 'I1-3&II1+', 'I1-3&II2+', 'I1-3&3+', 'I0-2&II1-3', 'I0-2&II1-2', 'I0-2&II2-3',
            'I0-2&II2+', 'I2-3&II0-2', 'I2-3&II0-1', 'I2-3&II1-2', 'I2-3&II1-3', 'GG&I1+', 'GG&I2+', 'GG&II1+',
            'GG&II2+', 'GG&I1+II1+', 'IGG&3+', 'IGG&4+', 'IIGG&3+', 'IIGG&4+',
            'ne1&3+', 'ne GG3+']
    l = ['I NG', 'X-X2', 'II NG', '2-1X', 'X2-12', 'X2-X2', 'X2-1', '1X-X2', '12-12', 'X-12', '12-2', '2-12', '1X-2',
         '1-12', 'II 1X', 'X2-2', '1X-X', 'X2-X', 'II X2', '1X-1', '1-1X', '12-X2', '1-X2', '12-1X', 'X-1X', '2-X2',
         '1X-12', 'II 12', '1X-1X', '12-1', 'X2-1X', '12-X']
    head = head + l
    j = -3
    for i in range(32):
        ids.append(j)
        j = j - 1
    async with aiohttp.ClientSession() as session:
        match_ids = await fetch_events(session)
        print(f'Balkan bet: {len(match_ids)}')
        if match_ids:
            tasks = [fetch_event(session, match_id, ids) for match_id in match_ids]
            results = await asyncio.gather(*tasks)
            results = [result for result in results if result is not None]
            if results:
                df = pd.DataFrame(results)
                df.columns = head
                df = df.replace(0, 1.0)
                df['ID'] = [f'Balkan{i}' for i in range(len(df))]
                df.to_csv('/content/balkan.csv', index=False)
            else:
                print("No valid results to save.")
        else:
            print("No match IDs found.")


if __name__ == '__main__':
    asyncio.run(balkan())

