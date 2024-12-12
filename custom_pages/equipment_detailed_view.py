import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def show_page():
    st.title("장비 그룹별 개별 가동율 현황")

    # Parquet 파일 경로 지정
    model_path = 'C:\\Users\\vms\\Downloads\\20241210-P-BOM2_Engine_20241210081853\\Experiment 1\\Result 0\\'
    file_path = 'CAPA_ALLOCATION_INFO.parquet'

    # Parquet 파일 읽기
    df = pd.read_parquet(model_path + file_path, engine='pyarrow')

    # 데이터 처리 공통 함수
    def process_data(df_filtered, group_col):
        grouped = df_filtered.groupby(group_col).agg({
            'TOTAL_CAPA': 'sum',
            'OFF_TIME_CAPA': 'sum',
            'ALLOCATION_CAPA': 'sum',
            'PM_CAPA': 'sum',
            'SETUP_CAPA': 'sum',
            'REMAIN_CAPA': 'sum'
        }).reset_index()

        # 비율 계산
        grouped['OFF_TIME_CAPA_%'] = (grouped['OFF_TIME_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['ALLOCATION_CAPA_%'] = (grouped['ALLOCATION_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['PM_CAPA_%'] = (grouped['PM_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['SETUP_CAPA_%'] = (grouped['SETUP_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['REMAIN_CAPA_%'] = (grouped['REMAIN_CAPA'] / grouped['TOTAL_CAPA']) * 100

        # Allocation_capa 퍼센티지 기준으로 정렬
        grouped = grouped.sort_values(by='ALLOCATION_CAPA_%', ascending=False)

        return grouped

    # 그래프 생성 함수
    def create_chart(grouped, group_col, title):
        categories = ['Allocation_capa', 'Setup_capa', 'Pm_capa', 'Off_time_capa', 'Remain_capa']
        colors = ['#66CC66', '#FF6666', '#FFE066', '#808080', '#F2F2F2']
        fig = go.Figure()

        for i, (category, color) in enumerate(zip(categories, colors)):
            fig.add_trace(
                go.Bar(
                    x=grouped[group_col],
                    y=grouped[f'{category.upper()}_%'],
                    name=category.capitalize(),
                    marker_color=color,
                    hovertemplate=(f"{category.capitalize()}: %{{y:.2f}}%<extra></extra>"),
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
            template="plotly_white",
            margin=dict(l=10, r=10, t=30, b=70),
        )
        return fig

    # 전체 데이터를 사용하여 처리
    grouped_time = process_data(df, 'RES_GROUP_ID')

    # RES_GROUP_ID 선택
    selected_group = st.selectbox("세부 그래프를 볼 RES_GROUP_ID를 선택하세요:", grouped_time['RES_GROUP_ID'])

    # 선택된 RES_GROUP_ID의 TARGET_ID 세부 그래프 출력
    if selected_group:
        st.subheader(f"선택된 RES_GROUP_ID: {selected_group}")
        df_target = df[df['RES_GROUP_ID'] == selected_group]
        grouped_target = process_data(df_target, 'TARGET_ID')
        fig_target = create_chart(grouped_target, 'TARGET_ID', f"TARGET_ID별 CAPA Distribution ({selected_group})")
        st.plotly_chart(fig_target, use_container_width=True)

# 실행
if __name__ == "__main__":
    show_page()
