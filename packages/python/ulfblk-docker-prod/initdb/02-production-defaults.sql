-- Production defaults for bloques ecosystem
-- Runs on first PostgreSQL container start

-- Statement timeout to prevent long-running queries (30 seconds)
ALTER DATABASE bloques_prod SET statement_timeout = '30s';

-- Default search path
ALTER DATABASE bloques_prod SET search_path TO public;

-- Lock timeout to prevent deadlock waits
ALTER DATABASE bloques_prod SET lock_timeout = '10s';

-- Idle transaction timeout
ALTER DATABASE bloques_prod SET idle_in_transaction_session_timeout = '60s';
