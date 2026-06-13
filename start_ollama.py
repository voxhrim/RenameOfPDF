"""
Останавливает все запущенные копии Ollama и запускает новую с CPU-режимом.
"""

import subprocess
import socket
import time
import os
import sys
from config import OLLAMA_EXE


def is_port_busy(port=11434) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def kill_ollama():
    """Завершает все процессы ollama.exe."""
    subprocess.run(
        ["taskkill", "/F", "/IM", "ollama.exe"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    # Ждём пока порт освободится
    for _ in range(10):
        if not is_port_busy():
            return True
        time.sleep(0.5)
    return False


def start_ollama():
    """Запускает Ollama в фоне с отключённым GPU."""
    if not os.path.exists(OLLAMA_EXE):
        print(f"❌ Ollama не найден по пути: {OLLAMA_EXE}")
        print("   Проверьте OLLAMA_EXE в config.py")
        sys.exit(1)

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "-1"
    env["OLLAMA_NUM_GPU"] = "0"

    subprocess.Popen(
        [OLLAMA_EXE, "serve"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Ждём пока сервер поднимется
    print("⏳ Запускаем Ollama...", end="", flush=True)
    for _ in range(20):
        if is_port_busy():
            print(" готово!")
            return True
        time.sleep(0.5)
        print(".", end="", flush=True)

    print("\n❌ Ollama не запустился за 10 секунд.")
    sys.exit(1)


def ensure_ollama_running():
    """Главная функция: убивает старый процесс и запускает новый."""
    print("🔄 Перезапускаем Ollama (CPU-режим)...")
    kill_ollama()
    time.sleep(1)
    start_ollama()
