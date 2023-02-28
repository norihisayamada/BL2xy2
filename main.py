import folium
import io
import json
import  numpy as np
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import folium_static
import time
from io import StringIO


st.title('緯度経度を平面直角座標に換算するアプリです')
st.header('概要')
st.write('国土地理院APIを使用し、第6系に対応しています')

df = pd.DataFrame()

lat_list = []
lon_list = []
grid_list = []
scale_list = []

def readFile(file):
    if file is not None:
        st.subheader('ファイル詳細')
        # To read file as bytes:
        # bytes_data = uploaded_file.getvalue()
        # st.write(bytes_data)

        # To convert to a string based IO:
        # stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        # st.write(stringio)
        #
        # # To read file as string:
        # string_data = stringio.read()
        # st.write(string_data)

        # Can be used wherever a "file-like" object is accepted:
        global  df
        df = pd.read_csv(file, encoding='UTF-8')
        st.write(df)

def tranceBL(df):
    for index, row in df.iterrows():
        url = "http://vldb.gsi.go.jp/sokuchi/surveycalc/surveycalc/bl2xy.pl?"
        params = {'latitude': row.lat, 'longitude': row.lon, "refFrame": 2, "zone": 6, 'outputType': 'json'}

        res = requests.get(url, params=params)
        time.sleep(1)
        if res.status_code == requests.codes.ok:
            print(res.json())
        lat_list.append(res.json()["OutputData"]["publicX"])
        lon_list.append(res.json()["OutputData"]["publicY"])
        grid_list.append((res.json()["OutputData"]["gridConv"]))
        scale_list.append((res.json()["OutputData"]["scaleFactor"]))

# 変換先の平面直角座標系を入力してください
# st.select_slider('Select a color of the rainbow')

#緯度経度（CSV形式）ファイルを選択してください
st.subheader('緯度経度（CSV形式）ファイルを選択してください')
uploaded_file = st.file_uploader("Choose a CSV file")
readFile(uploaded_file)

#緯度経度から平面直角座標の換算
st.subheader('平面直角座標に変換します')
st.text('indexはlat lonとしてください。 数値は度単位で入力してください。（例：35.123456, 139.123456）')
if st.button('平面直角座標に変換します'):
    tranceBL(df)
    df_new = df.copy()
    df_new['X'] = lat_list
    df_new['Y'] = lon_list
    df_new['gridConv'] = grid_list
    df_new['scaleFactor'] = scale_list
    # df_new.to_csv('./res.csv', encoding='UTF-8', index=False)
    st.write(df_new)
    m = folium.Map(location=[df_new[0:1].lat, df_new[0:1].lon], tiles='OpenStreetMap', zoom_start=10)
    for i, marker in df_new.iterrows():
        print(marker)
        name = 'Location:' + str(i)
        lat = marker.lat
        lon = marker.lon
        popup = "<strong>{0}</strong><br>Lat:{1:.3f}<br>Long:{2:.3f}".format(name, lat, lon)
        folium.Marker(location=[lat, lon], popup=popup, icon=folium.Icon(color='lightgreen')).add_to(m)
    folium_static(m)

# mapに描画する
# for i, marker in df_new.iterrows():
#     print(marker)
#     name='Location:'+str(i)
#     lat = marker.lat
#     lon = marker.lon
#     popup ="<strong>{0}</strong><br>Lat:{1:.3f}<br>Long:{2:.3f}".format(name, lat, lon)
#     folium.Marker(location=[lat, lon], popup=popup, icon=folium.Icon(color='lightgreen')).add_to(m)

# HTML出力（ブラウザで見る場合はchromeなどでブラウジングすることもできます）
# m.save('./mapping' + '.html')

# st.write('地図に表示しますか？')
# if st.button('地図に表示します'):
#     'mapping...'
#     folium_static(m)

# df = pd.DataFrame(
#     np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
#     columns=['lat', 'lon'])
# st.map(df)

#How to download a Pandas DataFrame as a CSV?

# @st.experimental_memo
# def convert_df(df):
#    return df.to_csv(index=False).encode('utf-8')
#
#
# csv = convert_df(df)
#
# st.download_button(
#    "Press to Download",
#    csv,
#    "file.csv",
#    "text/csv",
#    key='download-csv'
# )

