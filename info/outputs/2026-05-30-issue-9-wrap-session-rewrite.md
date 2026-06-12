# wrap-session SKILL.md rewrite — 2026-05-30

**Issue:** GuidoAmici/rabbitek-workspace#9

## Changes applied

- Title: hyphen → em-dash (`— End of Session`)
- Opening: added "in strict order" and note not to print progress during Step 1
- Step 1a: added `bash .claude/hooks/get-datetime.sh full` call
- Step 1b: added "Build a list of touched org names. The org name is the repo prefix before `-workspace`."
- Reordered sub-steps: inference file (1c) now runs **before** user daily (1d) and org daily (1e)
- Step 1f: added "Only create outputs files for content that was actually produced, not for the session log itself."
- Step 2: removed ✓ emoji prefix from example lines; added outputs example line
- Step 5: "Do NOT dump a list" → "Do not dump a markdown list. Do not use free-form text. One call per item, wait for a response before asking the next."
- Step 5: "If nothing unsaved: say so in one line and skip this step" → "If nothing is unsaved, say so in one line and stop."
