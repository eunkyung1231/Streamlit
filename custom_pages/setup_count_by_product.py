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
        st.write("데이터 로드 성공")
        st.dataframe(res.head())

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
                # "Setup" 행의 다음 ITEM_ID를 FROM_ITEM_ID로 설정
                for idx in df.index[:-1]:  # 마지막 줄 제외
                    if df.loc[idx, "ALLOCATION_TYPE"] == "Setup":
                        df.loc[idx, "FROM_ITEM_ID"] = df.loc[idx + 1, "ITEM_ID"]
            return df[df["ALLOCATION_TYPE"] == "Setup"]

        result_res = grouped_res.groupby(["RES_GROUP_ID", "RES_ID", "PLAN_DATE"]).apply(assign_from_item_id).reset_index(drop=True)

        # 필요한 컬럼만 선택
        final_table = result_res[["RES_GROUP_ID", "RES_ID", "PLAN_DATE", "SHIFT_NAME", "ALLOCATION_SEQ", "FROM_ITEM_ID"]]

        # 결과 출력
        st.subheader("Setup 데이터")
        st.dataframe(final_table)

        # CSV 다운로드
        csv = final_table.to_csv(index=False)
        st.download_button(
            label="Setup 데이터 CSV 다운로드",
            data=csv,
            file_name="setup_with_from_item.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
