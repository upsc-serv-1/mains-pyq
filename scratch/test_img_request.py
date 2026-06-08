import urllib.request
import urllib.error

url = "http://localhost:8000/solved%20paper/pwonlyias/images/pw_ancient_history_and_art__culture_q936_img1.jpg"

try:
    with urllib.request.urlopen(url) as response:
        print(f"Status Code: {response.status}")
        print(f"Content Type: {response.info().get_content_type()}")
        print(f"Length: {len(response.read())}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
except Exception as e:
    print(f"Connection Error: {e}")
