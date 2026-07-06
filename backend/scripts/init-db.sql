-- ===========================
-- DealOS AI — Database Initialization
-- ===========================
-- This script runs once when the PostgreSQL container is first created.
-- It enables required extensions before Alembic migrations run.

-- Enable pgvector for embedding storage and similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for fuzzy text matching (used by BM25 fallback)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable uuid-ossp for UUID generation at the database level
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
