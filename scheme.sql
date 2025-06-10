-- قاعدة البيانات: autoecol (في SQLite يتم تحديد الاسم عند فتح الملف autoecol.db)

-- حذف الجداول القديمة إن وُجدت (اختياري أثناء التطوير)
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS lessons;
DROP TABLE IF EXISTS students;

-- إنشاء جدول الطلاب (المتدربون)
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,  -- بدون AUTOINCREMENT
    full_name TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    registration_date DATE DEFAULT (date('now')),
    file_number TEXT NOT NULL UNIQUE,
    training_type TEXT,
    status TEXT,
    folder_path TEXT
);


-- إنشاء جدول الدروس
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    lesson_date DATE,
    lesson_time TEXT,
    lesson_type TEXT,
    instructor TEXT,
    status TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- إنشاء جدول المدفوعات
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    amount REAL,
    payment_date DATE,
    method TEXT,
    notes TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- إنشاء جدول الوثائق
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    document_type TEXT,
    file_path TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
