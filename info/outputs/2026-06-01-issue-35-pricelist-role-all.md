# issue-35: fix PriceListController ValidRoles

**Date:** 2026-06-01  
**Repo:** GuidoAmici/newhaze-api  
**Employee:** minimal-change-engineer  
**Status:** already applied — no new changes needed

## Finding

All three changes from the agent brief were already committed in a prior session:

- Commit: `a1b7712 fix: corregir ValidRoles a consumer/retailer/wholesaler/all`
- Branch: `dev`

### State of PriceListController.cs

```csharp
private static readonly string[] ValidRoles = ["consumer", "retailer", "wholesaler", "all"];

/// <summary>Obtiene la lista de precios filtrada por rol (consumer, retailer, wholesaler, all)</summary>
// ...
if (!ValidRoles.Contains(role, StringComparer.OrdinalIgnoreCase))
```

All acceptance criteria from the brief are met in the committed code.

## Pending

- `docs/openapi/openapi.json` regeneration requires the PowerShell script (`scripts/generate-openapi.ps1`) — must be run from Windows/PowerShell environment.
- PR `dev → stg` not yet opened.
