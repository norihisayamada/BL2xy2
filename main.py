import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import folium_static
import time


st.title('緯度経度を平面直角座標に変換するアプリです')
st.header('国土地理院APIを使用し、第6系の平面直角座標に変換します')
st.write('Pythonで記述しています。コードは下記よりダウンロード又はForkしてご利用下さい')
st.write('https://github.com/norihisayamada/BL2xy2')

st.write('サンプルデータをダウンロード')
with open('./sample.csv') as f:
    df = f.read()
    st.download_button('Download sampleData', df, 'test.csv', 'text/csv')

df = pd.DataFrame()

lat_list = []
lon_list = []
grid_list = []
scale_list = []

def readFile(file):
    if file is not None:
        st.subheader('変換前の緯度経度を表示します')
        global  df
        df = pd.read_csv(file, encoding='UTF-8')
        st.write(df)

def tranceBL(df):
    for index, row in df.iterrows():
        url = "http://vldb.gsi.go.jp/sokuchi/surveycalc/surveycalc/bl2xy.pl?"
        params = {'latitude': row.lat, 'longitude': row.lon, "refFrame": 2, "zone": 6, 'outputType': 'json'}

        res = requests.get(url, params=params)
        time.sleep(1.5)
        if res.status_code == requests.codes.ok:
            print(res.json())
        lat_list.append(res.json()["OutputData"]["publicX"])
        lon_list.append(res.json()["OutputData"]["publicY"])
        grid_list.append((res.json()["OutputData"]["gridConv"]))
        scale_list.append((res.json()["OutputData"]["scaleFactor"]))

#緯度経度（CSV形式）ファイルを選択してください
st.subheader('変換するファイルを選択してください')
st.text('インデックスは、lat lonとしてください')
st.text('数値は度単位で入力してください。入力例：35.123456, 139.123456')
uploaded_file = st.file_uploader("ファイルを選択して下さい")
readFile(uploaded_file)

#緯度経度から平面直角座標の換算
st.subheader('平面直角座標に変換します')
if st.button('変換実行'):
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