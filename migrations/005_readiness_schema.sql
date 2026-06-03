CREATE TABLE IF NOT EXISTS readiness_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    pdf_id UUID NOT NULL,
    overall_score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    level VARCHAR(20) NOT NULL DEFAULT 'needs_review',
    gaps JSONB NOT NULL DEFAULT '[]',
    strengths JSONB NOT NULL DEFAULT '[]',
    total_prerequisites INT NOT NULL DEFAULT 0,
    total_gaps INT NOT NULL DEFAULT 0,
    total_strengths INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id)
);

CREATE INDEX IF NOT EXISTS idx_readiness_pdf ON readiness_results(pdf_id);
CREATE INDEX IF NOT EXISTS idx_readiness_level ON readiness_results(level);

COMMENT ON TABLE readiness_results IS 'Resultados de análise de prontidão';
COMMENT ON COLUMN readiness_results.gaps IS 'Pré-requisitos com score abaixo do threshold';
COMMENT ON COLUMN readiness_results.strengths IS 'Pré-requisitos com score acima do threshold';
