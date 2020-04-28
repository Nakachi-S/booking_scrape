import os
import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse
import re
import pickle
import pprint
import csv

# main関数
# hotel.pklから基本的な情報を読み込む


def main():
    # pickle展開
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
    for i in range(1, 30):
        check_in = datetime.date.today() + datetime.timedelta(days=i)
        check_out = datetime.date.today() + datetime.timedelta(days=i+1)
        option = '?checkin=' + str(check_in) + '&checkout=' + str(check_out) + \
            '&selected_currency=JPY&changed_currency=1&top_currency=1&lang=ja&group_adults=1&no_rooms=1'
        urls.append(url + option)
    return urls


# scrape関数
# bs4を用いてwebから取得
# 1実行で１ホテル
def scrape(urls, hotel):
    head = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"}
    print('###########################')
    print(hotel['name'])
    print('###########################')
    pprint.pprint(hotel)
    save_list = []
    for url in urls:
        print('###########################')
        print(url)
        r = requests.get(url, headers=head)
        soup = BeautifulSoup(r.text, 'lxml')
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
        try:  # table自体、無い場合がある
            table = soup.find('table', class_='hprt-table').find('tbody')
        except:
            print('この日はbooking.comでは予約できません')
            price = ''
            available = 0
            for room in hotel['rooms']:
                write_list = [room['id'], room['name'], check_in, check_out, price, person, available, created]
                save_list.append(write_list)
            continue
        
        for room in hotel['rooms']:
            room_name = ''
            available = 0
            occupancy = ''
            price = ''
            for tr in table.find_all('tr'):  # tr行
                if tr.select_one('td.hprt-table-cell.-first'):  # 最初の行のみ
                    # 次はroom idで検索
                    if tr.select_one('td.hprt-table-cell.-first').find('a', id='room_type_id_'+room['id']):
                        flg_avaliable = 0
                        for td in tr.find_all('td'):            # 該当するデータを抽出
                            if td.find('div', class_='hprt-roomtype-name'):
                                room_name = td.find(
                                    'div', class_='hprt-roomtype-name').text.replace('\n', '')
                                # 何室空いているか
                                if td.find('div', class_='thisRoomAvailabilityNew'):
                                    available = td.find(
                                        'div', class_='thisRoomAvailabilityNew').text.replace('\n', '')
                                    available = re.sub("\\D", "", available)
                                    flg_avaliable = 1
                                else:  # 無いなら1。
                                    print('何室空いているかの情報がない。')
                                    available = 1
                            elif td.find('div', class_='hprt-occupancy-occupancy-info'):  # 定員
                                occupancy = td.find(
                                    'div', class_='hprt-occupancy-occupancy-info').text.replace('\n', '')
                            elif td.find('div', class_='hprt-price-block'):               # 金額
                                # price = td.find('div', class_='hprt-price-block').find(
                                #     'div', class_='bui-price-display').text.replace('\n', '')
                                price = td.find('div', class_='hprt-price-block').find(
                                    'div', class_='bui-price-display__value').text.replace('\n', '')
                            elif td.find('div', class_='thisRoomAvailabilityNew') and flg_avaliable == 0:
                                print('最初はなかったがこの列にあったよ！')
                                available = td.find(
                                    'div', class_='thisRoomAvailabilityNew').text.replace('\n', '')
                                available = re.sub("\\D", "", available)

            write_list = [room['id'], room['name'], check_in, check_out, price, person, available, created]
            pprint.pprint(write_list)
            save_list.append(write_list)
    save_name = hotel['save_dir'] + '_' + datetime.date.today().strftime("%Y-%m-%d") + '.csv'
    # 保存するディレクトリ
    if not os.path.exists(os.path.join('scrape', hotel['save_dir'])):
        os.mkdir(hotel['save_dir'])
    with open(os.path.join('scrape', hotel['save_dir'], save_name), 'w') as f:
        writer = csv.writer(f)
        writer.writerows(save_list)

if __name__ == '__main__':
    print("Booking scraping start....")
    main()
