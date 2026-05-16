import sqlite3
import os
from datetime import datetime, date

DB_PATH = 'school_management.db'


def create_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        print(f"DB error: {e}")
        return None


def initialize_database():
    conn = create_connection()
    if not conn:
        return False
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        grade INTEGER NOT NULL
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        subject TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        dob DATE,
        gender TEXT CHECK(gender IN ('Male','Female','Other')),
        address TEXT,
        phone TEXT,
        email TEXT,
        section_id INTEGER,
        enrollment_year INTEGER,
        batch_year INTEGER,
        registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT CHECK(status IN ('Active','Inactive','Passed Out','Pending')) DEFAULT 'Active',
        FOREIGN KEY (section_id) REFERENCES sections(id)
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS student_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        section_id INTEGER,
        grade INTEGER,
        batch_year INTEGER,
        enrollment_year INTEGER,
        graduated_year INTEGER,
        status TEXT,
        notes TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (section_id) REFERENCES sections(id)
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        teacher_id INTEGER,
        section_id INTEGER,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id),
        FOREIGN KEY (section_id) REFERENCES sections(id)
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER,
        date DATE NOT NULL,
        status TEXT CHECK(status IN ('present','absent','late')) NOT NULL,
        remarks TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (course_id) REFERENCES courses(id),
        UNIQUE(student_id, date, course_id)
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        mid_term REAL,
        final_exam REAL,
        assignment REAL,
        overall REAL,
        grade TEXT,
        exam_date DATE,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (course_id) REFERENCES courses(id),
        UNIQUE(student_id, course_id)
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        due_date DATE,
        paid_date DATE,
        payment_method TEXT CHECK(payment_method IN ('Cash','Bank Transfer','Cheque')),
        status TEXT CHECK(status IN ('paid','unpaid','overdue','partial')) DEFAULT 'unpaid',
        notes TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )''')

    # Migrate: add new columns if they don't exist
    for col, defn in [
        ('enrollment_year', 'INTEGER'),
        ('batch_year',      'INTEGER'),
    ]:
        try:
            cur.execute(f"ALTER TABLE students ADD COLUMN {col} {defn}")
        except sqlite3.OperationalError:
            pass

    # Update status CHECK to allow Passed Out (recreate isn't needed; just ensure values work)

    # Seed sections: Grades 1-10, sections A-D
    cur.execute("SELECT COUNT(*) FROM sections")
    if cur.fetchone()[0] == 0:
        rows = []
        for g in range(1, 11):
            for sec in ['A', 'B', 'C', 'D']:
                rows.append((sec, g))
        cur.executemany("INSERT INTO sections (name, grade) VALUES (?, ?)", rows)

    # Seed teachers
    cur.execute("SELECT COUNT(*) FROM teachers")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO teachers (first_name, last_name, email, phone, subject) VALUES (?,?,?,?,?)",
            [
                ('Ayesha', 'Khalid', 'a.khalid@school.edu.pk', '0300-1112223', 'Mathematics'),
                ('Jawad',  'Akhtar', 'j.akhtar@school.edu.pk', '0321-4445556', 'Science'),
                ('Sobia',  'Malik',  's.malik@school.edu.pk',  '0333-7778889', 'English'),
                ('Tahir',  'Ahmed',  't.ahmed@school.edu.pk',  '0312-0001112', 'Urdu'),
            ]
        )

    # Seed courses
    cur.execute("SELECT COUNT(*) FROM courses")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO courses (name, teacher_id, section_id) VALUES (?,?,?)",
            [
                ('Mathematics', 1, 1), ('Mathematics', 1, 5),
                ('Science',     2, 2), ('Science',     2, 6),
                ('English',     3, 3), ('English',     3, 7),
                ('Urdu',        4, 4), ('Urdu',        4, 8),
            ]
        )

    conn.commit()
    cur.close()
    conn.close()
    return True


# ── Students ─────────────────────────────────────────────────────────────────

def get_all_students(include_passed_out=False):
    conn = create_connection()
    if not conn:
        return []
    cur = conn.cursor()
    if include_passed_out:
        where = ""
    else:
        where = "WHERE s.status != 'Passed Out'"
    cur.execute(f"""
        SELECT s.id, s.first_name, s.last_name, s.dob, s.gender,
               s.address, s.phone, s.email, s.status,
               s.registration_date, s.enrollment_year, s.batch_year,
               sec.name AS section_name, sec.grade
        FROM students s
        LEFT JOIN sections sec ON s.section_id = sec.id
        {where}
        ORDER BY s.registration_date DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def search_students(query, year_filter=None, grade_filter=None, section_filter=None,
                    status_filter=None, include_history=True, include_all=False):
    """
    Professional search: searches name, email, phone, ID, batch year, grade, section.
    Optionally filter by year, grade, section, status.
    include_all: if True, includes Passed Out students in results.
    """
    conn = create_connection()
    if not conn:
        return []
    cur = conn.cursor()
    like = f"%{query}%"
    conditions = ["""(
        s.first_name LIKE ? OR s.last_name LIKE ?
        OR s.email LIKE ? OR s.phone LIKE ?
        OR CAST(s.id AS TEXT) LIKE ?
        OR CAST(s.batch_year AS TEXT) LIKE ?
        OR CAST(s.enrollment_year AS TEXT) LIKE ?
        OR (s.first_name || ' ' || s.last_name) LIKE ?
        OR sec.name LIKE ?
    )"""]
    params = [like, like, like, like, like, like, like, like, like]

    if year_filter:
        conditions.append("(s.batch_year = ? OR s.enrollment_year = ?)")
        params += [year_filter, year_filter]
    if grade_filter:
        conditions.append("sec.grade = ?")
        params.append(grade_filter)
    if section_filter:
        conditions.append("sec.name = ?")
        params.append(section_filter)
    if status_filter and status_filter != 'All':
        conditions.append("s.status = ?")
        params.append(status_filter)

    where_clause = " AND ".join(conditions)
    cur.execute(f"""
        SELECT s.id, s.first_name, s.last_name, s.dob, s.gender,
               s.phone, s.email, s.status, s.registration_date,
               s.enrollment_year, s.batch_year,
               sec.name AS section_name, sec.grade
        FROM students s
        LEFT JOIN sections sec ON s.section_id = sec.id
        WHERE {where_clause}
        ORDER BY s.first_name
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_student_by_id(student_id):
    conn = create_connection()
    if not conn:
        return None
    cur = conn.cursor()
    cur.execute("""
        SELECT s.*, sec.name AS section_name, sec.grade
        FROM students s
        LEFT JOIN sections sec ON s.section_id = sec.id
        WHERE s.id = ?
    """, (student_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None


def register_student(first_name, last_name, dob, gender, address,
                     phone, email, section_id, status='Active',
                     batch_year=None, enrollment_year=None):
    conn = create_connection()
    if not conn:
        return None, "Database connection failed"
    if not batch_year:
        batch_year = date.today().year
    if not enrollment_year:
        enrollment_year = date.today().year
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO students
              (first_name, last_name, dob, gender, address, phone, email,
               section_id, status, batch_year, enrollment_year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, dob, gender, address, phone, email,
              section_id, status, batch_year, enrollment_year))
        conn.commit()
        new_id = cur.lastrowid
        # Log initial history
        _log_student_history(conn, new_id, section_id, enrollment_year, batch_year, status)
        conn.commit()
        cur.close()
        conn.close()
        return new_id, None
    except sqlite3.Error as e:
        conn.close()
        return None, str(e)


def _log_student_history(conn, student_id, section_id, enrollment_year, batch_year, status, notes='', graduated_year=None):
    cur = conn.cursor()
    # get grade from section
    cur.execute("SELECT grade FROM sections WHERE id = ?", (section_id,))
    row = cur.fetchone()
    grade = row['grade'] if row else None
    cur.execute("""
        INSERT INTO student_history
          (student_id, section_id, grade, batch_year, enrollment_year, graduated_year, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, section_id, grade, batch_year, enrollment_year, graduated_year, status, notes))
    cur.close()


def update_student(student_id, **fields):
    conn = create_connection()
    if not conn:
        return False, "Connection failed"
    allowed = {'first_name', 'last_name', 'dob', 'gender', 'address',
               'phone', 'email', 'section_id', 'status', 'batch_year', 'enrollment_year'}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return False, "No valid fields"
    set_clause = ', '.join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [student_id]
    try:
        cur = conn.cursor()
        cur.execute(f"UPDATE students SET {set_clause} WHERE id = ?", values)
        conn.commit()
        cur.close()
        conn.close()
        return True, None
    except sqlite3.Error as e:
        conn.close()
        return False, str(e)


def delete_student(student_id):
    conn = create_connection()
    if not conn:
        return False, "Connection failed"
    try:
        cur = conn.cursor()
        # Delete related records first
        cur.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
        cur.execute("DELETE FROM grades WHERE student_id = ?", (student_id,))
        cur.execute("DELETE FROM fees WHERE student_id = ?", (student_id,))
        cur.execute("DELETE FROM student_history WHERE student_id = ?", (student_id,))
        cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True, None
    except sqlite3.Error as e:
        conn.close()
        return False, str(e)


def mark_student_passed_out(student_id):
    """Mark student as passed out and log to history."""
    conn = create_connection()
    if not conn:
        return False, "Connection failed"
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        s = cur.fetchone()
        if not s:
            conn.close()
            return False, "Student not found"
        s = dict(s)
        graduated_year = date.today().year
        cur.execute("UPDATE students SET status = 'Passed Out' WHERE id = ?", (student_id,))
        # Log history
        _log_student_history(conn, student_id, s['section_id'],
                             s['enrollment_year'], s['batch_year'],
                             'Passed Out', 'Completed Grade 10', graduated_year)
        conn.commit()
        cur.close()
        conn.close()
        return True, None
    except sqlite3.Error as e:
        conn.close()
        return False, str(e)


def re_enroll_student(student_id, section_id, batch_year=None):
    """Re-enroll a passed-out student in a new batch/section."""
    conn = create_connection()
    if not conn:
        return False, "Connection failed"
    try:
        cur = conn.cursor()
        year = batch_year or date.today().year
        cur.execute("""
            UPDATE students SET section_id=?, status='Active',
            batch_year=?, enrollment_year=? WHERE id=?
        """, (section_id, year, year, student_id))
        _log_student_history(conn, student_id, section_id, year, year, 'Active', f'Re-enrolled batch {year}')
        conn.commit()
        cur.close()
        conn.close()
        return True, None
    except sqlite3.Error as e:
        conn.close()
        return False, str(e)


def auto_check_passed_out():
    """Auto-promote students in grade 10 who completed the year to Passed Out."""
    conn = create_connection()
    if not conn:
        return 0
    cur = conn.cursor()
    current_year = date.today().year
    # Students in grade 10, active, enrolled before this year
    cur.execute("""
        SELECT s.id FROM students s
        JOIN sections sec ON s.section_id = sec.id
        WHERE sec.grade = 10 AND s.status = 'Active'
          AND s.enrollment_year < ?
    """, (current_year,))
    ids = [r['id'] for r in cur.fetchall()]
    count = 0
    for sid in ids:
        cur.execute("UPDATE students SET status='Passed Out' WHERE id=?", (sid,))
        graduated_year = current_year
        cur.execute("SELECT section_id, enrollment_year, batch_year FROM students WHERE id=?", (sid,))
        s = dict(cur.fetchone())
        _log_student_history(conn, sid, s['section_id'],
                             s['enrollment_year'], s['batch_year'],
                             'Passed Out', 'Auto: completed Grade 10', graduated_year)
        count += 1
    conn.commit()
    cur.close()
    conn.close()
    return count


def get_student_history(student_id):
    conn = create_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT sh.*, sec.name AS section_name, sec.grade
        FROM student_history sh
        LEFT JOIN sections sec ON sh.section_id = sec.id
        WHERE sh.student_id = ?
        ORDER BY sh.id ASC
    """, (student_id,))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_students_by_batch_year(year):
    conn = create_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, s.first_name, s.last_name, s.dob, s.gender,
               s.phone, s.email, s.status, s.registration_date,
               s.enrollment_year, s.batch_year,
               sec.name AS section_name, sec.grade
        FROM students s
        LEFT JOIN sections sec ON s.section_id = sec.id
        WHERE s.batch_year = ? OR s.enrollment_year = ?
        ORDER BY s.first_name
    """, (year, year))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


# ── Sections ──────────────────────────────────────────────────────────────────

def get_sections():
    conn = create_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT sec.id, sec.name, sec.grade,
               COUNT(s.id) AS student_count
        FROM sections sec
        LEFT JOIN students s ON s.section_id = sec.id AND s.status='Active'
        GROUP BY sec.id
        ORDER BY sec.grade, sec.name
    """)
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_section_names():
    conn = create_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT id, name, grade FROM sections ORDER BY CAST(grade AS INTEGER), name")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


# ── Teachers ──────────────────────────────────────────────────────────────────

def get_all_teachers():
    conn = create_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT * FROM teachers ORDER BY first_name")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def add_teacher(first_name, last_name, email, phone, subject):
    conn = create_connection()
    if not conn:
        return None, "Connection failed"
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO teachers (first_name, last_name, email, phone, subject)
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, last_name, email, phone, subject))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return new_id, None
    except sqlite3.IntegrityError:
        conn.close()
        return None, "Email already exists"


def delete_teacher(teacher_id):
    conn = create_connection()
    if not conn:
        return False, "Connection failed"
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True, None
    except sqlite3.Error as e:
        conn.close()
        return False, str(e)


# ── Attendance ────────────────────────────────────────────────────────────────

def mark_attendance(student_id, att_date, status, course_id=None, remarks=''):
    conn = create_connection()
    if not conn:
        return False, "Connection failed"
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO attendance (student_id, course_id, date, status, remarks)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id, date, course_id)
            DO UPDATE SET status=excluded.status, remarks=excluded.remarks
        """, (student_id, course_id, att_date, status, remarks))
        conn.commit()
        cur.close()
        conn.close()
        return True, None
    except sqlite3.Error as e:
        conn.close()
        return False, str(e)


def get_attendance_by_date(att_date, section_id=None):
    conn = create_connection()
    if not conn:
        return []
    cur = conn.cursor()
    if section_id:
        cur.execute("""
            SELECT s.id, s.first_name, s.last_name,
                   a.status, a.remarks, a.date
            FROM students s
            LEFT JOIN attendance a ON a.student_id = s.id AND a.date = ?
            WHERE s.section_id = ? AND s.status='Active'
            ORDER BY s.first_name
        """, (att_date, section_id))
    else:
        cur.execute("""
            SELECT s.id, s.first_name, s.last_name,
                   a.status, a.remarks, a.date
            FROM students s
            LEFT JOIN attendance a ON a.student_id = s.id AND a.date = ?
            WHERE s.status='Active'
            ORDER BY s.first_name
        """, (att_date,))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_fees_by_student(student_id):
    conn = create_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT id, amount, due_date, paid_date, payment_method, status, notes
        FROM fees
        WHERE student_id = ?
        ORDER BY due_date DESC
    """, (student_id,))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_attendance_by_student(student_id):
    conn = create_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT a.date, a.status, a.remarks, c.name AS course_name
        FROM attendance a
        LEFT JOIN courses c ON a.course_id = c.id
        WHERE a.student_id = ?
        ORDER BY a.date DESC
    """, (student_id,))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_attendance_summary(student_id):
    conn = create_connection()
    if not conn:
        return {}
    cur = conn.cursor()
    cur.execute("""
        SELECT status, COUNT(*) as count
        FROM attendance WHERE student_id = ?
        GROUP BY status
    """, (student_id,))
    summary = {row['status']: row['count'] for row in cur.fetchall()}
    cur.close()
    conn.close()
    return summary


def get_attendance_rate(section_id=None):
    conn = create_connection()
    if not conn:
        return 0.0
    cur = conn.cursor()
    if section_id:
        cur.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) as present
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE s.section_id = ?
        """, (section_id,))
    else:
        cur.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) as present
            FROM attendance
        """)
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row and row['total']:
        return round((row['present'] / row['total']) * 100, 1)
    return 0.0


# ── Grades ────────────────────────────────────────────────────────────────────

def _compute_grade(overall):
    if overall is None:
        return None
    if overall >= 90: return 'A+'
    if overall >= 80: return 'A'
    if overall >= 70: return 'B'
    if overall >= 60: return 'C'
    if overall >= 50: return 'D'
    return 'F'


def save_grade(student_id, course_id, mid_term, final_exam, assignment, exam_date=None):
    overall = round((mid_term * 0.3 + final_exam * 0.5 + assignment * 0.2), 1)
    grade = _compute_grade(overall)
    conn = create_connection()
    if not conn:
        return False, "Connection failed"
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO grades
              (student_id, course_id, mid_term, final_exam, assignment, overall, grade, exam_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id, course_id)
            DO UPDATE SET mid_term=excluded.mid_term, final_exam=excluded.final_exam,
                          assignment=excluded.assignment, overall=excluded.overall,
                          grade=excluded.grade, exam_date=excluded.exam_date
        """, (student_id, course_id, mid_term, final_exam, assignment, overall, grade, exam_date))
        conn.commit()
        cur.close()
        conn.close()
        return True, None
    except sqlite3.Error as e:
        conn.close()
        return False, str(e)


def get_grades_by_course(course_id):
    conn = create_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, s.first_name, s.last_name,
               sec.name AS section_name, sec.grade AS section_grade,
               g.mid_term, g.final_exam, g.assignment, g.overall, g.grade, g.exam_date
        FROM students s
        LEFT JOIN grades g ON g.student_id = s.id AND g.course_id = ?
        LEFT JOIN sections sec ON s.section_id = sec.id
        ORDER BY s.first_name
    """, (course_id,))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_grades_by_student(student_id):
    conn = create_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name AS course_name, g.mid_term, g.final_exam,
               g.assignment, g.overall, g.grade, g.exam_date
        FROM grades g
        JOIN courses c ON g.course_id = c.id
        WHERE g.student_id = ?
        ORDER BY g.exam_date DESC
    """, (student_id,))
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


# ── Fees ──────────────────────────────────────────────────────────────────────

def add_fee_record(student_id, amount, due_date, status='unpaid'):
    conn = create_connection()
    if not conn:
        return None, "Connection failed"
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO fees (student_id, amount, due_date, status)
            VALUES (?, ?, ?, ?)
        """, (student_id, amount, due_date, status))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return new_id, None
    except sqlite3.Error as e:
        conn.close()
        return None, str(e)


def record_payment(fee_id, paid_date, payment_method):
    conn = create_connection()
    if not conn:
        return False, "Connection failed"
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE fees SET status='paid', paid_date=?, payment_method=?
            WHERE id=?
        """, (paid_date, payment_method, fee_id))
        conn.commit()
        cur.close()
        conn.close()
        return True, None
    except sqlite3.Error as e:
        conn.close()
        return False, str(e)


def get_all_fees():
    conn = create_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT f.*, s.first_name, s.last_name
        FROM fees f
        JOIN students s ON f.student_id = s.id
        ORDER BY f.due_date DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def get_fee_summary():
    conn = create_connection()
    if not conn:
        return {}
    cur = conn.cursor()
    cur.execute("""
        SELECT
          COALESCE(SUM(CASE WHEN status='paid'    THEN amount ELSE 0 END), 0) AS collected,
          COALESCE(SUM(CASE WHEN status='unpaid'  THEN amount ELSE 0 END), 0) AS pending,
          COALESCE(SUM(CASE WHEN status='overdue' THEN amount ELSE 0 END), 0) AS overdue,
          COUNT(CASE WHEN status IN ('unpaid','overdue') THEN 1 END)          AS pending_count
        FROM fees
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else {'collected': 0, 'pending': 0, 'overdue': 0, 'pending_count': 0}


# ── Dashboard ─────────────────────────────────────────────────────────────────

def get_dashboard_stats():
    conn = create_connection()
    if not conn:
        return {}
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM students WHERE status='Active'")
    total_students = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM teachers")
    total_teachers = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) as present
        FROM attendance
        WHERE date >= date('now', '-7 days')
    """)
    att = cur.fetchone()
    att_rate = round((att['present'] / att['total']) * 100, 1) if att and att['total'] else 0.0
    cur.close()
    conn.close()
    fee_summary = get_fee_summary()
    return {
        'total_students':  total_students,
        'total_teachers':  total_teachers,
        'attendance_rate': att_rate,
        'fees_collected':  fee_summary.get('collected') or 0,
        'fees_pending':    fee_summary.get('pending_count') or 0,
    }
