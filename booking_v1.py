import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse
import re
import pickle
import pprint

# main関数
# hotel.pklから基本的な情報を読み込む


def main():
    with open('hotel.pkl', 'rb') as f:
        hotel_pk = pickle.load(f)
    # ホテルの数だけforが回る
    for hotel in hotel_pk:
        urls = urls_get(hotel['url'])  # チェックインなどの指定。複数のurlが帰ってくる。
        scrape(urls, hotel)


# urls_get関数
# クエリパラメータを指定
def urls_get(url):
    urls = []
    for i in range(1, 2):
        check_in = datetime.date.today() + datetime.timedelta(days=i)
        check_out = datetime.date.today() + datetime.timedelta(days=i+1)
        option = '?checkin=' + str(check_in) + '&checkout=' + str(check_out) + \
            '&selected_currency=JPY&changed_currency=1&top_currency=1&lang=ja&group_adults=1&no_rooms=1'
        urls.append(url + option)
    return urls


# scrape関数
# bs4を用いてwebから取得
def scrape(urls, hotel):
    head = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"}
    print('###########################')
    print(hotel['name'])
    print('###########################')
    pprint.pprint(hotel)
    for url in urls:
        print(url)
        r = requests.get(url, headers=head)
        soup = BeautifulSoup(r.text, 'lxml')
        # name = soup.find('h2', id='hp_hotel_name').strings  # hotel name
        # name = list(name)[2].replace('\n', '')
        ###############################################
        qs = urllib.parse.urlparse(url).query
        qs_d = urllib.parse.parse_qs(qs)
        created = datetime.date.today().strftime("%Y-%m-%d")
        check_in = qs_d['checkin'][0]
        check_out = qs_d['checkout'][0]
        person = qs_d['group_adults'][0]
        print(hotel['name'], created, check_in, check_out, person)
        ################################################
        # ここまでurlなどから取得可能な情報
        # 以下は、実際にサイトから取得する
        table = soup.find('table', class_='hprt-table').find('tbody')
        for tr in table.find_all('tr'):                 # tr行
            if tr.select_one('td.hprt-table-cell.-first'):  # 最初の行のみ
                for td in tr.find_all('td'):            # 該当するデータを抽出
                    if td.find('div', class_='hprt-roomtype-name'):               # 部屋の名前
                        print(
                            td.find('div', class_='hprt-roomtype-name').text.replace('\n', ''))
                        print(
                            td.find('div', class_='thisRoomAvailabilityNew').text.replace('\n', ''))
                    elif td.find('div', class_='hprt-occupancy-occupancy-info'):  # 定員
                        print(
                            td.find('div', class_='hprt-occupancy-occupancy-info').text.replace('\n', ''))
                    elif td.find('div', class_='hprt-price-block'):               # 金額
                        print(td.find(
                            'div', class_='hprt-price-block').find('div', class_='bui-price-display').text.replace('\n', ''))

            else:
                continue
        # print(table.find('tr'))


if __name__ == '__main__':
    print("Booking scraping start....")
    main()
