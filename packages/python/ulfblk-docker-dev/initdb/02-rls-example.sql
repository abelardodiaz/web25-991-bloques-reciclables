-- Example RLS setup matching bloque-multitenant patterns
-- See: bloque_multitenant/rls/setup.py:generate_rls_sql()
--
-- This creates a demo table with RLS enabled using the
-- current_setting('app.current_tenant', true) pattern.
-- Adapt this for your own tables.

-- Demo table
CREATE TABLE IF NOT EXISTS demo_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS on demo_items
ALTER TABLE demo_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE demo_items FORCE ROW LEVEL SECURITY;

-- Policy: only show rows matching current tenant
CREATE POLICY tenant_isolation ON demo_items
    USING (tenant_id::text = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id::text = current_setting('app.current_tenant', true));
