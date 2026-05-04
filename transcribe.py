import whisper
import os
import json
import shutil
import tempfile

# Path to ffmpeg
os.environ["PATH"] = r"C:\ffmpeg\bin" + os.pathsep + os.environ["PATH"]

MODEL_NAME = "medium"
VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov")
OUTPUT_FILE = "transcripts.json"
BASE_DIR = os.path.abspath("videos")
START_DIR = os.getcwd()

# Загружаем уже готовые данные если файл существует
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    done_files = set(d["file"] for d in all_data)
    print(f"Найден существующий JSON: {len(all_data)} сегментов, {len(done_files)} файлов уже готово")
else:
    all_data = []
    done_files = set()

print(f"Loading model: {MODEL_NAME}")
model = whisper.load_model(MODEL_NAME)

for root, dirs, files in os.walk(BASE_DIR):
    dirs.sort()
    for filename in sorted(files):
        if not filename.lower().endswith(VIDEO_EXTENSIONS):
            continue

        filepath = os.path.join(root, filename)
        relative_path = os.path.relpath(filepath, BASE_DIR)

        # Пропускаем уже обработанные
        if relative_path in done_files:
            print(f"Пропускаем (уже готово): {relative_path}")
            continue

        print(f"Transcribing: {relative_path}")

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                tmp_path = tmp.name
            shutil.copy2(filepath, tmp_path)
            result = model.transcribe(tmp_path, language="ru")
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

        for segment in result["segments"]:
            all_data.append({
                "file": relative_path,
                "start": round(segment["start"], 1),
                "end": round(segment["end"], 1),
                "text": segment["text"].strip()
            })

        # Сохраняем после каждого файла
        with open(os.path.join(START_DIR, OUTPUT_FILE), "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        print(f"  OK, segments: {len(result['segments'])}")

print(f"\nDone. Total segments: {len(all_data)}")