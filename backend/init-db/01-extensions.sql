-- Initialize simFocus database
-- This script creates the database structure and seeds initial data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable text search for full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Note: Vector extension will be added in P2 when using pgvector-enabled PostgreSQL
-- Note: Tables are created automatically by SQLAlchemy
-- This file is for manual adjustments and data seeding
