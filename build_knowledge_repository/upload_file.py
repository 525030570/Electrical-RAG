import gradio as gr
import os
import shutil
import pandas as pd
STRUCTURED_FILE_PATH = "File/Structured"
UNSTRUCTURED_FILE_PATH = "File/Unstructured"
# 刷新非结构化类目
def refresh_label():
    return os.listdir(UNSTRUCTURED_FILE_PATH)

# 刷新结构化数据表
def refresh_data_table():
    return os.listdir(STRUCTURED_FILE_PATH)

# 上传非结构化数据
def upload_unstructured_file(files, label_name):
    if files is None:
        gr.Info("请上传文件")
    elif len(label_name) == 0:
        gr.Info("请输入类目名称")
    else:
        try:
            # 确保目标文件夹存在（无论是否已存在）
            os.makedirs(os.path.join(UNSTRUCTURED_FILE_PATH, label_name), exist_ok=True)
            
            for file in files:
                file_path = file.name
                file_name = os.path.basename(file_path)
                destination_file_path = os.path.join(UNSTRUCTURED_FILE_PATH, label_name, file_name)
                
                # 移动文件到目标文件夹（即使文件已存在也会覆盖）
                shutil.move(file_path, destination_file_path)
            
            gr.Info(f"文件已上传至{label_name}类目中，请前往创建知识库")
        
        except Exception as e:
            gr.Info(f"文件移动失败: {str(e)}")

# 上传结构化数据
def upload_structured_file(files, label_name):
    if files is None:
        gr.Info("请上传文件")
    elif len(label_name) == 0:
        gr.Info("请输入数据表名称")
    else:
        try:
            # 确保目标文件夹存在（无论是否已存在）
            os.makedirs(os.path.join(STRUCTURED_FILE_PATH, label_name), exist_ok=True)
            
            for file in files:
                file_path = file.name
                file_name = os.path.basename(file_path)
                destination_file_path = os.path.join(STRUCTURED_FILE_PATH, label_name, file_name)
                
                # 移动文件到目标文件夹（即使文件已存在也会覆盖）
                shutil.move(file_path, destination_file_path)
                
                # 根据文件类型读取数据
                if os.path.splitext(destination_file_path)[1] == ".xlsx":
                    df = pd.read_excel(destination_file_path)
                elif os.path.splitext(destination_file_path)[1] == ".csv":
                    df = pd.read_csv(destination_file_path)
                else:
                    gr.Info(f"不支持的文件格式: {file_name}")
                    continue  # 跳过非 Excel/CSV 文件
                
                # 生成对应的 .txt 文件
                txt_file_name = os.path.splitext(file_name)[0] + ".txt"
                columns = df.columns
                with open(os.path.join(STRUCTURED_FILE_PATH, label_name, txt_file_name), "w", encoding="utf-8") as f:
                    for idx, row in df.iterrows():
                        f.write("【")
                        info = []
                        for col in columns:
                            info.append(f"{col}:{row[col]}")
                        f.write(",".join(info))
                        if idx != len(df) - 1:
                            f.write("】\n")
                        else:
                            f.write("】")
                
                # 删除原始文件
                os.remove(destination_file_path)
            
            gr.Info(f"文件已上传至{label_name}数据表中，请前往创建知识库")
        
        except Exception as e:
            gr.Info(f"文件处理失败: {str(e)}")

# 实时更新结构化数据表
def update_datatable():
    return gr.update(choices=os.listdir(STRUCTURED_FILE_PATH))


# 实时更新非结构化类目
def update_label():
    return gr.update(choices=os.listdir(UNSTRUCTURED_FILE_PATH))

# 删除类目
def delete_label(label_name):
    if label_name is not None:
        for label in label_name:
            folder_path = os.path.join(UNSTRUCTURED_FILE_PATH,label)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                gr.Info(f"{label}类目已删除")

# 删除数据表
def delete_data_table(table_name):
    if table_name is not None:
        for table in table_name:
            folder_path = os.path.join(STRUCTURED_FILE_PATH,table)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                gr.Info(f"{table}数据表已删除")