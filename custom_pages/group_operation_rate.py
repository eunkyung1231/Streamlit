import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components

def show_page():
    st.title("장비 그룹별 가동율 현황")

    # Parquet 파일 경로 지정
    model_path = 'C:\\Users\\vms\\Downloads\\20241210-P-BOM2_Engine_20241210081853\\Experiment 1\\Result 0\\'
    file_path = 'CAPA_ALLOCATION_INFO.parquet'

    # Parquet 파일 읽기
    df = pd.read_parquet(model_path + file_path, engine='pyarrow')

    # 조건 필터링 및 그룹화 로직 (공통 함수)
    def process_data(df_filtered):
        grouped = df_filtered.groupby('RES_GROUP_ID').agg({
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

        # Allocation_capa 퍼센테이지 기준으로 정렬
        grouped = grouped.sort_values(by='ALLOCATION_CAPA_%', ascending=False)

        # X축 레이블: RES_GROUP_ID만 표시
        grouped['X_LABEL'] = grouped['RES_GROUP_ID']

        # customdata에 비율 값, 원래 값, 기준값 추가 (3차원 배열로)
        grouped['customdata'] = grouped.apply(
            lambda row: [
                (row['ALLOCATION_CAPA_%'], row['ALLOCATION_CAPA'], row['TOTAL_CAPA']),
                (row['SETUP_CAPA_%'], row['SETUP_CAPA'], row['TOTAL_CAPA']),
                (row['PM_CAPA_%'], row['PM_CAPA'], row['TOTAL_CAPA']),
                (row['OFF_TIME_CAPA_%'], row['OFF_TIME_CAPA'], row['TOTAL_CAPA']),
                (row['REMAIN_CAPA_%'], row['REMAIN_CAPA'], row['TOTAL_CAPA']),
            ],
            axis=1
        )
        return grouped
    

    # X축 스크롤을 조건적으로 활성화하는 함수
    def create_chart(grouped, title):
        categories = ['Allocation_capa', 'Setup_capa', 'Pm_capa', 'Off_time_capa', 'Remain_capa']
        colors = ['#66CC66', '#FF6666', '#FFE066', '#808080', '#F2F2F2']
        fig = go.Figure()

        for i, (category, color) in enumerate(zip(categories, colors)):
            fig.add_trace(
                go.Bar(
                    x=grouped['X_LABEL'],
                    y=grouped[f'{category.upper()}_%'],
                    name=category.capitalize(),
                    marker_color=color,
                    customdata=np.stack(grouped['customdata'].to_numpy()),  # customdata를 2차원 배열로 전달
                    hovertemplate=(f"{category.capitalize()}: %{{customdata[{i}][0]:.2f}}% "
                                f"(%{{customdata[{i}][1]:,.0f}}/%{{customdata[{i}][2]:,.0f}})<extra></extra>")
                )
            )

        # X축 범위를 조건적으로 설정
        if len(grouped['X_LABEL']) > 10:  # 10개 초과일 경우
            fig.update_layout(
                xaxis=dict(
                    title="장비 그룹 (RES_GROUP_ID)",
                    tickangle=45,  # x축 라벨 각도
                    automargin=True,  # 여백 자동 조정
                    range=[-0.5, 9.5],  # 처음 10개만 표시
                    fixedrange=False,  # 확대/축소 가능
                )
            )
        else:  # 10개 이하일 경우 (스크롤 및 확대/축소 비활성화)
            fig.update_layout(
                xaxis=dict(
                    title="장비 그룹 (RES_GROUP_ID)",
                    tickangle=45,  # x축 라벨 각도
                    automargin=True,  # 여백 자동 조정
                    fixedrange=True,  # 스크롤 및 확대/축소 비활성화
                )
            )

        # 그래프 레이아웃 설정
        fig.update_layout(
            title=title,
            yaxis_title="백분율 (%)",
            barmode='stack',  # 스택형 막대 그래프
            template="plotly_white",
            hovermode="x unified",  # 마우스 오버 시 모든 데이터 표시
            margin=dict(l=10, r=10, t=30, b=70),  # 마진 조정
        )
        return fig

    # Time 데이터 차트 생성
    df_time = df[(df['TARGET_TYPE'] == 'Resource') & (df['CAPA_TYPE'] == 'Time')]
    grouped_time = process_data(df_time)
    fig_time = create_chart(grouped_time, "RES_GROUP_ID별 CAPA Distribution (Time)")

    # Quantity 데이터 차트 생성
    df_quantity = df[(df['TARGET_TYPE'] == 'Resource') & (df['CAPA_TYPE'] == 'Quantity')]
    grouped_quantity = process_data(df_quantity)
    fig_quantity = create_chart(grouped_quantity, "RES_GROUP_ID별 CAPA Distribution (Quantity)")

    # AddResource + Time 데이터 차트 생성
    df_addresource_time = df[(df['TARGET_TYPE'] == 'AddResource') & (df['CAPA_TYPE'] == 'Time')]
    grouped_addresource_time = process_data(df_addresource_time)
    fig_addresource_time = create_chart(grouped_addresource_time, "RES_GROUP_ID별 CAPA Distribution (AddResource + Time)")

    # 그래프 출력
    st.plotly_chart(fig_time, use_container_width=True)
    st.plotly_chart(fig_quantity, use_container_width=True)
    st.plotly_chart(fig_addresource_time, use_container_width=True)

# 실행
if __name__ == "__main__":
    show_page()