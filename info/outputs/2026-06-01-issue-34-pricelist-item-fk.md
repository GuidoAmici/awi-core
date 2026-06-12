# Issue #34 — price_list: rename category→tier + item_id FK

**Date:** 2026-06-01
**Repo:** GuidoAmici/newhaze-api
**Branch:** dev
**Agent:** Senior Developer (claude-sonnet-4-6)

## Changes delivered

### Migration
- `supabase/migrations/20260601_012_pricelist_item_fk.sql` — renames `price_list.category` to `tier`, adds nullable `item_id INT REFERENCES items(id)`

### C# (committed in single logical commit)
- `NewHaze.Api/DTOs/ErpSalesDto.cs`
  - `PriceListRow`: `Category` → `Tier`, added `ItemId int?`, added `Items PriceListItemRef?`
  - New nested class `PriceListItemRef { Category, Subcategory }` for the items JOIN
  - `PriceListEntryDto`: `Category` → `Tier`, added `ItemId int?`
- `NewHaze.Api/Services/ErpSupabaseClient.cs`
  - `GetLatestPricesAsync`: `select=*` → `select=*,items(category,subcategory)`
  - `GetPriceListAsync`: same select update, parameter renamed `category` → `tier`, filter uses `tier=eq.`
- `NewHaze.Api/Repositories/PriceListRepository.cs`
  - `Tier = r.Tier ?? "consumer"` (was `r.Category ?? "retail"`)
  - `ProductCategory = r.Items?.Category`
  - `ProductSubcategory = r.Items?.Subcategory`
- `NewHaze.Api/DTOs/PriceListItemDto.cs`
  - Added `ProductCategory string?` and `ProductSubcategory string?`

### Script
- `scripts/import_sheets.py` — `import_price_list()` uses key `"tier"` instead of `"category"` in the insert dict

### OpenAPI
- `docs/openapi/openapi.json`
  - `/api/PriceList` GET: 200 response now references `PriceListItemDto` array schema
  - Added `PriceListItemDto` component schema with `code`, `name`, `unitPrice`, `quantity`, `tier` (enum), `active`, `productCategory`, `productSubcategory`

## Commits
- `db286f3` feat(db): rename price_list.category → tier and add item_id FK
- `3b1aed9` feat(pricelist): rename Category→Tier, add ItemId FK and JOIN to items
- `494edb8` feat(pricelist): update import script and openapi spec for tier/item FK

## Out of scope (per brief)
- Data seed (issue #33)
- SET NOT NULL on item_id (after seed, issue #33)
- PriceListController / PriceListService changes
