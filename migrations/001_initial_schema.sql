-- Schema inicial para o Adaptive Leveling System

-- Habilitar extensão para UUID se não existir
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tabela para armazenar metadados de documentos PDF
CREATE TABLE IF NOT EXISTS pdf_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hash VARCHAR(64) UNIQUE NOT NULL,           -- SHA-256 do arquivo para idempotência
    filename VARCHAR(255) NOT NULL,             -- Nome original do arquivo
    size BIGINT NOT NULL,                        -- Tamanho em bytes
    bucket_key VARCHAR(500) NOT NULL,           -- Caminho/Key no S3/Minio
    content_text TEXT,                           -- Texto extraído (opcional, se couber no DB)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para busca rápida
CREATE INDEX IF NOT EXISTS idx_pdf_documents_hash ON pdf_documents(hash);

-- Comentários da tabela
COMMENT ON TABLE pdf_documents IS 'Metadados dos PDFs processados pelo sistema';
COMMENT ON COLUMN pdf_documents.hash IS 'Hash SHA-256 para evitar reprocessamento do mesmo arquivo';
