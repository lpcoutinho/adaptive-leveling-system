-- Tabela para armazenar avaliações diagnósticas geradas via LLM

CREATE TABLE IF NOT EXISTS assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pdf_id UUID NOT NULL UNIQUE REFERENCES pdf_documents(id) ON DELETE CASCADE,
    questions JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para busca rápida por PDF
CREATE INDEX IF NOT EXISTS idx_assessments_pdf_id ON assessments(pdf_id);

-- Comentários
COMMENT ON TABLE assessments IS 'Armazena avaliações diagnósticas geradas pelo LLM';
COMMENT ON COLUMN assessments.questions IS 'Estrutura JSON com array de questões (QuizQuestion[])';
