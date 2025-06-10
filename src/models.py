from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    address = Column(String)
    registration_date = Column(Date, default=func.now())
    file_number = Column(String, unique=True, nullable=False)
    training_type = Column(String)  # Théorique / Pratique
    status = Column(String)  # Active / Completed / Dropped
    folder_path = Column(String)  # مسار مجلد المتدرب
    documents = relationship("Document", back_populates="student")
    lessons = relationship("Lesson", back_populates="student")
    payments = relationship("Payment", back_populates="student")

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    lesson_date = Column(Date)
    lesson_time = Column(String)  # hh:mm format
    lesson_type = Column(String)  # Theoretical / Practical
    instructor = Column(String)
    status = Column(String)  # Completed / Missed / Planned
    student = relationship("Student", back_populates="lessons")

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    amount = Column(Float)
    payment_date = Column(Date)
    method = Column(String)  # Cash / CCP / BaridiMob / Other
    notes = Column(String)
    student = relationship("Student", back_populates="payments")

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    document_type = Column(String)  # IDCard, MedicalCertificate, etc.
    file_path = Column(String)
    student = relationship("Student", back_populates="documents")

# إعداد قاعدة البيانات
engine = create_engine('sqlite:///DrivingSchool.db')
Base.metadata.create_all(engine)