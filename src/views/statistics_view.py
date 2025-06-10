from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from models import engine, Student, Lesson, Payment
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

class StatisticsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = sessionmaker(bind=engine)()

        layout = QVBoxLayout(self)

        # إحصائيات عامة
        stats_layout = QHBoxLayout()
        self.total_students = QLabel("عدد المتدربين: 0")
        self.total_lessons = QLabel("عدد الدروس: 0")
        self.total_payments = QLabel("إجمالي المدفوعات: 0")
        stats_layout.addWidget(self.total_students)
        stats_layout.addWidget(self.total_lessons)
        stats_layout.addWidget(self.total_payments)
        layout.addLayout(stats_layout)

        # جدول الإحصائيات حسب المتدرب
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["المتدرب", "عدد الدروس", "إجمالي المدفوعات", "الحالة"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # زر تصدير PDF
        export_btn = QPushButton("تصدير إلى PDF")
        export_btn.clicked.connect(self.export_to_pdf)
        layout.addWidget(export_btn)

        self.load_statistics()

    def load_statistics(self):
        # إحصائيات عامة
        total_students = self.session.query(func.count(Student.id)).scalar()
        total_lessons = self.session.query(func.count(Lesson.id)).scalar()
        total_payments = self.session.query(func.sum(Payment.amount)).scalar() or 0

        self.total_students.setText(f"عدد المتدربين: {total_students}")
        self.total_lessons.setText(f"عدد الدروس: {total_lessons}")
        self.total_payments.setText(f"إجمالي المدفوعات: {total_payments}")

        # إحصائيات حسب المتدرب
        self.table.setRowCount(0)
        students = self.session.query(Student).all()
        for row, student in enumerate(students):
            lessons_count = self.session.query(func.count(Lesson.id)).filter(Lesson.student_id == student.id).scalar()
            payments_sum = self.session.query(func.sum(Payment.amount)).filter(Payment.student_id == student.id).scalar() or 0
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(student.full_name))
            self.table.setItem(row, 1, QTableWidgetItem(str(lessons_count)))
            self.table.setItem(row, 2, QTableWidgetItem(str(payments_sum)))
            self.table.setItem(row, 3, QTableWidgetItem(student.status))

    def export_to_pdf(self):
        pdf_path = str(Path("Reports") / "Statistics_Report.pdf")
        Path("Reports").mkdir(exist_ok=True)
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)

        y = 750
        c.drawString(100, y, "تقرير إحصائيات مدرسة تعليم القيادة")
        y -= 30

        total_students = self.session.query(func.count(Student.id)).scalar()
        total_lessons = self.session.query(func.count(Lesson.id)).scalar()
        total_payments = self.session.query(func.sum(Payment.amount)).scalar() or 0
        c.drawString(100, y, f"عدد المتدربين: {total_students}")
        y -= 20
        c.drawString(100, y, f"عدد الدروس: {total_lessons}")
        y -= 20
        c.drawString(100, y, f"إجمالي المدفوعات: {total_payments}")
        y -= 30

        c.drawString(100, y, "تفاصيل المتدربين:")
        y -= 20
        c.drawString(100, y, "الاسم | عدد الدروس | إجمالي المدفوعات | الحالة")
        y -= 20

        students = self.session.query(Student).all()
        for student in students:
            lessons_count = self.session.query(func.count(Lesson.id)).filter(Lesson.student_id == student.id).scalar()
            payments_sum = self.session.query(func.sum(Payment.amount)).filter(Payment.student_id == student.id).scalar() or 0
            c.drawString(100, y, f"{student.full_name} | {lessons_count} | {payments_sum} | {student.status}")
            y -= 20
            if y < 50:
                c.showPage()
                y = 750

        c.save()
        QMessageBox.information(self, "نجاح", f"تم تصدير التقرير إلى {pdf_path}")