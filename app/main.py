import os, re, uuid, enum
from pathlib import Path
from datetime import date, datetime, timedelta, timezone
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import create_engine, String, Boolean, DateTime, Date, Integer, Float, Text, ForeignKey, Enum, JSON, text, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session
class Settings(BaseSettings):
 model_config=SettingsConfigDict(env_file='.env',extra='ignore')
 database_url:str='sqlite:///./preppilot.db'
 jwt_secret:str='development-only-change-this-secret-to-at-least-32-characters'
 access_token_minutes:int=30
 frontend_origin:str='http://localhost:5173'
 max_upload_mb:int=5
 upload_dir:str='private_uploads'
settings=Settings()
connect_args={'check_same_thread':False} if settings.database_url.startswith('sqlite') else {}
engine=create_engine(settings.database_url,pool_pre_ping=True,connect_args=connect_args)
if settings.database_url.startswith('sqlite'):
 @event.listens_for(engine,'connect')
 def enable_sqlite_foreign_keys(dbapi_connection,connection_record):
  cursor=dbapi_connection.cursor(); cursor.execute('PRAGMA foreign_keys=ON'); cursor.close()
SessionLocal=sessionmaker(engine,autoflush=False,expire_on_commit=False)
class Base(DeclarativeBase): pass
def uid(): return str(uuid.uuid4())
class Role(str,enum.Enum): student='student'; admin='admin'
class User(Base):
 __tablename__='users'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); email:Mapped[str]=mapped_column(String(320),unique=True,index=True); password_hash:Mapped[str]=mapped_column(String(255)); role:Mapped[Role]=mapped_column(Enum(Role),default=Role.student); is_active:Mapped[bool]=mapped_column(Boolean,default=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Profile(Base):
 __tablename__='profiles'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),unique=True); full_name:Mapped[Optional[str]]=mapped_column(String(160)); college:Mapped[Optional[str]]=mapped_column(String(200)); graduation_year:Mapped[Optional[int]]=mapped_column(Integer); target_role:Mapped[Optional[str]]=mapped_column(String(120)); target_company:Mapped[Optional[str]]=mapped_column(String(120)); deadline:Mapped[Optional[date]]=mapped_column(Date); daily_minutes:Mapped[int]=mapped_column(Integer,default=60)
class Skill(Base):
 __tablename__='skills'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); name:Mapped[str]=mapped_column(String(120),unique=True); category:Mapped[str]=mapped_column(String(80),default='core'); base_minutes:Mapped[int]=mapped_column(Integer,default=180); active:Mapped[bool]=mapped_column(Boolean,default=True)
class Resource(Base):
 __tablename__='resources'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); title:Mapped[str]=mapped_column(String(240)); url:Mapped[str]=mapped_column(String(1000)); kind:Mapped[str]=mapped_column(String(40)); difficulty:Mapped[str]=mapped_column(String(40),default='beginner'); skill_id:Mapped[Optional[str]]=mapped_column(ForeignKey('skills.id',ondelete='SET NULL')); verified:Mapped[bool]=mapped_column(Boolean,default=False); active:Mapped[bool]=mapped_column(Boolean,default=True)
class Question(Base):
 __tablename__='questions'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); prompt:Mapped[str]=mapped_column(Text); options:Mapped[list]=mapped_column(JSON); answer_index:Mapped[int]=mapped_column(Integer); explanation:Mapped[str]=mapped_column(Text); skill_id:Mapped[Optional[str]]=mapped_column(ForeignKey('skills.id',ondelete='SET NULL')); difficulty:Mapped[str]=mapped_column(String(40),default='medium'); active:Mapped[bool]=mapped_column(Boolean,default=True)
class Attempt(Base):
 __tablename__='attempts'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); submitted_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow); score:Mapped[float]=mapped_column(Float); total:Mapped[int]=mapped_column(Integer); details:Mapped[list]=mapped_column(JSON)
class Roadmap(Base):
 __tablename__='roadmaps'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); version:Mapped[int]=mapped_column(Integer,default=1); target_role:Mapped[str]=mapped_column(String(120)); change_reason:Mapped[str]=mapped_column(String(300)); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow); tasks:Mapped[list['Task']]=relationship(back_populates='roadmap',cascade='all,delete-orphan')
