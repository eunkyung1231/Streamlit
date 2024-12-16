import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show_page(uploaded_files):
    st.title("DEMAND_QTY 분석 (일별, 주별, 월별)")

    # 파일 검사
    if "DEMAND.parquet" not in uploaded_files:
        st.error("DEMAND.parquet 파일이 업로드되지 않았습니다.")
        return

    # Parquet 파일 읽기
    df = pd.read_parquet(uploaded_files["DEMAND.parquet"], engine='pyarrow')

    # 날짜 데이터 형식 변환
    df['DUE_DATE'] = pd.to_datetime(df['DUE_DATE'])

    # ---------------------
    # 일별 분석
    # ---------------------
    st.subheader("1. 일별 DEMAND_QTY 분석")

    daily_grouped_df = (
        df.groupby("DUE_DATE", as_index=False)["DEMAND_QTY"].sum()
        .sort_values("DUE_DATE")
        .reset_index(drop=True)
    )
    daily_grouped_df['CUMULATIVE_DEMAND'] = daily_grouped_df['DEMAND_QTY'].cumsum()

    # 슬라이더 설정
    start, end = st.slider("범위를 선택하세요", 0, len(daily_grouped_df)-1, (0, min(10, len(daily_grouped_df)-1)))

    # 일별 그래프 (Matplotlib 사용)
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.bar(daily_grouped_df['DUE_DATE'][start:end+1], daily_grouped_df['DEMAND_QTY'][start:end+1], color='skyblue', label='일별 DEMAND_QTY')
    ax2 = ax1.twinx()
    ax2.plot(daily_grouped_df['DUE_DATE'][start:end+1], daily_grouped_df['CUMULATIVE_DEMAND'][start:end+1], color='red', label='누적 DEMAND')
    ax1.set_xlabel("DUE_DATE")
    ax1.set_ylabel("DEMAND_QTY", color='blue')
    ax2.set_ylabel("CUMULATIVE DEMAND", color='red')
    ax1.tick_params(axis='x', rotation=45)
    ax1.tick_params(axis='y', labelcolor='blue')
    ax2.tick_params(axis='y', labelcolor='red')
    fig1.legend(loc="upper left")
    st.pyplot(fig1)

    # ---------------------
    # 주별 분석
    # ---------------------
    st.subheader("2. 주별 DEMAND_QTY 분석")

    df['WEEK'] = df['DUE_DATE'].dt.to_period('W').apply(lambda r: r.start_time)
    weekly_grouped_df = (
        df.groupby("WEEK", as_index=False)["DEMAND_QTY"].sum()
        .sort_values("WEEK")
        .reset_index(drop=True)
    )
    weekly_grouped_df['CUMULATIVE_DEMAND'] = weekly_grouped_df['DEMAND_QTY'].cumsum()

    # 슬라이더 설정
    start, end = st.slider("주별 범위를 선택하세요", 0, len(weekly_grouped_df)-1, (0, min(10, len(weekly_grouped_df)-1)))

    # 주별 그래프 (Matplotlib 사용)
    fig2, ax3 = plt.subplots(figsize=(12, 6))
    ax3.bar(weekly_grouped_df['WEEK'][start:end+1], weekly_grouped_df['DEMAND_QTY'][start:end+1], color='lightgreen', label='주별 DEMAND_QTY')
    ax4 = ax3.twinx()
    ax4.plot(weekly_grouped_df['WEEK'][start:end+1], weekly_grouped_df['CUMULATIVE_DEMAND'][start:end+1], color='orange', label='누적 DEMAND')
    ax3.set_xlabel("WEEK")
    ax3.set_ylabel("DEMAND_QTY", color='green')
    ax4.set_ylabel("CUMULATIVE DEMAND", color='orange')
    ax3.tick_params(axis='x', rotation=45)
    ax3.tick_params(axis='y', labelcolor='green')
    ax4.tick_params(axis='y', labelcolor='orange')
    fig2.legend(loc="upper left")
    st.pyplot(fig2)

    # ---------------------
    # 월별 분석
    # ---------------------
    st.subheader("3. 월별 DEMAND_QTY 분석")

    df['MONTH'] = df['DUE_DATE'].dt.to_period('M').apply(lambda r: r.start_time)
    monthly_grouped_df = (
        df.groupby("MONTH", as_index=False)["DEMAND_QTY"].sum()
        .sort_values("MONTH")
        .reset_index(drop=True)
    )
    monthly_grouped_df['CUMULATIVE_DEMAND'] = monthly_grouped_df['DEMAND_QTY'].cumsum()

    # 슬라이더 설정
    start, end = st.slider("월별 범위를 선택하세요", 0, len(monthly_grouped_df)-1, (0, min(10, len(monthly_grouped_df)-1)))

    # 월별 그래프 (Matplotlib 사용)
    fig3, ax5 = plt.subplots(figsize=(12, 6))
    ax5.bar(monthly_grouped_df['MONTH'][start:end+1], monthly_grouped_df['DEMAND_QTY'][start:end+1], color='gold', label='월별 DEMAND_QTY')
    ax6 = ax5.twinx()
    ax6.plot(monthly_grouped_df['MONTH'][start:end+1], monthly_grouped_df['CUMULATIVE_DEMAND'][start:end+1], color='purple', label='누적 DEMAND')
    ax5.set_xlabel("MONTH")
    ax5.set_ylabel("DEMAND_QTY", color='darkorange')
    ax6.set_ylabel("CUMULATIVE DEMAND", color='purple')
    ax5.tick_params(axis='x', rotation=45)
    ax5.tick_params(axis='y', labelcolor='darkorange')
    ax6.tick_params(axis='y', labelcolor='purple')
    fig3.legend(loc="upper left")
    st.pyplot(fig3)
