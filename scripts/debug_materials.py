#!/usr/bin/env python3
"""
Debug script to verify material loading in the pipeline.
Tests:
1. PDF upload processing
2. pCloud URL handling
3. Direct URL handling
4. Context assembly with materials
"""
import sys
sys.path.insert(0, 'src')

from core import PhysicsState
from utils.pcloud_manager import PCloudManager
import json

print("=" * 70)
print("DEBUG: Material Loading Pipeline")
print("=" * 70)

# TEST 1: PDF extraction (simulated)
print("\n[TEST 1] PDF Upload Processing")
print("-" * 70)

test_pdf_content = """
Potencial Elétrico - Aula 6

O potencial elétrico é a energia potencial por unidade de carga.

V = U/q = W/(q·q')

Onde:
- V: potencial elétrico (volts)
- U: energia potencial elétrica (joules)
- q: carga de teste (coulombs)
- W: trabalho realizado

Exemplos práticos em laboratório...
"""

print(f"✓ Simulated PDF extraction: {len(test_pdf_content)} caracteres")

# TEST 2: pCloud URL handling
print("\n[TEST 2] pCloud URL Handling")
print("-" * 70)

pcloud_urls = [
    "https://u.pcloud.com/#/publink?code=kZwnXZ5JRkIVuJIKjhmWtlGzorl0jp6UeX",  # Valid format
    "https://filedn.com/lzMfmyW5BK1YhaV0f4rLG2J/pf/penAula-31-03-2026/Aula_6_Potencial_eletrico.pdf",  # Direct URL
]

for url in pcloud_urls:
    print(f"\nURL: {url[:60]}...")
    if "code=" in url:
        code = url.split("code=")[-1]
        print(f"  ✓ pCloud format detected, extracted code: {code[:20]}...")
        # Try to fetch (will likely fail with network/auth, but tests parsing)
        result = PCloudManager.fetch_notes(url)
        if result:
            print(f"  ✓ Content fetched: {len(result)} caracteres")
        else:
            print(f"  ✗ No content fetched (code may be invalid or API unreachable)")
    else:
        print(f"  ✗ NOT a pCloud URL (missing 'code=' parameter)")
        print(f"    This is a direct file URL, not supported by pCloud API")
        result = PCloudManager.fetch_notes(url)
        print(f"  Result: {result if result else '(empty - as expected)'}")

# TEST 3: Context assembly with materials
print("\n[TEST 3] Context Assembly with Materials")
print("-" * 70)

state = PhysicsState(raw_input="Explique potencial elétrico")

# Simulate materials being loaded
state.professor_notes_text = test_pdf_content  # PDF upload
state.ufsm_context = "Disciplina: Física II (FSC1028)\nTemas: Eletromagnetismo, Potencial Elétrico"
state.pcloud_session_text = ""  # Empty since URL didn't work
state.pcloud_repo_text = ""

context = state.build_context()
print(f"\nBuilt context: {len(context)} caracteres")
print(f"\nContext structure:")
print(context[:400] + "...\n")

# TEST 4: Verify context is ready for agents
print("\n[TEST 4] Verify Context for Agent Use")
print("-" * 70)

has_ufsm = "[EMENTA UFSM]" in context
has_notes = "[NOTAS DO PROFESSOR]" in context
has_pcloud = "[MATERIAL DO ALUNO - pCloud]" in context

print(f"✓ UFSM context present: {has_ufsm}")
print(f"✓ Professor notes present: {has_notes}")
print(f"✓ pCloud material present: {has_pcloud}")

if not has_notes:
    print("\n⚠️  WARNING: Professor notes are empty!")
    print("   Check if PDF was correctly uploaded and extracted")

print("\n" + "=" * 70)
print("DEBUG COMPLETE")
print("=" * 70)

# TEST 5: What happens with direct URLs
print("\n[DIAGNOSIS] Direct URL Issue")
print("-" * 70)
print("""
The URL you provided:
  https://filedn.com/lzMfmyW5BK1YhaV0f4rLG2J/pf/penAula-31-03-2026/Aula_6_Potencial_eletrico.pdf

This is a DIRECT FILE LINK (not pCloud format).

The system expects pCloud format:
  https://u.pcloud.com/#/publink?code=XXXXXXXXXX

Solutions:
1. Convert to pCloud public link (recommended):
   - Create a folder in pCloud
   - Add your PDFs to it
   - Right-click → "Get public link"
   - Use the generated link in the sidebar

2. Alternatively, we can add direct URL support (feature request)

For now, the PDF you uploaded manually should work fine.
Check that you filled out the "👨‍🏫 Notas Manuais" field correctly.
""")
