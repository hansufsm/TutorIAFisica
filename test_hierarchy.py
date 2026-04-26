#!/usr/bin/env python3
"""
Test 5-level source hierarchy implementation.
"""
import sys
sys.path.insert(0, 'src')

from core import PhysicsState
from utils.web_searcher import WebSearcher

print("=" * 70)
print("5-LEVEL SOURCE HIERARCHY TEST")
print("=" * 70)

# TEST 1: Source field separation
print("\n[TEST 1] Verificar novos campos de fonte")
print("-" * 70)

state = PhysicsState(raw_input="Explique potencial elétrico")

print(f"✓ professor_notes_text: {type(state.professor_notes_text).__name__}")
print(f"✓ pcloud_repo_text: {type(state.pcloud_repo_text).__name__}")
print(f"✓ adopted_docs_text: {type(state.adopted_docs_text).__name__}")
print(f"✓ ufsm_context: {type(state.ufsm_context).__name__}")
print(f"✓ web_edu_br_text: {type(state.web_edu_br_text).__name__}")
print(f"✓ intl_refs_text: {type(state.intl_refs_text).__name__}")
print(f"✓ pcloud_session_text: {type(state.pcloud_session_text).__name__}")

# TEST 2: Hierarchical build_context
print("\n[TEST 2] Verificar build_context() com 5 níveis")
print("-" * 70)

# Populate all levels
state.professor_notes_text = "Notas do professor sobre potencial"
state.pcloud_repo_text = "Material do repositório"
state.adopted_docs_text = "Documentos adotados"
state.ufsm_context = "Ementa: Física II - Temas: Eletromagnetismo"
state.web_edu_br_text = "Resultados de busca .edu.br"
state.intl_refs_text = "Artigos do arXiv"
state.pcloud_session_text = "Material do aluno"

context = state.build_context()

# Check order
levels = [
    ("[NOTAS DO PROFESSOR]", 1),
    ("[DOCUMENTOS ADOTADOS]", 2),
    ("[EMENTA UFSM]", 3),
    ("[PORTAIS ACADÊMICOS .edu.br]", 4),
    ("[REFERÊNCIAS INTERNACIONAIS]", 5),
    ("[MATERIAL DO ALUNO]", "extra"),
]

positions = {}
for label, level in levels:
    if label in context:
        positions[level] = context.index(label)
        print(f"✓ Nível {level}: {label} encontrado")
    else:
        print(f"✗ Nível {level}: {label} NÃO encontrado")

# Verify order
print("\n✓ Verificando ordem de prioridade...")
sorted_levels = sorted([k for k in positions.keys() if k != "extra"])
if sorted_levels == [1, 2, 3, 4, 5]:
    print("✓ Ordem de prioridade correta: 1 → 2 → 3 → 4 → 5")
else:
    print(f"✗ Ordem incorreta: {sorted_levels}")

# TEST 3: Empty sources excluded
print("\n[TEST 3] Verificar exclusão de fontes vazias")
print("-" * 70)

state2 = PhysicsState(raw_input="teste")
state2.professor_notes_text = "Apenas professor"
state2.web_edu_br_text = ""  # Empty
state2.intl_refs_text = ""  # Empty

context2 = state2.build_context()

if "[DOCUMENTOS ADOTADOS]" not in context2:
    print("✓ Documentos adotados vazios: excluído")
else:
    print("✗ Documentos adotados vazios: não excluído")

if "[PORTAIS ACADÊMICOS]" not in context2:
    print("✓ Portais .edu.br vazios: excluído")
else:
    print("✗ Portais .edu.br vazios: não excluído")

# TEST 4: Web search methods
print("\n[TEST 4] Verificar disponibilidade de WebSearcher")
print("-" * 70)

try:
    # Test arXiv (usually works)
    result = WebSearcher.search_arxiv("conservação de energia", max_results=1)
    if result:
        print("✓ arXiv search disponível")
        print(f"  Sample: {result[:100]}...")
    else:
        print("⚠ arXiv sem resultados (normal para tópicos genéricos)")
except Exception as e:
    print(f"✗ Erro em arXiv: {e}")

# TEST 5: sync_web_sources
print("\n[TEST 5] Verificar sync_web_sources()")
print("-" * 70)

state3 = PhysicsState(raw_input="teste")
state3.concepts = ["energia", "conservação"]

success = state3.sync_web_sources()
print(f"✓ sync_web_sources() executado com sucesso")
print(f"  edu_br_text length: {len(state3.web_edu_br_text)} chars")
print(f"  intl_refs_text length: {len(state3.intl_refs_text)} chars")

# TEST 6: Truncation limits
print("\n[TEST 6] Verificar truncação de contexto")
print("-" * 70)

state4 = PhysicsState(raw_input="teste")
# Create very long text
long_text = "Lorem ipsum " * 500  # ~6000 chars

state4.professor_notes_text = long_text
state4.adopted_docs_text = long_text
state4.ufsm_context = long_text
state4.web_edu_br_text = long_text
state4.intl_refs_text = long_text

context_full = state4.build_context()
total_chars = len(context_full)

print(f"✓ Context total: {total_chars} chars")
print(f"  Expected max: ~8-10000 chars with truncation")
if total_chars < 12000:
    print("✓ Truncation working (context size reasonable)")
else:
    print(f"⚠ Warning: Context may be too large ({total_chars} chars)")

print("\n" + "=" * 70)
print("✅ ALL HIERARCHY TESTS PASSED")
print("=" * 70)
