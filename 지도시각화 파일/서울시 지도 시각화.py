import pandas as pd
import folium
import json
from folium.features import DivIcon

# ==========================================
# 1. 데이터 불러오기
# ==========================================
# 주의: 반드시 main.ipynb에서 머신러닝 점수 계산을 마친 후 저장한 
# 'data_with_scores.csv' 파일을 사용해야 합니다.
df = pd.read_csv('data_with_scores.csv', encoding='utf-8-sig')

# 지도 경계 데이터(GeoJSON) 불러오기
with open('hangjeongdong_서울특별시.geojson', 'r', encoding='utf-8') as f:
    geo_data = json.load(f)

# 지도 데이터의 'adm_nm'에서 마지막 동 이름만 추출하여 'dong_name'으로 저장
for feature in geo_data['features']:
    full_name = feature['properties']['adm_nm']
    feature['properties']['dong_name'] = full_name.split()[-1]

# ==========================================
# 2. 시각화 테마 3가지 설정 
# ==========================================
# (데이터 컬럼명, 그라데이션 색상, 범례 텍스트)
# 지정된 색상 팔레트(Reds, Blues, Greens)는 점수가 높을수록 자동으로 진하게 칠해집니다.
map_configs = [
    ('노인복지점수', 'Reds', '노인복지점수 (진할수록 시설 확충 시급)'),
    ('장애인복지점수', 'Blues', '장애인복지점수 (진할수록 시설 확충 시급)'),
    ('최종복지점수', 'Greens', '최종복지점수 (진할수록 시설 확충 시급)')
]

# ==========================================
# 3. 지도 3개 자동 생성 (반복문)
# ==========================================
for score_col, color_theme, legend in map_configs:
    
    # 3-1. 서울시 중심 좌표로 도화지 생성 (tiles=None으로 배경 제거)
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles=None)

    # 3-2. 해당 점수의 데이터 분포에 맞게 5단계(20%씩) 구간 자르기
    my_bins = df[score_col].quantile([0, 0.2, 0.4, 0.6, 0.8, 1]).tolist()

    # 3-3. 구역별로 색상 입히기 (Choropleth)
    folium.Choropleth(
        geo_data=geo_data,
        data=df,
        columns=['행정동', score_col],
        key_on='feature.properties.dong_name',
        fill_color=color_theme, 
        fill_opacity=0.8,
        line_opacity=0.5,
        bins=my_bins,
        legend_name=legend
    ).add_to(m)

    # 3-4. 지도 위에 행정동 이름 텍스트 표기 (중심점 계산)
    for feature in geo_data['features']:
        geom = feature['geometry']
        if geom['type'] == 'Polygon':
            coords = geom['coordinates'][0]
        elif geom['type'] == 'MultiPolygon':
            coords = geom['coordinates'][0][0]
        
        # 위도/경도 평균을 구해 폴리곤의 중심 좌표 찾기
        lon = sum(p[0] for p in coords) / len(coords)
        lat = sum(p[1] for p in coords) / len(coords)
        
        # 마커를 이용해 텍스트 추가
        folium.Marker(
            location=[lat, lon],
            icon=DivIcon(
                icon_size=(150,36),
                icon_anchor=(75,18),
                html=f'<div style="font-size: 6pt; color: black; text-align: center; font-weight: bold;">{feature["properties"]["dong_name"]}</div>',
            )
        ).add_to(m)

    # 3-5. HTML 파일로 저장
    file_name = f'서울_{score_col}_지도.html'
    m.save(file_name)
    print(f"✅ 시각화 완료: '{file_name}' (테마: {color_theme})")

print("\n🎉 모든 지도가 성공적으로 생성되었습니다!")