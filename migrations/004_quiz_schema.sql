-- Tabela para sessões de quiz

CREATE TABLE IF NOT EXISTS quiz_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    student_id VARCHAR(255) NOT NULL DEFAULT 'anonymous',
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    answers JSONB NOT NULL DEFAULT '[]',
    total_score DOUBLE PRECISION DEFAULT 0.0,
    max_score DOUBLE PRECISION DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quiz_sessions_assessment ON quiz_sessions(assessment_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_student ON quiz_sessions(student_id);

COMMENT ON TABLE quiz_sessions IS 'Sessões de quiz dos estudantes';
COMMENT ON COLUMN quiz_sessions.answers IS 'Array JSON com respostas do aluno';
