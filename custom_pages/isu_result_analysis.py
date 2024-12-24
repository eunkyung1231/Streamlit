import streamlit as st
import pandas as pd
import os

def find_parquet_files_in_folder(base_folder):
    """지정된 폴더에서 모든 PARQUET 파일을 재귀적으로 검색."""
    parquet_files = []
    for root, _, files in os.walk(base_folder):
        for file in files:
            if file.endswith('.parquet'):
                parquet_files.append(os.path.join(root, file))
    return parquet_files

def compare_parquet_files_in_subfolders(folder1, folder2):
    """Data와 Experiment 1 하위 폴더에서 PARQUET 파일 비교."""
    data_folder1 = os.path.join(folder1, 'Data')
    data_folder2 = os.path.join(folder2, 'Data')
    experiment_folder1 = os.path.join(folder1, 'Experiment 1')
    experiment_folder2 = os.path.join(folder2, 'Experiment 1')

    # 각 폴더에서 파일 검색
    data_files1 = find_parquet_files_in_folder(data_folder1)
    data_files2 = find_parquet_files_in_folder(data_folder2)
    experiment_files1 = find_parquet_files_in_folder(experiment_folder1)
    experiment_files2 = find_parquet_files_in_folder(experiment_folder2)

    # 파일 이름별로 매칭하기 위해 딕셔너리 생성
    data_files1_dict = {os.path.basename(file): file for file in data_files1}
    data_files2_dict = {os.path.basename(file): file for file in data_files2}
    experiment_files1_dict = {os.path.basename(file): file for file in experiment_files1}
    experiment_files2_dict = {os.path.basename(file): file for file in experiment_files2}

    # Data 폴더 비교
    data_common_files = set(data_files1_dict.keys()).intersection(data_files2_dict.keys())
    data_differences = []
    for file_name in data_common_files:
        try:
            df1 = pd.read_parquet(data_files1_dict[file_name], engine="pyarrow")
            df2 = pd.read_parquet(data_files2_dict[file_name], engine="pyarrow")

            row_count1 = len(df1)
            row_count2 = len(df2)

            data_differences.append({
                "파일명": file_name,
                "폴더1 행 개수": row_count1,
                "폴더2 행 개수": row_count2,
                "차이": row_count1 - row_count2
            })
        except Exception as e:
            data_differences.append({
                "파일명": file_name,
                "폴더1 행 개수": "오류",
                "폴더2 행 개수": "오류",
                "차이": f"Error: {e}"
            })

    # Experiment 1 폴더 비교
    experiment_common_files = set(experiment_files1_dict.keys()).intersection(experiment_files2_dict.keys())
    experiment_differences = []
    for file_name in experiment_common_files:
        try:
            df1 = pd.read_parquet(experiment_files1_dict[file_name], engine="pyarrow")
            df2 = pd.read_parquet(experiment_files2_dict[file_name], engine="pyarrow")

            row_count1 = len(df1)
            row_count2 = len(df2)

            experiment_differences.append({
                "파일명": file_name,
                "폴더1 행 개수": row_count1,
                "폴더2 행 개수": row_count2,
                "차이": row_count1 - row_count2
            })
        except Exception as e:
            experiment_differences.append({
                "파일명": file_name,
                "폴더1 행 개수": "오류",
                "폴더2 행 개수": "오류",
                "차이": f"Error: {e}"
            })

    # 차이가 있는 파일 개수 계산
    data_diff_count = sum(1 for diff in data_differences if diff.get("차이") not in [0, "오류"])
    experiment_diff_count = sum(1 for diff in experiment_differences if diff.get("차이") not in [0, "오류"])

    return pd.DataFrame(data_differences), pd.DataFrame(experiment_differences), data_diff_count, experiment_diff_count

def show_page():
    st.title("ISU 결과 분석")

    # 두 개의 경로를 입력받는 UI
    folder1 = st.text_input("첫 번째 경로를 입력하세요", placeholder="예: D:\Model\Production_ISU\P-20241224-M-01_Engine_20241224100304")
    folder2 = st.text_input("두 번째 경로를 입력하세요", placeholder="예: D:\Model\Development_ISU\P-20241223-M-01_Engine_20241223180754")

    if st.button("비교 시작"):
        if not folder1 or not folder2:
            st.error("두 경로를 모두 입력하세요.")
            return

        if folder1 == folder2:
            st.error("두 경로가 동일합니다. 다른 경로를 선택하세요.")
            return

        # Data와 Experiment 1 폴더 비교
        data_diff, experiment_diff, data_diff_count, experiment_diff_count = compare_parquet_files_in_subfolders(folder1, folder2)

        # 결과 출력
        st.subheader("Data 폴더 내 PARQUET 파일 비교 결과")
        st.dataframe(data_diff, use_container_width=True)
        st.write(f"Data 폴더에서 차이가 있는 파일 개수: {data_diff_count}")

        st.subheader("Experiment 1 폴더 내 PARQUET 파일 비교 결과")
        st.dataframe(experiment_diff, use_container_width=True)
        st.write(f"Experiment 1 폴더에서 차이가 있는 파일 개수: {experiment_diff_count}")

if __name__ == "__main__":
    show_page()
