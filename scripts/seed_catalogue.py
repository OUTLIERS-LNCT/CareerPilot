"""Idempotently load the starter skills, questions and resource catalogue.
Run: python -m scripts.seed_catalogue
"""
from app.main import SessionLocal, Skill, Resource, Question
SKILLS=[('Data Structures and Algorithms','DSA',240),('SQL','Databases',180),('DBMS','Databases',180),('Object-Oriented Programming','Programming',150),('Operating Systems','Core CS',180),('Computer Networks','Core CS',180),('JavaScript','Web Development',180),('Python','Programming',180)]
# Curated sources chosen from official documentation or established interactive lessons.
RESOURCES=[
('SQLBolt interactive SQL lessons','https://sqlbolt.com/','SQL','interactive','beginner'),
('PostgreSQL official tutorial','https://www.postgresql.org/docs/current/tutorial.html','SQL','documentation','beginner'),
('Python classes tutorial','https://docs.python.org/3/tutorial/classes.html','Python','documentation','beginner'),
('MDN JavaScript Guide','https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide','JavaScript','documentation','beginner'),
('Operating Systems Three Easy Pieces','https://pages.cs.wisc.edu/~remzi/OSTEP/','Operating Systems','book','intermediate'),
('MDN HTTP overview','https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview','Computer Networks','documentation','beginner'),
('LeetCode Explore learning cards','https://support.leetcode.com/hc/en-us/articles/360013578114-How-to-use-Explore','Data Structures and Algorithms','practice','beginner')]
QUESTIONS=[
('What is the time complexity of binary search on a sorted array?',['O(1)','O(log n)','O(n)','O(n log n)'],1,'Each step halves the remaining search interval.','Data Structures and Algorithms','easy'),
('Which SQL clause filters grouped aggregate results?',['WHERE','ORDER BY','HAVING','LIMIT'],2,'HAVING filters groups after aggregation.','SQL','easy'),
('Which OOP concept hides internal state behind a public interface?',['Encapsulation','Compilation','Iteration','Normalization'],0,'Encapsulation bundles state and behavior and controls access through an interface.','Object-Oriented Programming','easy'),
('Which data structure follows FIFO order?',['Stack','Queue','Heap','Tree'],1,'A queue removes items in the order they were added.','Data Structures and Algorithms','easy'),
('What does a database index primarily improve?',['Read lookup speed','Password hashing','Network encryption','Transaction isolation'],0,'An index can speed up lookups, with storage and write costs.','DBMS','medium')]
def seed():
    db=SessionLocal()
    try:
        by_name={s.name:s for s in db.query(Skill).all()}
        for name,category,minutes in SKILLS:
            if name not in by_name: by_name[name]=Skill(name=name,category=category,base_minutes=minutes); db.add(by_name[name])
        db.flush()
        existing={r.title for r in db.query(Resource).all()}
        for title,url,skill,kind,difficulty in RESOURCES:
            if title not in existing: db.add(Resource(title=title,url=url,kind=kind,difficulty=difficulty,skill_id=by_name[skill].id,verified=True,active=True))
        existing_prompts={q.prompt for q in db.query(Question).all()}
        for prompt,options,answer,explanation,skill,difficulty in QUESTIONS:
            if prompt not in existing_prompts: db.add(Question(prompt=prompt,options=options,answer_index=answer,explanation=explanation,skill_id=by_name[skill].id,difficulty=difficulty,active=True))
        db.commit(); print(f'Catalogue ready: {len(SKILLS)} skills, {len(RESOURCES)} resources, {len(QUESTIONS)} starter questions (existing entries preserved).')
    except Exception: db.rollback(); raise
    finally: db.close()
if __name__=='__main__': seed()
