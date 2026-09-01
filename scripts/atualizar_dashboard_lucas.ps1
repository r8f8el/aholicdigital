$files = @("dashboard.html", "index.html")

$novoLead = @{
    slug = "lucas-aguiar-nutri"
    nome = "Lucas Aguiar | Nutrição Clínica & Comportamental"
    nicho = "Nutrição Clínica & Esportiva"
    cidade = "Fortaleza"
    nota = 5.0
    avaliacoes = 56
    email = "contato@lucasaguiarnutri.com.br"
    telefone = "(85) 98211-9199"
    whatsapp = "5585982119199"
    siteAntigo = $null
    motivo = "Criação do Primeiro Site Oficial (Lumina Luxury Editorial • Clínica MENTA / Fortaleza)"
    status = "redesenhado"
    urlNova = "sites/lucas-aguiar-nutri/index.html"
    dataProposta = "2026-09-01"
    valor = 1900.0
    manutencao = 150.0
    pago = 0
    contratoStatus = "pendente"
    contratoEm = $null
    docCliente = $null
    endCliente = "Clínica MENTA, Fortaleza - CE"
    obs = "Mestre em Saúde Coletiva UNIFOR, Pós Albert Einstein, Especialista AMBULIM/USP. Best Quality Doctoralia 2024 e 2025. CRN11 19551."
    direcaoCriativa = @{
        presetId = "lumina-architecture-luxury"
        presetNome = "Lumina Architecture | Luxury & Refined"
        composicao = "sculptural-architectural-catalog"
        tipografia = @{
            display = "Cinzel (Bold 700 / 900)"
            body = "Plus Jakarta Sans + JetBrains Mono"
        }
        paleta = @{
            estilo = "deep-obsidian-travertine-champagne"
            sugestoes = @{
                fundo = "#0B0C0E"
                superficie = "#131518"
                texto = "#F5F2EB"
                acento = "#C5A880"
                acento_secundario = "#10B981"
            }
        }
        justificativa = "Design dark luxury de alta autoridade científica com tipografia Cinzel, fotos reais do consultório na Clínica MENTA, diagnóstico prévio interativo e avaliações 5.0★ verificadas."
        data = "2026-09-01"
        status = "direcao_definida"
    }
    versoes = @(
        @{
            numero = 1
            nome_estilo = "Lumina Luxury Editorial"
            descricao = "Landing Page de alta conversão em dark luxury obsidian e champagne, fotos reais, credenciais UNIFOR/Einstein/USP e diagnóstico interativo"
            arquivo = "sites/lucas-aguiar-nutri/index.html"
            criado_em = "2026-09-01 11:08"
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
            
            # Remove se já existir para atualizar
            $obj.leads = @($obj.leads | Where-Object { $_.slug -ne "lucas-aguiar-nutri" })
            
            # Adiciona no topo ou lista
            $leadsList = [System.Collections.ArrayList]@($obj.leads)
            $leadsList.Insert(0, $novoLead)
            $obj.leads = $leadsList
            $obj.atualizado = (Get-Date).ToString("yyyy-MM-dd HH:mm")
            
            $newJson = $obj | ConvertTo-Json -Depth 10 -Compress
            $newScript = '<script id="dados" type="application/json">' + $newJson + '</script>'
            $updatedHtml = $html -replace '<script id="dados" type="application/json">[\s\S]*?</script>', $newScript
            
            Set-Content -Path $f -Value $updatedHtml -Encoding UTF8
            Write-Host "OK: $f atualizado com Lucas Aguiar!"
        }
    }
}
