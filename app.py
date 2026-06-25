import os
import json
import uuid
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models.database import init_db, get_db, save_analysis, get_user_analyses
from utils.parser import parse_resume, extract_name, extract_email
from utils.skill_extractor import extract_skills
from utils.ats_calculator import calculate_ats_score
from utils.report_generator import generate_report

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ai-resume-analyzer-secret-2024')

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.before_request
def setup():
    init_db()

# ─── Page Routes ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    user = None
    if 'user_id' in session:
        user = {'name': session.get('user_name'), 'email': session.get('user_email')}
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if not name or not email or not password:
            flash('All fields are required', 'error')
            return render_template('register.html')
        hashed = generate_password_hash(password)
        try:
            conn = get_db()
            conn.execute('INSERT INTO users (name, email, password) VALUES (?,?,?)', (name, email, hashed))
            conn.commit()
            conn.close()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Email already registered', 'error')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    analyses = get_user_analyses(session['user_id'])
    user = {'name': session.get('user_name'), 'email': session.get('user_email')}
    return render_template('dashboard.html', analyses=analyses, user=user)

# ─── API Routes ──────────────────────────────────────────────────────────────

@app.route('/api/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF and DOCX files are allowed'}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(filepath)

    text = parse_resume(filepath)
    if not text or len(text) < 20:
        os.remove(filepath)
        return jsonify({'error': 'Could not extract text from file'}), 400

    session['resume_text'] = text
    session['resume_name'] = filename
    session['resume_path'] = filepath
    session['candidate_name'] = extract_name(text)

    return jsonify({
        'success': True,
        'filename': filename,
        'text_preview': text[:500],
        'word_count': len(text.split()),
        'candidate_name': session['candidate_name']
    })

@app.route('/api/extract-skills', methods=['POST'])
def api_extract_skills():
    data = request.get_json()
    text = data.get('text') or session.get('resume_text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    result = extract_skills(text)
    return jsonify({
        'skills': result['all'],
        'technical': result['technical'],
        'soft': result['soft']
    })

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json()
    resume_text = data.get('resume_text') or session.get('resume_text', '')
    jd_text = data.get('job_description', '')

    if not resume_text:
        return jsonify({'error': 'No resume text. Please upload your resume first.'}), 400

    result = calculate_ats_score(resume_text, jd_text)

    # Save to DB if logged in
    if 'user_id' in session:
        try:
            save_analysis(
                session['user_id'],
                session.get('resume_name', 'unknown'),
                result['ats_score'],
                result['job_match'],
                result['skills_found'],
                result['missing_skills'],
                result['suggestions']
            )
        except:
            pass

    session['last_analysis'] = json.dumps(result)
    return jsonify(result)

@app.route('/api/download-report')
def download_report():
    analysis_json = session.get('last_analysis')
    if not analysis_json:
        return jsonify({'error': 'No analysis found. Please analyze a resume first.'}), 400

    try:
        analysis_data = json.loads(analysis_json)
        candidate_name = session.get('candidate_name', 'Candidate')
        resume_name = session.get('resume_name', 'resume')
        filepath, filename = generate_report(analysis_data, candidate_name, resume_name)
        return send_file(filepath, as_attachment=True, download_name=filename, mimetype='application/pdf')
    except Exception as e:
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

@app.route('/api/history')
@login_required
def api_history():
    analyses = get_user_analyses(session['user_id'])
    return jsonify(analyses)

# if __name__ == '__main__':
#     init_db()
#     app.run(debug=True, port=5000)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)