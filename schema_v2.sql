-- ══════════════════════════════════════════════════════════════════════
--  RetailOS v2 — Supabase Schema
--  Run this ONCE in Supabase SQL Editor
-- ══════════════════════════════════════════════════════════════════════

-- USERS
create table if not exists users (
  id       bigserial primary key,
  name     text not null,
  email    text unique not null,
  password text not null,
  role     text not null default 'staff'
);

-- PRODUCTS
create table if not exists products (
  id       bigserial primary key,
  name     text not null,
  price    numeric(10,2) not null,
  quantity integer not null default 0,
  category text not null default 'General'
);

-- ORDERS (legacy single-product orders)
create table if not exists orders (
  id          bigserial primary key,
  product_id  bigint references products(id) on delete set null,
  quantity    integer not null,
  total_price numeric(10,2) not null,
  created_at  timestamptz not null default now()
);

-- SUPPLIERS
create table if not exists suppliers (
  id           bigserial primary key,
  name         text not null,
  contact_name text,
  email        text,
  phone        text,
  address      text,
  gstin        text,
  category     text default 'General',
  status       text default 'active',
  created_at   timestamptz not null default now()
);

-- PROCUREMENT (Purchase Orders)
create table if not exists procurement (
  id           bigserial primary key,
  supplier_id  bigint references suppliers(id) on delete set null,
  product_id   bigint references products(id) on delete set null,
  quantity     integer not null,
  unit_cost    numeric(10,2) not null,
  total_cost   numeric(10,2) not null,
  status       text not null default 'pending',
  po_number    text,
  notes        text,
  created_at   timestamptz not null default now(),
  received_at  timestamptz
);

-- SALES (multi-item sales with customer info)
create table if not exists sales (
  id               bigserial primary key,
  invoice_no       text unique not null,
  customer_name    text not null,
  customer_phone   text,
  customer_email   text,
  customer_address text,
  subtotal         numeric(10,2) not null default 0,
  discount         numeric(10,2) not null default 0,
  tax              numeric(10,2) not null default 0,
  total            numeric(10,2) not null default 0,
  payment_mode     text default 'cash',
  status           text default 'paid',
  notes            text,
  created_at       timestamptz not null default now()
);

-- SALE ITEMS (line items per sale)
create table if not exists sale_items (
  id           bigserial primary key,
  sale_id      bigint references sales(id) on delete cascade,
  product_id   bigint references products(id) on delete set null,
  product_name text not null,
  quantity     integer not null,
  unit_price   numeric(10,2) not null,
  total_price  numeric(10,2) not null
);

-- ── RLS: Enable but allow service_role key to bypass ──────────────────
-- The app uses the service_role key which bypasses RLS automatically.
-- These tables have RLS enabled but no restrictive policies,
-- so the service_role key has full access.
alter table users        enable row level security;
alter table products     enable row level security;
alter table orders       enable row level security;
alter table suppliers    enable row level security;
alter table procurement  enable row level security;
alter table sales        enable row level security;
alter table sale_items   enable row level security;

-- ── Sample Data ───────────────────────────────────────────────────────
insert into suppliers (name, contact_name, email, phone, category) values
  ('AgroTrade Pvt Ltd', 'Ramesh Kumar',  'ramesh@agrotrade.in',  '9845001234', 'Groceries'),
  ('FreshFarms Supply', 'Sunita Reddy',  'sunita@freshfarms.in', '9876543210', 'Groceries'),
  ('Metro Wholesale',   'Ajay Sharma',   'ajay@metro.in',        '9900112233', 'General')
on conflict do nothing;

insert into products (name, price, quantity, category) values
  ('Basmati Rice 5kg',  350.00, 48, 'Groceries'),
  ('Cooking Oil 1L',    120.00, 30, 'Groceries'),
  ('Wheat Flour 10kg',  300.00, 22, 'Groceries'),
  ('Sugar 1kg',          65.00, 15, 'Groceries'),
  ('Toor Dal 1kg',      150.00, 60, 'Groceries'),
  ('Milk 1L',            65.00,  8, 'Dairy'),
  ('Biscuits 100g',      20.00, 80, 'Snacks'),
  ('Soap 100g',          40.00, 45, 'Personal Care')
on conflict do nothing;

-- ── Superadmin account ────────────────────────────────────────────────────
-- Email: admin@gmail.com | Password: admin123
-- This uses a fixed salt so the hash is deterministic and reproducible.
insert into users (name, email, password, role) values
  ('Super Admin', 'admin@gmail.com',
   'retailos_superadmin_salt_2024:d195be03d07f6b3293dca8a5c226e2874eede4c0d35bea9c964f549d574b233c',
   'superadmin')
on conflict (email) do update set
  password = 'retailos_superadmin_salt_2024:d195be03d07f6b3293dca8a5c226e2874eede4c0d35bea9c964f549d574b233c',
  role = 'superadmin',
  name = 'Super Admin';
