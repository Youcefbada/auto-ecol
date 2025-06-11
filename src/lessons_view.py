from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QDateEdit, QLineEdit, QLabel
from PyQt6.QtCore import Qt, QDate 
from sqlalchemy.orm import sessionmaker
from models import engine, Lesson, Student
from PyQt6.QtWidgets import QMessageBox

class LessonsView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إدارة الدروس")
        self.setMinimumSize(800, 400)
        layout = QVBoxLayout(self)
        self.session = sessionmaker(bind=engine)()

        #layout = QVBoxLayout(self)

        # فلتر
        filter_layout = QHBoxLayout()
        self.student_filter = QComboBox()
        self.student_filter.addItem("جميع المتدربين", 0)
        students = self.session.query(Student).all()
        for student in students:
            self.student_filter.addItem(f"{student.full_name} ({student.file_number})", student.id)
        self.student_filter.currentIndexChanged.connect(self.load_lessons)
        filter_layout.addWidget(QLabel("المتدرب:"))
        filter_layout.addWidget(self.student_filter)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Completed", "Missed", "Planned"])
        self.status_filter.currentIndexChanged.connect(self.load_lessons)
        filter_layout.addWidget(QLabel("الحالة:"))
        filter_layout.addWidget(self.status_filter)
        layout.addLayout(filter_layout)

        # جدول الدروس
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["المتدرب", "التاريخ", "الوقت", "النوع", "المدرب", "الحالة"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # أضافة درس
        add_layout = QHBoxLayout()
        self.add_student = QComboBox()
        for student in students:
            self.add_student.addItem(f"{student.full_name} ({student.file_number})", student.id)
        add_layout.addWidget(QLabel("المتدرب:"))
        add_layout.addWidget(self.add_student)

        self.add_date = QDateEdit()
        self.add_date.setDate(QDate.currentDate())
        add_layout.addWidget(QLabel("التاريخ:"))
        add_layout.addWidget(self.add_date)
        self.add_time = QLineEdit()
        self.add_time.setPlaceholderText("hh:mm")
        add_layout.addWidget(QLabel("الوقت:"))
        add_layout.addWidget(self.add_time)

        self.add_type = QComboBox()
        self.add_type.addItems(["Theoretical", "Practical"])
        add_layout.addWidget(QLabel("النوع:"))
        add_layout.addWidget(self.add_type)

        self.add_instructor = QLineEdit()
        self.add_instructor.setPlaceholderText("اسم المدرب")
        add_layout.addWidget(QLabel("المدرب:"))
        add_layout.addWidget(self.add_instructor)

        self.add_status = QComboBox()
        self.add_status.addItems(["Planned", "Completed", "Missed"])
        add_layout.addWidget(QLabel("الحالة:"))
        add_layout.addWidget(self.add_status)

        add_btn = QPushButton("إضافة درس")
        add_btn.clicked.connect(self.add_lesson)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)

        self.load_lessons()

    def load_lessons(self):
        self.table.setRowCount(0)
        student_id = self.student_filter.currentData()
        status = self.status_filter.currentText()

        query = self.session.query(Lesson).join(Student)
        if student_id:
            query = query.filter(Lesson.student_id == student_id)
        if status != "All":
            query = query.filter(Lesson.status == status)

        lessons = query.all()

        for row, lesson in enumerate(lessons):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(lesson.student.full_name))
            self.table.setItem(row, 1, QTableWidgetItem(str(lesson.lesson_date)))
            self.table.setItem(row, 2, QTableWidgetItem(lesson.lesson_time))
            self.table.setItem(row, 3, QTableWidgetItem(lesson.lesson_type))
            self.table.setItem(row, 4, QTableWidgetItem(lesson.instructor))
            self.table.setItem(row, 5, QTableWidgetItem(lesson.status))

    def add_lesson(self):
        student_id = self.add_student.currentData()
        lesson_date = self.add_date.date().toPython()
        lesson_time = self.add_time.text().strip()
        lesson_type = self.add_type.currentText()
        instructor = self.add_instructor.text().strip()
        status = self.add_status.currentText()

        if not student_id or not lesson_time or not instructor:
            QMessageBox.warning(self, "خطأ", "يرجى ملء جميع الحقول!")
            return

        lesson = Lesson(
            student_id=student_id,
            lesson_date=lesson_date,
            lesson_time=lesson_time,
            lesson_type=lesson_type,
            instructor=instructor,
            status=status
        )
        self.session.add(lesson)
        self.session.commit()
        self.load_lessons()
        QMessageBox.information(self, "نجاح", "تم إضافة الدرس!")
