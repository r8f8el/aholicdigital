$txt = Get-Content 'C:\Users\rafae\.gemini\antigravity-ide\brain\b5361fdb-4d6b-4423-85cf-2f5285037eef\.system_generated\steps\121\content.md' -Raw

Write-Host "=== FOTOS ENCONTRADAS ==="
$imgMatches = [regex]::Matches($txt, 'https://[^\s"'']+\.(?:jpg|jpeg|png)')
$uniqueImgs = $imgMatches | ForEach-Object { $_.Value } | Select-Object -Unique
foreach ($img in $uniqueImgs) {
    Write-Host $img
}

Write-Host "`n=== SOBRE / APRESENTACAO ==="
if ($txt -match 'data-object-type="doctor"[\s\S]*?<div class="[^"]*text-muted[^"]*">([\s\S]*?)</div>') {
    $clean = ($matches[1] -replace '<[^>]+>', ' ').Trim()
    Write-Host $clean
}

Write-Host "`n=== ENDERECO ==="
if ($txt -match 'itemprop="streetAddress">([^<]+)<') { Write-Host "RUA: $($matches[1].Trim())" }
if ($txt -match 'itemprop="addressLocality">([^<]+)<') { Write-Host "LOCAL: $($matches[1].Trim())" }

Write-Host "`n=== DEPOIMENTOS REAIS ==="
$comments = [regex]::Matches($txt, 'data-test-id="opinion-comment-text">([\s\S]*?)</div>')
for ($i = 0; $i -lt [Math]::Min(5, $comments.Count); $i++) {
    $c = ($comments[$i].Groups[1].Value -replace '<[^>]+>', ' ').Trim()
    Write-Host "• Depoimento $($i+1): $c"
}
