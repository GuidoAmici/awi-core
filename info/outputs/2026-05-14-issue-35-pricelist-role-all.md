# Issue #35 — PriceList role=all fix

**Date:** 2026-05-14  
**Branch:** dev  
**Files changed:** 2

## Changes

### `NewHaze.Api/Controllers/PriceListController.cs`
1. Added `"all"` to `ValidRoles[]` (line 18)
2. Changed `ValidRoles.Contains(role)` → `ValidRoles.Contains(role, StringComparer.OrdinalIgnoreCase)` (case-insensitive matching)
3. Updated XML docstring to include `"all"` in valid roles list

### `docs/openapi/openapi.json`
- Added `enum: ["all", "retail", "wholesale", "distributor"]` to the `role` query parameter schema.
- Note: `dotnet` is not available in this environment — the spec was updated manually to reflect the new valid values. A full Swashbuckle regeneration should be done on the next dev machine with dotnet installed.

## Scope self-check

- Touched only `PriceListController.cs` and `openapi.json` — the two files specified in the task
- Did NOT touch `PriceListService.cs`, any other controller, or any test files
- No refactors, no enum extraction, no abstractions

## Diff summary
- Controller: 3 lines changed (ValidRoles array, docstring, Contains call)
- OpenAPI: 1 line added (enum field)
