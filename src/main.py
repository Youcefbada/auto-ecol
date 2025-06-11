from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import sys
import qtawesome as qta
import os
import shutil

from pathlib import Path
from models import engine, Student, Document
from datetime import date
from student_dialog import StudentDialog
from lessons_view import LessonsView
from payments_view import PaymentsView
from statistics_view import StatisticsView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Driving School Management")
        self.setMinimumSize(800, 600)

        self.session = sessionmaker(bind=engine)()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)

        nav_layout = QHBoxLayout()
        buttons = [
            ("المتدربون", self.load_students, "mdi.account-group"),
            ("إضافة متدرب", self.add_student, "mdi.account-plus"),
            ("الدروس", self.show_lessons, "mdi.book-open-variant"),
            ("المدفوعات", self.show_payments, "mdi.cash"),
            ("الملفات", self.view_files, "mdi.folder"),
            ("الإحصائيات", self.show_statistics, "mdi.chart-bar")
        ]
        for text, callback, icon in buttons:
            btn = QPushButton(text)
            btn.setIcon(qta.icon(icon))
            btn.clicked.connect(callback)  # Verify connection
            nav_layout.addWidget(btn)
        self.layout.addLayout(nav_layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("ابحث بالاسم، الهاتف، أو رقم الملف")
        self.search_box.textChanged.connect(self.load_students)
        self.layout.addWidget(self.search_box)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["الاسم", "رقم الملف", "الهاتف", "الحالة", "الإجراءات"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.table)

        self.load_students()

    def load_students(self):
        search_term = self.search_box.text()
        self.table.setRowCount(0)
        students = self.session.query(Student).filter(
            Student.full_name.contains(search_term) |
            Student.file_number.contains(search_term) |
            Student.phone.contains(search_term)
        ).all()

        for row, student in enumerate(students):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(student.full_name))
            self.table.setItem(row, 1, QTableWidgetItem(student.file_number))
            self.table.setItem(row, 2, QTableWidgetItem(student.phone or ""))
            self.table.setItem(row, 3, QTableWidgetItem(student.status))

            btn_layout = QHBoxLayout()
            view_files_btn = QPushButton("عرض الملفات")
            view_files_btn.setIcon(qta.icon("mdi.folder-open"))
            view_files_btn.clicked.connect(lambda _, s=student: self.view_files(s))
            btn_layout.addWidget(view_files_btn)
            upload_btn = QPushButton("تحميل ملف")
            upload_btn.setIcon(qta.icon("mdi.upload"))
            upload_btn.clicked.connect(lambda _, s=student: self.upload_file(s))
            btn_layout.addWidget(upload_btn)
            details_btn = QPushButton("التفاصيل")
            details_btn.setIcon(qta.icon("mdi.information"))
            details_btn.clicked.connect(lambda _, s=student: self.view_details(s))
            btn_layout.addWidget(details_btn)

            cell_widget = QWidget()
            cell_widget.setLayout(btn_layout)
            self.table.setCellWidget(row, 4, cell_widget)

    def add_student(self):
        try:
            print("Opening Add Student dialog")
            dialog = StudentDialog(self)
            if dialog.exec():
                print("Student added successfully")
                self.load_students()
        except Exception as e:
            print(f"Error in add_student: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في إضافة المتدرب: {e}")

    def upload_file(self, student):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "تحميل ملف", "", "Documents (*.jpg *.png *.pdf)")
        if file_path:
            file_name = os.path.basename(file_path)
            dest_path = str(Path(student.folder_path) / file_name)
            shutil.copy(file_path, dest_path)
            document = Document(
                student_id=student.id,
                document_type="Certificate" if file_name.lower().endswith('.pdf') else "Photo",
                file_path=dest_path
            )
            self.session.add(document)
            self.session.commit()
            QMessageBox.information(self, "نجاح", "تم تحميل الملف!")

    def view_files(self, student=None):
        if not student:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار متدرب أولاً!")
            return
        documents = self.session.query(Document).filter_by(student_id=student.id).all()
        if not documents:
            QMessageBox.warning(self, "لا توجد ملفات", "لا توجد ملفات لهذا المتدرب.")
            return
        for doc in documents:
            os.startfile(doc.file_path)
    def view_details(self, student):
        lessons_count = len(student.lessons)
        total_payments = sum(p.amount for p in student.payments) if student.payments else 0
        documents_count = len(student.documents) if hasattr(student, 'documents') else 0
        QMessageBox.information(self, "تفاصيل المتدرب",
                                f"الاسم: {student.full_name}\n"
                                f"عدد الدروس: {lessons_count}\n"
                                f"إجمالي المدفوعات: {total_payments}\n"
                                f"عدد الملفات: {documents_count}")
    def show_lessons(self):
        self.lesson_view = LessonsView(self)
        self.lesson_view.exec()

    def show_payments(self):
        try:
            print("Opening Payments view")
            self.payment_view = PaymentsView(self)
            self.payment_view.show()
        except Exception as e:
            print(f"Error in show_payments: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في عرض المدفوعات: {e}")
    def show_statistics(self):
        try:
            print("Opening Statistics view")
            self.stats_view = StatisticsView(self)
            self.stats_view.exec()
        except Exception as e:
            print(f"Error in show_statistics: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في عرض الإحصائيات: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    with open('src/resources/styles.qss', 'r') as f:
        app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())