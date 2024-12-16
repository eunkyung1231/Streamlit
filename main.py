import streamlit as st
import os
import shutil
import zipfile
import custom_pages.demand_analysis as demand
import custom_pages.equipment_detail as equipment
import custom_pages.group_operation_rate as group_rate
import custom_pages.target_capa_analysis as target_capa

def find_parquet_files(base_dir, required_files):
    """재귀적으로 폴더를 탐색하며 필요한 파일을 찾는 함수"""
    found_files = {}
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file in required_files:
                found_files[file] = os.path.join(root, file)
    return found_files

def zip_parquet_files(folder_path, output_zip):
    """지정된 폴더에서 PARQUET 파일만 ZIP 파일로 압축하는 함수"""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.parquet'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)

# 폴더 경로 목록 관리
folder_data = st.session_state.get('folder_data', {})

# Streamlit UI
st.sidebar.header("폴더 경로 관리")
new_folder = st.sidebar.text_input("새로운 폴더 경로 추가")
new_name = st.sidebar.text_input("폴더 이름 지정")

if st.sidebar.button("폴더 추가"):
    if new_folder and os.path.exists(new_folder):
        display_name = new_name if new_name else new_folder
        if display_name in folder_data:
            st.warning("이미 사용 중인 이름입니다. 다른 이름을 입력하세요.")
        else:
            folder_data[display_name] = new_folder
            st.session_state['folder_data'] = folder_data
            st.success(f"폴더 경로 '{new_folder}'이 이름 '{display_name}'으로 추가되었습니다.")
    else:
        st.error("유효한 폴더 경로를 입력하세요.")

# 등록된 폴더 경로 목록 표시
if folder_data:
    selected_name = st.sidebar.selectbox("폴더를 선택하세요", list(folder_data.keys()))
    selected_folder = folder_data[selected_name]

    # ZIP 파일 생성 버튼
    if st.sidebar.button("선택된 폴더의 PARQUET 파일만 ZIP으로 압축"):
        zip_path = f"{selected_folder}_parquet_only.zip"
        zip_parquet_files(selected_folder, zip_path)
        st.success(f"PARQUET 파일만 성공적으로 압축되었습니다: {zip_path}")
        st.download_button(
            label="ZIP 파일 다운로드",
            data=open(zip_path, "rb").read(),
            file_name=os.path.basename(zip_path),
            mime="application/zip"
        )

    # 필요한 파일 정의
    required_files = [
        "TARGET_PLAN.parquet", "ROUTING_OPER.parquet", "OPER_RES.parquet",
        "DEMAND.parquet", "CAPA_ALLOCATION_INFO.parquet"
    ]
    found_files = find_parquet_files(selected_folder, required_files)

    # 페이지 선택
    st.sidebar.subheader("페이지 선택")
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
    st.warning("폴더 경로를 추가하세요.")
