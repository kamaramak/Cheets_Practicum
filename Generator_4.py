import requests
from bs4 import BeautifulSoup

INPUT_FILE = "links_4.txt"
OUTPUT_FILE = "4. API - интерфейс взаимодействия программ.html"
NAME = 'API - интерфейс взаимодействия программ'


def fetch_pdf_title(url):
    """Получаем заголовок PDF файла из URL или метаданных"""
    try:
        # Пробуем получить заголовок из заголовков HTTP
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.head(url, headers=headers,
                                 timeout=10, allow_redirects=True)

        # Пытаемся извлечь название из заголовка Content-Disposition
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            filename = re.findall(
                r'filename=["\']?(.*?)["\']?$', content_disposition)
            if filename:
                # Убираем расширение .pdf и декодируем URL-encoded символы
                title = filename[0].replace('.pdf', '').replace('%20', ' ')
                return title

        # Если не нашли в заголовках, берем из URL
        # Декодируем URL и убираем расширение
        title = url.split('/')[-1].replace('.pdf', '')
        title = requests.utils.unquote(title)  # Декодируем URL-encoded символы
        title = title.replace('%20', ' ')  # Заменяем %20 на пробелы

        return title

    except Exception as e:
        print(f"[!] Не удалось обработать PDF {url}: {e}")
        return url.split('/')[-1].replace('.pdf', '')


def fetch_html_title_and_text(url):
    """Получаем заголовок и текст HTML страницы"""
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


def fetch_title_and_text(url):
    """Определяем тип контента и обрабатываем соответствующим образом"""
    # Проверяем, является ли ссылка PDF
    if url.lower().endswith('.pdf') or 'pdf' in requests.head(url).headers.get('Content-Type', ''):
        print(f"📄 Обнаружен PDF: {url}")
        title = fetch_pdf_title(url)
        return title, f"PDF документ: {title}"
    else:
        # Обычная HTML страница
        return fetch_html_title_and_text(url)


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
    .pdf-link { color: #d93025; }
    .pdf-link:before { content: "📄 "; }
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
  <h1>""" + NAME + """</h1>
  <input type="text" id="searchBox" onkeyup="filterLinks()" placeholder="🔍 Поиск по содержимому страницы...">
  <ul id="linkList">
"""
    for idx, (url, title, text, is_pdf) in enumerate(links_data, start=1):
        clean_text = text.replace('"', "&quot;")
        link_class = 'pdf-link' if is_pdf else ''
        html += f'    <li data-text="{clean_text}"><strong>{idx}.</strong> <a href="{url}" target="_blank" class="{link_class}">{title}</a></li>\n'

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

        # Определяем тип ссылки
        is_pdf = link.lower().endswith('.pdf')

        if is_pdf:
            title = fetch_pdf_title(link)
            text = f"PDF документ: {title}"
        else:
            title, text = fetch_html_title_and_text(link)

        links_data.append((link, title, text, is_pdf))

    html = generate_html(links_data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Готово! Открывай файл: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
