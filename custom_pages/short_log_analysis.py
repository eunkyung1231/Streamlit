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

    # 결과 출력
    st.subheader("SHORT_REASON이 'NoOpResourceInfo'인 데이터")
    st.dataframe(filtered_df[['SHORT_REASON'] + [col for col in filtered_df.columns if col != 'SHORT_REASON']])

    # DEMAND_ITEM_ID 중복 제거 및 출력
    unique_demand_items = filtered_df['DEMAND_ITEM_ID'].drop_duplicates().reset_index(drop=True)
    st.subheader("DEMAND_ITEM_ID 목록 (중복 제거)")
    st.dataframe(unique_demand_items)

if __name__ == "__main__":
    uploaded_files = {"SHORT_LOG.parquet": "path/to/SHORT_LOG.parquet"}
    show_page(uploaded_files)
