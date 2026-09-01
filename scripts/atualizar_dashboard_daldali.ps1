$files = @("dashboard.html", "index.html")

$novoLead = @{
    slug = "daldali-coffee-paris"
    nome = "DALDALI • Café & Pâtisserie Coréenne"
    nicho = "Coffee Shop & Pâtisserie"
    cidade = "Paris (França)"
    nota = 4.9
    avaliacoes = 48
    email = "contact@daldaliparis.com"
    telefone = "+33 1 40 00 00 00"
    whatsapp = "https://instagram.com/daldali_paris"
    siteAntigo = $null
    motivo = "Criação do Primeiro Site Oficial (Super Travel Luxury • Pigalle / Paris 9e)"
    status = "redesenhado"
    urlNova = "sites/daldali-coffee-paris/index.html"
    dataProposta = "2026-09-01"
    valor = 2800.0
    manutencao = 250.0
    pago = 0
    contratoStatus = "pendente"
    contratoEm = $null
    docCliente = $null
    endCliente = "23 Rue Marguerite de Rochechouart, 75009 Paris, France"
    obs = "Café de especialidade e doces coreanos artesanais (Yakgwa ao mel, Matcha e Banana Latte). Avaliação 4.9★ no Google Maps. Sem site próprio (apenas Instagram @daldali_paris)."
    direcaoCriativa = @{
        presetId = "super-travel-luxury"
        presetNome = "Super Travel Luxury"
        composicao = "stagger-grid-asymmetric-100px"
        tipografia = @{
            display = "League Spartan (Black 900) + Playfair Itálico"
            body = "League Spartan (Regular 400-500)"
        }
        paleta = @{
            estilo = "rose-sand-charcoal"
            sugestoes = @{
                fundo = "#fdf8f3"
                superficie = "#f5f0eb"
                texto = "#262626"
                acento = "#e4a4bd"
                acento_secundario = "#c8809c"
            }
        }
        justificativa = "Design editorial de alta-costura (estilo Karla Barros), com League Spartan 900, paleta rose/areia, Stagger Grid com offset de 100px, selo 4.9★ flutuante de concierge e cardápio de especialidades."
        data = "2026-09-01"
        status = "direcao_definida"
    }
    versoes = @(
        @{
            numero = 1
            nome_estilo = "Super Travel Luxury (Parisien & Séoul)"
            descricao = "Design System Super Travel Luxury com League Spartan 900, paleta rose linho (#fdf8f3 e #e4a4bd), Stagger Grid 100px e selo 4.9★ flutuante"
            arquivo = "sites/daldali-coffee-paris/index.html"
            criado_em = "2026-09-01 17:56"
            ativo = 1
        }
    )
}

foreach ($f in $files) {
    if (Test-Path $f) {
        $html = Get-Content $f -Raw
        if ($html -match '<script id="dados" type="application/json">([\s\S]*?)</script>') {
            $jsonStr = $matches[1]
            $obj = $jsonStr | ConvertFrom-Json
            
            $obj.leads = @($obj.leads | Where-Object { $_.slug -ne "daldali-coffee-paris" })
            
            $leadsList = [System.Collections.ArrayList]@($obj.leads)
            $leadsList.Insert(0, $novoLead)
            $obj.leads = $leadsList
            $obj.atualizado = (Get-Date).ToString("yyyy-MM-dd HH:mm")
            
            $newJson = $obj | ConvertTo-Json -Depth 10 -Compress
            $newScript = '<script id="dados" type="application/json">' + $newJson + '</script>'
            $updatedHtml = $html -replace '<script id="dados" type="application/json">[\s\S]*?</script>', $newScript
            
            Set-Content -Path $f -Value $updatedHtml -Encoding UTF8
            Write-Host "OK: $f atualizado com Daldali Paris!"
        }
    }
}
