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

client = OpenAI(api_key=api_key, base_url=api_url)

today = datetime.now()
today_str = today.strftime("%Y-%m-%d")
day_name = today.strftime("%A")

output_dir = "public/data"
os.makedirs(output_dir, exist_ok=True)
filename = os.path.join(output_dir, f"did-you-know-{today_str}.json")
latest_filename = os.path.join(output_dir, "latest.json")

prompt = f"""Hari ini adalah {day_name}, {today_str}.

Hasilkan 1 fakta menarik dalam bahasa Indonesia yang menarik dan informatif.
Gunakan TEPAT dua key berikut, tidak boleh diganti:
- "date": "{today_str}"
- "fact": kalimat fakta menarik"""

try:
    print(f"Memanggil API untuk tanggal {today_str}...")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Kamu adalah ensiklopedia fakta menarik. Jawab HANYA dengan JSON object valid. Gunakan key 'date' dan 'fact' saja."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=300,
        temperature=0.8,
        response_format={"type": "json_object"}
    )

    raw_content = str(response.choices[0].message.content or "").strip()  # type: ignore[union-attr]
    content_json = json.loads(raw_content)

    # Normalize key jika model masih pakai "fakta"
    if "fakta" in content_json and "fact" not in content_json:
        content_json["fact"] = content_json.pop("fakta")
    if "date" not in content_json:
        content_json["date"] = today_str

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
