CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pdf_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    current_node VARCHAR(50) DEFAULT '',
    state JSONB NOT NULL DEFAULT '{}',
    progress DOUBLE PRECISION DEFAULT 0.0,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workflow_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_pdf ON workflow_executions(pdf_id);

COMMENT ON TABLE workflow_executions IS 'Execuções de workflow LangGraph';
COMMENT ON COLUMN workflow_executions.state IS 'Snapshot do GraphState em JSON';
