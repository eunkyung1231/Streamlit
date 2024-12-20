import streamlit as st
import pandas as pd

def load_parquet(file_name, uploaded_files):
    if file_name not in uploaded_files:
        st.error(f"{file_name} 파일이 필요합니다.")
        return None
    return pd.read_parquet(uploaded_files[file_name], engine="pyarrow")

def show_page(uploaded_files):
    st.title("SHORT LOG 분석")

    # 파일 로드
    short_log = load_parquet("SHORT_LOG.parquet", uploaded_files)
    shipment_plan = load_parquet("SHIPMENT_PLAN.parquet", uploaded_files)
    demand = load_parquet("DEMAND.parquet", uploaded_files)

    if short_log is None or shipment_plan is None or demand is None:
        return

    # SHORT_LOG 데이터 처리
    filtered_df = short_log[short_log['SHORT_REASON'] == 'NoOpResourceInfo']
    with st.expander("할 수 있는 설비가 없는 DEMAND_ITEM_ID 목록"):
        st.dataframe(filtered_df[['SHORT_REASON'] + [col for col in filtered_df.columns if col != 'SHORT_REASON']])
        unique_demand_items = filtered_df[['DEMAND_ID', 'DEMAND_ITEM_ID']].drop_duplicates().reset_index(drop=True)
        st.dataframe(unique_demand_items)

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
    merged_df["SHORT_QTY"] = merged_df["DEMAND_QTY"] - merged_df["TOTAL_QTY"].fillna(0)

    # REASON 업데이트 (SHORT_QTY > 0인 경우에만 적용)
    demand_oper_mapping_dict = dict(zip(demand_oper_mapping["DEMAND_ID"], demand_oper_mapping["OPER_ID"]))
    merged_df["REASON"] = merged_df.apply(
        lambda row: f"{demand_oper_mapping_dict[row['DEMAND_ID']]} 공정에서 사용 할 수 있는 설비가 없음"
        if row["SHORT_QTY"] > 0 and row["DEMAND_ID"] in demand_oper_mapping_dict else "",
        axis=1
    )

    # 컬럼 재정렬
    demand_columns = list(demand.columns)
    new_columns = demand_columns[:demand_columns.index("DEMAND_QTY") + 1] + ["ON_TIME_QTY", "LATE_QTY", "SHORT_QTY", "REASON"] + demand_columns[demand_columns.index("DEMAND_QTY") + 1:]
    merged_df = merged_df[new_columns]

    # 결과 출력
    st.subheader("DEMAND 테이블 및 SHORT_QTY 계산 결과")
    st.dataframe(merged_df)

if __name__ == "__main__":
    uploaded_files = {
        "SHORT_LOG.parquet": "path/to/SHORT_LOG.parquet",
        "SHIPMENT_PLAN.parquet": "path/to/SHIPMENT_PLAN.parquet",
        "DEMAND.parquet": "path/to/DEMAND.parquet"
    }
    show_page(uploaded_files)
