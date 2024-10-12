import requests
from htmldate import find_date
if __name__ == "__main__":
    html_content = requests.get("https://dxy.com/article/103873").text
    date = find_date(htmlobject=html_content)
    print(date)
