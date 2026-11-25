import React,{useEffect,useMemo,useState} from 'react';
import{createRoot}from'react-dom/client';
import{LayoutDashboard,Users,Building2,CalendarCheck,CalendarDays,Wallet,Star,BriefcaseBusiness,ClipboardCheck,Bell,Search,Plus,LogOut,Menu,ChevronRight,RefreshCw,CheckCircle2,Clock3,UserRound,ArrowUpRight}from'lucide-react';
import{ResponsiveContainer,BarChart,Bar,XAxis,YAxis,Tooltip,CartesianGrid,PieChart,Pie,Cell}from'recharts';
import './style.css';

const API='/api';
const money=v=>'₹'+Number(v||0).toLocaleString('en-IN');
const full=e=>`${e.first_name||''} ${e.last_name||''}`.trim();
const initials=e=>`${e.first_name?.[0]||''}${e.last_name?.[0]||''}`.toUpperCase();
async function api(path,token,options={}) {
 const r=await fetch(API+path,{...options,headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`}:{}) ,...(options.headers||{})}});
 const data=await r.json().catch(()=>({}));
 if(!r.ok)throw new Error(data.error||`Request failed (${r.status})`);
 return data;
}
function App(){
 const[token,setToken]=useState(localStorage.getItem('e360_token')||'');
 const[user,setUser]=useState(JSON.parse(localStorage.getItem('e360_user')||'null'));
 const[page,setPage]=useState('Dashboard');
 const[data,setData]=useState({}); const[busy,setBusy]=useState(false); const[error,setError]=useState('');
 const[search,setSearch]=useState(''); const[modal,setModal]=useState(false); const[refresh,setRefresh]=useState(0);
 const nav=[
  ['Dashboard',LayoutDashboard],['Employees',Users],['Departments',Building2],
  ['Attendance',CalendarCheck],['Leave management',CalendarDays],['Payroll',Wallet],
  ['Performance',Star],['Recruitment',BriefcaseBusiness],['Onboarding',ClipboardCheck],['Notifications',Bell]
 ];
 async function load(){
  if(!token)return;setBusy(true);setError('');
  const paths={Dashboard:'/dashboard',Employees:'/employees',Departments:'/departments',Attendance:'/attendance', 'Leave management':'/leaves',Payroll:'/payroll',Performance:'/performance',Recruitment:'/jobs',Onboarding:'/onboarding',Notifications:'/notifications'};
  try{
   const result=await api(paths[page]||'/dashboard',token);
   setData(old=>({...old,[page]:result}));
   if(page==='Dashboard'){
    const [emps,leaves,jobs]=await Promise.all([api('/employees',token),api('/leaves',token),api('/jobs',token)]);
    setData(old=>({...old,Employees:emps, 'Leave management':leaves,Recruitment:jobs}));
   }
  }catch(e){setError(e.message)}finally{setBusy(false)}
 }
 useEffect(()=>{if(token)load()},[token,page,refresh]);
 async function login(email,password){const d=await api('/auth/login',null,{method:'POST',body:JSON.stringify({email,password})});localStorage.setItem('e360_token',d.access_token);localStorage.setItem('e360_user',JSON.stringify(d.user));setToken(d.access_token);setUser(d.user)}
 function logout(){localStorage.removeItem('e360_token');localStorage.removeItem('e360_user');setToken('');setUser(null);setData({})}
 async function create(path,payload){await api(path,token,{method:'POST',body:JSON.stringify(payload)});setModal(false);setRefresh(x=>x+1)}
 if(!token)return <Login onLogin={login}/>;
 const rows=data[page]||[];
 return <div className="shell">
  <aside className="sidebar"><div className="brand"><div className="brand-logo">e</div><div><b>employee<span>360</span></b><small>PEOPLE PLATFORM</small></div></div>
   <div className="workspace"><span className="green-dot"/> Organization workspace</div><div className="nav-title">MAIN MENU</div>
   {nav.map(([n,I])=><button key={n} className={`nav-item ${page===n?'active':''}`} onClick={()=>setPage(n)}><I size={17}/><span>{n}</span>{n==='Notifications'&&<i className="nav-dot"/>}</button>)}
   <div className="side-bottom"><div className="help"><b>People, connected.</b><p>One workspace for your entire employee lifecycle.</p><small>EMPLOYEE 360 · HRMS</small></div><div className="user-mini"><div className="avatar">{user?.role?.slice(0,2).toUpperCase()}</div><div><b>{user?.email?.split('@')[0]}</b><small>{user?.role}</small></div><button onClick={logout} title="Logout"><LogOut size={16}/></button></div></div>
  </aside>
  <main className="main"><header className="topbar"><div className="breadcrumb">Workspace <ChevronRight size={14}/><b>{page}</b></div><div className="top-right"><span className="role-pill">{user?.role}</span><button className="icon-btn" onClick={()=>setRefresh(x=>x+1)}><RefreshCw size={16}/></button><div className="avatar admin">{user?.role?.slice(0,2).toUpperCase()}</div></div></header>
   <section className="content">
    {error&&<div className="alert">{error}</div>}
    {page==='Dashboard'?<Dashboard data={data.Dashboard||{}} employees={data.Employees||[]} leaves={data['Leave management']||[]} jobs={data.Recruitment||[]} go={setPage}/>:
    <Module page={page} rows={rows} search={search} setSearch={setSearch} busy={busy} onAdd={()=>setModal(true)} onAction={async (path,payload)=>{try{await api(path,token,{method:'POST',body:JSON.stringify(payload)});setRefresh(x=>x+1)}catch(e){setError(e.message)}}}/>}
   </section>
  </main>
  {modal&&<RecordModal page={page} data={data} onClose={()=>setModal(false)} onSave={create}/>}
 </div>
}
function Login({onLogin}){
 const[email,setEmail]=useState('admin@employee360.local'),[password,setPassword]=useState('Admin@12345'),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 async function submit(e){e.preventDefault();setBusy(true);setError('');try{await onLogin(email,password)}catch(x){setError(x.message)}finally{setBusy(false)}}
 return <div className="login-screen"><div className="login-card"><div className="brand centered"><div className="brand-logo">e</div><div><b>employee<span>360</span></b><small>PEOPLE PLATFORM</small></div></div><p className="eyebrow">WELCOME BACK</p><h1>Sign in to your workspace</h1><p className="muted">Manage your people and everything around them.</p>{error&&<div className="alert">{error}</div>}<form onSubmit={submit}><label>Work email<input type="email" value={email} onChange={e=>setEmail(e.target.value)} required/></label><label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} required/></label><button className="primary full" disabled={busy}>{busy?'Signing in...':'Sign in'}</button></form><div className="demo-note">Demo account: admin@employee360.local · Admin@12345</div></div></div>
}
function Dashboard({data,employees,leaves,jobs,go}){
 const s=data.summary||{};
 const dept=data.departments||[];
 const pie=dept.map(d=>({name:d.name,value:Number(d.count)}));
 return <><div className="heading"><div><div className="eyebrow">MONDAY, YOUR PEOPLE AT A GLANCE</div><h1>People overview</h1><p>Here’s what’s happening across your organization.</p></div><button className="secondary" onClick={()=>go('Employees')}>Employee directory <ArrowUpRight size={15}/></button></div>
  <div className="stats-grid"><Stat icon={Users} label="Total employees" value={s.total||0} tone="violet" note="Across the organization"/><Stat icon={CheckCircle2} label="Active employees" value={s.active||0} tone="green" note="Currently working"/><Stat icon={CalendarDays} label="Pending leave requests" value={data.pending_leaves||0} tone="orange" note="Awaiting review"/><Stat icon={BriefcaseBusiness} label="Open positions" value={data.open_jobs||0} tone="blue" note="Recruitment pipeline"/></div>
  <div className="dashboard-grid"><article className="panel"><div className="panel-head"><div><h2>Department overview</h2><p>Employee distribution by department</p></div><button className="link" onClick={()=>go('Departments')}>View departments →</button></div><div className="chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={dept}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="name" tick={{fontSize:10}}/><YAxis allowDecimals={false} tick={{fontSize:10}}/><Tooltip/><Bar dataKey="count" fill="#6d63e8" radius={[5,5,0,0]}/></BarChart></ResponsiveContainer></div></article>
   <article className="panel"><div className="panel-head"><div><h2>Workforce mix</h2><p>By department</p></div></div><div className="pie-wrap"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={pie} dataKey="value" nameKey="name" innerRadius={55} outerRadius={83} paddingAngle={3}>{pie.map((x,i)=><Cell key={x.name} fill={['#6d63e8','#32b58c','#efa64f','#5796dc','#d57bb0'][i%5]}/>)}</Pie><Tooltip/></PieChart></ResponsiveContainer></div><div className="legend">{pie.map((x,i)=><span><i style={{background:['#6d63e8','#32b58c','#efa64f','#5796dc','#d57bb0'][i%5]}}/>{x.name}</span>)}</div></article>
  </div>
  <div className="dashboard-grid lower"><article className="panel"><div className="panel-head"><div><h2>Recent employees</h2><p>Latest people records</p></div><button className="link" onClick={()=>go('Employees')}>View all →</button></div><Table rows={employees.slice(0,5)} cols={['employee','role','department','status']}/></article><article className="panel"><div className="panel-head"><div><h2>HR action center</h2><p>Items requiring attention</p></div></div><button className="action-row" onClick={()=>go('Leave management')}><span className="action-icon orange"><CalendarDays/></span><span><b>Leave requests</b><small>Review employee leave applications</small></span><strong>{data.pending_leaves||0}</strong></button><button className="action-row" onClick={()=>go('Recruitment')}><span className="action-icon blue"><BriefcaseBusiness/></span><span><b>Open positions</b><small>Manage hiring pipeline</small></span><strong>{data.open_jobs||0}</strong></button><button className="action-row" onClick={()=>go('Onboarding')}><span className="action-icon green"><ClipboardCheck/></span><span><b>Onboarding</b><small>Track joining tasks</small></span><ChevronRight/></button></article></div>
 </>
}
function Stat({icon:Icon,label,value,tone,note}){return <article className="stat"><div className={'stat-icon '+tone}><Icon size={19}/></div><small>{label}</small><h2>{value}</h2><p>{note}</p></article>}
function Table({rows,cols=['employee','role','department','status'],actions}){
 return <div className="table-wrap"><table><thead><tr>{cols.map(c=><th>{c.toUpperCase()}</th>)}{actions&&<th>ACTIONS</th>}</tr></thead><tbody>{rows.map((r,i)=><tr>{cols.map(c=><td>{c==='employee'?<div className="person"><span className="avatar">{initials(r)}</span><span><b>{r.employee_name||full(r)}</b><small>{r.employee_code||r.email||''}</small></span></div>:c==='status'?<span className="status">{r.status||r.stage||'—'}</span>:c==='role'?r.job_title||r.title||r.leave_type||r.task_name||'—':c==='department'?r.department||r.department_name||'—':r[c]??'—'}</td>)}{actions&&<td>{actions(r)}</td>}</tr>)}</tbody></table>{!rows.length&&<div className="empty">No records available yet.</div>}</div>
}
function Module({page,rows,search,setSearch,busy,onAdd,onAction}){
 const config={
  Employees:{title:'Employee directory',desc:'Manage your workforce and employee records.',add:'Add employee',cols:['employee','role','department','status']},
  Departments:{title:'Departments',desc:'Your organizational structure and teams.',add:'Add department',cols:['name','description','manager_name']},
  Attendance:{title:'Attendance',desc:'Daily check-in, check-out and attendance history.',add:'Check in',cols:['employee_name','work_date','check_in','check_out','status']},
  'Leave management':{title:'Leave management',desc:'Submit, review and manage employee leave requests.',add:'Apply for leave',cols:['employee_name','leave_type','start_date','end_date','status']},
  Payroll:{title:'Payroll',desc:'Salary records and payroll processing overview.',add:'Create payroll record',cols:['employee_name','pay_month','base_salary','net_pay','status']},
  Performance:{title:'Performance reviews',desc:'Employee goals, feedback and review ratings.',add:'Add review',cols:['employee_name','review_period','rating','status']},
  Recruitment:{title:'Recruitment',desc:'Open roles and hiring pipeline.',add:'Create job opening',cols:['title','department','location','employment_type','status']},
  Onboarding:{title:'Onboarding',desc:'Track employee joining tasks and readiness.',add:'Add onboarding task',cols:['employee_name','task_name','owner','due_date','status']},
  Notifications:{title:'Notifications',desc:'Your HR workflow updates and reminders.',add:null,cols:['title','message','created_at']}
 };
 const c=config[page]||config.Employees;
 let filtered=rows;
 if(page==='Employees')filtered=rows.filter(x=>[full(x),x.email,x.employee_code,x.job_title,x.department].join(' ').toLowerCase().includes(search.toLowerCase()));
 const role=localStorage.getItem('e360_user')?JSON.parse(localStorage.getItem('e360_user')).role:'Employee';
 return <><div className="heading"><div><div className="eyebrow">PEOPLE OPERATIONS</div><h1>{c.title}</h1><p>{c.desc}</p></div><div className="heading-actions">{c.add&&<button className="primary" onClick={()=>page==='Attendance'?onAction('/attendance/check-in',{}):onAdd()}><Plus size={16}/>{c.add}</button>}{page==='Attendance'&&<button className="secondary" onClick={()=>onAction('/attendance/check-out',{})}>Check out</button>}</div></div>
  <article className="panel module-panel"><div className="toolbar">{page==='Employees'&&<div className="search"><Search size={16}/><input placeholder="Search name, email, role or employee ID..." value={search} onChange={e=>setSearch(e.target.value)}/></div>}<span className="record-count">{filtered.length} records</span></div><Table rows={filtered} cols={c.cols}/></article>
  {page==='Leave management'&&role!=='Employee'&&<div className="review-hint">Select a pending request in the table to review it. Approval actions are available through the API endpoint.</div>}
 </>
}
function RecordModal({page,data,onClose,onSave}){
 const employees=data.Employees||[];const depts=data.Departments||[];
 const [x,setX]=useState({});const [err,setErr]=useState('');const set=(k,v)=>setX(o=>({...o,[k]:v}));
 const schemas={
  Employees:[['employee_code','Employee ID'],['first_name','First name'],['last_name','Last name'],['email','Work email'],['phone','Phone'],['job_title','Job title'],['location','Location'],['joining_date','Joining date'],['manager_id','Manager employee ID'],['department_id','Department ID']],
  Departments:[['name','Department name'],['description','Description']],
  'Leave management':[['leave_type','Leave type'],['start_date','Start date'],['end_date','End date'],['reason','Reason']],
  Payroll:[['employee_id','Employee ID'],['pay_month','Pay month (YYYY-MM)'],['base_salary','Base salary'],['allowances','Allowances'],['deductions','Deductions']],
  Performance:[['employee_id','Employee ID'],['review_period','Review period'],['rating','Rating (0–5)'],['goals','Goals'],['feedback','Feedback']],
  Recruitment:[['title','Job title'],['location','Location'],['employment_type','Employment type'],['description','Description']],
  Onboarding:[['employee_id','Employee ID'],['task_name','Task'],['owner','Task owner'],['due_date','Due date']]
 };
 const fields=schemas[page]||[];
 const endpoints={Employees:'/employees',Departments:'/departments','Leave management':'/leaves',Payroll:'/payroll',Performance:'/performance',Recruitment:'/jobs',Onboarding:'/onboarding'};
 async function submit(e){e.preventDefault();try{let payload={...x};['employee_id','department_id','manager_id','rating','base_salary','allowances','deductions'].forEach(k=>{if(payload[k]!==undefined&&payload[k]!=='')payload[k]=Number(payload[k])});await onSave(endpoints[page],payload)}catch(e){setErr(e.message)}}
 return <div className="overlay"><form className="modal" onSubmit={submit}><div className="modal-head"><div><div className="eyebrow">EMPLOYEE 360</div><h2>{page==='Employees'?'Add employee':`New ${page.toLowerCase()} record`}</h2></div><button type="button" className="icon-btn" onClick={onClose}>✕</button></div>{err&&<div className="alert">{err}</div>}<div className="form-grid">{fields.map(([k,label])=><label>{label}{['description','reason','goals','feedback','task_name'].includes(k)?<textarea value={x[k]||''} onChange={e=>set(k,e.target.value)}/>:<input required={['employee_code','first_name','last_name','email','job_title','name','leave_type','start_date','end_date','employee_id','pay_month','base_salary','review_period','rating','title'].includes(k)} type={k.includes('date')?'date':k==='email'?'email':k==='rating'||k.includes('salary')||k==='employee_id'||k==='department_id'||k==='manager_id'?'number':'text'} value={x[k]||''} onChange={e=>set(k,e.target.value)}/>}</label>)}</div><div className="modal-actions"><button type="button" className="secondary" onClick={onClose}>Cancel</button><button className="primary">Save record</button></div></form></div>
}
createRoot(document.getElementById('root')).render(<App/>);
