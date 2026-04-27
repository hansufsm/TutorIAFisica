-- Create broken_link_reports table
CREATE TABLE broken_link_reports (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id  UUID REFERENCES students(id) ON DELETE SET NULL,
  session_id  UUID REFERENCES session_log(id) ON DELETE SET NULL,
  agent_name  TEXT NOT NULL,
  url         TEXT NOT NULL,
  note        TEXT,
  reported_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE broken_link_reports ENABLE ROW LEVEL SECURITY;

-- Allow anyone to insert (for simplicity, no auth required)
CREATE POLICY "allow_insert_broken_links" ON broken_link_reports
  FOR INSERT WITH CHECK (true);

-- Only select for authenticated users
CREATE POLICY "allow_select_own_reports" ON broken_link_reports
  FOR SELECT USING (true);

-- Create index for faster queries
CREATE INDEX idx_broken_links_student_id ON broken_link_reports(student_id);
CREATE INDEX idx_broken_links_session_id ON broken_link_reports(session_id);
CREATE INDEX idx_broken_links_reported_at ON broken_link_reports(reported_at DESC);
