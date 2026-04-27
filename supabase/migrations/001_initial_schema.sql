-- TutorIAFisica Database Schema
-- Supabase PostgreSQL setup with pgvector support
-- Created: 2026-04-27

-- Habilitar extensão pgvector para embeddings futuros (Student Model)
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- TABELA: students (Perfis dos alunos)
-- =====================================================
CREATE TABLE students (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email        TEXT UNIQUE NOT NULL,
  name         TEXT,
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  last_seen    TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- TABELA: concept_status (Student Model: status de cada conceito por aluno)
-- =====================================================
CREATE TABLE concept_status (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id          UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  concept_id          TEXT NOT NULL,           -- ex: "newton_segunda_lei"
  topic               TEXT NOT NULL,           -- ex: "Dinâmica"
  status              TEXT DEFAULT 'not_started',
    -- 'not_started' | 'developing' | 'mastered' | 'consolidated'
  mastery_level       FLOAT DEFAULT 0.0,       -- 0.0 a 1.0
  review_interval_days INT DEFAULT 1,          -- algoritmo SM-2
  ease_factor         FLOAT DEFAULT 2.5,       -- fator de facilidade SM-2
  last_reviewed       TIMESTAMPTZ,
  next_review         TIMESTAMPTZ,
  date_introduced     TIMESTAMPTZ DEFAULT NOW(),
  date_mastered       TIMESTAMPTZ,
  embedding           vector(1536),            -- para busca semântica futura
  UNIQUE(student_id, concept_id)
);

-- =====================================================
-- TABELA: misconceptions (Misconceptions detectadas por aluno)
-- =====================================================
CREATE TABLE misconceptions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id    UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  concept_id    TEXT NOT NULL,
  misconception_id TEXT NOT NULL,             -- ex: "mc_forca_velocidade"
  description   TEXT,
  detected_at   TIMESTAMPTZ DEFAULT NOW(),
  resolved_at   TIMESTAMPTZ,                  -- null = ainda ativa
  attempts      INT DEFAULT 1
);

-- =====================================================
-- TABELA: session_log (Log de sessões)
-- =====================================================
CREATE TABLE session_log (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id    UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  question      TEXT NOT NULL,
  topic         TEXT,
  model_used    TEXT,
  fallback      BOOLEAN DEFAULT FALSE,
  agents_output JSONB,                        -- saída completa dos 5 agentes
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- ÍNDICES para performance
-- =====================================================
CREATE INDEX idx_concept_student ON concept_status(student_id);
CREATE INDEX idx_concept_next_review ON concept_status(next_review);
CREATE INDEX idx_misconceptions_student ON misconceptions(student_id, resolved_at);
CREATE INDEX idx_session_student ON session_log(student_id, created_at DESC);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- Cada aluno só acessa seus próprios dados
-- =====================================================
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE concept_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE misconceptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_log ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES
-- =====================================================

-- Aluno acessa próprios conceitos
CREATE POLICY "aluno_acessa_proprios_conceitos" ON concept_status
  FOR ALL USING (student_id = auth.uid());

-- Aluno acessa próprias misconceptions
CREATE POLICY "aluno_acessa_proprias_misconceptions" ON misconceptions
  FOR ALL USING (student_id = auth.uid());

-- Aluno acessa próprias sessões
CREATE POLICY "aluno_acessa_proprias_sessoes" ON session_log
  FOR ALL USING (student_id = auth.uid());
