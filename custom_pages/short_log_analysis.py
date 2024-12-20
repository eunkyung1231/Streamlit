import streamlit as st
import pandas as pd

def show_page(uploaded_files):
    st.title("SHORT LOG 분석")

    # SHORT_LOG.parquet 파일 확인
    if "SHORT_LOG.parquet" not in uploaded_files:
        st.error("SHORT_LOG.parquet 파일이 필요합니다.")
        return

    # SHORT_LOG.parquet 파일 읽기
    file_path = uploaded_files["SHORT_LOG.parquet"]
    df = pd.read_parquet(file_path, engine="pyarrow")

    # SHORT_REASON이 NoOpResourceInfo인 데이터 필터링
    filtered_df = df[df['SHORT_REASON'] == 'NoOpResourceInfo']

    # 결과 출력 및 DEMAND_ITEM_ID 목록 (접기 기능 추가)
    with st.expander("할 수 있는 설비가 없는 DEMAND_ITEM_ID 목록"):
        st.subheader("SHORT_REASON이 'NoOpResourceInfo'인 데이터")
        st.dataframe(filtered_df[['SHORT_REASON'] + [col for col in filtered_df.columns if col != 'SHORT_REASON']])

        st.subheader("DEMAND_ITEM_ID 목록 (중복 제거)")
        unique_demand_items = filtered_df[['DEMAND_ID', 'DEMAND_ITEM_ID']].drop_duplicates().reset_index(drop=True)
        st.dataframe(unique_demand_items)

    # SHIPMENT_PLAN.parquet 파일 확인
    if "SHIPMENT_PLAN.parquet" not in uploaded_files:
        st.error("SHIPMENT_PLAN.parquet 파일이 필요합니다.")
        return

    # SHIPMENT_PLAN.parquet 파일 읽기
    shipment_file_path = uploaded_files["SHIPMENT_PLAN.parquet"]
    shipment_df = pd.read_parquet(shipment_file_path, engine="pyarrow")

    # SHIPMENT_PLAN 테이블에서 DEMAND_ID로 그룹화 및 ON_TIME_QTY와 LATE_QTY 합산 (각 행 반영)
    shipment_df["TOTAL_QTY"] = shipment_df["ON_TIME_QTY"] + shipment_df["LATE_QTY"]
    shipment_grouped = shipment_df.groupby("DEMAND_ID", as_index=False).agg({
        "ON_TIME_QTY": "sum",
        "LATE_QTY": "sum",
        "TOTAL_QTY": "sum"
    })

    # DEMAND.parquet 파일 확인
    if "DEMAND.parquet" not in uploaded_files:
        st.error("DEMAND.parquet 파일이 필요합니다.")
        return

    # DEMAND.parquet 파일 읽기
    demand_file_path = uploaded_files["DEMAND.parquet"]
    demand_df = pd.read_parquet(demand_file_path, engine="pyarrow")

    # DEMAND 테이블에서 TOTAL_QTY와 DEMAND_QTY 계산
    merged_df = pd.merge(demand_df, shipment_grouped, on="DEMAND_ID", how="left")
    merged_df["SHORT_QTY"] = merged_df["DEMAND_QTY"] - merged_df["TOTAL_QTY"].fillna(0)

    # DEMAND_ID가 unique_demand_items의 DEMAND_ID 목록에 있는 경우 SHORT_REASON 추가
    unique_demand_ids_set = set(unique_demand_items['DEMAND_ID'])
    merged_df["SHORT_REASON"] = merged_df["DEMAND_ID"].apply(
        lambda x: "할 수 있는 설비가 없음" if x in unique_demand_ids_set else ""
    )

    # 컬럼 순서 재정렬 (DEMAND_QTY 다음에 ON_TIME_QTY, LATE_QTY, SHORT_QTY, SHORT_REASON 추가)
    demand_columns = list(demand_df.columns)
    new_columns = demand_columns[:demand_columns.index("DEMAND_QTY") + 1] + ["ON_TIME_QTY", "LATE_QTY", "SHORT_QTY"]
    if 'SHORT_REASON' in merged_df.columns:
        new_columns += ["SHORT_REASON"]
    new_columns += demand_columns[demand_columns.index("DEMAND_QTY") + 1:]
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
