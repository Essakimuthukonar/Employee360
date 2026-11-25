import os
from datetime import date, datetime
from decimal import Decimal
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import psycopg
from psycopg.rows import dict_row
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY", "unsafe-local-secret-change-me")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(os.getenv("JWT_HOURS", "8")) * 3600
CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)
REQUESTS = 0

def db():
    return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)

def normalize(value):
    if isinstance(value, (date, datetime)): return value.isoformat()
    if isinstance(value, Decimal): return float(value)
    if isinstance(value, dict): return {k: normalize(v) for k,v in value.items()}
    if isinstance(value, list): return [normalize(v) for v in value]
    return value

def query_one(sql, params=()):
    with db() as c: row = c.execute(sql, params).fetchone()
    return normalize(dict(row)) if row else None

def query_all(sql, params=()):
    with db() as c: rows = c.execute(sql, params).fetchall()
    return normalize([dict(r) for r in rows])

def body():
    return request.get_json(silent=True) or {}

def fail(message, code=400):
    return jsonify(error=message), code

def roles(*allowed):
    def deco(fn):
        @wraps(fn)
        @jwt_required()
        def wrapped(*args, **kwargs):
            ident = get_jwt_identity()
            user = query_one("SELECT id,employee_id,email,role,active FROM users WHERE id=%s", (int(ident),))
            if not user or not user["active"]: return fail("Account is inactive", 403)
            if allowed and user["role"] not in allowed: return fail("Insufficient permissions", 403)
            request.current_user = user
            return fn(*args, **kwargs)
        return wrapped
    return deco

@app.before_request
def count_request():
    global REQUESTS
    REQUESTS += 1

@app.get("/api/health")
def health():
    try:
        query_one("SELECT 1 AS ok")
        return jsonify(status="ok", database="connected")
    except Exception:
        return fail("Database unavailable", 503)

@app.get("/api/metrics")
def metrics():
    return (f"# HELP employee360_http_requests_total HTTP requests handled\\n"
            f"# TYPE employee360_http_requests_total counter\\n"
            f"employee360_http_requests_total {REQUESTS}\\n",
            200, {"Content-Type":"text/plain; version=0.0.4"})

@app.post("/api/auth/login")
def login():
    x = body()
    user = query_one("SELECT * FROM users WHERE lower(email)=lower(%s)", (x.get("email",""),))
    if not user or not user["active"] or not check_password_hash(user["password_hash"], x.get("password","")):
        return fail("Invalid email or password", 401)
    token = create_access_token(identity=str(user["id"]))
    return jsonify(access_token=token, user={"id":user["id"],"email":user["email"],"role":user["role"],"employee_id":user["employee_id"]})

@app.get("/api/auth/me")
@roles()
def me():
    return jsonify(user=request.current_user)

@app.get("/api/dashboard")
@roles()
def dashboard():
    summary = query_one("""SELECT COUNT(*) total,
      COUNT(*) FILTER(WHERE status='Active') active,
      COUNT(*) FILTER(WHERE status='On Leave') on_leave,
      COUNT(*) FILTER(WHERE status='Inactive') inactive
      FROM employees""")
    departments = query_all("""SELECT d.id,d.name,COUNT(e.id) count
      FROM departments d LEFT JOIN employees e ON e.department_id=d.id
      GROUP BY d.id ORDER BY d.name""")
    pending = query_one("SELECT COUNT(*) count FROM leave_requests WHERE status='Pending'")
    open_jobs = query_one("SELECT COUNT(*) count FROM job_openings WHERE status='Open'")
    return jsonify(summary=summary, departments=departments, pending_leaves=pending["count"], open_jobs=open_jobs["count"])

@app.get("/api/employees")
@roles()
def employees():
    q = "%" + request.args.get("search","").strip() + "%"
    status = request.args.get("status","")
    return jsonify(query_all("""SELECT e.*,d.name department FROM employees e
      LEFT JOIN departments d ON d.id=e.department_id
      WHERE (%s='' OR e.first_name ILIKE %s OR e.last_name ILIKE %s OR e.email ILIKE %s OR e.employee_code ILIKE %s OR e.job_title ILIKE %s)
      AND (%s='' OR e.status=%s) ORDER BY e.id DESC""",
      (request.args.get("search",""),q,q,q,q,q,status,status)))

