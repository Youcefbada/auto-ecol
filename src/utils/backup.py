import shutil
from datetime import datetime
from pathlib import Path
import schedule
import time

class BackupManager:
    @staticmethod
    def backup():
        backup_dir = Path("Backup")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # نسخ قاعدة البيانات
        db_file = Path("DrivingSchool.db")
        if db_file.exists():
            backup_db = backup_dir / f"DrivingSchool_{timestamp}.db"
            shutil.copy(db_file, backup_db)
        
        # نسخ مجلد Documents
        documents_src = Path("Documents")
        if documents_src.exists():
            documents_dest = backup_dir / f"Documents_{timestamp}"
            shutil.copytree(documents_src, documents_dest, dirs_exist_ok=True)

    @staticmethod
    def schedule_weekly_backup():
        schedule.every().week.do(BackupManager.backup)
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    BackupManager.backup()