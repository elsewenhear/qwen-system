-- Данные для наполнения системы (примеры проектов)

-- Проект 1: Мобильное приложение для клиентов
INSERT INTO projects (code, name, description, owner, priority, current_status, start_date, meta_attributes, tags)
VALUES (
    'MOB-APP-01',
    'Мобильное приложение для клиентов',
    'Разработка нативного приложения для iOS и Android с личным кабинетом клиента',
    'CPO',
    'High',
    'Разработка',
    '2024-01-15',
    '{"platform": "iOS/Android", "team_size": 6, "budget_usd": 150000, "tech_stack": ["Swift", "Kotlin", "Node.js"], "sprint_duration_weeks": 2}',
    'mobile, customer-facing, high-priority'
);

-- Проект 2: Аналитическая панель для руководства
INSERT INTO projects (code, name, description, owner, priority, current_status, start_date, end_date, meta_attributes, tags)
VALUES (
    'WEB-DASH-04',
    'Аналитическая панель для руководства',
    'Дашборд с ключевыми метриками бизнеса в реальном времени',
    'CPO',
    'Low',
    'Заморожен',
    '2023-11-01',
    '2024-03-30',
    '{"reason_hold": "ожидание данных от отдела аналитики", "stakeholder": "Director", "planned_features": ["revenue_chart", "user_cohorts", "funnel_analysis"], "blocked_by": "data_pipeline"}',
    'analytics, internal, frozen'
);

-- Проект 3: Интеграция с платежным шлюзом
INSERT INTO projects (code, name, description, owner, priority, current_status, start_date, meta_attributes, tags)
VALUES (
    'PAY-GW-02',
    'Интеграция с новым платежным шлюзом',
    'Подключение альтернативного платежного провайдера для снижения комиссий',
    'CPO',
    'Critical',
    'Тестирование',
    '2024-02-01',
    '{"provider": "CloudPayments", "expected_savings_percent": 1.5, "compliance_status": "approved", "api_version": "v2.1", "test_cards_configured": true}',
    'payments, integration, critical'
);

-- История статусов для Проекта 1
INSERT INTO status_history (project_id, old_status, new_status, changed_by, change_reason, changed_at)
VALUES 
    (1, NULL, 'Инициация', 'CPO', 'Создание проекта', '2024-01-15 09:00:00'),
    (1, 'Инициация', 'Исследование', 'CPO', 'Старт исследовательской фазы', '2024-01-22 14:30:00'),
    (1, 'Исследование', 'Разработка', 'CPO', 'Утверждение ТЗ, старт спринтов', '2024-02-05 10:00:00');

-- История статусов для Проекта 2
INSERT INTO status_history (project_id, old_status, new_status, changed_by, change_reason, changed_at)
VALUES 
    (2, NULL, 'Инициация', 'CPO', 'Создание проекта', '2023-11-01 11:00:00'),
    (2, 'Инициация', 'Исследование', 'CPO', 'Сбор требований', '2023-11-15 16:00:00'),
    (2, 'Исследование', 'Разработка', 'CPO', 'Начало разработки прототипа', '2023-12-10 09:30:00'),
    (2, 'Разработка', 'Заморожен', 'CPO', 'Ожидание данных от аналитиков', '2024-01-20 15:45:00');

-- История статусов для Проекта 3
INSERT INTO status_history (project_id, old_status, new_status, changed_by, change_reason, changed_at)
VALUES 
    (3, NULL, 'Инициация', 'CPO', 'Создание проекта', '2024-02-01 08:00:00'),
    (3, 'Инициация', 'Исследование', 'CPO', 'Анализ API провайдера', '2024-02-05 13:00:00'),
    (3, 'Исследование', 'Разработка', 'CPO', 'Старт интеграции', '2024-02-15 10:00:00'),
    (3, 'Разработка', 'Тестирование', 'CPO', 'Завершение разработки, начало тестов', '2024-03-01 11:30:00');

-- Артефакты для Проекта 1
INSERT INTO artifacts (project_id, artifact_type, title, content_url, description, metadata)
VALUES 
    (1, 'Link', 'Дизайн-макеты в Figma', 'https://figma.com/file/abc123', 'Основные экраны приложения', '{"frames_count": 45, "last_updated": "2024-02-20"}'),
    (1, 'Risk', 'Риск задержки API от бэкенда', NULL, 'Бэкенд-команда отстаёт на 1 спринт', '{"severity": "high", "mitigation": "добавить разработчика", "probability": 0.7}'),
    (1, 'Decision', 'Выбор кроссплатформенной архитектуры', NULL, 'Решено использовать нативную разработку вместо Flutter', '{"alternatives": ["Flutter", "React Native"], "decision_date": "2024-01-25"}'),
    (1, 'Note', 'Заметки по встрече со стейкхолдерами', NULL, 'Ключевые требования от маркетинга', '{"meeting_date": "2024-02-10", "attendees": ["CMO", "Product Lead"]}');

-- Артефакты для Проекта 2
INSERT INTO artifacts (project_id, artifact_type, title, content_url, description, metadata)
VALUES 
    (2, 'Link', 'Требования к дашборду', 'https://confluence.internal/dash-reqs', 'Документ с требованиями', '{"version": "1.3", "approved": false}'),
    (2, 'Risk', 'Недостаточное качество данных', NULL, 'Источники данных не готовы к продакшену', '{"severity": "critical", "owner": "Head of Analytics"}'),
    (2, 'Note', 'Причина заморозки', NULL, 'Официальное письмо от директора по данным', '{"document_ref": "DATA-2024-007"}');

-- Артефакты для Проекта 3
INSERT INTO artifacts (project_id, artifact_type, title, content_url, description, metadata)
VALUES 
    (3, 'Link', 'Документация CloudPayments API', 'https://developers.cloudpayments.ru', 'Официальная документация', '{"api_version": "v2.1"}'),
    (3, 'File', 'Сертификат PCI DSS', '/docs/certificates/pci-dss-2024.pdf', 'Сертификат соответствия', '{"expiry_date": "2025-06-30", "issuer": "PCI Council"}'),
    (3, 'Decision', 'Выбор метода оплаты', NULL, 'Поддержка 3-D Secure v2 обязательна', '{"compliance_required": true}'),
    (3, 'Metric', 'Конверсия платежей (тест)', NULL, 'Тестовая конверсия 94.5%', '{"value": 94.5, "unit": "percent", "sample_size": 1000}'),
    (3, 'Risk', 'Риск отказа в сертификации', NULL, 'Возможны проблемы при аудите', '{"severity": "medium", "mitigation": "пре-аудит"}');
