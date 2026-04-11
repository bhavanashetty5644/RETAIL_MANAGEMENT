-- ══════════════════════════════════════════════════════════════════
-- RetailOS — RLS Policy Fix
-- Run this in Supabase SQL Editor if you are using the anon key
-- for writes, OR switch to the service_role key in .env (recommended)
-- ══════════════════════════════════════════════════════════════════

-- Allow all operations for authenticated service_role (already default)
-- These policies allow the anon key to do everything (use only if needed)

-- USERS table
create policy "allow_all_users" on users
  for all using (true) with check (true);

-- PRODUCTS table
create policy "allow_all_products" on products
  for all using (true) with check (true);

-- ORDERS table
create policy "allow_all_orders" on orders
  for all using (true) with check (true);

-- ── OR disable RLS entirely (simpler, fine for private/internal apps) ──
alter table users        disable row level security;
alter table products     disable row level security;
alter table orders       disable row level security;
alter table suppliers    disable row level security;
alter table procurement  disable row level security;
alter table sales        disable row level security;
alter table sale_items   disable row level security;

-- Grant usage on sequences so IDs increment correctly
grant usage, select on all sequences in schema public to service_role, anon, authenticated;
grant all on all tables in schema public to service_role, anon, authenticated;