class Task(Base):
 __tablename__='roadmap_tasks'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); roadmap_id:Mapped[str]=mapped_column(ForeignKey('roadmaps.id',ondelete='CASCADE'),index=True); skill_id:Mapped[Optional[str]]=mapped_column(ForeignKey('skills.id',ondelete='SET NULL')); title:Mapped[str]=mapped_column(String(240)); due_date:Mapped[Optional[date]]=mapped_column(Date); estimated_minutes:Mapped[int]=mapped_column(Integer); priority:Mapped[float]=mapped_column(Float); status:Mapped[str]=mapped_column(String(24),default='pending'); resource_url:Mapped[Optional[str]]=mapped_column(String(1000)); roadmap:Mapped[Roadmap]=relationship(back_populates='tasks')
class Resume(Base):
 __tablename__='resume_documents'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); filename:Mapped[str]=mapped_column(String(255)); storage_path:Mapped[str]=mapped_column(String(1000)); extracted_text:Mapped[Optional[str]]=mapped_column(Text); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Analysis(Base):
 __tablename__='analyses'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); resume_id:Mapped[Optional[str]]=mapped_column(ForeignKey('resume_documents.id',ondelete='SET NULL')); job_description:Mapped[str]=mapped_column(Text); result:Mapped[dict]=mapped_column(JSON); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Interview(Base):
 __tablename__='interview_sessions'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); user_id:Mapped[str]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); target_role:Mapped[str]=mapped_column(String(120)); status:Mapped[str]=mapped_column(String(24),default='active'); transcript:Mapped[list]=mapped_column(JSON,default=list); feedback:Mapped[Optional[dict]]=mapped_column(JSON); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
pwd=CryptContext(schemes=['bcrypt'],deprecated='auto'); oauth=OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token')
def get_db():
 db=SessionLocal()
 try: yield db
 finally: db.close()
def current_user(token:str=Depends(oauth),db:Session=Depends(get_db)):
 try: data=jwt.decode(token,settings.jwt_secret,algorithms=['HS256']); u=db.get(User,data['sub'])
 except (JWTError,KeyError): u=None
 if not u or not u.is_active: raise HTTPException(401,'Invalid or expired token')
 return u
def require_admin(u:User=Depends(current_user)):
 if u.role!=Role.admin: raise HTTPException(403,'Admin access required')
 return u
def make_token(u):
 now=datetime.now(timezone.utc); return jwt.encode({'sub':u.id,'role':u.role.value,'iat':now,'exp':now+timedelta(minutes=settings.access_token_minutes)},settings.jwt_secret,algorithm='HS256')
class Signup(BaseModel): email:EmailStr; password:str=Field(min_length=10,max_length=128)
class Login(BaseModel): email:EmailStr; password:str
class ProfileInput(BaseModel): full_name:Optional[str]=None; college:Optional[str]=None; graduation_year:Optional[int]=Field(default=None,ge=2000,le=2100); target_role:Optional[str]=None; target_company:Optional[str]=None; deadline:Optional[date]=None; daily_minutes:int=Field(default=60,ge=15,le=720)
class PlanInput(BaseModel): target_role:str=Field(min_length=2,max_length=120); deadline:date; daily_minutes:int=Field(ge=15,le=720); scores:dict[str,float]=Field(default_factory=dict)
class Answer(BaseModel): question_id:str; answer_index:int=Field(ge=0)
class AssessmentInput(BaseModel): answers:list[Answer]=Field(min_length=1,max_length=100)
class TaskInput(BaseModel): status:str=Field(pattern='^(pending|in_progress|completed)$')
class JDInput(BaseModel): job_description:str=Field(min_length=30,max_length=30000); resume_id:Optional[str]=None
class ResourceInput(BaseModel): title:str; url:str; kind:str; difficulty:str='beginner'; skill_id:Optional[str]=None; verified:bool=False; active:bool=True
class QuestionInput(BaseModel): prompt:str; options:list[str]=Field(min_length=2,max_length=8); answer_index:int=Field(ge=0); explanation:str; skill_id:Optional[str]=None; difficulty:str='medium'; active:bool=True
class InterviewInput(BaseModel): target_role:str=Field(min_length=2,max_length=120)
class InterviewReply(BaseModel): answer:str=Field(min_length=1,max_length=8000)
app=FastAPI(title='PrepPilot AI API',version='1.0.0',description='Placement preparation backend. See README for current implementation limits.')
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_origin],allow_credentials=True,allow_methods=['*'],allow_headers=['Authorization','Content-Type'])
@app.on_event('startup')
def startup(): Base.metadata.create_all(engine)  # Development convenience; deploy with Alembic.
@app.get('/health/live')
def live(): return {'status':'alive'}
@app.get('/health/ready')
def ready(db:Session=Depends(get_db)):
 try: db.execute(text('SELECT 1')); return {'status':'ready'}
 except Exception: raise HTTPException(503,'Database unavailable')
