import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def show_page(uploaded_files):
    st.title("장비 그룹별 개별 가동율 현황")

    # 파일 검사
    if "CAPA_ALLOCATION_INFO.parquet" not in uploaded_files or "RES_MASTER.parquet" not in uploaded_files:
        st.error("CAPA_ALLOCATION_INFO.parquet와 RES_MASTER.parquet 파일이 모두 필요합니다.")
        return

    # Parquet 파일 읽기
    df = pd.read_parquet(uploaded_files["CAPA_ALLOCATION_INFO.parquet"], engine='pyarrow')
    res_master = pd.read_parquet(uploaded_files["RES_MASTER.parquet"], engine='pyarrow')

    # RES_MASTER 테이블에서 RES_ID와 RES_NAME 가져오기
    res_master = res_master[["RES_ID", "RES_NAME"]]

    # 데이터 처리 공통 함수
    def process_data(df_filtered, group_col):
        grouped = df_filtered.groupby(group_col).agg({
            'TOTAL_CAPA': 'sum',
            'OFF_TIME_CAPA': 'sum',
            'ALLOCATION_CAPA': 'sum',
            'PM_CAPA': 'sum',
            'SETUP_CAPA': 'sum',
            'REMAIN_CAPA': 'sum',
        }).reset_index()

        # 비율 계산 및 각 비율 컬럼 추가
        grouped['ALLOCATION_CAPA_%'] = (grouped['ALLOCATION_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['SETUP_CAPA_%'] = (grouped['SETUP_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['PM_CAPA_%'] = (grouped['PM_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['OFF_TIME_CAPA_%'] = (grouped['OFF_TIME_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['REMAIN_CAPA_%'] = (grouped['REMAIN_CAPA'] / grouped['TOTAL_CAPA']) * 100

        # customdata 생성
        grouped['customdata'] = grouped.apply(
            lambda row: [
                (row['ALLOCATION_CAPA_%'], row['ALLOCATION_CAPA'], row['TOTAL_CAPA']),
                (row['SETUP_CAPA_%'], row['SETUP_CAPA'], row['TOTAL_CAPA']),
                (row['PM_CAPA_%'], row['PM_CAPA'], row['TOTAL_CAPA']),
                (row['OFF_TIME_CAPA_%'], row['OFF_TIME_CAPA'], row['TOTAL_CAPA']),
                (row['REMAIN_CAPA_%'], row['REMAIN_CAPA'], row['TOTAL_CAPA']),
            ], axis=1
        )

        # ALLOCATION_CAPA_% 기준으로 데이터 정렬
        grouped = grouped.sort_values(by='ALLOCATION_CAPA_%', ascending=False)

        return grouped

    # 그래프 생성 함수
    def create_chart(grouped, group_col, title):
        categories = ['ALLOCATION_CAPA', 'SETUP_CAPA', 'PM_CAPA', 'OFF_TIME_CAPA', 'REMAIN_CAPA']
        colors = ['#66CC66', '#FF6666', '#FFE066', '#808080', '#F2F2F2']
        fig = go.Figure()

        for i, (category, color) in enumerate(zip(categories, colors)):
            fig.add_trace(
                go.Bar(
                    x=grouped[group_col],
                    y=grouped[f'{category}_%'],
                    name=category.replace('_', ' ').capitalize(),
                    marker_color=color,
                    customdata=grouped['customdata'],
                    hovertemplate=(
                        f"{category.replace('_', ' ').capitalize()}: %{{customdata[{i}][0]:.2f}}% "
                        f"(%{{customdata[{i}][1]:,.0f}}/%{{customdata[{i}][2]:,.0f}})<extra></extra>"
                    ),
                )
            )

        # X축 스크롤링 조건 설정 (10개 초과일 경우만)
        if len(grouped[group_col]) > 10:
            fig.update_layout(
                xaxis=dict(
                    title=f"{group_col}",
                    tickangle=45,
                    automargin=True,
                    range=[-0.5, 9.5],  # 처음엔 처음 10개만 보이도록 설정
                    fixedrange=False,  # 확대/축소 가능
                )
            )
        else:
            # X축 스크롤 및 확대/축소 비활성화
            fig.update_layout(
                xaxis=dict(
                    title=f"{group_col}",
                    tickangle=45,
                    automargin=True,
                    fixedrange=True,  # 확대/축소 불가
                )
            )

        fig.update_layout(
            title=title,
            yaxis_title="백분율 (%)",
            barmode='stack',
            hovermode="x unified",
            margin=dict(l=10, r=10, t=30, b=70),
        )
        return fig

    # 데이터 처리 및 RES_GROUP_ID별 선택
    grouped_time = process_data(df, 'RES_GROUP_ID')
    selected_group = st.selectbox("세부 그래프를 볼 RES_GROUP_ID를 선택하세요:", grouped_time['RES_GROUP_ID'])

    if selected_group:
        st.subheader(f"선택된 RES_GROUP_ID: {selected_group}")
        df_target = df[df['RES_GROUP_ID'] == selected_group]

        # TARGET_ID와 RES_MASTER 테이블 연결하여 RES_NAME + '_' + TARGET_ID 생성
        df_target = pd.merge(df_target, res_master, left_on='TARGET_ID', right_on='RES_ID', how='left')
        df_target['RES_NAME+RES_ID'] = df_target['RES_NAME'].fillna('Unknown') + '_' + df_target['TARGET_ID']

        grouped_target = process_data(df_target, 'RES_NAME+RES_ID')
        fig_target = create_chart(grouped_target, 'RES_NAME+RES_ID', f"TARGET_ID별 CAPA Distribution ({selected_group})")
        st.plotly_chart(fig_target, use_container_width=True)

if __name__ == "__main__":
    uploaded_files = {
        "CAPA_ALLOCATION_INFO.parquet": "D:/path/to/CAPA_ALLOCATION_INFO.parquet",
        "RES_MASTER.parquet": "D:/path/to/RES_MASTER.parquet"
    }
    show_page(uploaded_files)
