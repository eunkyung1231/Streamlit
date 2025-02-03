import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def show_page(uploaded_files):
    st.title("설비 대기 OPER&ITEM별 재공 수량")

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