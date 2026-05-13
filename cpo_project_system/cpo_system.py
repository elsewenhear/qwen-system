#!/usr/bin/env python3
"""
CPO Project Management System - CLI Interface
Управление проектами через командную строку
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = "cpo_projects.db"

def get_connection():
    """Подключение к базе данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Инициализация базы данных (создание таблиц)"""
    conn = get_connection()
    with open('schema.sql', 'r', encoding='utf-8') as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("✓ База данных инициализирована")

def seed_data():
    """Наполнение тестовыми данными"""
    conn = get_connection()
    with open('seed_data.sql', 'r', encoding='utf-8') as f:
        seed = f.read()
    conn.executescript(seed)
    conn.commit()
    conn.close()
    print("✓ Тестовые данные загружены")

def list_projects(status_filter: Optional[str] = None):
    """Список всех проектов с фильтрацией по статусу"""
    conn = get_connection()
    query = """
        SELECT id, code, name, current_status, priority, start_date, 
               meta_attributes, tags, is_archived, created_at, updated_at
        FROM projects
        WHERE is_archived = 0
    """
    params = []
    if status_filter:
        query += " AND current_status = ?"
        params.append(status_filter)
    query += " ORDER BY priority DESC, created_at DESC"
    
    cursor = conn.execute(query, params)
    projects = cursor.fetchall()
    conn.close()
    
    if not projects:
        print("Нет проектов для отображения")
        return
    
    print(f"\n{'ID':<4} {'Code':<12} {'Название':<45} {'Статус':<15} {'Приоритет':<10}")
    print("=" * 90)
    for p in projects:
        meta = json.loads(p['meta_attributes']) if p['meta_attributes'] else {}
        team_size = meta.get('team_size', '-')
        print(f"{p['id']:<4} {p['code']:<12} {p['name']:<45} {p['current_status']:<15} {p['priority']:<10}")

def show_project_details(project_id: int):
    """Подробная информация о проекте"""
    conn = get_connection()
    
    # Основная информация
    cursor = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()
    if not project:
        print(f"Проект с ID {project_id} не найден")
        conn.close()
        return
    
    print("\n" + "=" * 80)
    print(f"ПРОЕКТ: {project['name']} ({project['code']})")
    print("=" * 80)
    print(f"Статус: {project['current_status']}")
    print(f"Приоритет: {project['priority']}")
    print(f"Владелец: {project['owner']}")
    print(f"Описание: {project['description']}")
    print(f"Дата начала: {project['start_date']}")
    print(f"Дата окончания: {project['end_date'] or 'Не указана'}")
    print(f"Теги: {project['tags']}")
    
    if project['meta_attributes']:
        meta = json.loads(project['meta_attributes'])
        print("\nДинамические атрибуты:")
        for key, value in meta.items():
            print(f"  • {key}: {value}")
    
    # История статусов
    print("\n📊 ИСТОРИЯ СТАТУСОВ:")
    print("-" * 60)
    cursor = conn.execute("""
        SELECT old_status, new_status, changed_by, change_reason, changed_at
        FROM status_history
        WHERE project_id = ?
        ORDER BY changed_at DESC
    """, (project_id,))
    history = cursor.fetchall()
    for h in history:
        old = h['old_status'] or 'Начало'
        print(f"  [{h['changed_at']}] {old} → {h['new_status']} | Автор: {h['changed_by']}")
        if h['change_reason']:
            print(f"    Причина: {h['change_reason']}")
    
    # Артефакты
    print("\n📎 АРТЕФАКТЫ:")
    print("-" * 60)
    cursor = conn.execute("""
        SELECT artifact_type, title, content_url, description, metadata, created_at
        FROM artifacts
        WHERE project_id = ?
        ORDER BY created_at DESC
    """, (project_id,))
    artifacts = cursor.fetchall()
    
    type_icons = {
        'Link': '🔗', 'File': '📄', 'Note': '📝', 
        'Decision': '✅', 'Risk': '⚠️', 'Metric': '📈'
    }
    
    for a in artifacts:
        icon = type_icons.get(a['artifact_type'], '•')
        print(f"  {icon} [{a['artifact_type']}] {a['title']}")
        if a['description']:
            print(f"      {a['description']}")
        if a['content_url']:
            print(f"      Ссылка: {a['content_url']}")
        if a['metadata']:
            meta = json.loads(a['metadata'])
            for k, v in meta.items():
                print(f"      {k}: {v}")
    
    conn.close()

def add_project(code: str, name: str, description: str, priority: str = 'Medium', 
                status: str = 'Инициация', start_date: str = None, **meta_attrs):
    """Добавление нового проекта"""
    conn = get_connection()
    if not start_date:
        start_date = datetime.now().strftime('%Y-%m-%d')
    
    meta_json = json.dumps(meta_attrs) if meta_attrs else None
    
    try:
        cursor = conn.execute("""
            INSERT INTO projects (code, name, description, priority, current_status, start_date, meta_attributes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (code, name, description, priority, status, start_date, meta_json))
        conn.commit()
        project_id = cursor.lastrowid
        print(f"✓ Проект создан с ID: {project_id}")
    except sqlite3.IntegrityError as e:
        print(f"✗ Ошибка: {e}")
    finally:
        conn.close()

