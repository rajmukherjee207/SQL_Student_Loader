-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS school_db;
USE school_db;

-- SCHOOLS
CREATE TABLE ss_t_schools (
    school_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    contact_details VARCHAR(255),
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- GRADES
CREATE TABLE ss_t_grade (
    grade_id INT AUTO_INCREMENT PRIMARY KEY,
    school_id INT NOT NULL,
    grade_name VARCHAR(50) NOT NULL,
    active_flag TINYINT(1) DEFAULT 1,
    display_order INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES ss_t_schools(school_id)
);

-- SECTIONS
CREATE TABLE ss_t_section (
    section_id INT AUTO_INCREMENT PRIMARY KEY,
    grade_id INT NOT NULL,
    section_name VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (grade_id) REFERENCES ss_t_grade(grade_id)
);

-- SUBJECTS
CREATE TABLE ss_t_subject (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    school_id INT NOT NULL,
    subject_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES ss_t_schools(school_id)
);

-- TEACHERS
CREATE TABLE ss_t_teacher (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    school_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    contact_info VARCHAR(100),
    gender VARCHAR(10),
    qualification VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES ss_t_schools(school_id)
);

-- TEACHER - SECTION - SUBJECT MAP
CREATE TABLE ss_t_teacher_section_map (
    map_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    grade_id INT NOT NULL,
    section_id INT NOT NULL,
    subject_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES ss_t_teacher(teacher_id),
    FOREIGN KEY (grade_id) REFERENCES ss_t_grade(grade_id),
    FOREIGN KEY (section_id) REFERENCES ss_t_section(section_id),
    FOREIGN KEY (subject_id) REFERENCES ss_t_subject(subject_id)
);

-- STUDENTS
CREATE TABLE ss_t_student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    school_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    dob DATE,
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES ss_t_schools(school_id)
);

-- STUDENT ACADEMIC MAP
CREATE TABLE ss_t_student_academic_map (
    map_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    grade_id INT NOT NULL,
    section_id INT NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES ss_t_student(student_id),
    FOREIGN KEY (grade_id) REFERENCES ss_t_grade(grade_id),
    FOREIGN KEY (section_id) REFERENCES ss_t_section(section_id)
);

-- ATTENDANCE
CREATE TABLE ss_t_attendance_register (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent', 'Late'),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES ss_t_student(student_id)
);

-- CLASS DIARY
CREATE TABLE ss_t_class_diary (
    diary_id INT AUTO_INCREMENT PRIMARY KEY,
    grade_id INT NOT NULL,
    section_id INT NOT NULL,
    subject_id INT NOT NULL,
    teacher_id INT NOT NULL,
    diary_date DATE NOT NULL,
    activity TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (grade_id) REFERENCES ss_t_grade(grade_id),
    FOREIGN KEY (section_id) REFERENCES ss_t_section(section_id),
    FOREIGN KEY (subject_id) REFERENCES ss_t_subject(subject_id),
    FOREIGN KEY (teacher_id) REFERENCES ss_t_teacher(teacher_id)
);

-- HOMEWORK
CREATE TABLE ss_t_homework_details (
    homework_id INT AUTO_INCREMENT PRIMARY KEY,
    school_id INT NOT NULL,
    grade_id INT NOT NULL,
    section_id INT NOT NULL,
    subject_id INT NOT NULL,
    teacher_id INT NOT NULL,
    homework_date DATE NOT NULL,
    status ENUM('Pending', 'Submitted', 'Completed'),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES ss_t_schools(school_id),
    FOREIGN KEY (grade_id) REFERENCES ss_t_grade(grade_id),
    FOREIGN KEY (section_id) REFERENCES ss_t_section(section_id),
    FOREIGN KEY (subject_id) REFERENCES ss_t_subject(subject_id),
    FOREIGN KEY (teacher_id) REFERENCES ss_t_teacher(teacher_id)
);

-- TIMETABLE
CREATE TABLE ss_t_class_timetable (
    timetable_id INT AUTO_INCREMENT PRIMARY KEY,
    school_id INT NOT NULL,
    grade_id INT NOT NULL,
    section_id INT NOT NULL,
    subject_id INT NOT NULL,
    teacher_id INT NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    period_number INT NOT NULL,
    period_type ENUM('Class', 'Break', 'Free'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES ss_t_schools(school_id),
    FOREIGN KEY (grade_id) REFERENCES ss_t_grade(grade_id),
    FOREIGN KEY (section_id) REFERENCES ss_t_section(section_id),
    FOREIGN KEY (subject_id) REFERENCES ss_t_subject(subject_id),
    FOREIGN KEY (teacher_id) REFERENCES ss_t_teacher(teacher_id)
);

-- FEES
CREATE TABLE ss_t_student_fee_structure (
    fee_structure_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    fee_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES ss_t_student(student_id)
);

CREATE TABLE ss_t_fee_payment_installment (
    fee_payment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    fee_structure_id INT NOT NULL,
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES ss_t_student(student_id),
    FOREIGN KEY (fee_structure_id) REFERENCES ss_t_student_fee_structure(fee_structure_id)
);

CREATE TABLE ss_t_school_income (
    income_id INT AUTO_INCREMENT PRIMARY KEY,
    fee_payment_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (fee_payment_id) REFERENCES ss_t_fee_payment_installment(fee_payment_id)
);

-- TEACHER SALARY
CREATE TABLE ss_t_teacher_salary_structure (
    salary_structure_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    basic_pay DECIMAL(10,2) NOT NULL,
    hra DECIMAL(10,2),
    other_allowances DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES ss_t_teacher(teacher_id)
);

CREATE TABLE ss_t_teacher_salary_payslip (
    payslip_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    month_year VARCHAR(7) NOT NULL,
    gross_salary DECIMAL(10,2) NOT NULL,
    deductions DECIMAL(10,2),
    net_salary DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES ss_t_teacher(teacher_id)
);
