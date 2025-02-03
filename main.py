import streamlit as st
import os
import zipfile
import tempfile
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

def extract_parquet_from_zip(zip_path, extract_to):
    """ZIP 파일에서 .parquet 파일을 재귀적으로 추출하는 함수"""
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_to)

    # 추출된 폴더에서 모든 .parquet 파일 찾기
    found_files = {}
    for root, _, files in os.walk(extract_to):
        for file in files:
            if file.endswith(".parquet"):
                found_files[file] = os.path.join(root, file)
    return found_files

# Streamlit UI
st.title("Parquet 파일 분석 도구")

# ZIP 파일 업로드
uploaded_file = st.file_uploader("ZIP 파일을 업로드하세요", type=["zip"])

if uploaded_file:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, uploaded_file.name)
        
        # 업로드된 ZIP 파일을 임시 경로에 저장
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # ZIP 파일에서 .parquet 파일 추출
        found_files = extract_parquet_from_zip(zip_path, temp_dir)

        if found_files:
            st.success(f"{len(found_files)}개의 Parquet 파일을 발견했습니다.")
        else:
            st.error("ZIP 파일에 .parquet 파일이 포함되어 있지 않습니다.")
        
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
    st.warning("ZIP 파일을 업로드하세요.")
