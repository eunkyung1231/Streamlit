import streamlit as st
import pandas as pd

def show_page(uploaded_files):
    st.title("제품별 Setup 횟수")

    if "RES_PLAN.parquet" not in uploaded_files:
        st.error("RES_PLAN.parquet 파일이 필요합니다.")
        return

    try:
        # 데이터 로드
        res = pd.read_parquet(uploaded_files["RES_PLAN.parquet"], engine="pyarrow")

        # ALLOCATION_TYPE 필터링
        filtered_res = res[res['ALLOCATION_TYPE'].isin(["Allocate", "Setup"])]
        if filtered_res.empty:
            st.warning("필터링된 데이터가 없습니다.")
            return

        # 그룹화 및 정렬
        grouped_res = (
            filtered_res.groupby(["RES_GROUP_ID", "RES_ID", "PLAN_DATE"])
            .apply(lambda x: x.sort_values(by="START_DATETIME"))
            .reset_index(drop=True)
        )

        # FROM_ITEM_ID 생성 로직
        def assign_from_item_id(df):
            df["FROM_ITEM_ID"] = None
            if not df.empty:
                for idx in df.index[:-1]:  # 마지막 줄 제외
                    if df.loc[idx, "ALLOCATION_TYPE"] == "Setup":
                        df.loc[idx, "FROM_ITEM_ID"] = df.loc[idx + 1, "ITEM_ID"]
            return df[df["ALLOCATION_TYPE"] == "Setup"]

        result_res = grouped_res.groupby(["RES_GROUP_ID", "RES_ID", "PLAN_DATE"]).apply(assign_from_item_id).reset_index(drop=True)

        # 필요한 컬럼만 선택
        final_table = result_res[["RES_GROUP_ID", "RES_ID", "PLAN_DATE", "FROM_ITEM_ID"]]

        # 그룹화하여 COUNT 계산
        grouped_count = (
            final_table.groupby(["RES_GROUP_ID", "RES_ID", "PLAN_DATE", "FROM_ITEM_ID"])
            .size()
            .reset_index(name="COUNT")
        )

        # COUNT가 2 이상인 데이터 필터링
        filtered_table = grouped_count[grouped_count["COUNT"] >= 2]

        # 결과 출력
        st.subheader("제품별 Setup 횟수")
        st.dataframe(grouped_count)

        st.subheader("제품별 Setup 횟수가 2번 이상인 데이터")
        st.dataframe(filtered_table)

    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
