$files = @("dashboard.html", "index.html")

$leadDaldali = @{
    slug = "daldali-coffee-paris"
    nome = "DALDALI | Café & Pâtisserie Coréenne"
    nicho = "Cafeteria & Pâtisserie"
    cidade = "Paris (9e / Pigalle)"
    nota = 4.9
    avaliacoes = 48
    email = "contact@daldali.fr"
    telefone = ""
    whatsapp = ""
    siteAntigo = $null
    motivo = "Cafeteria artesanal franco-coreana perto de Sacré-Cœur, atendimento intimista sem site próprio."
    status = "site_pronto"
    urlNova = "sites/daldali-coffee-paris/index.html"
    dataProposta = "2026-09-01"
    valor = 2400.0
    manutencao = 190.0
    pago = 0
    contratoStatus = "pendente"
    contratoEm = $null
    docCliente = $null
    endCliente = "23 Rue Marguerite de Rochechouart, 75009 Paris"
    obs = "Especialidade em Yakgwa de mel e matcha cerimonial. Estilo Super Travel Luxury com tema verde floresta das paredes do café."
}

$leadCafeShin = @{
    slug = "cafe-shin"
    nome = "Apocalypse Coffee Roasters | Café Shin"
    nicho = "Torrefação Especial & Grãos Orgânicos"
    cidade = "Superdesign Roastery"
    nota = 4.9
    avaliacoes = 62
    email = "contact@apocalypsecoffee.com"
    telefone = ""
    whatsapp = ""
    siteAntigo = "apocalypsecoffee.com"
    motivo = "Torrefação artesanal de cafés orgânicos especiais. Design de alta conversão importado via Superdesign."
    status = "site_pronto"
    urlNova = "sites/cafe-shin/index.html"
    dataProposta = "2026-09-01"
    valor = 2200.0
    manutencao = 180.0
    pago = 0
    contratoStatus = "pendente"
    contratoEm = $null
    docCliente = $null
    endCliente = "Online / Global Roastery"
    obs = "Design importado do Superdesign (Draft 5b241203-69b7-47f1-9fb2-c073f47850bf). Assinatura de café, notas sensoriais e rastreabilidade."
}

foreach ($f in $files) {
    if (Test-Path $f) {
        $html = Get-Content $f -Raw
        if ($html -match '<script id="dados" type="application/json">([\s\S]*?)</script>') {
            $jsonStr = $matches[1]
            $obj = $jsonStr | ConvertFrom-Json
            
            # Remove se ja existir
            $obj.leads = @($obj.leads | Where-Object { $_.slug -ne "daldali-coffee-paris" -and $_.slug -ne "cafe-shin" })
            
            $leadsList = [System.Collections.ArrayList]@($obj.leads)
            $leadsList.Insert(0, $leadCafeShin)
            $leadsList.Insert(1, $leadDaldali)
            $obj.leads = $leadsList
            $obj.atualizado = (Get-Date).ToString("yyyy-MM-dd HH:mm")
            
            $newJson = $obj | ConvertTo-Json -Depth 10 -Compress
            $newScript = '<script id="dados" type="application/json">' + $newJson + '</script>'
            $updatedHtml = $html -replace '<script id="dados" type="application/json">[\s\S]*?</script>', $newScript
            
            Set-Content -Path $f -Value $updatedHtml -Encoding UTF8
            Write-Host "OK: $f atualizado com Daldali e Cafe Shin!"
        }
    }
}
