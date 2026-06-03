-- Tabela para armazenar o grafo de conhecimento e pré-requisitos extraídos via LLM

CREATE TABLE IF NOT EXISTS prerequisites_graph (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pdf_id UUID NOT NULL UNIQUE REFERENCES pdf_documents(id) ON DELETE CASCADE,
    main_concepts JSONB NOT NULL,    -- Lista de conceitos principais (nome, desc, ids_pre)
    prerequisites JSONB NOT NULL,    -- Detalhamento dos pré-requisitos (nome, desc, importância, tópicos)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para busca rápida por PDF
CREATE INDEX IF NOT EXISTS idx_prerequisites_graph_pdf_id ON prerequisites_graph(pdf_id);

-- Comentários
COMMENT ON TABLE prerequisites_graph IS 'Armazena a inteligência extraída das aulas pelo LLM';
COMMENT ON COLUMN prerequisites_graph.main_concepts IS 'Estrutura JSON com os conceitos centrais da aula';
COMMENT ON COLUMN prerequisites_graph.prerequisites IS 'Estrutura JSON com os pré-requisitos e seus níveis de importância';
