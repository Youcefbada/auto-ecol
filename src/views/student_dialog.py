from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox, QLabel
from PyQt6.QtCore import Qt
from sqlalchemy.orm import sessionmaker
from models import engine, Student
from pathlib import Path
import os

class StudentDialog(QDialog):
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة/تعديل متدرب")
        self.setMinimumWidth(400)
        self.student = student
        self.session = sessionmaker(bind=engine)()

        layout = QVBoxLayout(self)

        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("الاسم الكامل")
        layout.addWidget(QLabel("الاسم الكامل:"))
        layout.addWidget(self.full_name)

        self.file_number = QLineEdit()
        self.file_number.setPlaceholderText("رقم الملف")
        layout.addWidget(QLabel("رقم الملف:"))
        layout.addWidget(self.file_number)

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("رقم الهاتف")
        layout.addWidget(QLabel("رقم الهاتف:"))
        layout.addWidget(self.phone)

        self.address = QLineEdit()
        self.address.setPlaceholderText("العنوان")
        layout.addWidget(QLabel("العنوان:"))
        layout.addWidget(self.address)

        self.training_type = QComboBox()
        self.training_type.addItems(["Théorique", "Pratique"])
        layout.addWidget(QLabel("نوع التدريب:"))
        layout.addWidget(self.training_type)

        self.status = QComboBox()
        self.status.addItems(["Active", "Completed", "Dropped"])
        layout.addWidget(QLabel("الحالة:"))
        layout.addWidget(self.status)

        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.save_student)
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

        if student:
            self.full_name.setText(student.full_name)
            self.file_number.setText(student.file_number)
            self.phone.setText(student.phone or "")
            self.address.setText(student.address or "")
            self.training_type.setCurrentText(student.training_type or "Pratique")
            self.status.setCurrentText(student.status or "Active")

    def save_student(self):
        full_name = self.full_name.text().strip()
        file_number = self.file_number.text().strip()
        phone = self.phone.text().strip() or None
        address = self.address.text().strip() or None
        training_type = self.training_type.currentText()
        status = self.status.currentText()

        if not full_name or not file_number:
            QMessageBox.warning(self, "خطأ", "الاسم الكامل ورقم الملف مطلوبان!")
            return

        folder_path = str(Path("Documents") / f"{full_name}_{file_number}")

        if self.student:
            self.student.full_name = full_name
            self.student.file_number = file_number
            self.student.phone = phone
            self.student.address = address
            self.student.training_type = training_type
            self.student.status = status
            if self.student.folder_path != folder_path:
                if os.path.exists(self.student.folder_path):
                    os.rename(self.student.folder_path, folder_path)
                self.student.folder_path = folder_path
        else:
            existing_student = self.session.query(Student).filter_by(file_number=file_number).first()
            if existing_student:
                QMessageBox.warning(self, "خطأ", "رقم الملف موجود بالفعل!")
                return
            self.student = Student(
                full_name=full_name,
                file_number=file_number,
                phone=phone,
                address=address,
                training_type=training_type,
                status=status,
                folder_path=folder_path
            )
            self.session.add(self.student)

        os.makedirs(folder_path, exist_ok=True)
        self.session.commit()
        self.accept()