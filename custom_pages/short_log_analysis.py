import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def show_page(uploaded_files):
    st.title("SHORT LOG 분석")

    # SHORT_LOG.parquet 파일 확인 및 읽기
    if "SHORT_LOG.parquet" not in uploaded_files:
        st.error("SHORT_LOG.parquet 파일이 필요합니다.")
        return
    short_log = pd.read_parquet(uploaded_files["SHORT_LOG.parquet"], engine="pyarrow")

    # SHIPMENT_PLAN.parquet 파일 확인 및 읽기
    if "SHIPMENT_PLAN.parquet" not in uploaded_files:
        st.error("SHIPMENT_PLAN.parquet 파일이 필요합니다.")
        return
    shipment_plan = pd.read_parquet(uploaded_files["SHIPMENT_PLAN.parquet"], engine="pyarrow")

    # DEMAND.parquet 파일 확인 및 읽기
    if "DEMAND.parquet" not in uploaded_files:
        st.error("DEMAND.parquet 파일이 필요합니다.")
        return
    demand = pd.read_parquet(uploaded_files["DEMAND.parquet"], engine="pyarrow")

    # SHORT_LOG 데이터 처리
    filtered_df = short_log[short_log['SHORT_REASON'] == 'NoOpResourceInfo']
    unique_demand_items = filtered_df[['DEMAND_ID', 'DEMAND_ITEM_ID']].drop_duplicates().reset_index(drop=True)

    # DEMAND_ID와 OPER_ID 매핑
    demand_oper_mapping = filtered_df[['DEMAND_ID', 'OPER_ID']].drop_duplicates()

    # SHIPMENT_PLAN 데이터 처리
    shipment_plan["TOTAL_QTY"] = shipment_plan["ON_TIME_QTY"] + shipment_plan["LATE_QTY"]
    shipment_grouped = shipment_plan.groupby("DEMAND_ID", as_index=False).agg({
        "ON_TIME_QTY": "sum",
        "LATE_QTY": "sum",
        "TOTAL_QTY": "sum"
    })

    # DEMAND 데이터와 결합
    merged_df = pd.merge(demand, shipment_grouped, on="DEMAND_ID", how="left")
    merged_df = pd.merge(merged_df, short_log[['DEMAND_ID', 'SHORT_REASON']], on="DEMAND_ID", how="left")
    merged_df["SHORT_QTY"] = merged_df["DEMAND_QTY"] - merged_df["TOTAL_QTY"].fillna(0)

    # 첫 번째 조건: SHORT_QTY > 0이고 SHORT_REASON이 NoOpResourceInfo인 경우
    no_op_resource_info_ids = set(short_log[short_log["SHORT_REASON"] == "NoOpResourceInfo"]["DEMAND_ID"])
    merged_df["REASON"] = merged_df.apply(
        lambda row: f"{short_log.loc[short_log['DEMAND_ID'] == row['DEMAND_ID'], 'OPER_ID'].iloc[0]} 공정에서 사용 할 수 있는 설비가 없음"
        if row["SHORT_QTY"] > 0 and row["DEMAND_ID"] in no_op_resource_info_ids else "",
        axis=1
    )

    # 두 번째 조건: SHORT_QTY > 0이고 REASON이 빈 값이며 SHORT_LOG에서 SHORT_REASON이 NoBwBomPathShort
    no_reason_df = merged_df[(merged_df["SHORT_QTY"] > 0) & (merged_df["REASON"] == "")]
    short_log_mapping = short_log[short_log["SHORT_REASON"] == "NoBwBomPathShort"]
    bom_issue_ids = set(short_log_mapping["DEMAND_ID"])
    merged_df.loc[
        (merged_df["DEMAND_ID"].isin(bom_issue_ids)) & (merged_df["SHORT_QTY"] > 0) & (merged_df["REASON"] == ""),
        "REASON"
    ] = "투입까지 전개할 수 있는 BOM 정보가 없음"

    # 세 번째 조건: SHORT_QTY > 0이고 REASON이 빈 값이며 SHORT_LOG에서 SHORT_REASON이 LackOfResourceCapacity
    lack_of_capacity_mapping = short_log[short_log["SHORT_REASON"] == "LackOfResourceCapacity"]
    capacity_issue_ids = set(lack_of_capacity_mapping["DEMAND_ID"])
    merged_df.loc[
        (merged_df["DEMAND_ID"].isin(capacity_issue_ids)) & (merged_df["SHORT_QTY"] > 0) & (merged_df["REASON"] == ""),
        "REASON"
    ] = merged_df.loc[
        (merged_df["DEMAND_ID"].isin(capacity_issue_ids)) & (merged_df["SHORT_QTY"] > 0) & (merged_df["REASON"] == ""),
        "DEMAND_ID"
    ].apply(lambda x: f"{short_log.loc[short_log['DEMAND_ID'] == x, 'OPER_ID'].iloc[0]} 공정에서 사용할 수 있는 설비 Capa가 부족" if x in short_log["DEMAND_ID"].values else "Unknown")

    # 네 번째 조건: SHORT_QTY > 0이고 REASON이 빈 값이며 SHORT_LOG에서 SHORT_REASON이 RemainingLots
    remaining_lots_mapping = short_log[short_log["SHORT_REASON"] == "RemainingLots"]
    remaining_lots_ids = set(remaining_lots_mapping["DEMAND_ID"])
    merged_df.loc[
        (merged_df["DEMAND_ID"].isin(remaining_lots_ids)) & (merged_df["SHORT_QTY"] > 0) & (merged_df["REASON"] == ""),
        "REASON"
    ] = "계획 생성 기간 내에 생산하지 못한 잔여 수량임. (계획 생성 기간을 늘릴 경우 생산할 수 있는 가능성이 있음.)"

    # 컬럼 재정렬
    demand_columns = list(demand.columns)
    new_columns = demand_columns[:demand_columns.index("DEMAND_QTY") + 1] + ["ON_TIME_QTY", "LATE_QTY", "SHORT_QTY", "SHORT_REASON", "REASON"] + demand_columns[demand_columns.index("DEMAND_QTY") + 1:]
    merged_df = merged_df[new_columns]

    # 결과 출력
    st.subheader("SHORT_QTY 계산 결과 및 REASON 분석")
    st.dataframe(merged_df)

    # 데이터 준비
    pie_data = merged_df[["ON_TIME_QTY", "LATE_QTY", "SHORT_QTY"]].sum()

    # 데이터프레임 생성 (Plotly 입력용)
    pie_chart_data = pd.DataFrame({
        "Category": ["ON_TIME_QTY", "LATE_QTY", "SHORT_QTY"],
        "Value": pie_data
    })

    # 파이차트 생성
    fig = px.pie(
        pie_chart_data,
        names="Category",
        values="Value",
        color="Category",
        color_discrete_map={
            "ON_TIME_QTY": "#48C2B0",  
            "LATE_QTY": "#F8A076",   
            "SHORT_QTY": "#D85F6B"  
        },
        title="DEMAND_QTY 구성 비율 분석",
        hole=0.4  # 도넛 형태로 표시
    )

    # 툴팁 커스터마이징 (소수점 없이 반올림 처리)
    fig.update_traces(
        hovertemplate="<b>%{label}</b>: %{value:,.0f} (%{percent:.1%})",  # .0f는 정수로 표시
        textinfo="percent"  # 차트에는 퍼센트만 표시
    )

    # Streamlit에서 차트 표시
    st.plotly_chart(fig)

if __name__ == "__main__":
    uploaded_files = {
        "SHORT_LOG.parquet": "path/to/SHORT_LOG.parquet",
        "SHIPMENT_PLAN.parquet": "path/to/SHIPMENT_PLAN.parquet",
        "DEMAND.parquet": "path/to/DEMAND.parquet"
    }
    show_page(uploaded_files)
