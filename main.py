import streamlit as st
from custom_pages import group_operation_rate, demand_analysis, equipment_detailed_view

# 사이드바 메뉴 구성
st.sidebar.title("페이지를 선택하세요")
menu = st.sidebar.radio("", ["DEMAND_QTY 분석", "장비 그룹별 가동율 현황", "장비 그룹별 개별 가동율 현황"])

# 메뉴 선택에 따라 각 페이지 호출
if menu == "DEMAND_QTY 분석":
    demand_analysis.show_page()  # "DEMAND_QTY 분석" 메뉴 페이지 호출
elif menu == "장비 그룹별 가동율 현황":
    group_operation_rate.show_page()
elif menu == "장비 그룹별 개별 가동율 현황":
    equipment_detailed_view.show_page()

    
