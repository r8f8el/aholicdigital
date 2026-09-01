$files = @(
    @{ Nome = "Lucas Aguiar"; Path = "C:\Users\rafae\.gemini\antigravity-ide\brain\b5361fdb-4d6b-4423-85cf-2f5285037eef\.system_generated\steps\121\content.md"; Especialidade = "Nutrição Esportiva, Hipertrofia & Emagrecimento" },
    @{ Nome = "Dra. Carolina Bessa"; Path = "C:\Users\rafae\.gemini\antigravity-ide\brain\b5361fdb-4d6b-4423-85cf-2f5285037eef\.system_generated\steps\123\content.md"; Especialidade = "Nutrição Clínica, Saúde da Mulher & Emagrecimento" },
    @{ Nome = "Dra. Ana Beatriz Carneiro"; Path = "C:\Users\rafae\.gemini\antigravity-ide\brain\b5361fdb-4d6b-4423-85cf-2f5285037eef\.system_generated\steps\125\content.md"; Especialidade = "Nutrição Materno-Infantil, Introdução Alimentar & Família" },
    @{ Nome = "Priscila Mustafa"; Path = "C:\Users\rafae\.gemini\antigravity-ide\brain\b5361fdb-4d6b-4423-85cf-2f5285037eef\.system_generated\steps\127\content.md"; Especialidade = "Reeducação Alimentar, Nutrição Comportamental & Longevidade" },
    @{ Nome = "Luana Abreu"; Path = "C:\Users\rafae\.gemini\antigravity-ide\brain\b5361fdb-4d6b-4423-85cf-2f5285037eef\.system_generated\steps\136\content.md"; Especialidade = "Nutrição Clínica, Emagrecimento & Desempenho" }
)

foreach ($f in $files) {
    $txt = Get-Content $f.Path -Raw
    $opinions = if ($txt -match 'data-eec-opinions-count=[''"]?(\d+)[''"]') { $matches[1] } else { "N/A" }
    $rating = if ($txt -match 'data-eec-stars-rating=[''"]?(\d+)[''"]') { $matches[1] } else { "5" }
    
    $phones = [regex]::Matches($txt, '(\(?85\)?\s?9?\d{4}[-\s]?\d{4})') | ForEach-Object { $_.Value } | Select-Object -Unique
    $phoneDisplay = if ($phones) { $phones[0] } else { "A consultar" }
    
    Write-Host "[$($f.Nome)] | Nota: $rating.0 ★ | Avaliações: $opinions | Tel/WhatsApp: $phoneDisplay | Especialidade: $($f.Especialidade)"
}
