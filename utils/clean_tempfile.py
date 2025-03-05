import shutil

def delete_folder(folder_path):
    try:
        # 删除文件夹及其所有内容
        shutil.rmtree(folder_path)
        print(f"Deleted folder: {folder_path}")
    except Exception as e:
        print(f"Error deleting folder {folder_path}: {e}")

# 指定要删除的文件夹路径
folder_path = '/path/to/your/folder'

# 调用函数删除文件夹
delete_folder(folder_path)
