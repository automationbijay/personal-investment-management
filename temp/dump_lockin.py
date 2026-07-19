import requests
url = "https://www.sharesansar.com/promoter-lockin"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
with open("temp/promoter.html", "w", encoding="utf-8") as f:
    f.write(response.text)
