# School Onboarding & Data Population via Excel

## 📌 Overview
This project automates **school setup onboarding** into a clean MySQL database using Excel files.
The loader reads Excel sheets, validates data, maintains referential integrity, and ensures all functional requirements are met.

---
## 📂 Folder Structure
project/
├── create_tables.sql # MySQL-compatible schema with FK constraints
├── data_loader.py # Python loader script (MySQL version)
├── sample_excels/ # Folder for Excel input files
│ ├── schools.xlsx
│ ├── grades.xlsx
│ ├── sections.xlsx
│ ├── subjects.xlsx
│ ├── teachers.xlsx
│ ├── teacher_section_map.xlsx
│ ├── students.xlsx
│ ├── student_academic_map.xlsx
│ ├── attendance.xlsx
│ ├── class_diary.xlsx
│ ├── homework.xlsx
│ ├── timetable.xlsx
│ ├── fees.xlsx
│ ├── fee_payments.xlsx
│ ├── teacher_salary_structure.xlsx
│ ├── teacher_payslips.xlsx
├── README.md # This documentation
└── data_loader.log # Log file after running script
---

## ⚙️ How to Run the Loader (MySQL/XAMPP)

### 1. Start MySQL in XAMPP
- Open **XAMPP Control Panel**
- Start **MySQL** and **Apache**

### 2. Create Database & Tables
- Open **phpMyAdmin** at `http://localhost/phpmyadmin/`
- Create a database:
  ```sql
  CREATE DATABASE school_db;
  ```
- Import `create_tables.sql` into `school_db`

### 3. Install Python Requirements
```bash
pip install pandas sqlalchemy pymysql openpyxl
```

### 4. Update DB Connection in `data_loader.py`
```python
DB_URL = "mysql+pymysql://root:@localhost/school_db"
```
*(If you set a password for MySQL `root` user, add it after `root:`)*

### 5. Prepare Excel Files
- Place your `.xlsx` files in `sample_excels/`
- If the folder is empty, the script will **auto-generate sample templates** with dummy data

### 6. Run Loader
```bash
python data_loader.py
```

---

## 🔄 Changes Made
- Converted schema from **PostgreSQL** to **MySQL** (replaced `SERIAL` with `INT AUTO_INCREMENT`, `BOOLEAN` with `TINYINT(1)`, `ENUM` for fixed values)
- Adjusted `data_loader.py` to use **pymysql** for MySQL connections
- Added `ON UPDATE CURRENT_TIMESTAMP` to audit columns
- Ensured MySQL-compatible `FOREIGN KEY` syntax
- Used MySQL `ENUM` types for attendance status, homework status, and period types

---

## ✅ Criteria Coverage (Point-Wise)

1. **School Setup** - 1 school created with 3 grades and 2 sections per grade  
2. **Students** - 10 students per section → 60 students total, ≥ 80% attendance  
3. **Teachers** - 8 teachers, ≥ 2 sections each, 3 homework entries (Pending, Submitted, Completed), 2 diary entries  
4. **Lesson Plans** - Linked to homework  
5. **Timetable** - Weekly schedule with breaks and free periods  
6. **Fees** - At least 1 installment per student, linked to income  
7. **Salaries** - Payslips for June and July  
8. **Data Integrity** - Foreign key constraints maintained  
9. **Automation** - Excel-driven ETL pipeline  
10. **Documentation** - This README file

---

## 📊 How to Verify
Example SQL checks in phpMyAdmin:

**Attendance ≥ 80%**
```sql
SELECT student_id,
       100 * SUM(status='Present') / COUNT(*) AS attendance_pct
FROM ss_t_attendance_register
GROUP BY student_id;
```

**Homework Count**
```sql
SELECT teacher_id, status, COUNT(*)
FROM ss_t_homework_details
GROUP BY teacher_id, status;
```

**Class Diary**
```sql
SELECT teacher_id, COUNT(*)
FROM ss_t_class_diary
GROUP BY teacher_id;
```

**Fee Income**
```sql
SELECT * FROM ss_t_school_income;
```

**Payslips**
```sql
SELECT teacher_id, month_year
FROM ss_t_teacher_salary_payslip;
```
