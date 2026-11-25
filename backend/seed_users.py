import os, psycopg
from werkzeug.security import generate_password_hash
DB=os.environ["DATABASE_URL"]
users=[
 ("admin@employee360.local","Admin@12345","Admin","aarav.sharma@example.com"),
 ("hr@employee360.local","Hr@12345","HR","priya.nair@example.com"),
 ("manager@employee360.local","Manager@12345","Manager","aarav.sharma@example.com"),
 ("employee@employee360.local","Employee@12345","Employee","kabir.mehta@example.com"),
]
with psycopg.connect(DB) as c:
 for email,password,role,employee_email in users:
  c.execute("""INSERT INTO users(employee_id,email,password_hash,role)
   VALUES((SELECT id FROM employees WHERE email=%s),%s,%s,%s)
   ON CONFLICT(email) DO NOTHING""",(employee_email,email,generate_password_hash(password),role))