@app.post('/api/v1/auth/signup',status_code=201)
def signup(x:Signup,db:Session=Depends(get_db)):
 email=str(x.email).lower()
 if db.query(User).filter_by(email=email).first(): raise HTTPException(409,'Email already registered')
 u=User(email=email,password_hash=pwd.hash(x.password),role=Role.student); db.add(u); db.flush(); db.add(Profile(user_id=u.id)); db.commit(); return {'id':u.id,'email':u.email,'role':u.role.value}
@app.post('/api/v1/auth/login')
def login(x:Login,db:Session=Depends(get_db)):
 u=db.query(User).filter_by(email=str(x.email).lower()).first()
 if not u or not pwd.verify(x.password,u.password_hash): raise HTTPException(401,'Incorrect email or password')
 return {'access_token':make_token(u),'token_type':'bearer'}
@app.post('/api/v1/auth/token')
def login_form(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
 u=db.query(User).filter_by(email=form.username.strip().lower()).first()
 if not u or not pwd.verify(form.password,u.password_hash): raise HTTPException(401,'Incorrect email or password')
 return {'access_token':make_token(u),'token_type':'bearer'}
@app.get('/api/v1/auth/me')
def me(u:User=Depends(current_user)): return {'id':u.id,'email':u.email,'role':u.role.value}
@app.post('/api/v1/admin/bootstrap',status_code=201)
def bootstrap(x:Signup,secret:Optional[str]=None,db:Session=Depends(get_db)):
 expected=os.getenv('ADMIN_BOOTSTRAP_SECRET')
 if not expected or secret!=expected: raise HTTPException(403,'Valid bootstrap secret required')
 if db.query(User).filter_by(role=Role.admin).first(): raise HTTPException(409,'Admin already exists')
 u=User(email=str(x.email).lower(),password_hash=pwd.hash(x.password),role=Role.admin); db.add(u); db.commit(); return {'id':u.id,'email':u.email,'role':'admin'}
@app.get('/api/v1/profile')
def get_profile(db:Session=Depends(get_db),u:User=Depends(current_user)):
 p=db.query(Profile).filter_by(user_id=u.id).first()
 return {k:getattr(p,k) for k in ('id','user_id','full_name','college','graduation_year','target_role','target_company','deadline','daily_minutes')}
@app.put('/api/v1/profile')
def update_profile(x:ProfileInput,db:Session=Depends(get_db),u:User=Depends(current_user)):
 p=db.query(Profile).filter_by(user_id=u.id).first()
 for k,v in x.model_dump().items(): setattr(p,k,v)
 db.commit(); db.refresh(p); return {k:getattr(p,k) for k in ('id','user_id','full_name','college','graduation_year','target_role','target_company','deadline','daily_minutes')}
@app.get('/api/v1/catalogue/skills')
def skills(db:Session=Depends(get_db),u:User=Depends(current_user)): return db.query(Skill).filter_by(active=True).all()
@app.get('/api/v1/resources')
def resources(skill_id:Optional[str]=None,db:Session=Depends(get_db),u:User=Depends(current_user)):
 q=db.query(Resource).filter_by(active=True,verified=True)
 if skill_id: q=q.filter_by(skill_id=skill_id)
 return q.all()
@app.get('/api/v1/assessments/questions')
def questions(skill_id:Optional[str]=None,db:Session=Depends(get_db),u:User=Depends(current_user)):
 q=db.query(Question).filter_by(active=True)
 if skill_id: q=q.filter_by(skill_id=skill_id)
 return [{'id':z.id,'prompt':z.prompt,'options':z.options,'skill_id':z.skill_id,'difficulty':z.difficulty} for z in q.all()]
@app.post('/api/v1/assessments/submit')
def submit(x:AssessmentInput,db:Session=Depends(get_db),u:User=Depends(current_user)):
 ids=[a.question_id for a in x.answers]
 if len(set(ids))!=len(ids): raise HTTPException(422,'Duplicate question IDs')
 qs={q.id:q for q in db.query(Question).filter(Question.id.in_(ids),Question.active.is_(True)).all()}
 if len(qs)!=len(ids): raise HTTPException(404,'Question not found')
 details=[]; correct=0; topics={}
 for a in x.answers:
  q=qs[a.question_id]
  if a.answer_index>=len(q.options): raise HTTPException(422,'Answer index out of range')
  ok=a.answer_index==q.answer_index; correct+=ok; k=q.skill_id or 'general'; topics.setdefault(k,[0,0]); topics[k][0]+=ok; topics[k][1]+=1
  details.append({'question_id':q.id,'selected':a.answer_index,'correct':ok,'correct_index':q.answer_index,'explanation':q.explanation,'skill_id':q.skill_id})
 attempt=Attempt(user_id=u.id,score=round(correct*100/len(ids),2),total=len(ids),details=details); db.add(attempt); db.commit()
 latest=db.query(Roadmap).filter_by(user_id=u.id).order_by(Roadmap.created_at.desc()).first()
 if latest:
  profile=db.query(Profile).filter_by(user_id=u.id).first(); skill_scores={s.name:round(topics[s.id][0]*100/max(1,topics[s.id][1]),2) for s in db.query(Skill).all() if s.id in topics}
  deadline=(profile.deadline if profile and profile.deadline and profile.deadline>date.today() else max([t.due_date for t in latest.tasks if t.due_date and t.due_date>date.today()] or [date.today()+timedelta(days=30)]))
  revised=build_roadmap(db,u,latest.target_role,deadline,profile.daily_minutes if profile else 60,skill_scores); revised.version=latest.version+1; revised.change_reason=f'Updated after assessment {attempt.id}'; db.commit()
 return {'attempt_id':attempt.id,'score':attempt.score,'correct':correct,'total':len(ids),'topic_scores':{k:round(v[0]*100/v[1],2) for k,v in topics.items()},'roadmap_updated':bool(latest),'details':details}
@app.get('/api/v1/assessments/attempts')
def attempts(db:Session=Depends(get_db),u:User=Depends(current_user)): return db.query(Attempt).filter_by(user_id=u.id).order_by(Attempt.submitted_at.desc()).all()
def build_roadmap(db,u,role,deadline,daily,scores):
 budget=max(0,(deadline-date.today()).days*daily*78//100); spent=0; cursor=date.today(); plan=Roadmap(user_id=u.id,target_role=role,change_reason='Initial plan from supplied skill scores',version=1); db.add(plan); db.flush(); ranked=[]
 for s in db.query(Skill).filter_by(active=True).all():
  score=max(0,min(100,float(scores.get(s.name,50)))); relevance=.8 if any(x in role.lower() for x in ('software','developer','engineer')) else .5; priority=.5*(100-score)/100+.35*relevance+.15*.5; ranked.append((priority,s))
 for priority,s in sorted(ranked,key=lambda z:z[0],reverse=True):
  mins=min(s.base_minutes,max(30,daily*2))
  if spent+mins>budget: continue
  spent+=mins; cursor+=timedelta(days=max(1,(mins+daily-1)//daily)); res=db.query(Resource).filter_by(skill_id=s.id,active=True,verified=True).first(); db.add(Task(roadmap_id=plan.id,skill_id=s.id,title=f'Study and practice {s.name}',due_date=min(cursor,deadline),estimated_minutes=mins,priority=priority,resource_url=res.url if res else None))
 db.commit(); db.refresh(plan); return plan
@app.post('/api/v1/roadmaps',status_code=201)
def create_roadmap(x:PlanInput,db:Session=Depends(get_db),u:User=Depends(current_user)):
 if x.deadline<=date.today(): raise HTTPException(422,'Deadline must be in the future')
 return build_roadmap(db,u,x.target_role,x.deadline,x.daily_minutes,x.scores)
@app.get('/api/v1/roadmaps')
def roadmaps(db:Session=Depends(get_db),u:User=Depends(current_user)): return db.query(Roadmap).filter_by(user_id=u.id).order_by(Roadmap.created_at.desc()).all()
@app.get('/api/v1/roadmaps/{rid}')
def roadmap(rid:str,db:Session=Depends(get_db),u:User=Depends(current_user)):
 r=db.query(Roadmap).filter_by(id=rid,user_id=u.id).first()
 if not r: raise HTTPException(404,'Roadmap not found')
 return r
@app.patch('/api/v1/roadmaps/tasks/{tid}')
def task_update(tid:str,x:TaskInput,db:Session=Depends(get_db),u:User=Depends(current_user)):
 t=db.query(Task).join(Roadmap).filter(Task.id==tid,Roadmap.user_id==u.id).first()
 if not t: raise HTTPException(404,'Task not found')
 t.status=x.status; db.commit(); return t
@app.post('/api/v1/resumes',status_code=201)
async def upload_resume(file:UploadFile=File(...),db:Session=Depends(get_db),u:User=Depends(current_user)):
 ext=Path(file.filename or '').suffix.lower()
 if ext not in {'.pdf','.docx','.txt'}: raise HTTPException(415,'Use PDF, DOCX or TXT')
 data=await file.read(settings.max_upload_mb*1024*1024+1)
 if len(data)>settings.max_upload_mb*1024*1024: raise HTTPException(413,'File exceeds upload limit')
 folder=Path(settings.upload_dir)/u.id; folder.mkdir(parents=True,exist_ok=True); path=folder/(uid()+ext); path.write_bytes(data); extracted=None
 try:
  if ext=='.txt': extracted=data.decode('utf-8',errors='replace')[:50000]
  elif ext=='.docx':
   from docx import Document
   import io
   extracted='\n'.join(p.text for p in Document(io.BytesIO(data)).paragraphs)[:50000]
  else:
   import fitz
   extracted='\n'.join(p.get_text() for p in fitz.open(stream=data,filetype='pdf'))[:50000]
 except Exception: extracted=None
 d=Resume(user_id=u.id,filename=Path(file.filename or 'resume').name,storage_path=str(path),extracted_text=extracted); db.add(d); db.commit(); db.refresh(d); return {'id':d.id,'filename':d.filename,'text_extracted':bool(extracted),'created_at':d.created_at}
@app.get('/api/v1/resumes')
def resumes(db:Session=Depends(get_db),u:User=Depends(current_user)): return [{'id':d.id,'filename':d.filename,'created_at':d.created_at} for d in db.query(Resume).filter_by(user_id=u.id).all()]
@app.delete('/api/v1/resumes/{rid}',status_code=204)
def delete_resume(rid:str,db:Session=Depends(get_db),u:User=Depends(current_user)):
 d=db.query(Resume).filter_by(id=rid,user_id=u.id).first()
 if not d: raise HTTPException(404,'Resume not found')
 Path(d.storage_path).unlink(missing_ok=True); db.delete(d); db.commit()
@app.post('/api/v1/analysis')
def analyze(x:JDInput,db:Session=Depends(get_db),u:User=Depends(current_user)):
 resume=''
 if x.resume_id:
  d=db.query(Resume).filter_by(id=x.resume_id,user_id=u.id).first()
  if not d: raise HTTPException(404,'Resume not found')
  resume=d.extracted_text or ''
 rows=[]
 for s in db.query(Skill).filter_by(active=True).all():
  pat=r'(?<!\w)'+re.escape(s.name.lower())+r'(?!\w)'; req=bool(re.search(pat,x.job_description.lower())); matched=bool(re.search(pat,resume.lower())); rows.append({'skill':s.name,'required':req,'match':matched,'gap':req and not matched})
 required=[r for r in rows if r['required']]; result={'skills':rows,'match_percent':round(sum(r['match'] for r in required)*100/len(required)) if required else None,'caveat':'Dictionary matching is a basic signal, not semantic AI.'}; a=Analysis(user_id=u.id,resume_id=x.resume_id,job_description=x.job_description,result=result); db.add(a); db.commit(); result['analysis_id']=a.id; return result
@app.post('/api/v1/interviews',status_code=201)
def start_interview(x:InterviewInput,db:Session=Depends(get_db),u:User=Depends(current_user)):
 s=Interview(user_id=u.id,target_role=x.target_role,transcript=[{'speaker':'assistant','text':f'Tell me about a project that shows your skills for a {x.target_role} role.'}]); db.add(s); db.commit(); db.refresh(s); return s
@app.post('/api/v1/interviews/{sid}/answers')
def answer_interview(sid:str,x:InterviewReply,db:Session=Depends(get_db),u:User=Depends(current_user)):
 s=db.query(Interview).filter_by(id=sid,user_id=u.id).first()
 if not s: raise HTTPException(404,'Interview not found')
 if s.status!='active': raise HTTPException(409,'Interview is closed')
 tr=list(s.transcript or []); tr.extend([{'speaker':'student','text':x.answer},{'speaker':'assistant','text':'What was the technical challenge and how did you measure the result?'}]); s.transcript=tr; db.commit(); return s
@app.post('/api/v1/interviews/{sid}/complete')
def complete_interview(sid:str,db:Session=Depends(get_db),u:User=Depends(current_user)):
 s=db.query(Interview).filter_by(id=sid,user_id=u.id).first()
 if not s: raise HTTPException(404,'Interview not found')
 s.status='completed'; s.feedback={'answer_count':sum(m['speaker']=='student' for m in s.transcript),'coaching':'Explain context, your actions, technical choices and measurable results. This is a checklist, not an AI evaluation.'}; db.commit(); return s
@app.get('/api/v1/dashboard')
def dashboard(db:Session=Depends(get_db),u:User=Depends(current_user)):
 attempts=db.query(Attempt).filter_by(user_id=u.id).order_by(Attempt.submitted_at.desc()).all(); r=db.query(Roadmap).filter_by(user_id=u.id).order_by(Roadmap.created_at.desc()).first(); total=len(r.tasks) if r else 0; done=sum(t.status=='completed' for t in r.tasks) if r else 0; sessions=db.query(StudySession).filter_by(user_id=u.id).all()
 return {'attempt_count':len(attempts),'latest_score':attempts[0].score if attempts else None,'score_trend':[{'date':a.submitted_at.date().isoformat(),'score':a.score} for a in reversed(attempts[:10])],'roadmap_id':r.id if r else None,'roadmap_version':r.version if r else None,'roadmap_completion_percent':round(done*100/total) if total else 0,'study_minutes_total':sum(x.actual_minutes for x in sessions),'study_sessions_count':len(sessions),'next_action':next((t.title for t in r.tasks if t.status!='completed'),'Create a roadmap') if r else 'Complete a diagnostic assessment'}
@app.post('/api/v1/admin/skills',status_code=201)
def add_skill(x:dict,db:Session=Depends(get_db),u:User=Depends(require_admin)):
 s=Skill(name=x['name'],category=x.get('category','core'),base_minutes=x.get('base_minutes',180)); db.add(s); db.commit(); db.refresh(s); return s
@app.post('/api/v1/admin/resources',status_code=201)
def add_resource(x:ResourceInput,db:Session=Depends(get_db),u:User=Depends(require_admin)):
 r=Resource(**x.model_dump()); db.add(r); db.commit(); db.refresh(r); return r
@app.post('/api/v1/admin/questions',status_code=201)
def add_question(x:QuestionInput,db:Session=Depends(get_db),u:User=Depends(require_admin)):
 if x.answer_index>=len(x.options): raise HTTPException(422,'answer_index must select an option')
 q=Question(**x.model_dump()); db.add(q); db.commit(); db.refresh(q); return q
@app.get('/api/v1/admin/content')
def admin_content(db:Session=Depends(get_db),u:User=Depends(require_admin)): return {'skills':db.query(Skill).count(),'resources':db.query(Resource).count(),'questions':db.query(Question).count()}


# Persistent study tracking and AI guidance snapshots
class StudySession(Base):
 __tablename__='study_sessions'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 user_id:Mapped[str]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True)
 task_id:Mapped[Optional[str]]=mapped_column(ForeignKey('roadmap_tasks.id',ondelete='SET NULL'),index=True)
 planned_minutes:Mapped[int]=mapped_column(Integer,default=0)
 actual_minutes:Mapped[int]=mapped_column(Integer)
 reflection:Mapped[Optional[str]]=mapped_column(Text)
 created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class StudyGuidance(Base):
 __tablename__='study_guidance'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 user_id:Mapped[str]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True)
 roadmap_id:Mapped[str]=mapped_column(ForeignKey('roadmaps.id',ondelete='CASCADE'),index=True)
 payload:Mapped[dict]=mapped_column(JSON)
 created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class StudySessionInput(BaseModel):
 task_id:Optional[str]=None
 planned_minutes:int=Field(default=0,ge=0,le=720)
 actual_minutes:int=Field(ge=1,le=720)
 reflection:Optional[str]=Field(default=None,max_length=2000)
class GuideOut(BaseModel):
 focus:list[str]
 practice_steps:list[str]
 timebox_minutes:int=Field(ge=5,le=720)
 reason:str
 resource_ids:list[str]
 source:str
@app.post('/api/v1/study-sessions',status_code=201)
def log_study(x:StudySessionInput,db:Session=Depends(get_db),u:User=Depends(current_user)):
 task=None
 if x.task_id:
  task=db.query(Task).join(Roadmap).filter(Task.id==x.task_id,Roadmap.user_id==u.id).first()
  if not task: raise HTTPException(404,'Roadmap task not found')
  if task.status=='pending': task.status='in_progress'
 row=StudySession(user_id=u.id,task_id=x.task_id,planned_minutes=x.planned_minutes,actual_minutes=x.actual_minutes,reflection=x.reflection); db.add(row); db.commit(); db.refresh(row); return row
@app.get('/api/v1/study-sessions')
def study_history(limit:int=50,db:Session=Depends(get_db),u:User=Depends(current_user)):
 limit=max(1,min(limit,100)); return db.query(StudySession).filter_by(user_id=u.id).order_by(StudySession.created_at.desc()).limit(limit).all()
@app.get('/api/v1/roadmaps/{rid}/study-guide')
async def study_guide(rid:str,db:Session=Depends(get_db),u:User=Depends(current_user)):
 plan=db.query(Roadmap).filter_by(id=rid,user_id=u.id).first()
 if not plan: raise HTTPException(404,'Roadmap not found')
 pending=[{'id':t.id,'title':t.title,'minutes':t.estimated_minutes,'priority':t.priority,'status':t.status,'resource_url':t.resource_url} for t in plan.tasks if t.status!='completed']
 candidates=[{'id':r.id,'title':r.title,'url':r.url,'kind':r.kind} for r in db.query(Resource).filter_by(active=True,verified=True).all()]
 data=await __import__('app.ai',fromlist=['json_completion']).json_completion('You are a study coach. Use only provided tasks and resource IDs. Do not change deadlines, scores, or facts. Return focus (short list), practice_steps (short list), timebox_minutes (integer), reason (one short sentence), resource_ids (only IDs from provided catalogue).',{'role':plan.target_role,'pending_tasks':pending[:12],'verified_catalogue':candidates[:30]},500)
 valid_ids={r['id'] for r in candidates};
 if data:
  try:
   guide=GuideOut.model_validate({'focus':data.get('focus',[]),'practice_steps':data.get('practice_steps',[]),'timebox_minutes':data.get('timebox_minutes',45),'reason':data.get('reason','Based on pending roadmap tasks.'),'resource_ids':[x for x in data.get('resource_ids',[]) if x in valid_ids],'source':'openrouter'})
  except Exception: data=None
 if not data:
  first=pending[0] if pending else None; chosen=[r for r in candidates if first and r['url']==first['resource_url']]
  guide=GuideOut(focus=[first['title']] if first else ['Review recent assessment results'],practice_steps=['Study the linked verified resource','Write a short summary from memory','Complete practice questions for this topic'],timebox_minutes=min(60,first['minutes']) if first else 30,reason='Generated from your next incomplete roadmap task; no AI provider response was available.',resource_ids=[r['id'] for r in chosen],source='deterministic')
 snapshot=StudyGuidance(user_id=u.id,roadmap_id=plan.id,payload=guide.model_dump()); db.add(snapshot); db.commit(); return {**guide.model_dump(),'guidance_id':snapshot.id,'created_at':snapshot.created_at}
@app.get('/api/v1/resources/recommendations')
async def recommend_resources(roadmap_id:Optional[str]=None,db:Session=Depends(get_db),u:User=Depends(current_user)):
 q=db.query(Roadmap).filter_by(user_id=u.id)
 if roadmap_id: q=q.filter_by(id=roadmap_id)
 plan=q.order_by(Roadmap.created_at.desc()).first()
 if roadmap_id and not plan: raise HTTPException(404,'Roadmap not found')
 tasks=sorted([t for t in (plan.tasks if plan else []) if t.status!='completed'],key=lambda t:t.priority,reverse=True)
 candidates=[]
 for task in tasks[:12]:
  skill=db.get(Skill,task.skill_id) if task.skill_id else None
  for r in db.query(Resource).filter_by(skill_id=task.skill_id,active=True,verified=True).all(): candidates.append({'id':r.id,'title':r.title,'url':r.url,'kind':r.kind,'skill':skill.name if skill else task.title,'task_id':task.id,'priority':task.priority})
 candidates=candidates[:30]; chosen_ids=[r['id'] for r in candidates]; explanations={}
 if candidates:
  data=await __import__('app.ai',fromlist=['json_completion']).json_completion('Choose useful resources for the next incomplete tasks. Return picks as objects with resource_id and reason. Use only provided IDs. Do not invent URLs.',{'target_role':plan.target_role if plan else None,'resources':candidates},400)
  if data:
   for item in data.get('picks',[]):
    if isinstance(item,dict) and item.get('resource_id') in chosen_ids and isinstance(item.get('reason'),str): explanations[item['resource_id']]=item['reason'][:240]
 return {'roadmap_id':plan.id if plan else None,'items':[{'id':c['id'],'title':c['title'],'url':c['url'],'kind':c['kind'],'skill':c['skill'],'task_id':c['task_id'],'priority':c['priority'],'reason':explanations.get(c['id'],'Verified catalogue resource linked to an incomplete priority task.')} for c in candidates]}
@app.post('/api/v1/interviews/{sid}/ai-answer')
async def ai_interview_answer(sid:str,x:InterviewReply,db:Session=Depends(get_db),u:User=Depends(current_user)):
 s=db.query(Interview).filter_by(id=sid,user_id=u.id).first()
 if not s: raise HTTPException(404,'Interview not found')
 if s.status!='active': raise HTTPException(409,'Interview is closed')
 history=list(s.transcript or [])[-12:]
 data=await __import__('app.ai',fromlist=['json_completion']).json_completion('Act as a supportive technical interviewer. Evaluate the candidate answer for correctness, clarity, completeness, and concrete examples. Scores must be integers 1-5. Give one short improvement and one role-relevant follow-up question. Do not claim objective hiring readiness. Return keys: scores (object with correctness, clarity, completeness, examples), improvement (string), next_question (string).',{'target_role':s.target_role,'recent_transcript':history,'candidate_answer':x.answer},500)
 if data:
  try:
   scores={k:max(1,min(5,int(data['scores'][k]))) for k in ('correctness','clarity','completeness','examples')}; improvement=str(data['improvement'])[:500]; next_q=str(data['next_question'])[:700]
  except Exception: data=None
 if not data:
  scores={'correctness':3,'clarity':3,'completeness':3,'examples':2}; improvement='Add a concrete example, explain your own contribution, and include the result.'; next_q='What trade-off did you consider, and what would you change if you repeated the project?'
 tr=list(s.transcript or []); tr.extend([{'speaker':'student','text':x.answer,'evaluation':{'scores':scores,'improvement':improvement}},{'speaker':'assistant','text':next_q}]); s.transcript=tr; db.commit(); return {'session_id':s.id,'scores':scores,'improvement':improvement,'next_question':next_q,'source':'openrouter' if data else 'deterministic','session':s}
@app.get('/api/v1/ai/status')
def ai_status(u:User=Depends(current_user)):
 from app.ai import config
 return {'enabled':bool(config.openrouter_api_key),'provider':'openrouter' if config.openrouter_api_key else None,'model':config.openrouter_model if config.openrouter_api_key else None}




