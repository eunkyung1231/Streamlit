import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def show_page(uploaded_files):
    st.title("장비 그룹별 가동율 현황")

    # 파일 검사
    if "CAPA_ALLOCATION_INFO.parquet" not in uploaded_files:
        st.error("CAPA_ALLOCATION_INFO.parquet 파일이 업로드되지 않았습니다.")
        return

    # Parquet 파일 읽기
    df = pd.read_parquet(uploaded_files["CAPA_ALLOCATION_INFO.parquet"], engine='pyarrow')

    # 조건 필터링 및 그룹화 로직 (공통 함수)
    def process_data(df_filtered):
        if df_filtered.empty:  # 필터링된 데이터가 없는 경우
            return pd.DataFrame()  # 빈 데이터프레임 반환

        grouped = df_filtered.groupby('RES_GROUP_ID').agg({
            'TOTAL_CAPA': 'sum',
            'OFF_TIME_CAPA': 'sum',
            'ALLOCATION_CAPA': 'sum',
            'PM_CAPA': 'sum',
            'SETUP_CAPA': 'sum',
            'REMAIN_CAPA': 'sum'
        }).reset_index()

        if grouped.empty:  # 그룹화 결과가 빈 경우
            return pd.DataFrame()

        # 비율 계산
        grouped['OFF_TIME_CAPA_%'] = (grouped['OFF_TIME_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['ALLOCATION_CAPA_%'] = (grouped['ALLOCATION_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['PM_CAPA_%'] = (grouped['PM_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['SETUP_CAPA_%'] = (grouped['SETUP_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['REMAIN_CAPA_%'] = (grouped['REMAIN_CAPA'] / grouped['TOTAL_CAPA']) * 100

        # Allocation_capa 퍼센티지 기준으로 정렬
        grouped = grouped.sort_values(by='ALLOCATION_CAPA_%', ascending=False)

        # X축 레이블: RES_GROUP_ID만 표시
        grouped['X_LABEL'] = grouped['RES_GROUP_ID']

        # customdata 생성
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

    # X축 스크롤 모드 활성화 함수
    def create_chart(grouped, title):
        if grouped.empty:  # 데이터프레임이 빈 경우
            st.warning(f"{title} 에 대한 데이터가 없습니다.")
            return None

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
                    customdata=np.stack(grouped['customdata'].to_numpy()),
                    hovertemplate=(f"{category.capitalize()}: %{{customdata[{i}][0]:.2f}}% "
                                f"(%{{customdata[{i}][1]:,.0f}}/%{{customdata[{i}][2]:,.0f}})<extra></extra>"),
                )
            )

        # X축 스크롤링 조건 설정 (10개 초과일 경우만)
        if len(grouped['X_LABEL']) > 10:
            fig.update_layout(
                xaxis=dict(
                    title="장비 그룹 (RES_GROUP_ID)",
                    tickangle=45,
                    automargin=True,
                    range=[-0.5, 9.5],  # 처음에 처음 10개만 보이도록 설정
                    fixedrange=False,  # 확대/축소 가능
                )
            )
        else:
            fig.update_layout(
                xaxis=dict(
                    title="장비 그룹 (RES_GROUP_ID)",
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


    # 데이터 필터링 및 차트 생성
    df_time = df[(df['TARGET_TYPE'] == 'Resource') & (df['CAPA_TYPE'] == 'Time')]
    grouped_time = process_data(df_time)

    df_quantity = df[(df['TARGET_TYPE'] == 'Resource') & (df['CAPA_TYPE'] == 'Quantity')]
    grouped_quantity = process_data(df_quantity)

    df_addresource_time = df[(df['TARGET_TYPE'] == 'AddResource') & (df['CAPA_TYPE'] == 'Time')]
    grouped_addresource_time = process_data(df_addresource_time)

    # 그래프 생성 및 표시
    fig_time = create_chart(grouped_time, "RES_GROUP_ID별 CAPA Distribution (Time)")
    if fig_time:
        st.plotly_chart(fig_time, use_container_width=True)

    fig_quantity = create_chart(grouped_quantity, "RES_GROUP_ID별 CAPA Distribution (Quantity)")
    if fig_quantity:
        st.plotly_chart(fig_quantity, use_container_width=True)

    fig_addresource_time = create_chart(grouped_addresource_time, "RES_GROUP_ID별 CAPA Distribution (AddResource + Time)")
    if fig_addresource_time:
        st.plotly_chart(fig_addresource_time, use_container_width=True)

if __name__ == "__main__":
    show_page()
