import streamlit as st
import pandas as pd
import zipfile
import os
import tempfile
import custom_pages.demand_analysis as demand
import custom_pages.equipment_detail as equipment
import custom_pages.group_operation_rate as group_rate
import custom_pages.target_capa_analysis as target_capa

def extract_zip(uploaded_zip):
    # 임시 폴더 생성
    temp_dir = tempfile.TemporaryDirectory()
    zip_path = os.path.join(temp_dir.name, "uploaded.zip")
    
    # ZIP 파일 저장
    with open(zip_path, "wb") as f:
        f.write(uploaded_zip.getbuffer())

    # ZIP 파일 해제
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir.name)

    return temp_dir

def find_parquet_files(base_dir, required_files):
    """재귀적으로 폴더를 탐색하며 필요한 파일을 찾는 함수"""
    found_files = {}
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file in required_files:
                found_files[file] = os.path.join(root, file)
    return found_files

# Streamlit UI
st.sidebar.header("ZIP 파일 업로드")
uploaded_zip = st.sidebar.file_uploader("ZIP 파일을 업로드하세요", type="zip")

if uploaded_zip:
    # ZIP 파일 해제
    temp_dir = extract_zip(uploaded_zip)
    st.success("ZIP 파일이 성공적으로 업로드 및 해제되었습니다!")

    # 필요한 파일 정의
    required_files = ["TARGET_PLAN.parquet", "ROUTING_OPER.parquet", "OPER_RES.parquet", "DEMAND.parquet", "CAPA_ALLOCATION_INFO.parquet"]
    found_files = find_parquet_files(temp_dir.name, required_files)

    # 페이지 선택
    page = st.sidebar.radio(
        "페이지를 선택하세요",
        ["DEMAND_QTY 분석", "장비 그룹별 가동율 현황", "장비 그룹별 개별 가동율 현황", "TARGET 대비 CAPA 분석"]
    )

    # 페이지 라우팅
    if page == "DEMAND_QTY 분석":
        demand.show_page(found_files)
    elif page == "장비 그룹별 가동율 현황":
        group_rate.show_page(found_files)
    elif page == "장비 그룹별 개별 가동율 현황":
        equipment.show_page(found_files)
    elif page == "TARGET 대비 CAPA 분석":
        target_capa.show_page(found_files)
    else:
        st.error("parquet 파일이 필요합니다.")

else:
    st.warning("ZIP 파일을 업로드하세요.")
