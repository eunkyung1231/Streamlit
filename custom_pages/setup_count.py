import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def process_factory_config(con, total_shift_count):
    # FACTORY_START_TIME을 datetime 형식으로 변환
    con['FACTORY_START_TIME'] = pd.to_datetime(con['FACTORY_START_TIME'], format='%H:%M:%S', errors='coerce').dt.time

    # SHIFT_NAME에서 문자열 변환 및 처리
    con['SHIFT_NAME'] = con['SHIFT_NAME'].astype(str).str.replace(" ", "").str.split(",")
    con['SHIFT_COUNT'] = con['SHIFT_NAME'].apply(len)

    # 24 / total_shift_count 계산
    shift_duration = 24 / total_shift_count  # 시간 단위
    shift_duration_timedelta = timedelta(hours=shift_duration)

    # CALCULATED_TIME 생성
    con['CALCULATED_TIME'] = con['FACTORY_START_TIME'].apply(
        lambda x: (datetime.combine(datetime.today(), x) + shift_duration_timedelta).time()
        if pd.notnull(x) else None
    )
    return con

def process_res_plan(res, factory_start_time, calculated_time):
    # RES_PLAN에서 ALLOCATION_TYPE이 'Setup'인 데이터만 필터링
    res_filtered = res[res['ALLOCATION_TYPE'] == 'Setup']

    # SHIFT 컬럼 추가
    def determine_shift(res_end_datetime):
        if factory_start_time and calculated_time:
            if factory_start_time < res_end_datetime.time() <= calculated_time:
                return "주간"
            elif res_end_datetime.time() > calculated_time or res_end_datetime.time() <= factory_start_time:
                return "야간"
        return None

    res_filtered['SHIFT'] = res_filtered['RES_END_DATETIME'].apply(determine_shift)

    # PLAN_DATE와 SHIFT 추가 그룹화
    grouped_with_plan_date = res_filtered.groupby(['RES_GROUP_ID', 'RES_ID', 'PLAN_DATE', 'SHIFT']).size().reset_index(name='COUNT')

    return grouped_with_plan_date

def show_page(uploaded_files):
    st.title("설비별 Setup 횟수")

    # 파일 검사
    if "FACTORY_CONFIG.parquet" not in uploaded_files or "RES_PLAN.parquet" not in uploaded_files:
        st.error("FACTORY_CONFIG.parquet와 RES_PLAN.parquet 파일이 모두 필요합니다.")
        return

    # Parquet 파일 읽기
    con = pd.read_parquet(uploaded_files["FACTORY_CONFIG.parquet"], engine='pyarrow')
    res = pd.read_parquet(uploaded_files["RES_PLAN.parquet"], engine='pyarrow')

    # FACTORY_CONFIG 처리
    total_shift_count = 2  # 이 값은 동적으로 계산하거나 설정할 수 있습니다.
    con = process_factory_config(con, total_shift_count)

    # FACTORY_START_TIME과 CALCULATED_TIME 추출
    factory_start_time = con['FACTORY_START_TIME'].iloc[0] if not con.empty else None
    calculated_time = con['CALCULATED_TIME'].iloc[0] if not con.empty else None

    # FACTORY_START_TIME과 CALCULATED_TIME 표시
    st.subheader("Factory Config 시간 정보")
    st.write(f"FACTORY_START_TIME: {factory_start_time}")
    st.write(f"CALCULATED_TIME: {calculated_time}")

    # RES_PLAN 처리
    grouped_with_plan_date = process_res_plan(res, factory_start_time, calculated_time)

    # PLAN_DATE와 SHIFT 추가 그룹화된 결과 표시
    st.subheader("PLAN_DATE 기준 그룹화 결과")
    st.dataframe(grouped_with_plan_date)

if __name__ == "__main__":
    # 테스트용 경로를 여기에 추가하세요
    uploaded_files = {
        "FACTORY_CONFIG.parquet": "path/to/FACTORY_CONFIG.parquet",
        "RES_PLAN.parquet": "path/to/RES_PLAN.parquet"
    }
    show_page(uploaded_files)