def update_status(project_id: int, new_status: str, reason: str = '', changed_by: str = 'CPO'):
    """Изменение статуса проекта"""
    conn = get_connection()
    
    # Проверка существования проекта
    cursor = conn.execute("SELECT current_status FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()
    if not project:
        print(f"Проект с ID {project_id} не найден")
        conn.close()
        return
    
    old_status = project['current_status']
    
    # Обновление статуса (триггер автоматически запишет историю)
    conn.execute("""
        UPDATE projects 
        SET current_status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_status, project_id))
    
    # Дополнительная запись причины в историю (если нужно переопределить)
    if reason:
        conn.execute("""
            INSERT INTO status_history (project_id, old_status, new_status, changed_by, change_reason)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, old_status, new_status, changed_by, reason))
    
    conn.commit()
    print(f"✓ Статус изменён: {old_status} → {new_status}")
    conn.close()

def add_artifact(project_id: int, artifact_type: str, title: str, 
                 description: str = '', content_url: str = None, **metadata):
    """Добавление артефакта к проекту"""
    conn = get_connection()
    
    valid_types = ['Link', 'File', 'Note', 'Decision', 'Risk', 'Metric']
    if artifact_type not in valid_types:
        print(f"✗ Неверный тип артефакта. Доступные: {', '.join(valid_types)}")
        conn.close()
        return
    
    meta_json = json.dumps(metadata) if metadata else None
    
    cursor = conn.execute("""
        INSERT INTO artifacts (project_id, artifact_type, title, description, content_url, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (project_id, artifact_type, title, description, content_url, meta_json))
    conn.commit()
    print(f"✓ Артефакт добавлен с ID: {cursor.lastrowid}")
    conn.close()

def show_stats():
    """Статистика по проектам"""
    conn = get_connection()
    
    print("\n📊 СТАТИСТИКА ПО ПРОЕКТАМ")
    print("=" * 60)
    
    # По статусам
    cursor = conn.execute("""
        SELECT current_status, COUNT(*) as count
        FROM projects
        WHERE is_archived = 0
        GROUP BY current_status
        ORDER BY count DESC
    """)
    print("\nПо статусам:")
    for row in cursor.fetchall():
        print(f"  {row['current_status']}: {row['count']}")
    
    # По приоритетам
    cursor = conn.execute("""
        SELECT priority, COUNT(*) as count
        FROM projects
        WHERE is_archived = 0
        GROUP BY priority
        ORDER BY 
            CASE priority 
                WHEN 'Critical' THEN 1 
                WHEN 'High' THEN 2 
                WHEN 'Medium' THEN 3 
                WHEN 'Low' THEN 4 
            END
    """)
    print("\nПо приоритетам:")
    for row in cursor.fetchall():
        print(f"  {row['priority']}: {row['count']}")
    
    # Всего артефактов
    cursor = conn.execute("""
        SELECT artifact_type, COUNT(*) as count
        FROM artifacts
        GROUP BY artifact_type
    """)
    print("\nАртефакты по типам:")
    for row in cursor.fetchall():
        print(f"  {row['artifact_type']}: {row['count']}")
    
    conn.close()

def print_help():
    """Справка по командам"""
    print("""
📘 CPO PROJECT MANAGEMENT SYSTEM - КОМАНДЫ

Основные команды:
  init              - Инициализировать базу данных
  seed              - Загрузить тестовые данные
  list [status]     - Показать все проекты (можно фильтровать по статусу)
  show <id>         - Подробная информация о проекте
  stats             - Статистика по проектам

Управление:
  add <code> <name> [priority] [status] - Добавить проект
  status <id> <new_status> [reason]     - Изменить статус проекта
  artifact <id> <type> <title>          - Добавить артефакт

Примеры:
  ./cpo_system.py init
  ./cpo_system.py seed
  ./cpo_system.py list
  ./cpo_system.py list Разработка
  ./cpo_system.py show 1
  ./cpo_system.py add PROJ-001 "Новый проект" High Инициация
  ./cpo_system.py status 1 Разработка "Старт спринтов"
  ./cpo_system.py artifact 1 Risk "Риск задержки" severity=high
""")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == 'init':
        init_database()
    elif command == 'seed':
        seed_data()
    elif command == 'list':
        status = sys.argv[2] if len(sys.argv) > 2 else None
        list_projects(status)
    elif command == 'show':
        if len(sys.argv) < 3:
            print("Укажите ID проекта: show <id>")
        else:
            show_project_details(int(sys.argv[2]))
    elif command == 'stats':
        show_stats()
    elif command == 'add':
        if len(sys.argv) < 4:
            print("Использование: add <code> <name> [priority] [status]")
        else:
            code = sys.argv[2]
            name = sys.argv[3]
            priority = sys.argv[4] if len(sys.argv) > 4 else 'Medium'
            status = sys.argv[5] if len(sys.argv) > 5 else 'Инициация'
            add_project(code, name, f"Описание для {name}", priority, status)
    elif command == 'status':
        if len(sys.argv) < 4:
            print("Использование: status <id> <new_status> [reason]")
        else:
            project_id = int(sys.argv[2])
            new_status = sys.argv[3]
            reason = sys.argv[4] if len(sys.argv) > 4 else ''
            update_status(project_id, new_status, reason)
    elif command == 'artifact':
        if len(sys.argv) < 5:
            print("Использование: artifact <id> <type> <title> [description]")
        else:
            project_id = int(sys.argv[2])
            art_type = sys.argv[3]
            title = sys.argv[4]
            desc = sys.argv[5] if len(sys.argv) > 5 else ''
            add_artifact(project_id, art_type, title, desc)
    else:
        print(f"Неизвестная команда: {command}")
        print_help()
