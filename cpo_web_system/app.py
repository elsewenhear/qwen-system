from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'cpo-secret-key-change-in-production'

# Кастомные фильтры для работы с JSON в шаблонах
@app.template_filter('fromjson')
def fromjson_filter(value):
    try:
        return json.loads(value) if value else []
    except:
        return []

@app.template_filter('tojson')
def tojson_filter(value, indent=None):
    try:
        if indent is not None:
            return json.dumps(value, indent=indent, ensure_ascii=False)
        return json.dumps(value, ensure_ascii=False)
    except:
        return '{}'

DB_PATH = os.path.join(os.path.dirname(__file__), 'cpo_projects.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Инициализация БД если не существует"""
    if not os.path.exists(DB_PATH):
        conn = get_db()
        cursor = conn.cursor()
        
        # Таблица проектов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                description TEXT,
                owner TEXT,
                priority TEXT DEFAULT 'Medium',
                current_status TEXT DEFAULT 'Инициация',
                start_date TEXT,
                end_date TEXT,
                meta_attributes TEXT DEFAULT '{}',
                tags TEXT DEFAULT '[]',
                is_archived INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица истории статусов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                status_name TEXT NOT NULL,
                changed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                changed_by TEXT DEFAULT 'System',
                comment TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')
        
        # Таблица артефактов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                content_url TEXT,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')
        
        conn.commit()
        conn.close()

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    
    # Фильтры из query params
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    search = request.args.get('search', '')
    
    query = "SELECT * FROM projects WHERE is_archived = 0"
    params = []
    
    if status_filter:
        query += " AND current_status = ?"
        params.append(status_filter)
    
    if priority_filter:
        query += " AND priority = ?"
        params.append(priority_filter)
    
    if search:
        query += " AND (name LIKE ? OR code LIKE ? OR description LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])
    
    query += " ORDER BY updated_at DESC"
    
    cursor.execute(query, params)
    projects = cursor.fetchall()
    
    # Получаем уникальные статусы для фильтра
    cursor.execute("SELECT DISTINCT current_status FROM projects WHERE is_archived = 0")
    statuses = [row['current_status'] for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('index.html', 
                         projects=projects, 
                         statuses=statuses,
                         current_status=status_filter,
                         current_priority=priority_filter,
                         search_query=search)

@app.route('/project/<int:project_id>')
def view_project(project_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()
    
    if not project:
        conn.close()
        flash('Проект не найден', 'error')
        return redirect(url_for('index'))
    
    # История статусов
    cursor.execute("""
        SELECT * FROM status_history 
        WHERE project_id = ? 
        ORDER BY changed_at DESC
    """, (project_id,))
    status_history = cursor.fetchall()
    
    # Артефакты
    cursor.execute("""
        SELECT * FROM artifacts 
        WHERE project_id = ? 
        ORDER BY created_at DESC
    """, (project_id,))
    artifacts = cursor.fetchall()
    
    conn.close()
    
    return render_template('project_detail.html', 
                         project=project, 
                         status_history=status_history,
                         artifacts=artifacts)

@app.route('/project/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        description = request.form.get('description', '')
        owner = request.form.get('owner', '')
        priority = request.form.get('priority', 'Medium')
        status = request.form.get('status', 'Инициация')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        tags = request.form.get('tags', '')
        meta_json = request.form.get('meta_attributes', '{}')
        
        try:
            meta_dict = json.loads(meta_json) if meta_json else {}
        except:
            meta_dict = {}
        
        tags_list = [t.strip() for t in tags.split(',') if t.strip()]
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO projects (name, code, description, owner, priority, 
                                    current_status, start_date, end_date, 
                                    meta_attributes, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, code, description, owner, priority, status, 
                  start_date, end_date, json.dumps(meta_dict), json.dumps(tags_list)))
            
            project_id = cursor.lastrowid
            
            # Запись в историю статусов
            cursor.execute("""
                INSERT INTO status_history (project_id, status_name, changed_by, comment)
                VALUES (?, ?, ?, ?)
            """, (project_id, status, 'System', 'Проект создан'))
            
            conn.commit()
            flash(f'Проект {code} успешно создан', 'success')
        except sqlite3.IntegrityError:
            flash(f'Проект с кодом {code} уже существует', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('index'))
    
    return render_template('add_project.html')

@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        owner = request.form.get('owner', '')
        priority = request.form.get('priority', 'Medium')
        end_date = request.form.get('end_date', '')
        tags = request.form.get('tags', '')
        meta_json = request.form.get('meta_attributes', '{}')
        
        try:
            meta_dict = json.loads(meta_json) if meta_json else {}
        except:
            meta_dict = {}
        
        tags_list = [t.strip() for t in tags.split(',') if t.strip()]
        
        cursor.execute("""
            UPDATE projects 
            SET name=?, description=?, owner=?, priority=?, end_date=?,
                meta_attributes=?, tags=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (name, description, owner, priority, end_date, 
              json.dumps(meta_dict), json.dumps(tags_list), project_id))
        
        conn.commit()
        conn.close()
        
        flash('Проект обновлен', 'success')
        return redirect(url_for('view_project', project_id=project_id))
    
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()
    conn.close()
    
    if not project:
        flash('Проект не найден', 'error')
        return redirect(url_for('index'))
    
    return render_template('edit_project.html', project=project)

@app.route('/project/<int:project_id>/status', methods=['POST'])
def change_status(project_id):
    new_status = request.form.get('status')
    comment = request.form.get('comment', '')
    changed_by = request.form.get('changed_by', 'User')
    
    if not new_status:
        flash('Статус не указан', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Обновляем текущий статус
    cursor.execute("""
        UPDATE projects 
        SET current_status=?, updated_at=CURRENT_TIMESTAMP 
        WHERE id=?
    """, (new_status, project_id))
    
    # Добавляем запись в историю
    cursor.execute("""
        INSERT INTO status_history (project_id, status_name, changed_by, comment)
        VALUES (?, ?, ?, ?)
    """, (project_id, new_status, changed_by, comment))
    
    conn.commit()
    conn.close()
    
    flash(f'Статус изменен на {new_status}', 'success')
    return redirect(url_for('view_project', project_id=project_id))

@app.route('/project/<int:project_id>/artifact/add', methods=['POST'])
def add_artifact(project_id):
    artifact_type = request.form.get('type')
    title = request.form.get('title')
    content_url = request.form.get('content_url', '')
    description = request.form.get('description', '')
    
    if not artifact_type or not title:
        flash('Тип и название обязательны', 'error')
        return redirect(url_for('view_project', project_id=project_id))
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO artifacts (project_id, type, title, content_url, description)
        VALUES (?, ?, ?, ?, ?)
    """, (project_id, artifact_type, title, content_url, description))
    
    conn.commit()
    conn.close()
    
    flash('Артефакт добавлен', 'success')
    return redirect(url_for('view_project', project_id=project_id))

@app.route('/project/<int:project_id>/archive', methods=['POST'])
def archive_project(project_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE projects 
        SET is_archived=1, updated_at=CURRENT_TIMESTAMP 
        WHERE id=?
    """, (project_id,))
    
    conn.commit()
    conn.close()
    
    flash('Проект архивирован', 'success')
    return redirect(url_for('index'))

@app.route('/api/stats')
def api_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    # Всего проектов
    cursor.execute("SELECT COUNT(*) as count FROM projects WHERE is_archived = 0")
    total = cursor.fetchone()['count']
    
    # По статусам
    cursor.execute("""
        SELECT current_status, COUNT(*) as count 
        FROM projects 
        WHERE is_archived = 0 
        GROUP BY current_status
    """)
    by_status = {row['current_status']: row['count'] for row in cursor.fetchall()}
    
    # По приоритетам
    cursor.execute("""
        SELECT priority, COUNT(*) as count 
        FROM projects 
        WHERE is_archived = 0 
        GROUP BY priority
    """)
    by_priority = {row['priority']: row['count'] for row in cursor.fetchall()}
    
    conn.close()
    
    return jsonify({
        'total': total,
        'by_status': by_status,
        'by_priority': by_priority
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
