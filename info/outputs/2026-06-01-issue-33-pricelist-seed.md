# Issue 33 — price_list seed: item_id resolution and tier mapping

**Date:** 2026-06-01
**Branch:** dev
**Repo:** GuidoAmici/newhaze-api
**Commit:** `feat(import): resolve item_id and map tier categories in import_price_list`

## What changed in `scripts/import_sheets.py`

### 1. `TIER_MAP` module-level constant (after config block)

Added a translation dict that converts Spanish category names from the Excel sheet to the English `tier` enum values expected by the DB:

```python
TIER_MAP = {
    "Consumidor":   "consumer",
    "Growshop":     "retailer",
    "Distribuidor": "wholesaler",
}
```

### 2. `import_price_list()` — tier mapping

Replaced `r.get("Category") or None` with:

```python
TIER_MAP.get(r.get("Category", ""), r.get("Category") or None)
```

This maps known Spanish values to English; unknown values fall through as-is (no silent data loss).

### 3. `import_price_list()` — item_id resolution

After building the `rows` list, the function now:
- Fetches all items from `/rest/v1/items?select=id,name` via Supabase REST (skipped in DRY_RUN)
- Builds a `name → id` lookup dict
- Pops `item_name` from each row and sets `item_id` via the lookup
- Prints a warning listing the first 10 unmatched names if any rows have no match

The `item_name` key is never sent to Supabase — only `item_id` is included in the insert payload.

## Pending — manual execution required

The Excel file must be locally accessible before running the script.

### Staging (stg — `rpgoixcgwynerezrxqhx`)

```bash
SUPABASE_URL=https://rpgoixcgwynerezrxqhx.supabase.co \
SUPABASE_SERVICE_KEY=<stg_service_role_key> \
SHEETS_DIR="D:/Descargas/New Haze DBs" \
python3 scripts/import_sheets.py --only price_list
```

Verify:
- Total rows: ~1995
- `SELECT COUNT(*) FROM price_list WHERE item_id IS NULL` → 0
- `SELECT DISTINCT tier FROM price_list` → only `consumer`, `retailer`, `wholesaler`, null

### Production (prod — `rbszzkivswvqagasrvdj`)

Same command with prod URL and key, after stg verification passes.

### Post-migration (after prod verification)

```sql
ALTER TABLE price_list ALTER COLUMN item_id SET NOT NULL;
```
