"""
Останавливает Ollama вручную.
Запуск: python stop_ollama.py
"""

from start_ollama import kill_ollama

print("🛑 Останавливаем Ollama...")
killed = kill_ollama()
if killed:
    print("✅ Ollama остановлен.")
else:
    print("⚠️  Ollama уже не запущен.")
