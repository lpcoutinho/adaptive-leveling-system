CREATE TABLE IF NOT EXISTS leveling_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    readiness_id UUID NOT NULL REFERENCES readiness_results(id) ON DELETE CASCADE,
    student_id VARCHAR(255) NOT NULL DEFAULT 'anonymous',
    explanations JSONB NOT NULL DEFAULT '[]',
    study_order JSONB NOT NULL DEFAULT '[]',
    total_gaps INT NOT NULL DEFAULT 0,
    total_completed INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(readiness_id)
);

CREATE INDEX IF NOT EXISTS idx_leveling_student ON leveling_plans(student_id);

COMMENT ON TABLE leveling_plans IS 'Planos de nivelamento personalizados';
COMMENT ON COLUMN leveling_plans.explanations IS 'Array JSON com explicações para cada gap';
COMMENT ON COLUMN leveling_plans.study_order IS 'Array JSON com ordem de estudo';
