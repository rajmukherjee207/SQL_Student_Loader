"""
data_loader.py

Reads Excel sheets from ./sample_excels/ and inserts into DB (Postgres) following create_tables.sql schema.

Assumptions:
- PostgreSQL (adjust DB_URL if using another DB)
- create_tables.sql has been applied already
- Excel files are named as:
    sample_excels/schools.xlsx
    sample_excels/grades.xlsx
    sample_excels/sections.xlsx
    sample_excels/subjects.xlsx
    sample_excels/teachers.xlsx
    sample_excels/teacher_section_map.xlsx (optional)
    sample_excels/students.xlsx
    sample_excels/student_academic_map.xlsx (optional)
    sample_excels/attendance.xlsx
    sample_excels/class_diary.xlsx
    sample_excels/homework.xlsx
    sample_excels/timetable.xlsx
    sample_excels/fees.xlsx
    sample_excels/fee_payments.xlsx
    sample_excels/teacher_salary_structure.xlsx
    sample_excels/teacher_payslips.xlsx

The script inserts in the correct order, validates presence of required columns,
and uses transactions. Adjust as needed for your exact Excel format.
"""

import os
import sys
import logging
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# ---------- CONFIG ----------
DB_URL = "mysql+pymysql://root:@localhost/school_db"
EXCEL_DIR = "sample_excels"
LOGFILE = "data_loader.log"
# ----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOGFILE), logging.StreamHandler(sys.stdout)]
)

engine = create_engine(DB_URL, echo=False, future=True)

# ---------- Helpers ----------
def read_sheet(name, required_cols=None):
    path = os.path.join(EXCEL_DIR, f"{name}.xlsx")
    if not os.path.exists(path):
        logging.warning(f"Sheet {name}.xlsx not found in {EXCEL_DIR}.")
        return None
    df = pd.read_excel(path, engine="openpyxl")
    if required_cols:
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"{name}.xlsx is missing columns: {missing}")
    return df

def ensure_dir():
    os.makedirs(EXCEL_DIR, exist_ok=True)

def create_sample_excels():
    """Create minimal sample excel files so user can fill/see formats."""
    ensure_dir()
    samples = {
        "schools": pd.DataFrame([{"name":"Demo School","type":"Private","contact_details":"9999999999","location":"Mumbai"}]),
        "grades": pd.DataFrame([{"school_id":1,"grade_name":"Grade 6","display_order":1},
                                {"school_id":1,"grade_name":"Grade 7","display_order":2},
                                {"school_id":1,"grade_name":"Grade 8","display_order":3}]),
        "sections": pd.DataFrame([{"grade_id":1,"section_name":"A"},{"grade_id":1,"section_name":"B"}]),
        "subjects": pd.DataFrame([{"school_id":1,"subject_name":"Math"},{"school_id":1,"subject_name":"Science"}]),
        "teachers": pd.DataFrame([{"school_id":1,"name":"Teacher A","contact_info":"111","gender":"M","qualification":"BEd"},
                                  {"school_id":1,"name":"Teacher B","contact_info":"222","gender":"F","qualification":"MEd"}]),
        "students": pd.DataFrame([{"school_id":1,"name":"Student 1","dob":"2012-01-01","gender":"M"}]),
        "student_academic_map": pd.DataFrame([{"student_id":1,"grade_id":1,"section_id":1,"academic_year":"2024-25"}]),
        "attendance": pd.DataFrame([{"student_id":1,"attendance_date":datetime.today().date(),"status":"Present"}]),
        "class_diary": pd.DataFrame([{"grade_id":1,"section_id":1,"subject_id":1,"teacher_id":1,"diary_date":datetime.today().date(),"activity":"Intro"}]),
        "homework": pd.DataFrame([{"school_id":1,"grade_id":1,"section_id":1,"subject_id":1,"teacher_id":1,"homework_date":datetime.today().date(),"status":"Pending","description":"Solve Q1"}]),
        "timetable": pd.DataFrame([{"school_id":1,"grade_id":1,"section_id":1,"subject_id":1,"teacher_id":1,"day_of_week":"Monday","period_number":1,"period_type":"Class"}]),
        "fees": pd.DataFrame([{"student_id":1,"fee_amount":1000.0}]),
        "fee_payments": pd.DataFrame([{"student_id":1,"fee_structure_id":1,"amount_paid":500.0,"payment_date":datetime.today().date(),"payment_method":"Online"}]),
        "teacher_salary_structure": pd.DataFrame([{"teacher_id":1,"basic_pay":30000.0,"hra":5000.0,"other_allowances":2000.0}]),
        "teacher_payslips": pd.DataFrame([{"teacher_id":1,"month_year":"2025-06","gross_salary":37000.0,"deductions":2000.0,"net_salary":35000.0}])
    }
    for name, df in samples.items():
        path = os.path.join(EXCEL_DIR, f"{name}.xlsx")
        df.to_excel(path, index=False)
        logging.info(f"Created sample {path}")

