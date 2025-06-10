import os
from pathlib import Path
import shutil
from PIL import Image

class FileManager:
    @staticmethod
    def create_student_folder(full_name, file_number):
        folder_name = f"{full_name}_{file_number}"
        folder_path = Path("Documents") / folder_name
        os.makedirs(folder_path, exist_ok=True)
        return str(folder_path)

    @staticmethod
    def upload_file(source_path, dest_folder, compress_image=False):
        file_name = os.path.basename(source_path)
        dest_path = Path(dest_folder) / file_name
        if compress_image and file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            img = Image.open(source_path)
            img.save(dest_path, quality=85, optimize=True)
        else:
            shutil.copy(source_path, dest_path)
        return str(dest_path)

    @staticmethod
    def open_file(file_path):
        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            raise FileNotFoundError(f"الملف {file_path} غير موجود")

    @staticmethod
    def rename_student_folder(old_path, new_full_name, new_file_number):
        if os.path.exists(old_path):
            new_folder_name = f"{new_full_name}_{new_file_number}"
            new_path = Path("Documents") / new_folder_name
            os.rename(old_path, new_path)
            return str(new_path)
        return old_path