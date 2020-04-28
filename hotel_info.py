import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse
import re
import pickle
import pprint


def main():
    urls = urls_get()
    scrape(urls)


def urls_get():
    base_urls = [
        'https://www.booking.com/hotel/jp/grand-base-hakata-haruyoshi.ja.html',
        'https://www.booking.com/hotel/jp/grand-base-tenjin.ja.html',
        'https://www.booking.com/hotel/jp/smart-hakata.ja.html',
        'https://www.booking.com/hotel/jp/apartment-tenjin-tumugu.ja.html',
        'https://www.booking.com/hotel/jp/dream-inn-hakata.ja.html',
        'https://www.booking.com/hotel/jp/mei-fukuoka-tenjin.ja.html',
        'https://www.booking.com/hotel/jp/a-good-day-fukuoka-riverside.ja.html'
    ]

    return base_urls


def scrape(urls):
    head = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"}
    hotel_pk = []
    for url in urls:
        hotel_pk_tmp = {}
        print(url)
        r = requests.get(url, headers=head)
        soup = BeautifulSoup(r.text, 'lxml')
        name = soup.find('h2', id='hp_hotel_name').strings  # hotel name
        name = list(name)[2].replace('\n', '')
        print(name)
        ###############################################
        rooms = []
        roomTypeTds = soup.find('table', class_='roomstable').find(
            'tbody').find_all('td', class_='roomType')

        for td in roomTypeTds:
            room = {}
            room_id = td.find('div')['id']
            room_name = td.find('div').find('a').text.replace(
                '\n', '').replace('\u3000', ' ')
            room['id'] = room_id
            room['name'] = room_name
            # room['person'] = 0
            rooms.append(room)

        save_dir = url.split('/')[-1].split('.')[0] # urlの一部を保存ディレクトリ名にする
        
        # 保存
        hotel_pk_tmp['name'] = name
        hotel_pk_tmp['save_dir'] = save_dir
        hotel_pk_tmp['url'] = url
        hotel_pk_tmp['rooms'] = rooms
        hotel_pk.append(hotel_pk_tmp)
    # 各ホテルの情報をpickleに保存
    print('#####################')
    print('以下の情報を保存します。')
    print('#####################')
    pprint.pprint(hotel_pk)
    with open("hotel.pkl", "wb") as f:
        pickle.dump(hotel_pk, f)  # 保存


if __name__ == '__main__':
    print("Getting hotel infomation.")
    main()
