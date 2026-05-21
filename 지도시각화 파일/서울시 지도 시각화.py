import pandas as pd
import folium
import json
from folium.features import DivIcon


# 1. 데이터 불러오기


df = pd.read_csv('data_with_scores.csv', encoding='utf-8-sig')

# 지도 경계 데이터(GeoJSON) 불러오기
with open('hangjeongdong_서울특별시.geojson', 'r', encoding='utf-8') as f:
    geo_data = json.load(f)

# 지도 데이터의 'adm_nm'에서 마지막 동 이름만 추출하여 'dong_name'으로 저장
for feature in geo_data['features']:
    full_name = feature['properties']['adm_nm']
    feature['properties']['dong_name'] = full_name.split()[-1]


map_configs = [
    ('노인복지점수', 'Reds', '노인복지점수 (진할수록 시설 확충 시급)'),
    ('장애인복지점수', 'Blues', '장애인복지점수 (진할수록 시설 확충 시급)'),
    ('최종복지점수', 'Greens', '최종복지점수 (진할수록 시설 확충 시급)')
]

# ==========================================
# 3. 지도 3개 자동 생성 (반복문)
# ==========================================
for score_col, color_theme, legend in map_configs:
    
  
    # 최고점에서 현재 점수를 빼서 순서를 반대로 만듭니다.
    df['시각화용_점수'] = df[score_col].max() - df[score_col]
    
    # 도화지 생성
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles=None)

    # 💡 주의: 구간(bins)도 원래 점수가 아닌 '시각화용_점수'를 기준으로 자릅니다!
    my_bins = df['시각화용_점수'].quantile([0, 0.2, 0.4, 0.6, 0.8, 1]).tolist()

    # 지도 색칠 (Choropleth)
    folium.Choropleth(
        geo_data=geo_data,
        data=df,
        columns=['행정동', '시각화용_점수'], 
        key_on='feature.properties.dong_name',
        fill_color=color_theme, 
        fill_opacity=0.8,
        line_opacity=0.5,
        bins=my_bins,
        
        legend_name=f'{legend} (※ 진한 색일수록 원래 점수는 낮음)' 
    ).add_to(m)

    # 지도 위에 행정동 이름 텍스트 표기 (중심점 계산)
    for feature in geo_data['features']:
        geom = feature['geometry']
        if geom['type'] == 'Polygon':
            coords = geom['coordinates'][0]
        elif geom['type'] == 'MultiPolygon':
            coords = geom['coordinates'][0][0]
        
        lon = sum(p[0] for p in coords) / len(coords)
        lat = sum(p[1] for p in coords) / len(coords)
        
        folium.Marker(
            location=[lat, lon],
            icon=DivIcon(
                icon_size=(150,36),
                icon_anchor=(75,18),
                html=f'<div style="font-size: 6pt; color: black; text-align: center; font-weight: bold;">{feature["properties"]["dong_name"]}</div>',
            )
        ).add_to(m)

    # HTML 파일로 저장
    file_name = f'서울_{score_col}_지도.html'
    m.save(file_name)
    print(f" 시각화 완료: '{file_name}' (점수가 낮을수록 진한 색으로 칠해졌습니다!)")