# ---------- Insert functions ----------
def insert_table_from_df(conn, df, table_name, cols=None):
    """Insert rows from df into table_name. Returns number of rows inserted."""
    if df is None or df.empty:
        logging.info(f"No data to insert for {table_name}.")
        return 0
    # Use parameterized insert with text()
    cols = cols or list(df.columns)
    col_list = ", ".join(cols)
    placeholders = ", ".join([f":{c}" for c in cols])
    stmt = text(f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})")
    rows = df[cols].to_dict(orient="records")
    conn.execute(stmt, rows)
    return len(rows)

def fetch_one(conn, query, params=None):
    res = conn.execute(text(query), params or {})
    return res.fetchone()

# ---------- High-level loader ----------
def run_loader():
    ensure_dir()
    # if directory empty - create sample excels
    if not os.listdir(EXCEL_DIR):
        logging.info(f"{EXCEL_DIR} empty — creating sample excel templates.")
        create_sample_excels()
        logging.info("Fill sample_excels/*.xlsx with your data and re-run the script.")
        return

    # Read sheets (non-fatal if some optional sheets missing)
    try:
        df_schools = read_sheet("schools", required_cols=["name"])
        df_grades = read_sheet("grades", required_cols=["school_id","grade_name"])
        df_sections = read_sheet("sections", required_cols=["grade_id","section_name"])
        df_subjects = read_sheet("subjects", required_cols=["school_id","subject_name"])
        df_teachers = read_sheet("teachers", required_cols=["school_id","name"])
        df_teacher_section_map = read_sheet("teacher_section_map")  # optional
        df_students = read_sheet("students", required_cols=["school_id","name"])
        df_student_academic_map = read_sheet("student_academic_map")  # optional
        df_attendance = read_sheet("attendance", required_cols=["student_id","attendance_date","status"])
        df_class_diary = read_sheet("class_diary", required_cols=["grade_id","section_id","subject_id","teacher_id","diary_date"])
        df_homework = read_sheet("homework", required_cols=["school_id","grade_id","section_id","subject_id","teacher_id","homework_date","status"])
        df_timetable = read_sheet("timetable", required_cols=["school_id","grade_id","section_id","subject_id","teacher_id","day_of_week","period_number","period_type"])
        df_fees = read_sheet("fees", required_cols=["student_id","fee_amount"])
        df_fee_payments = read_sheet("fee_payments", required_cols=["student_id","fee_structure_id","amount_paid","payment_date"])
        df_teacher_salary = read_sheet("teacher_salary_structure", required_cols=["teacher_id","basic_pay"])
        df_payslips = read_sheet("teacher_payslips", required_cols=["teacher_id","month_year","gross_salary"])
    except Exception as e:
        logging.exception("Error reading excel sheets: %s", e)
        return

    # Begin DB transaction and inserts
    try:
        with engine.begin() as conn:  # transaction
            # Order of insertion to satisfy FKs
            if df_schools is not None:
                inserted = insert_table_from_df(conn, df_schools, "ss_t_schools")
                logging.info(f"Inserted {inserted} schools")

            if df_grades is not None:
                inserted = insert_table_from_df(conn, df_grades, "ss_t_grade")
                logging.info(f"Inserted {inserted} grades")

            if df_sections is not None:
                inserted = insert_table_from_df(conn, df_sections, "ss_t_section")
                logging.info(f"Inserted {inserted} sections")

            if df_subjects is not None:
                inserted = insert_table_from_df(conn, df_subjects, "ss_t_subject")
                logging.info(f"Inserted {inserted} subjects")

            if df_teachers is not None:
                inserted = insert_table_from_df(conn, df_teachers, "ss_t_teacher")
                logging.info(f"Inserted {inserted} teachers")

            # If teacher_section_map provided insert, else attempt to auto-map teachers to sections (basic)
            if df_teacher_section_map is not None:
                inserted = insert_table_from_df(conn, df_teacher_section_map, "ss_t_teacher_section_map")
                logging.info(f"Inserted {inserted} teacher_section_map rows")
            else:
                # OPTIONAL: auto-assign each teacher to first 2 sections (if sections exist)
                logging.info("No teacher_section_map.xlsx found — attempting auto-assignment (2 sections per teacher)")
                sections = conn.execute(text("SELECT section_id, grade_id FROM ss_t_section ORDER BY section_id")).fetchall()
                teachers = conn.execute(text("SELECT teacher_id, school_id FROM ss_t_teacher ORDER BY teacher_id")).fetchall()
                # simple algorithm: round-robin assign 2 sections to each teacher
                assignments = []
                sec_ids = [s.section_id for s in sections]
                if sec_ids:
                    idx = 0
                    for t in teachers:
                        for _ in range(2):
                            sid = sec_ids[idx % len(sec_ids)]
                            # need grade_id for mapping
                            grade_id = conn.execute(text("SELECT grade_id FROM ss_t_section WHERE section_id = :sid"), {"sid": sid}).scalar()
                            # pick a subject for the school arbitrarily
                            subject_id = conn.execute(text("SELECT subject_id FROM ss_t_subject WHERE school_id = :s"), {"s": t.school_id}).scalar()
                            assignments.append({"teacher_id": t.teacher_id, "grade_id": grade_id, "section_id": sid, "subject_id": subject_id})
                            idx += 1
                    if assignments:
                        conn.execute(text("""INSERT INTO ss_t_teacher_section_map (teacher_id, grade_id, section_id, subject_id, created_at, updated_at)
                                              VALUES (:teacher_id, :grade_id, :section_id, :subject_id, NOW(), NOW())"""), assignments)
                        logging.info(f"Auto-assigned {len(assignments)} teacher-section mappings")

            # STUDENTS
            if df_students is not None:
                inserted = insert_table_from_df(conn, df_students, "ss_t_student")
                logging.info(f"Inserted {inserted} students")

            # STUDENT ACADEMIC MAP: if not provided, auto-map students evenly into sections
            if df_student_academic_map is not None:
                inserted = insert_table_from_df(conn, df_student_academic_map, "ss_t_student_academic_map")
                logging.info(f"Inserted {inserted} student_academic_map rows")
            else:
                logging.info("No student_academic_map.xlsx — auto-mapping students to sections (10 per section target)")
                students = conn.execute(text("SELECT student_id FROM ss_t_student ORDER BY student_id")).fetchall()
                sections = conn.execute(text("SELECT section_id, grade_id FROM ss_t_section ORDER BY section_id")).fetchall()
                records = []
                sec_idx = 0
                for i, s in enumerate(students):
                    sec = sections[sec_idx % len(sections)]
                    records.append({"student_id": s.student_id, "grade_id": sec.grade_id, "section_id": sec.section_id, "academic_year":"2024-25"})
                    # aim for 10 per section then move to next
                    if (i+1) % 10 == 0:
                        sec_idx += 1
                if records:
                    conn.execute(text("""INSERT INTO ss_t_student_academic_map (student_id, grade_id, section_id, academic_year, created_at, updated_at)
                                         VALUES (:student_id, :grade_id, :section_id, :academic_year, NOW(), NOW())"""), records)
                    logging.info(f"Auto-inserted {len(records)} student academic mappings")

            # ATTENDANCE - must ensure >= 80% attendance overall (business rule)
            if df_attendance is not None:
                inserted = insert_table_from_df(conn, df_attendance, "ss_t_attendance_register")
                logging.info(f"Inserted {inserted} attendance records")
            else:
                # Optionally generate attendance to satisfy >=80% for the month for all students
                logging.info("No attendance.xlsx — creating synthetic attendance with >=80% present for current month")
                students = conn.execute(text("SELECT student_id FROM ss_t_student")).fetchall()
                today = datetime.today()
                # example: generate 20 school days for month start
                dates = pd.date_range(start=today.replace(day=1), periods=20, freq='B')  # business days
                records = []
                for s in students:
                    for d in dates:
                        status = "Present" if (pd.np.random.rand() <= 0.85) else "Absent"  # ~85% present
                        records.append({"student_id": s.student_id, "attendance_date": d.date(), "status": status, "remarks": None})
                if records:
                    conn.execute(text("""INSERT INTO ss_t_attendance_register (student_id, attendance_date, status, remarks, created_at, updated_at)
                                         VALUES (:student_id, :attendance_date, :status, :remarks, NOW(), NOW())"""), records)
                    logging.info(f"Inserted synthetic {len(records)} attendance records")

            # CLASS DIARY
            if df_class_diary is not None:
                inserted = insert_table_from_df(conn, df_class_diary, "ss_t_class_diary")
                logging.info(f"Inserted {inserted} class diary rows")
            else:
                logging.info("No class_diary.xlsx — creating 2 diary entries per teacher (assignment requirement)")
                teachers = conn.execute(text("SELECT teacher_id FROM ss_t_teacher")).fetchall()
                diary_rows = []
                for t in teachers:
                    diary_rows.append({"grade_id": 1, "section_id": 1, "subject_id": 1, "teacher_id": t.teacher_id, "diary_date": datetime.today().date(), "activity":"Activity 1"})
                    diary_rows.append({"grade_id": 1, "section_id": 1, "subject_id": 1, "teacher_id": t.teacher_id, "diary_date": datetime.today().date(), "activity":"Activity 2"})
                conn.execute(text("""INSERT INTO ss_t_class_diary (grade_id, section_id, subject_id, teacher_id, diary_date, activity, created_at, updated_at)
                                     VALUES (:grade_id, :section_id, :subject_id, :teacher_id, :diary_date, :activity, NOW(), NOW())"""), diary_rows)
                logging.info(f"Inserted {len(diary_rows)} auto diary entries")

            # HOMEWORK - ensure 3 per teacher in statuses: Pending, Submitted, Completed
            if df_homework is not None:
                inserted = insert_table_from_df(conn, df_homework, "ss_t_homework_details")
                logging.info(f"Inserted {inserted} homework rows")
            else:
                logging.info("No homework.xlsx — creating 3 homework entries per teacher (Pending/Submitted/Completed)")
                teachers = conn.execute(text("SELECT teacher_id FROM ss_t_teacher")).fetchall()
                hw_rows = []
                statuses = ["Pending", "Submitted", "Completed"]
                for t in teachers:
                    for s in statuses:
                        hw_rows.append({"school_id":1,"grade_id":1,"section_id":1,"subject_id":1,"teacher_id":t.teacher_id,"homework_date":datetime.today().date(),"status":s,"description":f"HW {s}"})
                conn.execute(text("""INSERT INTO ss_t_homework_details (school_id, grade_id, section_id, subject_id, teacher_id, homework_date, status, description, created_at, updated_at)
                                     VALUES (:school_id, :grade_id, :section_id, :subject_id, :teacher_id, :homework_date, :status, :description, NOW(), NOW())"""), hw_rows)
                logging.info(f"Inserted {len(hw_rows)} auto homework rows")

            # TIMETABLE
            if df_timetable is not None:
                inserted = insert_table_from_df(conn, df_timetable, "ss_t_class_timetable")
                logging.info(f"Inserted {inserted} timetable rows")
            else:
                logging.info("No timetable.xlsx — creating minimal timetable entries")
                # create a single class period for demonstration
                conn.execute(text("""INSERT INTO ss_t_class_timetable (school_id, grade_id, section_id, subject_id, teacher_id, day_of_week, period_number, period_type, created_at, updated_at)
                                     VALUES (1,1,1,1,1,'Monday',1,'Class',NOW(),NOW())"""))
                logging.info("Inserted 1 timetable row")

            # FEES -> fee_structure and payments -> school_income
            if df_fees is not None:
                insert_table_from_df(conn, df_fees, "ss_t_student_fee_structure")
                logging.info("Inserted fee structures")
            if df_fee_payments is not None:
                insert_table_from_df(conn, df_fee_payments, "ss_t_fee_payment_installment")
                logging.info("Inserted fee payments")
                # propagate to school income
                payments = conn.execute(text("SELECT fee_payment_id FROM ss_t_fee_payment_installment ORDER BY fee_payment_id")).fetchall()
                income_rows = [{"fee_payment_id": p.fee_payment_id} for p in payments]
                if income_rows:
                    conn.execute(text("""INSERT INTO ss_t_school_income (fee_payment_id, created_at, updated_at) VALUES (:fee_payment_id, NOW(), NOW())"""), income_rows)
                    logging.info(f"Inserted {len(income_rows)} school income rows")
            else:
                logging.info("No fee_payments.xlsx — creating one payment per student and reflecting in school income")
                students = conn.execute(text("SELECT student_id FROM ss_t_student")).fetchall()
                payment_rows = []
                income_rows = []
                for s in students:
                    payment_rows.append({"student_id": s.student_id, "fee_structure_id": 1, "amount_paid": 500.0, "payment_date": datetime.today().date(), "payment_method": "Offline"})
                conn.execute(text("""INSERT INTO ss_t_fee_payment_installment (student_id, fee_structure_id, amount_paid, payment_date, payment_method, created_at, updated_at)
                                     VALUES (:student_id, :fee_structure_id, :amount_paid, :payment_date, :payment_method, NOW(), NOW())"""), payment_rows)
                payments = conn.execute(text("SELECT fee_payment_id FROM ss_t_fee_payment_installment ORDER BY fee_payment_id DESC LIMIT :n"), {"n": len(payment_rows)}).fetchall()
                for p in payments:
                    income_rows.append({"fee_payment_id": p.fee_payment_id})
                if income_rows:
                    conn.execute(text("""INSERT INTO ss_t_school_income (fee_payment_id, created_at, updated_at) VALUES (:fee_payment_id, NOW(), NOW())"""), income_rows)
                    logging.info(f"Inserted {len(income_rows)} school income rows")

            # TEACHER SALARY STRUCTURE and PAYSLIPS
            if df_teacher_salary is not None:
                inserted = insert_table_from_df(conn, df_teacher_salary, "ss_t_teacher_salary_structure")
                logging.info(f"Inserted {inserted} salary structures")
            if df_payslips is not None:
                inserted = insert_table_from_df(conn, df_payslips, "ss_t_teacher_salary_payslip")
                logging.info(f"Inserted {inserted} payslips")
            else:
                logging.info("No teacher_payslips.xlsx — creating payslips for June & July for each teacher")
                teachers = conn.execute(text("SELECT teacher_id FROM ss_t_teacher")).fetchall()
                pays = []
                for t in teachers:
                    pays.append({"teacher_id": t.teacher_id, "month_year":"2025-06", "gross_salary":35000.0, "deductions":2000.0, "net_salary":33000.0})
                    pays.append({"teacher_id": t.teacher_id, "month_year":"2025-07", "gross_salary":35000.0, "deductions":2000.0, "net_salary":33000.0})
                conn.execute(text("""INSERT INTO ss_t_teacher_salary_payslip (teacher_id, month_year, gross_salary, deductions, net_salary, created_at, updated_at)
                                     VALUES (:teacher_id, :month_year, :gross_salary, :deductions, :net_salary, NOW(), NOW())"""), pays)
                logging.info(f"Inserted {len(pays)} payslips")

            logging.info("Data load completed successfully within a transaction.")

    except SQLAlchemyError as e:
        logging.exception("Database error during load: %s", e)
    except Exception as e:
        logging.exception("Unexpected error during load: %s", e)

if __name__ == "__main__":
    run_loader()
