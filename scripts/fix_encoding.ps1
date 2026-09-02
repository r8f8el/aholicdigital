# Script de correcao de codificacao Mojibake (UTF-8 lido como Windows-1252)
$cp1252Map = @{
    8364 = 0x80; 8218 = 0x82; 402  = 0x83; 8222 = 0x84; 8230 = 0x85; 8224 = 0x86; 8225 = 0x87;
    710  = 0x88; 8240 = 0x89; 352  = 0x8A; 8249 = 0x8B; 338  = 0x8C; 381  = 0x8E;
    8216 = 0x91; 8217 = 0x92; 8220 = 0x93; 8221 = 0x94; 8226 = 0x95; 8211 = 0x96; 8212 = 0x97;
    732  = 0x98; 8482 = 0x99; 353  = 0x9A; 8250 = 0x9B; 339  = 0x9C; 382  = 0x9E; 376  = 0x9F;
}

function Fix-Text([string]$text) {
    if ([string]::IsNullOrEmpty($text)) { return $text }
    
    # Check if there are mojibake sequences
    # Specifically: character 195 (Ã) followed by 128..191, or 226 (â) followed by cp1252/latin1, or 240 (ð) followed by 159 (Ÿ)
    $hasMojibake = $false
    $chars = $text.ToCharArray()
    for ($i = 0; $i -lt $chars.Length - 1; $i++) {
        $c1 = [int]$chars[$i]
        $c2 = [int]$chars[$i+1]
        if ($c1 -eq 195 -or $c1 -eq 194 -or $c1 -eq 226 -or ($c1 -eq 240 -and $c2 -eq 376)) {
            $hasMojibake = $true
            break
        }
    }
    
    if (-not $hasMojibake) { return $text }

    # Attempt to decode
    try {
        $bytes = [System.Collections.Generic.List[byte]]::new()
        foreach ($ch in $chars) {
            $code = [int]$ch
            if ($cp1252Map.ContainsKey($code)) {
                $bytes.Add($cp1252Map[$code])
            } elseif ($code -le 255) {
                $bytes.Add([byte]$code)
            } else {
                # Untouched unicode character
                $sub = [System.Text.Encoding]::UTF8.GetBytes($ch.ToString())
                $bytes.AddRange($sub)
            }
        }
        
        $utf8Str = [System.Text.Encoding]::UTF8.GetString($bytes.ToArray())
        return $utf8Str
    } catch {
        return $text
    }
}

# Scan files
$targetFiles = @(
    "index.html",
    "dashboard.html",
    "leads.md"
)

# Also check sites/**/*.html
$siteFiles = Get-ChildItem -Path "sites" -Recurse -Filter "*.html" -ErrorAction SilentlyContinue
foreach ($sf in $siteFiles) {
    $targetFiles += $sf.FullName
}

Write-Output "Iniciando correcao de codificacao..."

$fixedCount = 0
foreach ($relPath in $targetFiles) {
    $fullPath = if ([System.IO.Path]::IsPathRooted($relPath)) { $relPath } else { Join-Path (Get-Location) $relPath }
    if (Test-Path $fullPath) {
        $raw = [System.IO.File]::ReadAllText($fullPath, [System.Text.Encoding]::UTF8)
        $fixed = Fix-Text $raw
        if ($fixed -ne $raw) {
            [System.IO.File]::WriteAllText($fullPath, $fixed, [System.Text.Encoding]::UTF8)
            Write-Output "[CORRIGIDO] $relPath"
            $fixedCount++
        } else {
            Write-Output "[OK / SEM MOJIBAKE] $relPath"
        }
    }
}

Write-Output "Concluido! Total de arquivos corrigidos: $fixedCount"
