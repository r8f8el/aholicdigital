$content = Get-Content 'C:\Users\rafae\.gemini\antigravity-ide\brain\b5361fdb-4d6b-4423-85cf-2f5285037eef\.system_generated\steps\59\content.md' -Raw

$pattern = 'data-doctor-name="([^"]+)"[\s\S]*?data-doctor-url="([^"]+)"[\s\S]*?data-eec-stars-rating=[''"]?(\d+)[''"]?[\s\S]*?data-eec-opinions-count=[''"]?(\d+)[''"]?'
$matches = [regex]::Matches($content, $pattern)

$results = foreach ($m in $matches) {
    [PSCustomObject]@{
        Nome = $m.Groups[1].Value.Trim()
        Url = $m.Groups[2].Value
        Nota = [double]$m.Groups[3].Value
        Avaliacoes = [int]$m.Groups[4].Value
    }
}

$results | Sort-Object -Property Avaliacoes -Descending | Out-String | Write-Host
