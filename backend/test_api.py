"""Quick test of /forecast and /risk endpoints to verify integration."""
import requests
import json

# Assume server is running at http://127.0.0.1:8000
BASE_URL = 'http://127.0.0.1:8000'

def test_endpoints():
    csv_file = 'demo_sales.csv'
    
    # Test /forecast endpoint
    print('Testing /forecast endpoint...')
    with open(csv_file, 'rb') as f:
        files = {'file': f}
        resp = requests.post(f'{BASE_URL}/forecast', files=files)
    
    if resp.status_code == 200:
        data = resp.json()
        print('✅ /forecast success')
        print(f"  Predictions: {data.get('predictions')}")
        print(f"  Risk: {data.get('risk')}")
        print(f"  Volatility: {data.get('volatility_percent')}%")
        print(f"  Insight (first 100 chars): {str(data.get('insight'))[:100]}...")
    else:
        print(f'❌ /forecast failed: {resp.status_code}')
        print(f"  {resp.text}")
    
    # Test /risk endpoint
    print('\nTesting /risk endpoint...')
    with open(csv_file, 'rb') as f:
        files = {'file': f}
        resp = requests.post(f'{BASE_URL}/risk', files=files)
    
    if resp.status_code == 200:
        data = resp.json()
        print('✅ /risk success')
        print(f"  Risk: {data.get('risk')}")
    else:
        print(f'❌ /risk failed: {resp.status_code}')
        print(f"  {resp.text}")

if __name__ == '__main__':
    test_endpoints()
