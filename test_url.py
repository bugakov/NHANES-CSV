import requests

# Test different URL patterns for NHANES data
test_urls = [
    "https://ftp.cdc.gov/pub/health_statistics/nchs/nhanes/continuousnhanes/1999-2000/DBQ.XPT",
    "https://www.cdc.gov/nchs/nhanes/data/continuousnhanes/1999-2000/DBQ.XPT",
    "https://wwwn.cdc.gov/nchs/nhanes/data/continuousnhanes/1999-2000/DBQ.XPT",
    "https://wwwn.cdc.gov/Nchs/Nhanes/1999-2000/DBQ.XPT",
    "https://ftp.cdc.gov/pub/health_statistics/nchs/nhanes/1999-2000/DBQ/DBQ.XPT",
    "https://ftp.cdc.gov/pub/health_statistics/nchs/nhanes/1999-2000/DBQ.XPT",
    "https://wwwn.cdc.gov/Nchs/Data/Nhanes/1999-2000/DBQ.XPT",
    "https://wwwn.cdc.gov/nchs/nhanes/1999-2000/DBQ.XPT",
    "https://wwwn.cdc.gov/nchs/data/nhanes/1999-2000/DBQ.XPT",
    "https://ftp.cdc.gov/pub/health_statistics/nchs/nhanes/1999-2000/DBQ.XPT",
    "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/1999/DBQ.XPT",
    "https://ftp.cdc.gov/pub/health_statistics/nchs/datasets/nhanes/1999-2000/DBQ.XPT",
    "https://nhanes.ipums.org/nhanes/data/1999/DBQ.XPT",
    "https://data.cdc.gov/api/views/XXXXXXX/rows.csv"  # Need correct dataset ID
]

for url in test_urls:
    try:
        response = requests.get(url, timeout=10)
        print(f"{url}: {response.status_code}")
        if response.status_code == 200:
            print(f"  Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"  Content-Length: {response.headers.get('content-length', 'unknown')}")
            if 'text/html' in response.headers.get('content-type', ''):
                print(f"  Content: {response.text[:200]}...")
            else:
                print("  Binary content (likely XPT file)")
        print()
    except Exception as e:
        print(f"{url}: Error - {e}")
        print()