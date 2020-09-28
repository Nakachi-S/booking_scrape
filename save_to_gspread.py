import gspread
import json
import pickle
import datetime
import csv
import os
import glob
import pprint
#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials

# 最初にgoogle spread sheetに必要な設定
#2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

#認証情報設定
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'reqrea-v1-c87d50ad18aa.json', scope)

#OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials)

#共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
SPREADSHEET_KEY = '1-QuOXys_xgEq3Q7g4Lb_ZqS2UnYBVb8Cm2QwWRlgqjs'

# ワークブックを開く
workbook = gc.open_by_key(SPREADSHEET_KEY)

#共有設定したスプレッドシートのシート1を開く
# worksheet = gc.open_by_key(SPREADSHEET_KEY).sheet1

# #A1セルの値を受け取る
# import_value = int(worksheet.acell('A1').value)

# #A1セルの値に100加算した値をB1セルに表示させる
# export_value = import_value+100
# worksheet.update_cell(1, 2, export_value)

def main():
    # pickleからシートを作る。あったらスルー
    check_sheet()
    # csvからgspreadに保存（今日だけ）
    save_booking()
    # csvからgspreadに保存（全て）
    # save_booking_all()

 
def check_sheet():
    worksheet_list = workbook.worksheets()
    worksheet_list_title = [worksheet.title for worksheet in worksheet_list]
    print(worksheet_list_title)
    with open('hotel.pkl', 'rb') as f:
        hotel_pk = pickle.load(f)
    
    for hotel in hotel_pk:
        if hotel['name'] not in worksheet_list_title:
            workbook.add_worksheet(title=hotel['name'], rows=100, cols=26)
            working_worksheet = workbook.worksheet(hotel['name'])
            working_worksheet.append_row(['room id', 'room name', 'check in', 'check out', 'price', 'person', 'avaliable', 'created'])
        else:
            print(hotel['name'], 'は既に作成済みです')


def save_booking():
    with open('hotel.pkl', 'rb') as f:
        hotel_pk = pickle.load(f)
    
    for hotel in hotel_pk:
        print(hotel['name'])
        save_name = hotel['save_dir'] + '_' + datetime.date.today().strftime("%Y-%m-%d") + '.csv'
        # save_name = hotel['save_dir'] + '_2020-04-27.csv'
        csv_path = os.path.join('scrape', hotel['save_dir'], save_name)
        with open(csv_path) as fp:
            append_list = list(csv.reader(fp))
        
        working_worksheet = workbook.worksheet(hotel['name'])
        working_worksheet.append_rows(append_list, value_input_option='USER_ENTERED')


def save_booking_all():
    with open('hotel.pkl', 'rb') as f:
        hotel_pk = pickle.load(f)
    
    for hotel in hotel_pk:
        print(hotel['name'])
        save_names = hotel['save_dir'] + '*.csv'
        hotel_all_csv_path = os.path.join('scrape', hotel['save_dir'], save_names)
        hotel_all_csv_path_list = sorted(glob.glob(hotel_all_csv_path))
        
        write_list = []
        for one_csv_path in hotel_all_csv_path_list:
            with open(one_csv_path) as fp:
                append_list = list(csv.reader(fp))
            write_list.extend(append_list)
        
        working_worksheet = workbook.worksheet(hotel['name'])
        working_worksheet.append_rows(write_list, value_input_option='USER_ENTERED')


print("Saving to Google Spread Sheet...")
main()
