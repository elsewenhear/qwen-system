-- Схема базы данных для управления проектами CPO
-- Версия 1.0

-- Таблица проектов
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    owner TEXT DEFAULT 'CPO',
    priority TEXT CHECK(priority IN ('Low', 'Medium', 'High', 'Critical')) DEFAULT 'Medium',
    current_status TEXT DEFAULT 'Инициация',
    start_date DATE,
    end_date DATE,
    meta_attributes JSON, -- Динамические атрибуты (JSON)
    tags TEXT, -- Теги через запятую
    is_archived BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Таблица истории статусов
CREATE TABLE IF NOT EXISTS status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    old_status TEXT,
    new_status TEXT NOT NULL,
    changed_by TEXT DEFAULT 'CPO',
    change_reason TEXT,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Таблица артефактов (документы, ссылки, риски, решения)
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    artifact_type TEXT CHECK(artifact_type IN ('Link', 'File', 'Note', 'Decision', 'Risk', 'Metric')) NOT NULL,
    title TEXT NOT NULL,
    content_url TEXT, -- Ссылка или путь к файлу
    description TEXT,
    metadata JSON, -- Дополнительные метаданные
    created_by TEXT DEFAULT 'CPO',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Триггер для автоматического обновления updated_at
CREATE TRIGGER IF NOT EXISTS update_projects_timestamp 
AFTER UPDATE ON projects
BEGIN
    UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Триггер для автоматической записи в историю при смене статуса
CREATE TRIGGER IF NOT EXISTS track_status_change
AFTER UPDATE OF current_status ON projects
WHEN OLD.current_status != NEW.current_status
BEGIN
    INSERT INTO status_history (project_id, old_status, new_status, changed_by, change_reason)
    VALUES (NEW.id, OLD.current_status, NEW.current_status, 'CPO', 'Автоматическая запись');
END;

-- Индексы для ускорения поиска
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(current_status);
CREATE INDEX IF NOT EXISTS idx_projects_priority ON projects(priority);
CREATE INDEX IF NOT EXISTS idx_projects_code ON projects(code);
CREATE INDEX IF NOT EXISTS idx_status_history_project ON status_history(project_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_project ON artifacts(project_id);