@app.get("/api/employees/<int:emp_id>")
@roles()
def employee(emp_id):
    row = query_one("""SELECT e.*,d.name department FROM employees e LEFT JOIN departments d ON d.id=e.department_id WHERE e.id=%s""",(emp_id,))
    if not row: return fail("Employee not found",404)
    return jsonify(row)

@app.post("/api/employees")
@roles("Admin","HR")
def create_employee():
    x=body()
    required=["employee_code","first_name","last_name","email","job_title"]
    if any(not x.get(k) for k in required): return fail("Employee code, name, email and job title are required")
    try:
        with db() as c:
            row=c.execute("""INSERT INTO employees(employee_code,first_name,last_name,email,phone,job_title,department_id,manager_id,employment_type,status,location,joining_date,date_of_birth,address,emergency_contact)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
            tuple(x.get(k) or None for k in ["employee_code","first_name","last_name","email","phone","job_title","department_id","manager_id","employment_type","status","location","joining_date","date_of_birth","address","emergency_contact"])).fetchone()
        return jsonify(normalize(dict(row))),201
    except psycopg.errors.UniqueViolation: return fail("Employee code or email already exists",409)

@app.put("/api/employees/<int:emp_id>")
@roles("Admin","HR")
def update_employee(emp_id):
    x=body()
    allowed=["first_name","last_name","email","phone","job_title","department_id","manager_id","employment_type","status","location","joining_date","date_of_birth","address","emergency_contact"]
    keys=[k for k in allowed if k in x]
    if not keys: return fail("No editable fields supplied")
    try:
        with db() as c:
            row=c.execute("UPDATE employees SET "+",".join(k+"=%s" for k in keys)+" WHERE id=%s RETURNING *",tuple(x[k] for k in keys)+(emp_id,)).fetchone()
        return (jsonify(normalize(dict(row))),200) if row else fail("Employee not found",404)
    except psycopg.errors.UniqueViolation: return fail("Email already exists",409)

@app.delete("/api/employees/<int:emp_id>")
@roles("Admin","HR")
def delete_employee(emp_id):
    with db() as c: row=c.execute("DELETE FROM employees WHERE id=%s RETURNING id",(emp_id,)).fetchone()
    return (jsonify(message="Employee deleted"),200) if row else fail("Employee not found",404)

@app.get("/api/departments")
@roles()
def departments():
    return jsonify(query_all("""SELECT d.*,e.first_name||' '||e.last_name manager_name
      FROM departments d LEFT JOIN employees e ON e.id=d.manager_employee_id ORDER BY d.name"""))

@app.post("/api/departments")
@roles("Admin","HR")
def create_department():
    x=body()
    if not x.get("name"): return fail("Department name is required")
    try:
        row=query_one("INSERT INTO departments(name,description,manager_employee_id) VALUES(%s,%s,%s) RETURNING *",(x["name"],x.get("description"),x.get("manager_employee_id") or None))
        return jsonify(row),201
    except psycopg.errors.UniqueViolation: return fail("Department already exists",409)

@app.get("/api/attendance")
@roles()
def attendance():
    emp=request.args.get("employee_id")
    if emp is not None:
        try: emp=int(emp)
        except ValueError: return fail("employee_id must be an integer")
    if request.current_user["role"]=="Employee": emp=request.current_user["employee_id"]
    sql="""SELECT a.*,e.first_name||' '||e.last_name employee_name,e.employee_code FROM attendance a JOIN employees e ON e.id=a.employee_id WHERE (CAST(%s AS INTEGER) IS NULL OR a.employee_id=%s) ORDER BY work_date DESC LIMIT 200"""
    return jsonify(query_all(sql,(emp,emp)))

@app.post("/api/attendance/check-in")
@roles()
def checkin():
    emp=request.current_user["employee_id"]
    if request.current_user["role"] in ("Admin","HR","Manager"): emp=body().get("employee_id",emp)
    if not emp: return fail("User is not linked to an employee profile",400)
    try:
        with db() as c:
            row=c.execute("""INSERT INTO attendance(employee_id,work_date,check_in,status) VALUES(%s,CURRENT_DATE,NOW(),'Present')
              ON CONFLICT(employee_id,work_date) DO UPDATE SET check_in=COALESCE(attendance.check_in,EXCLUDED.check_in) RETURNING *""",(emp,)).fetchone()
        return jsonify(normalize(dict(row))),201
    except Exception: return fail("Unable to check in")

@app.post("/api/attendance/check-out")
@roles()
def checkout():
    emp=request.current_user["employee_id"]
    if request.current_user["role"] in ("Admin","HR","Manager"): emp=body().get("employee_id",emp)
    row=query_one("UPDATE attendance SET check_out=NOW() WHERE employee_id=%s AND work_date=CURRENT_DATE AND check_out IS NULL RETURNING *",(emp,))
    return (jsonify(row),200) if row else fail("No open check-in found",404)

@app.get("/api/leaves")
@roles()
def leaves():
    emp=request.args.get("employee_id")
    if emp is not None:
        try: emp=int(emp)
        except ValueError: return fail("employee_id must be an integer")
    if request.current_user["role"]=="Employee": emp=request.current_user["employee_id"]
    return jsonify(query_all("""SELECT l.*,e.first_name||' '||e.last_name employee_name FROM leave_requests l JOIN employees e ON e.id=l.employee_id WHERE (CAST(%s AS INTEGER) IS NULL OR l.employee_id=%s) ORDER BY l.created_at DESC""",(emp,emp)))

@app.post("/api/leaves")
@roles()
def create_leave():
    x=body(); emp=request.current_user["employee_id"]
    if request.current_user["role"] in ("Admin","HR","Manager"): emp=x.get("employee_id",emp)
    if not emp or not all(x.get(k) for k in ["leave_type","start_date","end_date"]): return fail("Employee, leave type and dates are required")
    if x["end_date"] < x["start_date"]: return fail("End date cannot be before start date")
    row=query_one("INSERT INTO leave_requests(employee_id,leave_type,start_date,end_date,reason) VALUES(%s,%s,%s,%s,%s) RETURNING *",(emp,x["leave_type"],x["start_date"],x["end_date"],x.get("reason")))
    return jsonify(row),201

@app.post("/api/leaves/<int:leave_id>/decision")
@roles("Admin","HR","Manager")
def decide_leave(leave_id):
    x=body()
    if x.get("status") not in ("Approved","Rejected"): return fail("Decision must be Approved or Rejected")
    row=query_one("UPDATE leave_requests SET status=%s,reviewer_comment=%s WHERE id=%s AND status='Pending' RETURNING *",(x["status"],x.get("comment"),leave_id))
    return (jsonify(row),200) if row else fail("Pending leave request not found",404)

@app.get("/api/payroll")
@roles("Admin","HR")
def payroll():
    return jsonify(query_all("""SELECT p.*,e.first_name||' '||e.last_name employee_name,e.employee_code FROM payroll p JOIN employees e ON e.id=p.employee_id ORDER BY pay_month DESC"""))

@app.post("/api/payroll")
@roles("Admin","HR")
def create_payroll():
    x=body()
    try:
        base=float(x["base_salary"]); allowances=float(x.get("allowances",0)); deductions=float(x.get("deductions",0))
        if min(base,allowances,deductions)<0 or deductions>base+allowances: return fail("Invalid salary amounts")
        net=base+allowances-deductions
        row=query_one("""INSERT INTO payroll(employee_id,pay_month,base_salary,allowances,deductions,net_pay,status)
          VALUES(%s,%s,%s,%s,%s,%s,'Draft') RETURNING *""",(x["employee_id"],x["pay_month"],base,allowances,deductions,net))
        return jsonify(row),201
    except (KeyError,ValueError,TypeError): return fail("Provide employee_id, pay_month and valid salary amounts")
    except psycopg.errors.UniqueViolation: return fail("Payroll record already exists for this employee and month",409)

@app.get("/api/performance")
@roles()
def performance():
    return jsonify(query_all("""SELECT r.*,e.first_name||' '||e.last_name employee_name FROM performance_reviews r JOIN employees e ON e.id=r.employee_id ORDER BY created_at DESC"""))

@app.post("/api/performance")
@roles("Admin","HR","Manager")
def create_performance():
    x=body()
    try:
        row=query_one("""INSERT INTO performance_reviews(employee_id,reviewer_id,review_period,rating,goals,feedback)
          VALUES(%s,%s,%s,%s,%s,%s) RETURNING *""",(x["employee_id"],request.current_user["employee_id"],x["review_period"],float(x["rating"]),x.get("goals"),x.get("feedback")))
        return jsonify(row),201
    except (KeyError,ValueError,TypeError): return fail("Provide employee, review period and rating from 0 to 5")

@app.get("/api/jobs")
@roles()
def jobs():
    return jsonify(query_all("""SELECT j.*,d.name department FROM job_openings j LEFT JOIN departments d ON d.id=j.department_id ORDER BY created_at DESC"""))

@app.post("/api/jobs")
@roles("Admin","HR")
def create_job():
    x=body()
    if not x.get("title"): return fail("Job title is required")
    row=query_one("INSERT INTO job_openings(title,department_id,location,employment_type,description,status) VALUES(%s,%s,%s,%s,%s,%s) RETURNING *",(x["title"],x.get("department_id") or None,x.get("location"),x.get("employment_type"),x.get("description"),x.get("status","Open")))
    return jsonify(row),201

@app.get("/api/candidates")
@roles("Admin","HR","Manager")
def candidates():
    return jsonify(query_all("""SELECT c.*,j.title job_title FROM candidates c LEFT JOIN job_openings j ON j.id=c.job_id ORDER BY created_at DESC"""))

@app.post("/api/candidates")
@roles("Admin","HR")
def create_candidate():
    x=body()
    if not all(x.get(k) for k in ["first_name","last_name","email"]): return fail("Candidate name and email are required")
    row=query_one("INSERT INTO candidates(job_id,first_name,last_name,email,phone,stage,notes) VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING *",(x.get("job_id") or None,x["first_name"],x["last_name"],x["email"],x.get("phone"),x.get("stage","Applied"),x.get("notes")))
    return jsonify(row),201

@app.get("/api/onboarding")
@roles()
def onboarding():
    return jsonify(query_all("""SELECT t.*,e.first_name||' '||e.last_name employee_name FROM onboarding_tasks t JOIN employees e ON e.id=t.employee_id ORDER BY due_date NULLS LAST"""))

@app.post("/api/onboarding")
@roles("Admin","HR")
def create_onboarding():
    x=body()
    if not x.get("employee_id") or not x.get("task_name"): return fail("Employee and task name are required")
    row=query_one("INSERT INTO onboarding_tasks(employee_id,task_name,owner,due_date) VALUES(%s,%s,%s,%s) RETURNING *",(x["employee_id"],x["task_name"],x.get("owner"),x.get("due_date") or None))
    return jsonify(row),201

@app.patch("/api/onboarding/<int:task_id>")
@roles("Admin","HR")
def update_onboarding(task_id):
    x=body()
    status=x.get("status")
    if status not in ("Pending","In Progress","Completed","Blocked"):
        return fail("Status must be Pending, In Progress, Completed or Blocked")
    row=query_one("UPDATE onboarding_tasks SET status=%s,completed_at=CASE WHEN %s='Completed' THEN NOW() ELSE NULL END WHERE id=%s RETURNING *",(status,status,task_id))
    return (jsonify(row),200) if row else fail("Onboarding task not found",404)

@app.get("/api/notifications")
@roles()
def notifications():
    return jsonify(query_all("SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 100",(request.current_user["id"],)))

@app.errorhandler(404)
def not_found(_): return fail("Route not found",404)

@app.errorhandler(500)
def server_error(_): return fail("Internal server error",500)
