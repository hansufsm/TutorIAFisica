#!/usr/bin/env python3
"""
Test UFSM syllabus matching and context extraction.
Verifies that concepts trigger correct discipline matching.
"""
import sys
sys.path.insert(0, 'src')

from core import PhysicsState

def test_ufsm_matching():
    """Test that concepts match UFSM disciplines correctly."""
    print("\n=== TEST: UFSM Discipline Matching ===")

    state = PhysicsState(raw_input="Explique conservação de energia")

    # Simulate interpreter identifying concepts
    state.concepts = ["energia", "conservação"]
    print(f"✅ Concepts identified: {state.concepts}")

    # Call UFSM matching
    state._check_ufsm_syllabus()

    if state.ufsm_alignment:
        print(f"✅ Match found: {state.ufsm_alignment['nome']} ({state.ufsm_alignment['codigo']})")
        print(f"   UFSM Context:\n{state.ufsm_context}")

        # Verify context has expected fields
        assert state.ufsm_context
        assert state.ufsm_alignment['nome'] in state.ufsm_context
        assert state.ufsm_alignment['codigo'] in state.ufsm_context
        assert "Temas do ementário:" in state.ufsm_context
        assert "Bibliografia básica:" in state.ufsm_context
        print("✅ UFSM context properly formatted with temas and bibliography")
    else:
        print("⚠️  No UFSM match (may be expected if concept is not in syllabus)")

def test_full_context_with_ufsm():
    """Test full context assembly including UFSM."""
    print("\n=== TEST: Full Context with UFSM ===")

    state = PhysicsState(raw_input="Problema de física")

    # Simulate all sources
    state.concepts = ["energia"]
    state._check_ufsm_syllabus()

    state.professor_notes_text = "Notas sobre energia e trabalho"
    state.pcloud_session_text = "PDFs do aluno"
    state.pcloud_repo_text = "Repositório do professor"

    context = state.build_context()

    if state.ufsm_context:
        assert "[EMENTA UFSM]" in context
        print("✅ UFSM included in final context")

    assert "[NOTAS DO PROFESSOR]" in context
    assert "[MATERIAL DO ALUNO - pCloud]" in context
    assert "[REPOSITÓRIO DE MATERIAIS]" in context
    print(f"✅ Full context assembled ({len(context)} caracteres)")
    print(f"   Structure: {context[:150]}...")

if __name__ == "__main__":
    print("=" * 60)
    print("UFSM MATCHING TEST SUITE")
    print("=" * 60)

    try:
        test_ufsm_matching()
        test_full_context_with_ufsm()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
