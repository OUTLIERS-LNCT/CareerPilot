from datetime import date, timedelta
from app.main import build_roadmap

class Skill:
    def __init__(self, name, minutes=180): self.name=name; self.base_minutes=minutes; self.id=name
class Query:
    def filter_by(self, **kw): return self
    def all(self): return [Skill('SQL'), Skill('DSA')]
    def first(self): return None
class DB:
    def __init__(self): self.rows=[]
    def query(self, model): return Query()
    def add(self, value): self.rows.append(value)
    def flush(self): pass
    def commit(self): pass
    def refresh(self, value): pass

def test_roadmap_budget_and_version_metadata():
    db=DB(); plan=build_roadmap(db, type('U',(),{'id':'u'})(), 'Software Engineer', date.today()+timedelta(days=20), 60, {'SQL':10,'DSA':20})
    tasks=[x for x in db.rows if x.__class__.__name__=='Task']
    assert sum(t.estimated_minutes for t in tasks) <= 20*60*.78
    assert plan.version == 1 and plan.change_reason
