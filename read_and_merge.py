import datetime
from collections import Counter

import pandas as pd
import re
import os
import numpy as np


def read_merge_rename(house_price_data_path, start_year=101, city_code_filter=[]):
    # settable parameter
    # house_price_data_path = "data\\house_price_xls\\"

    year_list = list(str(x) for x in range(start_year, datetime.datetime.today().year - 1910))
    # city_code_filter = ['o']
    # city_code_filter = ['f']

    # fix parameter
    buy_names = "lvr_land_a.xls"
    presale_names = "lvr_land_b.xls"
    transfer_para = 1.8181 ** 2
    season_list = ['S' + str(i) for i in range(1, 5)]

    existing_house_df_list = []
    presale_df_list = []

    for year in year_list:
        for season in season_list:
            year_season = f"{year}_{season}"
            # year_season = '112_S3'
            house_price_path_sub = house_price_data_path + year_season

            if os.path.isdir(house_price_path_sub):
                print(f"載入-{house_price_path_sub} 的資料")
                all_files = os.listdir(house_price_path_sub)
                buy_files = [tmp_file for tmp_file in all_files if buy_names in tmp_file]
                presale_files = [tmp_file for tmp_file in all_files if presale_names in tmp_file]
                if city_code_filter:
                    def filter_fuc(x):
                        return x[0] in city_code_filter

                    buy_files = list(filter(filter_fuc, buy_files))
                    presale_files = list(filter(filter_fuc, presale_files))
                    print(f"    Only read city code: {'; '.join(city_code_filter)}")

                for buy_file in buy_files:
                    # tmp_df = pd.read_csv(f"{house_price_path_sub}\\{buy_file}")
                    tmp_df = pd.read_excel(f"{house_price_path_sub}\\{buy_file}")

                    tmp_df.drop(0, axis=0, inplace=True)  # row 0 is English statement, drop it
                    existing_house_df_list.append(tmp_df)

                for presale_file in presale_files:
                    # tmp_df = pd.read_csv(f"{house_price_path_sub}\\{presale_file}")
                    tmp_df = pd.read_excel(f"{house_price_path_sub}\\{presale_file}")
                    tmp_df.drop(0, axis=0, inplace=True)  # row 0 is English statement, drop it
                    presale_df_list.append(tmp_df)
            else:
                print(f"{house_price_path_sub}不存在")

    all_existing_house_df = pd.concat(existing_house_df_list, ignore_index=True)
    all_existing_house_df['is_presale'] = False
    # ['鄉鎮市區', '交易標的', '土地位置建物門牌', '土地移轉總面積平方公尺', '都市土地使用分區', '非都市土地使用分區',
    #  '非都市土地使用編定', '交易年月日', '交易筆棟數', '移轉層次', '總樓層數', '建物型態', '主要用途', '主要建材',
    #  '建築完成年月', '建物移轉總面積平方公尺', '建物現況格局-房', '建物現況格局-廳', '建物現況格局-衛',
    #  '建物現況格局-隔間', '有無管理組織', '總價元', '單價元平方公尺', '車位類別', '車位移轉總面積(平方公尺)',
    #  '車位總價元', '備註', '編號', '主建物面積', '附屬建物面積', '陽台面積', '電梯', '移轉編號',
    #  '車位移轉總面積平方公尺']
    all_existing_house_df['車位移轉總面積平方公尺'] = all_existing_house_df.apply(
        lambda tmp_row: tmp_row['車位移轉總面積(平方公尺)'] if pd.isna(tmp_row['車位移轉總面積平方公尺']) else tmp_row[
            '車位移轉總面積平方公尺'], axis=1)

    all_presale_df = pd.concat(presale_df_list, ignore_index=True)
    all_presale_df['is_presale'] = True
    # ['鄉鎮市區', '交易標的', '土地位置建物門牌', '土地移轉總面積平方公尺', '都市土地使用分區', '非都市土地使用分區',
    #  '非都市土地使用編定', '交易年月日', '交易筆棟數', '移轉層次', '總樓層數', '建物型態', '主要用途', '主要建材',
    #  '建築完成年月', '建物移轉總面積平方公尺', '建物現況格局-房', '建物現況格局-廳', '建物現況格局-衛',
    #  '建物現況格局-隔間', '有無管理組織', '總價元', '單價元平方公尺', '車位類別', '車位移轉總面積平方公尺', '車位總價元',
    #  '備註', '編號', '建案名稱', '棟及號', '解約情形']
    # all_presale_df[all_presale_df['建案名稱'] == '恆顧/世界首席']
    # a = all_presale_df[all_presale_df['建案名稱'].apply(lambda x:'恆顧' in str(x))]

    all_buy_df = pd.concat([all_existing_house_df, all_presale_df], ignore_index=True)

    all_buy_df.to_csv('ori_house_data.csv', encoding='utf-8-sig')

    # area relate
    all_buy_df['total_land_area'] = all_buy_df['土地移轉總面積平方公尺'].apply(lambda x: float(x) / transfer_para)
    all_buy_df['total_house_area'] = all_buy_df['建物移轉總面積平方公尺'].apply(lambda x: float(x) / transfer_para)
    all_buy_df['car_area'] = all_buy_df['車位移轉總面積平方公尺'].apply(lambda x: float(x) / transfer_para)
    all_buy_df['house_main_area'] = all_buy_df['主建物面積'].apply(lambda x: float(x) / transfer_para)
    all_buy_df['house_add_area'] = all_buy_df['附屬建物面積'].apply(lambda x: float(x) / transfer_para)
    all_buy_df['house_balcony_area'] = all_buy_df['陽台面積'].apply(lambda x: float(x) / transfer_para)
    full_width_numbers = {"０": "0", "１": "1", "２": "2", "３": "3", "４": "4", "５": "5", "６": "6", "７": "7", "８": "8",
                          "９": "9", }
    all_full_width = set(full_width_numbers.keys())
    all_buy_df['city'] = all_buy_df['鄉鎮市區']
    all_buy_df['build_case_name'] = all_buy_df['建案名稱']
    all_buy_df['address'] = all_buy_df['土地位置建物門牌'].apply(
        lambda x: ''.join(full_width_numbers[i] if i in all_full_width else i for i in x))
    all_buy_df['address'] = all_buy_df['address'].apply(lambda x: x.replace('', ','))
    all_buy_df['trading_land'] = all_buy_df['交易標的'].apply(lambda x: '土地' in x)
    all_buy_df['trading_house'] = all_buy_df['交易標的'].apply(lambda x: '建物' in x)
    all_buy_df['trading_car'] = all_buy_df['交易標的'].apply(lambda x: '車位' in x)
    all_buy_df['house_type'] = all_buy_df['建物型態']

    def turn_float(x):
        try:
            return float(x)
        except:
            return np.NaN

    # date relate
    all_buy_df['building_date'] = all_buy_df['建築完成年月'].apply(lambda x: turn_float(x))
    all_buy_df['trading_date'] = all_buy_df['交易年月日']

    # price relate
    all_buy_df['total_price'] = all_buy_df['總價元'].apply(lambda x: float(float(x) / 10000))
    all_buy_df['car_price'] = all_buy_df['車位總價元'].apply(lambda x: float(float(x) / 10000))

    all_buy_df_new = all_buy_df[['total_land_area',
                                 'total_house_area', 'car_area', 'house_main_area', 'house_add_area',
                                 'house_balcony_area', 'city', 'build_case_name', 'address',
                                 'trading_land', 'trading_house', 'trading_car', 'building_date',
                                 'trading_date', 'total_price', 'car_price', 'is_presale', 'house_type']]

    all_buy_df_new.to_csv('house_data.csv', encoding='utf-8-sig')
