import requests

url = 'https://ftp.cdc.gov/pub/health_statistics/nchs/nhanes/continuousnhanes/1999-2000/DBQ.XPT'
print(f"Testing URL: {url}")

try:
    r = requests.get(url, timeout=10)
    print(f'Status: {r.status_code}')
    print(f'Content-Type: {r.headers.get("content-type", "unknown")}')
    print(f'Length: {len(r.content)}')

    if 'text/html' in r.headers.get('content-type', ''):
        print('HTML content detected')
        print(f'First 200 chars: {r.text[:200]}')
    else:
        print('Binary content (likely XPT file)')
        # Check for XPT signature
        if len(r.content) > 10:
            first_bytes = r.content[:10]
            print(f'First 10 bytes: {first_bytes}')
            if b'SAS' in first_bytes or b'XPORT' in first_bytes:
                print('XPT file signature detected!')
            else:
                print('No XPT signature found')
except Exception as e:
    print(f'Error: {e}')