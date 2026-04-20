[System.Environment]::GetEnvironmentVariables('User').GetEnumerator() |
    Where-Object { $_.Key -like '*Supabase*' -or $_.Key -like '*supabase*' } |
    Select-Object Key, Value | Format-Table -AutoSize
