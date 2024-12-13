import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# "DEMAND_QTY 분석" 메뉴 선택 시
def show_page():
    st.title("DEMAND_QTY 분석 (일별, 주별, 월별)")

    # Parquet 파일 경로 지정
    model_path = 'D:\\Model\\Production_SHINSUNG\\P-20241211-M-02_Engine_20241211152108\\Data\\'
    file_path = 'DEMAND.parquet'

    # Parquet 파일 읽기
    df = pd.read_parquet(model_path + file_path, engine='pyarrow')

    # 날짜 데이터 형식 변환
    df['DUE_DATE'] = pd.to_datetime(df['DUE_DATE'])

    # ---------------------
    # 일별 분석
    # ---------------------
    st.subheader("1. 일별 DEMAND_QTY 분석")

    # 일별 데이터 그룹화
    daily_grouped_df = (
        df.groupby("DUE_DATE", as_index=False)["DEMAND_QTY"].sum()
        .sort_values("DUE_DATE")
        .reset_index(drop=True)
    )
    daily_grouped_df['CUMULATIVE_DEMAND'] = daily_grouped_df['DEMAND_QTY'].cumsum()

    # 일별 그래프
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.bar(daily_grouped_df['DUE_DATE'], daily_grouped_df['DEMAND_QTY'], color='skyblue', label='일별 DEMAND_QTY')
    ax1.set_xlabel("DUE_DATE")
    ax1.set_ylabel("DEMAND_QTY", color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # X축에 실제 데이터만 표시하도록 수정
    ax1.set_xticks(daily_grouped_df['DUE_DATE'])  # 실제 데이터만 표시
    ax1.set_xticklabels(daily_grouped_df['DUE_DATE'].dt.strftime('%Y-%m-%d'), rotation=45, ha='right')

    ax2 = ax1.twinx()
    ax2.plot(daily_grouped_df['DUE_DATE'], daily_grouped_df['CUMULATIVE_DEMAND'], color='red', label='누적 DEMAND', linewidth=2)
    ax2.set_ylabel("CUMULATIVE DEMAND", color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    fig1.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
    st.pyplot(fig1)

    # ---------------------
    # 주별 분석
    # ---------------------
    st.subheader("2. 주별 DEMAND_QTY 분석")

    # 주별 데이터 그룹화
    df['WEEK'] = df['DUE_DATE'].dt.to_period('W').apply(lambda r: r.start_time)
    weekly_grouped_df = (
        df.groupby("WEEK", as_index=False)["DEMAND_QTY"].sum()
        .sort_values("WEEK")
        .reset_index(drop=True)
    )
    weekly_grouped_df['CUMULATIVE_DEMAND'] = weekly_grouped_df['DEMAND_QTY'].cumsum()

    # 주별 그래프
    fig2, ax3 = plt.subplots(figsize=(12, 6))
    ax3.bar(weekly_grouped_df['WEEK'].astype(str), weekly_grouped_df['DEMAND_QTY'], color='lightgreen', label='주별 DEMAND_QTY')
    ax3.set_xlabel("WEEK")
    ax3.set_ylabel("DEMAND_QTY", color='green')
    ax3.tick_params(axis='y', labelcolor='green')
    ax3.set_xticks(range(len(weekly_grouped_df['WEEK'])))
    ax3.set_xticklabels(weekly_grouped_df['WEEK'].astype(str), rotation=45, ha='right')

    ax4 = ax3.twinx()
    ax4.plot(weekly_grouped_df['WEEK'].astype(str), weekly_grouped_df['CUMULATIVE_DEMAND'], color='orange', label='누적 DEMAND', linewidth=2)
    ax4.set_ylabel("CUMULATIVE DEMAND", color='orange')
    ax4.tick_params(axis='y', labelcolor='orange')
    fig2.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
    st.pyplot(fig2)

    # ---------------------
    # 월별 분석
    # ---------------------
    st.subheader("3. 월별 DEMAND_QTY 분석")

    # 월별 데이터 그룹화
    df['MONTH'] = df['DUE_DATE'].dt.to_period('M').apply(lambda r: r.start_time)
    monthly_grouped_df = (
        df.groupby("MONTH", as_index=False)["DEMAND_QTY"].sum()
        .sort_values("MONTH")
        .reset_index(drop=True)
    )
    monthly_grouped_df['CUMULATIVE_DEMAND'] = monthly_grouped_df['DEMAND_QTY'].cumsum()

    # 월별 그래프
    fig3, ax5 = plt.subplots(figsize=(12, 6))
    ax5.bar(monthly_grouped_df['MONTH'].astype(str), monthly_grouped_df['DEMAND_QTY'], color='gold', label='월별 DEMAND_QTY')
    ax5.set_xlabel("MONTH")
    ax5.set_ylabel("DEMAND_QTY", color='darkorange')
    ax5.tick_params(axis='y', labelcolor='darkorange')
    ax5.set_xticks(range(len(monthly_grouped_df['MONTH'])))
    ax5.set_xticklabels(monthly_grouped_df['MONTH'].astype(str), rotation=45, ha='right')

    ax6 = ax5.twinx()
    ax6.plot(monthly_grouped_df['MONTH'].astype(str), monthly_grouped_df['CUMULATIVE_DEMAND'], color='purple', label='누적 DEMAND', linewidth=2)
    ax6.set_ylabel("CUMULATIVE DEMAND", color='purple')
    ax6.tick_params(axis='y', labelcolor='purple')
    fig3.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
    st.pyplot(fig3)