import streamlit as st
import os
import shutil
import zipfile
import custom_pages.demand_analysis as demand
import custom_pages.equipment_detail as equipment
import custom_pages.group_operation_rate as group_rate
import custom_pages.target_capa_analysis as target_capa
import custom_pages.process_output_summary as process_output
import custom_pages.short_log_analysis as short_log
import custom_pages.isu_result_analysis as isu_result
import custom_pages.setup_count_by_res as res_setup
import custom_pages.setup_count_by_product as product_setup
import custom_pages.equipment_wip as equipment_wip

def find_all_parquet_files(base_dir):
    """재귀적으로 폴더를 탐색하며 모든 .parquet 파일을 찾는 함수"""
    found_files = {}
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".parquet"):
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
new_name = st.sidebar.text_input("버전 이름 지정")

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
    selected_name = st.sidebar.selectbox("버전을 선택하세요", list(folder_data.keys()))
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

    # 모든 .parquet 파일 찾기
    found_files = find_all_parquet_files(selected_folder)

    # 페이지 선택
    st.sidebar.subheader("페이지 선택")
    page = st.sidebar.radio(
        "페이지를 선택하세요",
        ["DEMAND_QTY 분석", "장비 그룹별 가동율 현황", "장비 그룹별 개별 가동율 현황", "TARGET 대비 CAPA 분석", "공정별 생산량 분석", "SHORT LOG 분석",
         "Parquet 파일 비교 분석", "설비별 Setup 횟수", "제품별 Setup 횟수", "설비 대기 ITEM별 재공 수량"]
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
    elif page == "공정별 생산량 분석":
        process_output.show_page(found_files)
    elif page == "SHORT LOG 분석":
        short_log.show_page(found_files)
    elif page == "Parquet 파일 비교 분석":
        isu_result.show_page()
    elif page == "설비별 Setup 횟수":
        res_setup.show_page(found_files)
    elif page == "제품별 Setup 횟수":
        product_setup.show_page(found_files)
    elif page == "설비 대기 ITEM별 재공 수량":
        equipment_wip.show_page(found_files)
else:
    st.warning("폴더 경로를 추가하세요.")
