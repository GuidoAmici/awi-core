$ts = [int](Get-Date -UFormat %s)
$adminEmail = "admin$ts@newhaze.ar"
$adminPass = "Test1234!"
$body = '{"email":"' + $adminEmail + '","password":"' + $adminPass + '","role":"consumer"}'
Write-Host "Body: $body"
Write-Host "Timestamp: $ts"
