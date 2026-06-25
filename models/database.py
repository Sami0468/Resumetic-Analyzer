import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        resume_name TEXT,
        ats_score REAL,
        job_match REAL,
        skills_found TEXT,
        missing_skills TEXT,
        suggestions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

def save_analysis(user_id, resume_name, ats_score, job_match, skills_found, missing_skills, suggestions):
    import json
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO analyses (user_id, resume_name, ats_score, job_match, skills_found, missing_skills, suggestions)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (user_id, resume_name, ats_score, job_match,
               json.dumps(skills_found), json.dumps(missing_skills), json.dumps(suggestions)))
    conn.commit()
    aid = c.lastrowid
    conn.close()
    return aid

def get_user_analyses(user_id):
    import json
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM analyses WHERE user_id=? ORDER BY created_at DESC', (user_id,))
    rows = c.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        for k in ['skills_found', 'missing_skills', 'suggestions']:
            try:
                d[k] = json.loads(d[k]) if d[k] else []
            except:
                d[k] = []
        result.append(d)
    return result