CREATE TABLE IF NOT EXISTS departments (
 id SERIAL PRIMARY KEY, name VARCHAR(100) UNIQUE NOT NULL, description TEXT,
 manager_employee_id INTEGER, created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS employees (
 id SERIAL PRIMARY KEY, employee_code VARCHAR(30) UNIQUE NOT NULL,
 first_name VARCHAR(80) NOT NULL, last_name VARCHAR(80) NOT NULL,
 email VARCHAR(180) UNIQUE NOT NULL, phone VARCHAR(40), job_title VARCHAR(120) NOT NULL,
 department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
 manager_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
 employment_type VARCHAR(30) DEFAULT 'Full-time',
 status VARCHAR(30) DEFAULT 'Active', location VARCHAR(120),
 joining_date DATE, date_of_birth DATE, address TEXT, emergency_contact VARCHAR(160),
 created_at TIMESTAMP DEFAULT NOW()
);
ALTER TABLE departments DROP CONSTRAINT IF EXISTS departments_manager_employee_id_fkey;
ALTER TABLE departments ADD CONSTRAINT departments_manager_employee_id_fkey
 FOREIGN KEY(manager_employee_id) REFERENCES employees(id) ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS users (
 id SERIAL PRIMARY KEY, employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
 email VARCHAR(180) UNIQUE NOT NULL, password_hash TEXT NOT NULL,
 role VARCHAR(30) NOT NULL CHECK(role IN ('Admin','HR','Manager','Employee')),
 active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS attendance (
 id SERIAL PRIMARY KEY, employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
 work_date DATE NOT NULL DEFAULT CURRENT_DATE, check_in TIMESTAMP, check_out TIMESTAMP,
 status VARCHAR(30) DEFAULT 'Present', notes TEXT, UNIQUE(employee_id, work_date)
);
CREATE TABLE IF NOT EXISTS leave_requests (
 id SERIAL PRIMARY KEY, employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
 leave_type VARCHAR(40) NOT NULL, start_date DATE NOT NULL, end_date DATE NOT NULL,
 reason TEXT, status VARCHAR(30) DEFAULT 'Pending', reviewer_id INTEGER REFERENCES employees(id),
 reviewer_comment TEXT, created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS payroll (
 id SERIAL PRIMARY KEY, employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
 pay_month VARCHAR(7) NOT NULL, base_salary NUMERIC(12,2) NOT NULL,
 allowances NUMERIC(12,2) DEFAULT 0, deductions NUMERIC(12,2) DEFAULT 0,
 net_pay NUMERIC(12,2) NOT NULL, status VARCHAR(30) DEFAULT 'Draft',
 paid_at TIMESTAMP, created_at TIMESTAMP DEFAULT NOW(), UNIQUE(employee_id,pay_month)
);
CREATE TABLE IF NOT EXISTS performance_reviews (
 id SERIAL PRIMARY KEY, employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
 reviewer_id INTEGER REFERENCES employees(id), review_period VARCHAR(40) NOT NULL,
 rating NUMERIC(3,1) NOT NULL CHECK(rating>=0 AND rating<=5), goals TEXT,
 feedback TEXT, status VARCHAR(30) DEFAULT 'Submitted', created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS job_openings (
 id SERIAL PRIMARY KEY, title VARCHAR(140) NOT NULL, department_id INTEGER REFERENCES departments(id),
 location VARCHAR(120), employment_type VARCHAR(30), description TEXT,
 status VARCHAR(30) DEFAULT 'Open', created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS candidates (
 id SERIAL PRIMARY KEY, job_id INTEGER REFERENCES job_openings(id) ON DELETE SET NULL,
 first_name VARCHAR(80) NOT NULL, last_name VARCHAR(80) NOT NULL,
 email VARCHAR(180) NOT NULL, phone VARCHAR(40), stage VARCHAR(40) DEFAULT 'Applied',
 notes TEXT, created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS onboarding_tasks (
 id SERIAL PRIMARY KEY, employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
 task_name VARCHAR(160) NOT NULL, owner VARCHAR(120), due_date DATE,
 status VARCHAR(30) DEFAULT 'Pending', completed_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS notifications (
 id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
 title VARCHAR(180) NOT NULL, message TEXT NOT NULL, read BOOLEAN DEFAULT FALSE,
 created_at TIMESTAMP DEFAULT NOW()
);

-- Synthetic demo records; only seed when the employees table is empty.
INSERT INTO departments(name,description) VALUES
 ('Engineering','Product and engineering'),('Human Resources','People operations'),
 ('Finance','Finance and payroll'),('Operations','Business operations'),('Sales','Commercial team')
ON CONFLICT(name) DO NOTHING;

INSERT INTO employees(employee_code,first_name,last_name,email,phone,job_title,department_id,employment_type,status,location,joining_date,manager_id)
SELECT 'E360-001','Aarav','Sharma','aarav.sharma@example.com','9000000001','Engineering Manager',id,'Full-time','Active','Mumbai','2022-04-11',NULL
FROM departments WHERE name='Engineering'
ON CONFLICT(employee_code) DO NOTHING;
INSERT INTO employees(employee_code,first_name,last_name,email,phone,job_title,department_id,employment_type,status,location,joining_date,manager_id)
SELECT 'E360-002','Priya','Nair','priya.nair@example.com','9000000002','HR Manager',id,'Full-time','Active','Mumbai','2021-08-16',NULL
FROM departments WHERE name='Human Resources'
ON CONFLICT(employee_code) DO NOTHING;
INSERT INTO employees(employee_code,first_name,last_name,email,phone,job_title,department_id,employment_type,status,location,joining_date,manager_id)
SELECT 'E360-003','Kabir','Mehta','kabir.mehta@example.com','9000000003','Software Engineer',id,'Full-time','Active','Pune','2024-01-08',1
FROM departments WHERE name='Engineering'
ON CONFLICT(employee_code) DO NOTHING;
INSERT INTO employees(employee_code,first_name,last_name,email,phone,job_title,department_id,employment_type,status,location,joining_date,manager_id)
SELECT 'E360-004','Anaya','Rao','anaya.rao@example.com','9000000004','Finance Analyst',id,'Full-time','On Leave','Mumbai','2023-06-12',NULL
FROM departments WHERE name='Finance'
ON CONFLICT(employee_code) DO NOTHING;
