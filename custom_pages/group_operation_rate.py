import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def show_page(uploaded_files):
    st.title("\ud56d\ube44 \uadf8\ub8f9\ubcc4 \uac00\ub3d9\c728 \ud604\ud669")

    # Parquet \ud30c\uc77c \uacbd\ub85c \uc9c0\uc815
    model_path = 'C:\\Users\\vms\\Downloads\\20241210-P-BOM2_Engine_20241210081853\\Experiment 1\\Result 0\\'
    file_path = 'CAPA_ALLOCATION_INFO.parquet'

    # Parquet \ud30c\uc77c \uc77d\uae30
    df = pd.read_parquet(model_path + file_path, engine='pyarrow')

    # \uc870\uac74 \ud544\ud130\ub9c1 \ubc0f \uadf8\ub8f9\ud654 \ub85c\uc9d1 (\uacf5\ud1b5 \ud568\uc218)
    def process_data(df_filtered):
        if df_filtered.empty:  # \ud544\ud130\ub9c1\ub41c \ub370\uc774\ud130\uac00 \uc5c6\ub294 \uacbd\uc6b0
            return pd.DataFrame()  # \ube48 \ub370\uc774\ud130\ud504\ub9ac\uc784 \ubc18\ud658

        grouped = df_filtered.groupby('RES_GROUP_ID').agg({
            'TOTAL_CAPA': 'sum',
            'OFF_TIME_CAPA': 'sum',
            'ALLOCATION_CAPA': 'sum',
            'PM_CAPA': 'sum',
            'SETUP_CAPA': 'sum',
            'REMAIN_CAPA': 'sum'
        }).reset_index()

        if grouped.empty:  # \uadf8\ub8f9\ud654 \uacb0\uacfc\uac00 \ube48 \uacbd\uc6b0
            return pd.DataFrame()

        # \ube44\uc728 \uacc4\uc0b0
        grouped['OFF_TIME_CAPA_%'] = (grouped['OFF_TIME_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['ALLOCATION_CAPA_%'] = (grouped['ALLOCATION_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['PM_CAPA_%'] = (grouped['PM_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['SETUP_CAPA_%'] = (grouped['SETUP_CAPA'] / grouped['TOTAL_CAPA']) * 100
        grouped['REMAIN_CAPA_%'] = (grouped['REMAIN_CAPA'] / grouped['TOTAL_CAPA']) * 100

        # Allocation_capa \ud37c\uc13c\ud2f0\uc9c0 \uae30\uc900\uc73c\ub85c \uc815\ub82c
        grouped = grouped.sort_values(by='ALLOCATION_CAPA_%', ascending=False)

        # X\uc축 \ub808\uc774\ube14: RES_GROUP_ID\ub9cc \ud45c\uc2dc
        grouped['X_LABEL'] = grouped['RES_GROUP_ID']

        # customdata \uc0dd\uc131
        grouped['customdata'] = grouped.apply(
            lambda row: [
                (row['ALLOCATION_CAPA_%'], row['ALLOCATION_CAPA'], row['TOTAL_CAPA']),
                (row['SETUP_CAPA_%'], row['SETUP_CAPA'], row['TOTAL_CAPA']),
                (row['PM_CAPA_%'], row['PM_CAPA'], row['TOTAL_CAPA']),
                (row['OFF_TIME_CAPA_%'], row['OFF_TIME_CAPA'], row['TOTAL_CAPA']),
                (row['REMAIN_CAPA_%'], row['REMAIN_CAPA'], row['TOTAL_CAPA']),
            ],
            axis=1
        )
        return grouped

    # X\uc축 \uc2a4\ud06c\ub864 \ubaa8\ub4dc \ud65c\uc131\ud654 \ud568\uc218
    def create_chart(grouped, title):
        if grouped.empty:  # \ub370\uc774\ud130\ud504\ub9ac\uc784\uc774 \ube48 \uacbd\uc6b0
            st.warning(f"{title} \uc5d0 \ub300\ud55c \ub370\uc774\ud130\uac00 \uc5c6\uc2b5\ub2c8\ub2e4.")
            return None

        categories = ['Allocation_capa', 'Setup_capa', 'Pm_capa', 'Off_time_capa', 'Remain_capa']
        colors = ['#66CC66', '#FF6666', '#FFE066', '#808080', '#F2F2F2']
        fig = go.Figure()

        for i, (category, color) in enumerate(zip(categories, colors)):
            fig.add_trace(
                go.Bar(
                    x=grouped['X_LABEL'],
                    y=grouped[f'{category.upper()}_%'],
                    name=category.capitalize(),
                    marker_color=color,
                    customdata=np.stack(grouped['customdata'].to_numpy()),
                    hovertemplate=(f"{category.capitalize()}: %{{customdata[{i}][0]:.2f}}% "
                                   f"(%{{customdata[{i}][1]:,.0f}}/%{{customdata[{i}][2]:,.0f}})<extra></extra>")
                )
            )

        fig.update_layout(
            title=title,
            xaxis=dict(title="\uc7a5\ube44 \uadf8\ub8f9 (RES_GROUP_ID)", tickangle=45),
            yaxis_title="\ubc31\ubd84\uc728 (%)",
            barmode='stack',
            hovermode="x unified",
            margin=dict(l=10, r=10, t=30, b=70),
        )
        return fig

    # \ub370\uc774\ud130 \ud544\ud130\ub9c1 \ubc0f \ucc44\ud305
    df_time = df[(df['TARGET_TYPE'] == 'Resource') & (df['CAPA_TYPE'] == 'Time')]
    grouped_time = process_data(df_time)

    df_quantity = df[(df['TARGET_TYPE'] == 'Resource') & (df['CAPA_TYPE'] == 'Quantity')]
    grouped_quantity = process_data(df_quantity)

    df_addresource_time = df[(df['TARGET_TYPE'] == 'AddResource') & (df['CAPA_TYPE'] == 'Time')]
    grouped_addresource_time = process_data(df_addresource_time)

    # \uadf8\ub798\ud504 \uc0dd\uc131 \ubc0f \ud45c\uc2dc
    fig_time = create_chart(grouped_time, "RES_GROUP_ID\ubcc4 CAPA Distribution (Time)")
    if fig_time:
        st.plotly_chart(fig_time, use_container_width=True)

    fig_quantity = create_chart(grouped_quantity, "RES_GROUP_ID\ubcc4 CAPA Distribution (Quantity)")
    if fig_quantity:
        st.plotly_chart(fig_quantity, use_container_width=True)

    fig_addresource_time = create_chart(grouped_addresource_time, "RES_GROUP_ID\ubcc4 CAPA Distribution (AddResource + Time)")
    if fig_addresource_time:
        st.plotly_chart(fig_addresource_time, use_container_width=True)

if __name__ == "__main__":
    show_page()
