import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def show_page(found_files):
    st.title("공정별 생산량 분석")

    # RES_PLAN.parquet 파일 확인
    if "RES_PLAN.parquet" not in found_files:
        st.error("RES_PLAN.parquet 파일이 필요합니다.")
        return

    # RES_PLAN.parquet 파일 읽기
    file_path = found_files["RES_PLAN.parquet"]
    df = pd.read_parquet(file_path, engine="pyarrow")

    # 필터링 조건 적용
    filtered_df = df[
        (df['ALLOCATION_TYPE'] == 'Allocate') & 
        (df['OPER_ID'].notnull())
    ]

    # PLAN_DATE를 datetime 형식으로 변환
    filtered_df['PLAN_DATE'] = pd.to_datetime(filtered_df['PLAN_DATE'])

    # OPER_ID 선택 박스 생성 (페이지 내부)
    unique_oper_ids = filtered_df['OPER_ID'].unique()
    selected_oper_id = st.selectbox("OPER_ID를 선택하세요", unique_oper_ids)

    # 선택한 OPER_ID로 필터링
    filtered_df = filtered_df[filtered_df['OPER_ID'] == selected_oper_id]

    # 일별 그룹화 - PLAN_DATE에 있는 날짜만 사용
    daily_df = filtered_df.groupby(['PLAN_DATE'], as_index=False)['PLAN_QTY'].sum()
    daily_df['OPER_ID'] = selected_oper_id
    daily_df = daily_df[['PLAN_DATE', 'OPER_ID', 'PLAN_QTY']]  # 컬럼 순서 조정

    # 주별 그룹화 (yyyy-mm 형식으로 포맷)
    filtered_df['WEEK'] = filtered_df['PLAN_DATE'].dt.to_period('W').astype(str)
    weekly_df = filtered_df.groupby(['WEEK'], as_index=False)['PLAN_QTY'].sum()

    # 월별 그룹화 (yyyy-mm 형식)
    filtered_df['MONTH'] = filtered_df['PLAN_DATE'].dt.to_period('M').astype(str)
    monthly_df = filtered_df.groupby(['MONTH'], as_index=False)['PLAN_QTY'].sum()

    # 결과 표시
    st.subheader(f"선택된 OPER_ID: {selected_oper_id}")
    st.subheader("일별 생산량")
    st.dataframe(daily_df)

    # 시각화: 일별 그래프
    st.subheader("일별 생산량 그래프")
    fig_daily = px.bar(
        daily_df,
        x='PLAN_DATE',
        y='PLAN_QTY',
        title="일별 생산량",
        labels={"PLAN_QTY": "생산량", "PLAN_DATE": "날짜"}
    )

    # X축 조건: 20개씩 스크롤되면서 각 막대에 모든 날짜 표시
    if len(daily_df['PLAN_DATE']) > 20:
        fig_daily.update_layout(
            xaxis=dict(
                tickmode='linear',
                dtick=86400000.0,  # 하루 단위(ms 기준)
                tickformat="%Y-%m-%d",
                range=[daily_df['PLAN_DATE'].iloc[0], daily_df['PLAN_DATE'].iloc[19]],
                fixedrange=False  # 스크롤 가능
            )
        )
    else:
        fig_daily.update_xaxes(
            tickmode='linear',
            dtick=86400000.0,  # 하루 단위
            tickformat="%Y-%m-%d",
            fixedrange=True
        )

    st.plotly_chart(fig_daily, use_container_width=True)

    # 시각화: 주별 그래프
    st.subheader("주별 생산량 그래프")
    fig_weekly = px.bar(
        weekly_df,
        x='WEEK',
        y='PLAN_QTY',
        title="주별 생산량",
        labels={"PLAN_QTY": "생산량", "WEEK": "주 (yyyy-mm)"}
    )
    fig_weekly.update_xaxes(type='category')  # X축 항목을 명확하게 문자열로 처리
    st.plotly_chart(fig_weekly, use_container_width=True)

    # 시각화: 월별 그래프
    st.subheader("월별 생산량 그래프")
    fig_monthly = px.bar(
        monthly_df,
        x='MONTH',
        y='PLAN_QTY',
        title="월별 생산량",
        labels={"PLAN_QTY": "생산량", "MONTH": "월 (yyyy-mm)"}
    )
    fig_monthly.update_xaxes(type='category')  # X축 항목을 명확하게 문자열로 처리
    st.plotly_chart(fig_monthly, use_container_width=True)


if __name__ == "__main__":
    show_page({"RES_PLAN.parquet": "path/to/RES_PLAN.parquet"})
