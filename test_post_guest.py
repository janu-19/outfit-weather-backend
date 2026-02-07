import requests

url = 'http://127.0.0.1:8000/predict/guest'
file_path = 'reference_images/coat/coat1.avif'

with open(file_path, 'rb') as f:
    files = {'file': ('coat1.avif', f, 'image/avif')}
    try:
        r = requests.post(url, files=files)
        print('Status:', r.status_code)
        print(r.text)
    except Exception as e:
        print('Request failed:', e)
