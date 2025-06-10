from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QDateEdit, QLineEdit, QLabel, QDoubleSpinBox
from PyQt6.QtCore import Qt, QDate
from sqlalchemy.orm import sessionmaker
from models import engine, Payment, Student

class PaymentsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = sessionmaker(bind=engine)()

        layout = QVBoxLayout(self)

        # فلتر
        filter_layout = QHBoxLayout()
        self.student_filter = QComboBox()
        self.student_filter.addItem("جميع المتدربين", 0)
        students = self.session.query(Student).all()
        for student in students:
            self.student_filter.addItem(f"{student.full_name} ({student.file_number})", student.id)
        self.student_filter.currentIndexChanged.connect(self.load_payments)
        filter_layout.addWidget(QLabel("المتدرب:"))
        filter_layout.addWidget(self.student_filter)

        self.method_filter = QComboBox()
        self.method_filter.addItems(["All", "Cash", "CCP", "BaridiMob", "Other"])
        self.method_filter.currentIndexChanged.connect(self.load_payments)
        filter_layout.addWidget(QLabel("طريقة الدفع:"))
        filter_layout.addWidget(self.method_filter)
        layout.addLayout(filter_layout)

        # جدول المدفوعات
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["المتدرب", "المبلغ", "التاريخ", "طريقة الدفع", "ملاحظات"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # إضافة دفعة
        add_layout = QHBoxLayout()
        self.add_student = QComboBox()
        for student in students:
            self.add_student.addItem(f"{student.full_name} ({student.file_number})", student.id)
        add_layout.addWidget(QLabel("المتدرب:"))
        add_layout.addWidget(self.add_student)

        self.add_amount = QDoubleSpinBox()
        self.add_amount.setMinimum(0)
        self.add_amount.setMaximum(1000000)
        add_layout.addWidget(QLabel("المبلغ:"))
        add_layout.addWidget(self.add_amount)

        self.add_date = QDateEdit()
        self.add_date.setDate(QDate.currentDate())
        add_layout.addWidget(QLabel("التاريخ:"))
        add_layout.addWidget(self.add_date)

        self.add_method = QComboBox()
        self.add_method.addItems(["Cash", "CCP", "BaridiMob", "Other"])
        add_layout.addWidget(QLabel("طريقة الدفع:"))
        add_layout.addWidget(self.add_method)

        self.add_notes = QLineEdit()
        self.add_notes.setPlaceholderText("ملاحظات (اختياري)")
        add_layout.addWidget(QLabel("ملاحظات:"))
        add_layout.addWidget(self.add_notes)

        add_btn = QPushButton("إضافة دفعة")
        add_btn.clicked.connect(self.add_payment)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)

        self.load_payments()

    def load_payments(self):
        self.table.setRowCount(0)
        student_id = self.student_filter.currentData()
        method = self.method_filter.currentText()

        query = self.session.query(Payment).join(Student)
        if student_id:
            query = query.filter(Payment.student_id == student_id)
        if method != "All":
            query = query.filter(Payment.method == method)

        payments = query.all()

        for row, payment in enumerate(payments):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(payment.student.full_name))
            self.table.setItem(row, 1, QTableWidgetItem(str(payment.amount)))
            self.table.setItem(row, 2, QTableWidgetItem(str(payment.payment_date)))
            self.table.setItem(row, 3, QTableWidgetItem(payment.method))
            self.table.setItem(row, 4, QTableWidgetItem(payment.notes or ""))

    def add_payment(self):
        student_id = self.add_student.currentData()
        amount = self.add_amount.value()
        payment_date = self.add_date.date().toPython()
        method = self.add_method.currentText()
        notes = self.add_notes.text().strip() or None

        if not student_id or amount <= 0:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار متدرب وإدخال مبلغ صالح!")
            return

        payment = Payment(
            student_id=student_id,
            amount=amount,
            payment_date=payment_date,
            method=method,
            notes=notes
        )
        self.session.add(payment)
        self.session.commit()
        self.load_payments()
        QMessageBox.information(self, "نجاح", "تم إضافة الدفعة!")