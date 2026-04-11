# RetailOS v2 — Smart Retail Management

## Quick Start

1. Set up Supabase — create a project and run `schema_v2.sql` in the SQL Editor
2. Fill in `.env` with your Supabase URL and service key
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python app.py`
5. Open: http://127.0.0.1:5000

## Superadmin Account

| Field    | Value            |
|----------|------------------|
| Email    | admin@gmail.com  |
| Password | admin123         |
| Role     | superadmin       |

The superadmin account is created by `schema_v2.sql`. Run it once in Supabase SQL Editor.

## Role Hierarchy

| Role       | Capabilities                                                    |
|------------|-----------------------------------------------------------------|
| superadmin | Full access — manages all admins & staff, promote/demote users  |
| admin      | Manages staff only — can add/edit/delete staff users            |
| staff      | Operational access — products, orders, suppliers, procurement   |

## Fixes in This Version

- **Modal forms now fully interactive** — Fixed CSS z-index stacking that prevented typing in modal inputs (suppliers, products, orders)
- **Superadmin role** — `admin@gmail.com / admin123` has superadmin powers
- **Promote/Demote** — Superadmin can promote staff → admin or demote admin → staff
- **Admin scope** — Admins can only manage staff, not other admins
- **Faster navigation** — DB cache TTL increased from 20s → 60s for snappier page loads
