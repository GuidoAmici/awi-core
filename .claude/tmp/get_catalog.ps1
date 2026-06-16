$token = [System.Environment]::GetEnvironmentVariable('META_ACCESS_TOKEN', 'User')
if (-not $token) { $token = $env:META_ACCESS_TOKEN }

$bizId = "328953658013053"

Write-Output "=== WhatsApp Business Accounts ==="
$r = Invoke-WebRequest -Uri "https://graph.facebook.com/v25.0/$bizId/whatsapp_business_accounts?access_token=$token" -UseBasicParsing
Write-Output $r.Content

Write-Output "`n=== Commerce accounts ==="
$r2 = Invoke-WebRequest -Uri "https://graph.facebook.com/v25.0/$bizId/commerce_merchant_settings?access_token=$token" -UseBasicParsing
Write-Output $r2.Content
