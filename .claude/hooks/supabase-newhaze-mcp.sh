#!/bin/bash
# Compatibilidad: el mcp.json de New Haze llama a este nombre. El puente es
# supabase-mcp.sh, que recibe la variable de Windows donde vive el token.
exec bash "$(dirname "$0")/supabase-mcp.sh" NewHaze_Supabase_Challenger_full_access
