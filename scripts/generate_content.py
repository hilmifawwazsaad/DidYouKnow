import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.environ.get("SUMOPOD_API_KEY")
api_url = os.environ.get("SUMOPOD_API_URL")
model = os.environ.get("SUMOPOD_MODEL")

if not api_key:
    print("Error: SUMOPOD_API_KEY environment variable not set.")
    exit(1)
if not model:
    print("Error: SUMOPOD_MODEL environment variable not set.")
    exit(1)

client = OpenAI(api_key=api_key, base_url=api_url)

today_str = datetime.now().strftime("%Y-%m-%d")

output_dir = "public/data"
os.makedirs(output_dir, exist_ok=True)
filename = os.path.join(output_dir, f"did-you-know-{today_str}.json")
latest_filename = os.path.join(output_dir, "latest.json")

MAX_RETRIES = 3
content_json = None
raw_content = ""

for attempt in range(1, MAX_RETRIES + 1):
    try:
        print(f"Memanggil API untuk tanggal {today_str}... (percobaan {attempt}/{MAX_RETRIES})")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Kamu seorang yang sangat berwawasan luas dengan informasi seputar dunia dan alam semesta."
                        "Balas HANYA JSON: {\"date\": \"YYYY-MM-DD\", \"fact\": \"...\"}. "
                        "Tanpa markdown, tanpa key lain."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Tanggal: {today_str}. "
                        "Tulis 1 fakta menarik dan mengejutkan dalam bahasa Indonesia, "
                        "topik bebas (sains, sejarah, alam, atau budaya). "
                        "Maksimal 2 kalimat, padat dan menarik."
                    ),
                },
            ],
            max_tokens=600,
            temperature=0.9,
            response_format={"type": "json_object"},
        )

        choice = response.choices[0]
        if choice.finish_reason == "length":
            print(f"Percobaan {attempt}: Respons terpotong (finish_reason=length), mencoba ulang...")
            continue

        raw_content = str(choice.message.content or "").strip()
        content_json = json.loads(raw_content)
        break

    except json.JSONDecodeError as e:
        print(f"Percobaan {attempt}: Respons API bukan JSON valid: {e}")
        if attempt < MAX_RETRIES:
            print("Mencoba ulang...")
            continue
        print(f"Raw response: {raw_content[:200]}")
        exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if content_json is None:
    print(f"Error: Gagal mendapatkan respons valid setelah {MAX_RETRIES} percobaan.")
    exit(1)

try:
    content_json.setdefault("date", today_str)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(content_json, f, ensure_ascii=False, indent=2)

    with open(latest_filename, "w", encoding="utf-8") as f:
        json.dump(content_json, f, ensure_ascii=False, indent=2)

    print(f"File {filename} berhasil dibuat.")
    print(f"File {latest_filename} diperbarui.")
    print(f"Topik: {content_json.get('topic', '-')}")

except json.JSONDecodeError as e:
    print(f"Error: Respons API bukan JSON valid: {e}")
    print(f"Raw response: {raw_content[:200]}")
    exit(1)
except Exception as e:
    print(f"Error: {e}")
    exit(1)
