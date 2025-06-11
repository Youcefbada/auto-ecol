from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship  # Added this import
from datetime import date

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    address = Column(String)
    registration_date = Column(Date, default=date.today)  # Use date.today as a callable
    file_number = Column(String, nullable=False, unique=True)
    training_type = Column(String)
    status = Column(String)
    folder_path = Column(String)
    lessons = relationship("Lesson", back_populates="student")  # Define the reverse relationship
    payments = relationship("Payment", back_populates="student")  # Define the reverse relationship

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
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    document_type = Column(String)
    file_path = Column(String)

# إعداد قاعدة البيانات
from sqlalchemy import create_engine  # Added this import
engine = create_engine('sqlite:///DrivingSchool.db')
Base.metadata.create_all(engine)