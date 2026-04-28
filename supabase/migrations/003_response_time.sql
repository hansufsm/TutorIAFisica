-- Add response_time_ms column to session_log for tracking request latency
ALTER TABLE session_log ADD COLUMN IF NOT EXISTS response_time_ms INT;

-- Index for analytics queries on response time
CREATE INDEX IF NOT EXISTS idx_session_response_time ON session_log(student_id, response_time_ms DESC);
