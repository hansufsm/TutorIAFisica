#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from dotenv import load_dotenv
load_dotenv()

import litellm
from config import Config

litellm.set_verbose = False

print("=" * 80)
print("🧪 TESTE DE CHAVES API")
print("=" * 80)

for name, info in Config.AVAILABLE_MODELS.items():
    key_name = Config.get_provider_key_name(name)
    api_key = os.getenv(key_name) if key_name else None

    if key_name and not api_key:
        print(f"⏭️  {name:25} chave {key_name} ausente no .env")
        continue

    try:
        resp = litellm.completion(
            model=info["id"],
            messages=[{"role": "user", "content": "oi"}],
            api_key=api_key,
            max_tokens=50
        )
        text = resp.choices[0].message.content.strip()
        preview = text[:80] + "..." if len(text) > 80 else text
        print(f"✅  {name:25} {preview}")
    except Exception as e:
        error_msg = str(e)[:70]
        print(f"❌  {name:25} {error_msg}")

print("=" * 80)
