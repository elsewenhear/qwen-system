#!/usr/bin/env python3
"""
CPO Project System - Web Interface
Запуск веб-сервера для управления проектами
"""

import os
import sys

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, init_db

if __name__ == '__main__':
    print("=" * 60)
    print("📊 CPO Project System - Веб-интерфейс")
    print("=" * 60)
    
    # Инициализация БД
    init_db()
    print("✅ База данных инициализирована")
    
    print("\n🌐 Запуск сервера...")
    print("   Откройте в браузере: http://localhost:5000")
    print("   Для остановки нажмите: Ctrl+C")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
