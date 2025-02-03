import streamlit as st
import pandas as pd
import plotly.express as px

def show_page(uploaded_files):
    st.title("설비 대기 ITEM별 재공 수량(Unitus)")

    # LOT_HISTORY.parquet 파일 확인 및 읽기
    if "LOT_HISTORY.parquet" not in uploaded_files:
        st.error("LOT_HISTORY.parquet 파일이 필요합니다.")
        return
    lot_history = pd.read_parquet(uploaded_files["LOT_HISTORY.parquet"], engine="pyarrow")

    # 데이터 필터링: EVENT_TYPE == "Creation"
    lot_history = lot_history[lot_history["EVENT_TYPE"] == "Creation"].copy()

    # 날짜 변환 (YYYY-MM-DD)
    lot_history["EVENT_DATETIME"] = pd.to_datetime(lot_history["EVENT_DATETIME"]).dt.date

    # 날짜별 + ITEM_ID별 LOT_QTY 합산
    grouped_data = (
        lot_history.groupby(["EVENT_DATETIME", "ITEM_ID"])["LOT_QTY"]
        .sum()
        .reset_index()
    )

    # 📌 테이블 출력
    st.subheader("📊 일별 ITEM별 재공 수량 집계")
    st.dataframe(grouped_data)

    # 📊 시각화 (Plotly 사용)
    st.subheader("📈 날짜별 ITEM 재공 수량 변화")

    fig = px.line(
        grouped_data,
        x="EVENT_DATETIME",
        y="LOT_QTY",
        color="ITEM_ID",
        markers=True,
        title="날짜별 ITEM 재공 수량 추이"
    )
    
    st.plotly_chart(fig)

