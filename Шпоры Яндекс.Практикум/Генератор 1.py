import requests
from bs4 import BeautifulSoup
import time

INPUT_FILE = "links 1.txt"
OUTPUT_FILE = "1. Основы_Углубленный Python.html"


def fetch_title_and_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string.strip() if soup.title else url

        # Убираем скрипты, стили и нечитабельное
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        visible_text = soup.get_text(separator=' ', strip=True)
        # Ограничим текст для производительности
        visible_text = " ".join(visible_text.split()[:1000])
        return title, visible_text
    except Exception as e:
        print(f"[!] Не удалось обработать {url}: {e}")
        return url, ""


def generate_html(links_data):
    html = """
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Мои шпаргалки</title>
  <style>
    body { font-family: sans-serif; background: #f9f9f9; padding: 40px; max-width: 800px; margin: auto; }
    h1 { text-align: center; }
    #searchBox { width: 100%; padding: 10px; font-size: 16px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 5px; }
    ul { list-style: none; padding: 0; }
    li { margin: 15px 0; }
    a { text-decoration: none; color: #3366cc; font-weight: bold; }
    a:hover { text-decoration: underline; }
  </style>
  <script>
    function filterLinks() {
      var input = document.getElementById("searchBox");
      var filter = input.value.toLowerCase();
      var ul = document.getElementById("linkList");
      var li = ul.getElementsByTagName("li");

      for (var i = 0; i < li.length; i++) {
        var a = li[i].getElementsByTagName("a")[0];
        var data = li[i].getAttribute("data-text").toLowerCase();
        var title = a.textContent.toLowerCase();

        if (title.includes(filter) || data.includes(filter)) {
          li[i].style.display = "";
        } else {
          li[i].style.display = "none";
        }
      }
    }
  </script>
</head>
<body>
  <h1>🧠 Мои шпаргалки</h1>
  <h1>Основы_Углубленный Python</h1>
  <input type="text" id="searchBox" onkeyup="filterLinks()" placeholder="🔍 Поиск по содержимому страницы...">
  <ul id="linkList">
"""
    for idx, (url, title, text) in enumerate(links_data, start=1):
        clean_text = text.replace('"', "&quot;")
        html += f'    <li data-text="{clean_text}"><strong>{idx}.</strong> <a href="{url}" target="_blank">{title}</a></li>\n'

    html += """  </ul>
</body>
</html>
"""
    return html


def main():
    links = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if url:
                links.append(url)

    links_data = []
    for i, link in enumerate(links, 1):
        print(f"[{i}/{len(links)}] Обработка: {link}")
        title, text = fetch_title_and_text(link)
        links_data.append((link, title, text))
        time.sleep(0.5)

    html = generate_html(links_data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Готово! Открывай файл: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
