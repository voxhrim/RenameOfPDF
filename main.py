"""
PDF Batch Renamer
=================
Запускает Ollama и переименовывает PDF-файлы по автору и названию.

Использование:
    python main.py
"""

import os
import re
import sys
import requests

from config import PDF_FOLDER, OLLAMA_MODEL, DRY_RUN, TIMEOUT
from start_ollama import ensure_ollama_running


def extract_first_pages_text(pdf_path: str, pages: int = 2) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        texts = []
        for page in reader.pages[:pages]:
            t = page.extract_text()
            if t:
                texts.append(t)
        return "\n".join(texts).strip()
    except Exception as e:
        print(f"  [!] Не удалось прочитать файл: {e}")
        return ""


def ask_ollama(text: str) -> tuple[str, str]:
    prompt = f"""Ниже приведён текст с первой страницы научной публикации, журнала или книги.
Определи:
1. Автора (или авторов). Если авторов несколько, перечисли через запятую. Используй формат "Фамилия И.О." или "Фамилия" если инициалы неизвестны.
2. Название работы.

Ответь СТРОГО в формате:
AUTHOR: <автор(ы)>
TITLE: <название>

Не добавляй ничего лишнего. Если автор неизвестен, напиши AUTHOR: Unknown. Если название неизвестно, напиши TITLE: Unknown.

Текст:
{text[:3000]}
"""
    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            },
            timeout=TIMEOUT
        )
        result = response.json()["message"]["content"].strip()
        author_match = re.search(r"AUTHOR:\s*(.+)", result)
        title_match = re.search(r"TITLE:\s*(.+)", result)
        author = author_match.group(1).strip() if author_match else "Unknown"
        title = title_match.group(1).strip() if title_match else "Unknown"
        return author, title
    except Exception as e:
        print(f"  [!] Ошибка Ollama: {type(e).__name__}: {e}")
        return "", ""


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]', "", name)
    return name.strip().rstrip(".")[:100]


def build_new_name(author: str, title: str) -> str:
    author_clean = sanitize_filename(author)
    title_clean = sanitize_filename(title)
    if author_clean and author_clean.lower() != "unknown":
        return f"{author_clean} - {title_clean}.pdf"
    return f"{title_clean}.pdf"


def unique_path(folder: str, filename: str) -> str:
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(folder, filename)
    counter = 2
    while os.path.exists(candidate):
        candidate = os.path.join(folder, f"{base} ({counter}){ext}")
        counter += 1
    return candidate


def main():
    # 1. Запускаем Ollama
    ensure_ollama_running()

    # 2. Проверяем папку
    if not os.path.isdir(PDF_FOLDER):
        print(f"❌ Папка не найдена: {PDF_FOLDER}")
        print("   Проверьте PDF_FOLDER в config.py")
        sys.exit(1)

    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("Нет PDF-файлов в указанной папке.")
        sys.exit(0)

    print(f"\n📂 Папка: {PDF_FOLDER}")
    print(f"📄 Найдено файлов: {len(pdf_files)}")
    print(f"🤖 Модель: {OLLAMA_MODEL}")
    if DRY_RUN:
        print("⚠️  Режим DRY RUN — файлы не переименовываются.\n")

    renamed = 0
    skipped = 0

    for idx, filename in enumerate(pdf_files, 1):
        pdf_path = os.path.join(PDF_FOLDER, filename)
        print(f"\n[{idx}/{len(pdf_files)}] {filename}")

        text = extract_first_pages_text(pdf_path)
        if not text:
            print("  → Текст не извлечён (возможно, скан). Пропускаем.")
            skipped += 1
            continue

        author, title = ask_ollama(text)
        if not author and not title:
            print("  → Ollama не ответил. Пропускаем.")
            skipped += 1
            continue

        print(f"  Автор   : {author}")
        print(f"  Название: {title}")

        if title.lower() == "unknown" and author.lower() == "unknown":
            print("  → Не удалось определить. Пропускаем.")
            skipped += 1
            continue

        new_filename = build_new_name(author, title)
        new_path = unique_path(PDF_FOLDER, new_filename)

        if os.path.basename(new_path) == filename:
            print("  → Имя уже корректное, пропускаем.")
            skipped += 1
            continue

        print(f"  ✅ Новое имя: {os.path.basename(new_path)}")

        if not DRY_RUN:
            os.rename(pdf_path, new_path)
            renamed += 1
        else:
            renamed += 1

    print(f"\n{'=' * 50}")
    print(f"✅ Готово! Переименовано: {renamed}, пропущено: {skipped}")
    if DRY_RUN:
        print("(DRY RUN — реальных изменений не было)")

    # Останавливаем Ollama после завершения
    print("\n🛑 Останавливаем Ollama...")
    from start_ollama import kill_ollama
    kill_ollama()
    print("Ollama остановлен.")


if __name__ == "__main__":
    main()
