import streamlit as st
import pandas as pd

def show_page():
    st.title("TARGET 대비 CAPA 분석 - Operation 데이터 확인")

    # 파일 경로 지정
    target_plan_path = 'D:\Model\Production_SHINSUNG\P-20241211-M-02_Engine_20241211152108\Experiment 1\Result 0\TARGET_PLAN.parquet'
    routing_oper_path = 'D:\Model\Production_SHINSUNG\P-20241211-M-02_Engine_20241211152108\Data\ROUTING_OPER.parquet'
    oper_res_path = 'D:\Model\Production_SHINSUNG\P-20241211-M-02_Engine_20241211152108\Data\OPER_RES.parquet'

    try:
        # Parquet 파일 읽기
        target_plan_df = pd.read_parquet(target_plan_path, engine='pyarrow')
        routing_oper_df = pd.read_parquet(routing_oper_path, engine='pyarrow')
        oper_res_df = pd.read_parquet(oper_res_path, engine='pyarrow')

        # IN_OUT 컬럼 값 정리
        target_plan_df['IN_OUT'] = target_plan_df['IN_OUT'].str.strip()

        # IN_OUT == 'Out'이고 ROUTING_ID와 OPER_ID가 빈값이 아닌 데이터 필터링
        valid_out_df = target_plan_df[
            (target_plan_df['IN_OUT'] == 'Out') &
            target_plan_df['ROUTING_ID'].notnull() & (target_plan_df['ROUTING_ID'] != "") &
            target_plan_df['OPER_ID'].notnull() & (target_plan_df['OPER_ID'] != "")
        ]
        st.write(f"IN_OUT == 'Out' 이고 ROUTING_ID 및 OPER_ID가 빈값이 아닌 행 수: {valid_out_df.shape[0]}")

        # ROUTING_ID와 OPER_ID를 키로 ROUTING_OPER 테이블에서 데이터 찾기
        merged_data = valid_out_df.merge(
            routing_oper_df,
            on=['ROUTING_ID', 'OPER_ID'],
            how='left'
        )

        # OPER_TYPE이 'Operation'인 행 필터링
        operation_rows = merged_data[merged_data['OPER_TYPE'] == 'Operation']
        st.write(f"IN_OUT == 'Out' 이고 ROUTING_ID 및 OPER_ID가 빈값이 아니고 OPER_TYPE == 'Operation' 인 행 수: {operation_rows.shape[0]}")

        # OPER_TYPE이 'Operation'인 데이터 표시
        st.write("IN_OUT == 'Out' 이고 ROUTING_ID 및 OPER_ID가 빈값이 아니고 OPER_TYPE == 'Operation' 인 데이터:")
        st.dataframe(operation_rows.reset_index(drop=True))

        # ITEM_ID, ROUTING_ID와 OPER_ID를 그룹으로 TARGET_QTY의 합 계산
        grouped_data = operation_rows.groupby(['ITEM_ID', 'ROUTING_ID', 'OPER_ID'])['TARGET_QTY'].sum().reset_index()

        # ROUTING_ID와 OPER_ID를 키로 OPER_RES 테이블에서 매칭된 행 수 계산, AVG_USAGE_PER 및 RES_IDS 생성
        resource_usage = oper_res_df.groupby(['ROUTING_ID', 'OPER_ID']).agg(
            RES_COUNT=('USAGE_PER', 'size'),
            RES_IDS=('RES_ID', lambda x: ','.join(x.astype(str))),
            AVG_USAGE_PER=('USAGE_PER', 'mean')
        ).reset_index()

        # RES_COUNT, RES_IDS, AVG_USAGE_PER을 ITEM_ID, ROUTING_ID, OPER_ID 그룹 데이터에 추가
        grouped_data = grouped_data.merge(
            resource_usage,
            on=['ROUTING_ID', 'OPER_ID'],
            how='left'
        )

        # DAILY_MAX_OUTPUT 계산
        grouped_data['DAILY_MAX_OUTPUT'] = 86400 / grouped_data['AVG_USAGE_PER']

        # NEED_DAYS 계산
        grouped_data['NEED_DAYS'] = grouped_data['TARGET_QTY'] / (grouped_data['DAILY_MAX_OUTPUT'] * grouped_data['RES_COUNT'])

        # 결과 데이터에서 ROUTING_ID는 제거
        grouped_data = grouped_data.drop(columns=['ROUTING_ID'], errors='ignore')

        # 차트에 표시하기 전 소수점 셋째 자리에서 반올림
        display_data = grouped_data.copy()
        display_data['TARGET_QTY'] = display_data['TARGET_QTY'].round(3)
        display_data['RES_COUNT'] = display_data['RES_COUNT'].round(3)
        display_data['AVG_USAGE_PER'] = display_data['AVG_USAGE_PER'].round(3)
        display_data['DAILY_MAX_OUTPUT'] = display_data['DAILY_MAX_OUTPUT'].round(3)
        display_data['NEED_DAYS'] = display_data['NEED_DAYS'].round(3)

        st.write("ITEM_ID를 그룹으로 TARGET_QTY 합계, OPER_ID, RES_COUNT, RES_IDS, AVG_USAGE_PER, DAILY_MAX_OUTPUT 및 NEED_DAYS 계산:")
        st.dataframe(display_data[['ITEM_ID', 'OPER_ID', 'TARGET_QTY', 'RES_COUNT', 'RES_IDS', 'AVG_USAGE_PER', 'DAILY_MAX_OUTPUT', 'NEED_DAYS']])

    except Exception as e:
        st.error(f"Error reading or processing the file: {e}")

# 실행
if __name__ == "__main__":
    show_page()
