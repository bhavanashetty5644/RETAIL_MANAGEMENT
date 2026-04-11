-- ── RetailOS Supabase Schema ─────────────────────────────────────────────────
-- Run this in your Supabase SQL Editor ONCE before starting the app.

create table if not exists users (
  id       bigserial primary key,
  name     text not null,
  email    text unique not null,
  password text not null,
  role     text not null default 'staff'  -- 'admin' or 'staff'
);

create table if not exists products (
  id       bigserial primary key,
  name     text not null,
  price    numeric(10,2) not null,
  quantity integer not null default 0,
  category text not null default 'General'
);

create table if not exists orders (
  id          bigserial primary key,
  product_id  bigint references products(id) on delete set null,
  quantity    integer not null,
  total_price numeric(10,2) not null,
  created_at  timestamptz not null default now()
);

-- RLS: service_role key bypasses all RLS, so this is safe
alter table users     enable row level security;
alter table products  enable row level security;
alter table orders    enable row level security;

-- ── IMPORTANT: Create your first admin user ───────────────────────────────────
-- After running the app, go to /register and create an account with role=admin.
-- OR insert manually with a hashed password (run hash_password.py to generate).

-- Sample products (optional)
insert into products (name, price, quantity, category) values
  ('Basmati Rice 5kg',  350.00, 48, 'Groceries'),
  ('Cooking Oil 1L',    120.00,  3, 'Groceries'),
  ('Wheat Flour 10kg',  300.00, 22, 'Groceries'),
  ('Sugar 1kg',          65.00,  2, 'Groceries'),
  ('Toor Dal 1kg',      150.00, 60, 'Groceries')
on conflict do nothing;
