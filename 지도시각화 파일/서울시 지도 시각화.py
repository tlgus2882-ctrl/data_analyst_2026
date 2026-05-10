import pandas as pd
import folium
import json
from folium.features import DivIcon

# 1. 파일 불러오기
# 인코딩 에러 방지를 위해 cp949 적용
df = pd.read_csv('데이터셋 최종.csv', encoding='cp949')

with open('hangjeongdong_서울특별시.geojson', 'r', encoding='utf-8') as f:
    geo_data = json.load(f)

# 2. 데이터 전처리 및 지수 계산
df['총시설수'] = df['총시설수'].fillna(0)
df['총생활인구수'] = df['총생활인구수'].fillna(0)

# '부족 시설'로 명칭 변경 및 계산
df['인구밀도'] = df['총생활인구수'] / df['면적(㎢)']
df['부족 시설'] = df['인구밀도'] / (df['총시설수'] + 1)

# 3. 지도 데이터 전처리 (이름 맞추기)
for feature in geo_data['features']:
    full_name = feature['properties']['adm_nm']
    dong_only = full_name.split()[-1]
    feature['properties']['dong_name'] = dong_only

# 4. 지도 생성 (배경 제거: tiles=None)
m = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles=None)

# 색상 구간 설정
my_bins = df['부족 시설'].quantile([0, 0.2, 0.4, 0.6, 0.8, 1]).tolist()

# 5. 단계구분도(Choropleth) 추가
folium.Choropleth(
    geo_data=geo_data,
    data=df,
    columns=['행정동', '부족 시설'],
    key_on='feature.properties.dong_name',
    fill_color='YlOrRd',
    fill_opacity=0.8,
    line_opacity=0.5,
    bins=my_bins,
    legend_name='부족 시설 정도 (빨간색일수록 시설 확충 시급)'
).add_to(m)

# 6. 지도 위에 '동 이름' 텍스트 쓰기
# 각 행정동의 중심 좌표에 글자를 배치합니다.
for feature in geo_data['features']:
    # 폴리곤의 중심점 대략적 계산 (간단한 평균값 방식)
    geom = feature['geometry']
    if geom['type'] == 'Polygon':
        coords = geom['coordinates'][0]
    elif geom['type'] == 'MultiPolygon':
        coords = geom['coordinates'][0][0]
    
    # 위도(lat), 경도(lon) 평균 계산
    lon = sum(p[0] for p in coords) / len(coords)
    lat = sum(p[1] for p in coords) / len(coords)
    
    # 지도 위에 글자 표시
    folium.Marker(
        location=[lat, lon],
        icon=DivIcon(
            icon_size=(150,36),
            icon_anchor=(75,18),
            html=f'<div style="font-size: 6pt; color: black; text-align: center; font-weight: bold;">{feature["properties"]["dong_name"]}</div>',
        )
    ).add_to(m)

# 7. 결과 저장
m.save('서울_시설부족_시각화_최종.html')
print("시각화가 완료되었습니다. 배경이 없는 서울 중심 지도가 생성되었습니다.")