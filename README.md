# PDF Batch Renamer

Автоматически переименовывает PDF-файлы в формат `Автор - Название.pdf` используя локальную AI-модель через Ollama.

## Требования

- Python 3.10+
- [Ollama](https://ollama.com) с моделью `mistral`

```bash
pip install pypdf requests
ollama pull mistral
```

## Структура

```
├── main.py          # Точка входа — запускает Ollama и переименовывает файлы
├── config.py        # Настройки (папка с PDF, модель, пути)
├── start_ollama.py  # Запуск/остановка Ollama
├── stop_ollama.py   # Ручная остановка Ollama
```

## Настройка

Откройте `config.py` и укажите:

```python
PDF_FOLDER = r"C:\путь\к\папке\с\PDF"
OLLAMA_EXE = r"C:\Users\ИМЯ\AppData\Local\Programs\Ollama\ollama.exe"
```

## Запуск

```bash
python main.py
```

Скрипт сам запустит Ollama, обработает все PDF и остановит Ollama по завершении.

Для тестового прогона без переименования установите в `config.py`:
```python
DRY_RUN = True
```

## Остановить Ollama вручную

```bash
python stop_ollama.py
```

## Примечания

- PDF-сканы без текстового слоя пропускаются
- Ollama запускается в CPU-режиме (флаг `CUDA_VISIBLE_DEVICES=-1`) из-за проблем совместимости с CUDA
- Первый запрос к модели занимает ~30-60 секунд (модель загружается в память)
