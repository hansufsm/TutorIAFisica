-- Sprint 3: Long-term RAG — add embeddings to session_log
-- Permite busca semântica por sessões anteriores similares

ALTER TABLE session_log ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- IVFFlat index for cosine similarity search (requires at least 1 row to build)
-- Created lazily; if it fails due to empty table, the <-> operator still works via seqscan.
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes WHERE indexname = 'idx_session_embedding'
  ) THEN
    CREATE INDEX idx_session_embedding ON session_log
      USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
  END IF;
EXCEPTION WHEN OTHERS THEN
  -- Index creation may fail on empty table; safe to skip
  NULL;
END;$$;

-- RPC function: busca top-N sessões semanticamente similares para um aluno
CREATE OR REPLACE FUNCTION match_sessions(
  p_student_id UUID,
  p_embedding  vector(1536),
  p_limit      INT DEFAULT 3
)
RETURNS TABLE(
  id           UUID,
  question     TEXT,
  topic        TEXT,
  agents_output JSONB,
  created_at   TIMESTAMPTZ,
  distance     FLOAT
)
LANGUAGE sql STABLE
AS $$
  SELECT
    id,
    question,
    topic,
    agents_output,
    created_at,
    (embedding <-> p_embedding)::FLOAT AS distance
  FROM session_log
  WHERE student_id = p_student_id
    AND embedding  IS NOT NULL
  ORDER BY embedding <-> p_embedding
  LIMIT p_limit;
$$;
