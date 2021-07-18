import requests
from bs4 import BeautifulSoup
from telethon.sync import TelegramClient

from h import ID, HASH, TOKEN


LINK = "https://www.creationwatches.com/products/orient-watches-252/orient-star-classic-automatic-power-reserve-saf02003w0-mens-watch-10652.html"
LIMIT = 310.0

# LINK = "https://www.creationwatches.com/products/seiko-automatic-sports-89/seiko-automatic-sports-snzg15-snzg15j1-snzg15j-mens-watch-2222.html"
# LIMIT = 150.0

# LINK = "https://www.creationwatches.com/products/hamilton-watches-250/hamilton-american-classic-boulton-mechanical-h13519711-mens-watch-20624.html"
# LIMIT = 600.0


def full(url):
    if url.startswith("https://www.creationwatches.com/products/"):
        return url
    elif url.startswith("/products"):
        return "https://www.creationwatches.com" + url
    else:
        return "https://www.creationwatches.com/products/" + url


def web1(url):
    code = requests.get(url)
    plain = code.text
    s = BeautifulSoup(plain, "html.parser")

    r = False, "", 0

    a = s.find('a', {'class': 'stock'})
    if a.get_text().find('In Stock'):
        n = s.find('p', {'class': 'para8'})
        name = n.get_text().split(': ')[1]
        for p in s.findAll('p', {'class': 'product-price1'}):
            price = p.get_text()
            if price.startswith('Price: US $'):
                r = True, name, float(price.split('$')[1])

    return r


def web2(url, model):
    code = requests.get(url)
    plain = code.text
    s = BeautifulSoup(plain, "html.parser")

    codes = []
    links = []
    models = []

    for p in s.findAll('div', {'class': 'brand-desc'}):
        t = p.get_text()
        if t not in codes:
            codes.append(t)
    for h in s.findAll('a', {'class': 'buy-btn'}):
        t = full(h.get('href'))
        if t not in links:
            links.append(t)
            for m in web3(t):
                models.append(m)

    if model in models:
        return True, tuple(codes), len(models)
    else:
        return False, tuple(codes), len(models)


def web3(url):
    code = requests.get(url)
    plain = code.text
    s = BeautifulSoup(plain, "html.parser")

    models = []
    links = []

    for m in web4(url):
        models.append(m)

    for n in s.findAll('a'):
        w = n.get('href')
        if w is not None and w.startswith('https') and w.find('index-') > 0 and w not in links:
            links.append(w)
            for m in web4(w):
                models.append(m)

    return tuple(models)


def web4(url):
    code = requests.get(url)
    plain = code.text
    s = BeautifulSoup(plain, "html.parser")

    models = []

    for p in s.findAll('p', {'class': 'product-model-no'}):
        t = p.get_text().split(': ')[1]
        if t not in models:
            models.append(t)

    return tuple(models)


w1 = web1(LINK + "?currency=USD")
if w1[0]:
    message = f"Cena zegarka {w1[1]} wynosi {w1[2]} USD. Oczekiwana cena to {LIMIT} USD.\n\n"

w2 = web2("https://www.creationwatches.com/products/index.php?main_page=sale_offer", w1[1])
if w2[0]:
    message = message + f"Zegarek {w1[1]} jest wsród kodów\n\n"
else:
    message = message + f"Zegarka {w1[1]} nie ma wsród kodów\n\n"
message = message + f"W promocji jest {w2[2]} zegarków. Kody:\n"
for i in w2[1]:
    message = message + f"\t{i.split(' ')[3]} na {i.split(' ')[12].strip('.')}\n"

print(message)
if w1[2] < LIMIT or w2[0]:
    client = TelegramClient('session', ID, HASH)
    client.connect()
    if not client.is_user_authorized():
        client.start(bot_token=TOKEN)
    client.send_message('aklimek', message)
    client.disconnect()
