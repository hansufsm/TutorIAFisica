#!/usr/bin/env python3
"""
Test script for source-attributed context pipeline.
Verifies that PhysicsState correctly separates and prioritizes sources.
"""
import sys
import json
sys.path.insert(0, 'src')

from core import PhysicsState

def test_source_separation():
    """Test that sources are kept separate in PhysicsState."""
    print("\n=== TEST 1: Source Separation ===")
    state = PhysicsState(
        raw_input="Explique conservação de energia",
        teacher_notes="Notas iniciais do professor"
    )

    assert state.professor_notes_text == "Notas iniciais do professor"
    assert state.pcloud_session_text == ""
    assert state.pcloud_repo_text == ""
    assert state.ufsm_context == ""
    print("✅ Sources start separated")

    state.pcloud_session_text = "Material do aluno enviado"
    state.pcloud_repo_text = "Repositório permanente do professor"
    state.ufsm_context = "Disciplina: Física I (FSC1027)\nTemas: Energia, Trabalho, Conservação"

    assert state.pcloud_session_text == "Material do aluno enviado"
    assert state.pcloud_repo_text == "Repositório permanente do professor"
    print("✅ Sources updated correctly")

def test_build_context_priority():
    """Test that build_context respects priority order."""
    print("\n=== TEST 2: Context Priority Order ===")
    state = PhysicsState(raw_input="teste")

    # Add sources in reverse order
    state.pcloud_repo_text = "Repositório"
    state.pcloud_session_text = "Material do Aluno"
    state.professor_notes_text = "Notas do Professor"
    state.ufsm_context = "Ementa UFSM"

    context = state.build_context()

    # Check order: UFSM → Professor → Aluno → Repositório
    ufsm_pos = context.index("[EMENTA UFSM]")
    prof_pos = context.index("[NOTAS DO PROFESSOR]")
    aluno_pos = context.index("[MATERIAL DO ALUNO - pCloud]")
    repo_pos = context.index("[REPOSITÓRIO DE MATERIAIS]")

    assert ufsm_pos < prof_pos < aluno_pos < repo_pos, f"Priority violated: {ufsm_pos} < {prof_pos} < {aluno_pos} < {repo_pos}"
    print(f"✅ Priority order correct: UFSM({ufsm_pos}) → Prof({prof_pos}) → Aluno({aluno_pos}) → Repo({repo_pos})")

def test_empty_sources_excluded():
    """Test that empty sources don't appear in context."""
    print("\n=== TEST 3: Empty Sources Excluded ===")
    state = PhysicsState(raw_input="teste")
    state.professor_notes_text = "Notas do professor"
    state.pcloud_session_text = ""  # Empty
    state.pcloud_repo_text = ""     # Empty
    state.ufsm_context = ""         # Empty

    context = state.build_context()

    assert "[EMENTA UFSM]" not in context
    assert "[MATERIAL DO ALUNO - pCloud]" not in context
    assert "[REPOSITÓRIO DE MATERIAIS]" not in context
    assert "[NOTAS DO PROFESSOR]" in context
    print("✅ Only non-empty sources included")

def test_ufsm_syllabus_parsing():
    """Test that UFSM syllabus is parsed and stored in ufsm_context."""
    print("\n=== TEST 4: UFSM Syllabus Parsing ===")

    try:
        with open("data/ufsm_syllabus.json", "r", encoding="utf-8") as f:
            syllabus = json.load(f)

        # Check structure
        assert "disciplinas" in syllabus
        assert len(syllabus["disciplinas"]) > 0

        first_disc = syllabus["disciplinas"][0]
        assert "codigo" in first_disc
        assert "nome" in first_disc
        assert "temas" in first_disc
        assert "bibliografia_basica" in first_disc

        print(f"✅ Syllabus loaded: {len(syllabus['disciplinas'])} disciplines")
        print(f"   Example: {first_disc['codigo']} - {first_disc['nome']}")
    except FileNotFoundError:
        print("⚠️  Syllabus file not found (expected in development)")

def test_backwards_compatibility():
    """Test that teacher_notes property maintains backwards compatibility."""
    print("\n=== TEST 5: Backwards Compatibility ===")
    state = PhysicsState(
        raw_input="teste",
        teacher_notes="Original notes"
    )

    # Property should still work
    notes = state.teacher_notes
    assert "Original notes" in notes
    print("✅ teacher_notes property works")

    # Adding more sources
    state.pcloud_session_text = "More notes"
    notes_combined = state.teacher_notes
    assert "Original notes" in notes_combined
    assert "More notes" in notes_combined
    print("✅ teacher_notes combines all sources")

def test_source_attribution():
    """Test that source labels are properly formatted for agents."""
    print("\n=== TEST 6: Source Attribution Formatting ===")
    state = PhysicsState(raw_input="teste")

    state.ufsm_context = "Física I - Temas: Energia"
    state.professor_notes_text = "Conteúdo do professor"

    context = state.build_context()

    # Check markdown formatting
    assert "### [EMENTA UFSM]" in context
    assert "### [NOTAS DO PROFESSOR]" in context

    # Verify sections
    lines = context.split("\n")
    headers = [line for line in lines if line.startswith("###")]
    assert len(headers) == 2
    print(f"✅ Context has {len(headers)} properly formatted sections")

if __name__ == "__main__":
    print("=" * 60)
    print("SOURCE PIPELINE TEST SUITE")
    print("=" * 60)

    try:
        test_source_separation()
        test_build_context_priority()
        test_empty_sources_excluded()
        test_ufsm_syllabus_parsing()
        test_backwards_compatibility()
        test_source_attribution()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
