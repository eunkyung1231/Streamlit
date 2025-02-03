import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def show_page(uploaded_files):
    st.title("설비 대기 ITEM별 재공 수량")

    # LOT_HISTORY.parquet 파일 확인 및 읽기
    if "LOT_HISTORY.parquet" not in uploaded_files:
        st.error("LOT_HISTORY.parquet 파일이 필요합니다.")
        return
    short_log = pd.read_parquet(uploaded_files["LOT_HISTORY.parquet"], engine="pyarrow")

    # RES_PLAN.parquet 파일 확인 및 읽기
    if "RES_PLAN.parquet" not in uploaded_files:
        st.error("RES_PLAN.parquet 파일이 필요합니다.")
        return
    shipment_plan = pd.read_parquet(uploaded_files["RES_PLAN.parquet"], engine="pyarrow")

    # LOT_HISTORY 테이블 데이터 처리 (DEMAND_ID가 'SafetyStock'으로 시작하는 데이터 제거)
    short_log = short_log[~short_log["DEMAND_ID"].astype(str).str.startswith("SafetyStock")]
    short_log = short_log[short_log["EVENT_TYPE"] == "Creation"].copy()
    short_log["EVENT_DATETIME"] = pd.to_datetime(short_log["EVENT_DATETIME"]).dt.date
    lot_grouped = (
        short_log.groupby(["EVENT_DATETIME", "ITEM_ID", "BUFFER_ID"])["LOT_QTY"]
        .sum()
        .reset_index()
    )

    # RES_PLAN 테이블 데이터 처리 (DEMAND_ID가 'SafetyStock'으로 시작하는 데이터 제거)
    shipment_plan = shipment_plan[~shipment_plan["DEMAND_ID"].astype(str).str.startswith("SafetyStock")]
    shipment_plan["PLAN_DATE"] = pd.to_datetime(shipment_plan["PLAN_DATE"]).dt.date
    res_grouped = (
        shipment_plan.groupby(["PLAN_DATE", "ITEM_ID", "BUFFER_ID"])["PLAN_QTY"]
        .sum()
        .reset_index()
    )

    # LOT_HISTORY와 RES_PLAN 데이터 병합 및 차이 계산
    merged_data = pd.merge(lot_grouped, res_grouped, left_on=["EVENT_DATETIME", "ITEM_ID", "BUFFER_ID"],
                           right_on=["PLAN_DATE", "ITEM_ID", "BUFFER_ID"], how="left").fillna(0)
    merged_data["WAITING_WIP_QTY"] = merged_data["LOT_QTY"] - merged_data["PLAN_QTY"]
    merged_data = merged_data[["EVENT_DATETIME", "ITEM_ID", "BUFFER_ID", "LOT_QTY", "PLAN_QTY", "WAITING_WIP_QTY"]]

    # BUFFER_ID와 ITEM_ID 기준으로 그룹화
    buffer_grouped = merged_data.groupby(["EVENT_DATETIME", "BUFFER_ID", "ITEM_ID"])[["WAITING_WIP_QTY"]].sum().reset_index()

    # 결과 출력
    st.subheader("일별 ITEM별 재공 수량")
    st.dataframe(lot_grouped)

    st.subheader("일별 ITEM별 PLAN_QTY")
    st.dataframe(res_grouped)

    st.subheader("BUFFER_ID별 ITEM_ID별 일별 잔여 재공 수량")
    st.dataframe(buffer_grouped)

    # 시각화
    st.subheader("📈 BUFFER_ID별 ITEM_ID별 날짜별 재공 수량 변화")
    fig = go.Figure()

    for (buffer_id, item_id) in buffer_grouped.groupby(["BUFFER_ID", "ITEM_ID"]).groups.keys():
        buffer_data = buffer_grouped[(buffer_grouped["BUFFER_ID"] == buffer_id) & (buffer_grouped["ITEM_ID"] == item_id)]
        fig.add_trace(go.Scatter(
            x=buffer_data["EVENT_DATETIME"],
            y=buffer_data["WAITING_WIP_QTY"],
            mode="lines+markers",
            name=f"BUFFER_ID: {buffer_id}, ITEM_ID: {item_id}"
        ))

    fig.update_layout(
        title="BUFFER_ID별 ITEM_ID별 날짜별 재공 수량 변화",
        xaxis_title="날짜",
        yaxis_title="잔여 재공 수량",
        legend_title="BUFFER_ID - ITEM_ID"
    )

    st.plotly_chart(fig)
