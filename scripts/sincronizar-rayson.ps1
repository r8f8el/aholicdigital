$supabaseUrl = "https://gpignxwsxfbkelckrebd.supabase.co"
$supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdwaWdueHdzeGZia2VsY2tyZWJkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc4NjQ3OTcsImV4cCI6MjEwMzQ0MDc5N30.Ex2iAC0VoW9svg2rMKNwWU9rYz5FNTQaz6qa9GL97tU"

$headers = @{
    "apikey" = $supabaseKey
    "Authorization" = "Bearer $supabaseKey"
    "Content-Type" = "application/json"
    "Prefer" = "resolution=merge-duplicates"
}

# 1. Inserir Lead no Supabase
$leadPayload = @{
    "slug" = "rayson-mendes-nutri"
    "nome" = "Rayson Mendes | Nutricionista Esportivo"
    "nicho" = "Nutrição Esportiva & Performance"
    "cidade" = "Catalão"
    "nota" = 5.0
    "avaliacoes" = 30
    "email" = "raysonmendesnutri@hotmail.com"
    "telefone" = "(64) 99957-5323"
    "whatsapp" = "5564999575323"
    "site_antigo" = $null
    "motivo" = "Criação do Primeiro Site Oficial (Modern Organic Editorial • Catalão / Davinópolis)"
    "status" = "redesenhado"
    "url_nova" = "sites/rayson-mendes-nutri/index.html"
    "data_proposta" = "2026-08-30"
    "valor" = 1800.0
    "manutencao" = 150.0
    "pago" = 0
    "contrato_status" = "pendente"
    "contrato_em" = $null
    "doc_cliente" = $null
    "end_cliente" = "Catalão - GO / Davinópolis - GO"
    "obs" = "Nutrição Esportiva Personalizada, Emagrecimento, Hipertrofia, BJJ e Performance. Atendimento presencial e online. Instagram @raysonmendesnutri com 4.8k seguidores."
    "direcao_criativa" = @{
        "presetId" = "modern-organic-editorial"
        "presetNome" = "Modern Organic Editorial"
        "composicao" = "warm-editorial-lifestyle"
        "tipografia" = @{
            "display" = "Plus Jakarta Sans 800 + Playfair Display Itálico"
            "body" = "Plus Jakarta Sans 400"
        }
        "paleta" = @{
            "estilo" = "dark-moss-olive-warm-sand"
            "sugestoes" = @{
                "fundo" = "#0D140F"
                "superficie" = "#15201A"
                "texto" = "#F4F6F0"
                "acento" = "#22C55E"
                "acento_secundario" = "#84CC16"
            }
        }
        "justificativa" = "Design editorial moderno e acolhedor para nutrição esportiva e alta performance com fotos reais do consultório, bio do Instagram e integração WhatsApp direta."
        "data" = "2026-08-30"
        "status" = "direcao_definida"
    }
} | ConvertTo-Json -Depth 10

try {
    $resLead = Invoke-RestMethod -Uri "$supabaseUrl/rest/v1/leads?on_conflict=slug" -Method Post -Headers $headers -Body $leadPayload
    Write-Host "✅ Lead Rayson Mendes inserido/sincronizado no Supabase Nuvem!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao inserir lead no Supabase: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Inserir Versão no Supabase
$versaoPayload = @{
    "lead_slug" = "rayson-mendes-nutri"
    "numero" = 1
    "nome_estilo" = "Modern Organic Editorial"
    "descricao" = "Layout lifestyle de alta conversão para nutrição esportiva com fotos reais do Instagram/Maps, seções de metodologia, planos e WhatsApp"
    "arquivo" = "sites/rayson-mendes-nutri/index.html"
    "criado_em" = "2026-08-30 15:04"
    "ativo" = 1
} | ConvertTo-Json -Depth 5

try {
    $resVersao = Invoke-RestMethod -Uri "$supabaseUrl/rest/v1/versoes_site?on_conflict=lead_slug,numero" -Method Post -Headers $headers -Body $versaoPayload
    Write-Host "✅ Versão do site registrada no Supabase Nuvem!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao inserir versão no Supabase: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Atualizar dashboard.html e index.html
$leadDash = @{
    "slug" = "rayson-mendes-nutri"
    "nome" = "Rayson Mendes | Nutricionista Esportivo"
    "nicho" = "Nutrição Esportiva & Performance"
    "cidade" = "Catalão"
    "nota" = 5.0
    "avaliacoes" = 30
    "email" = "raysonmendesnutri@hotmail.com"
    "telefone" = "(64) 99957-5323"
    "whatsapp" = "5564999575323"
    "siteAntigo" = $null
    "motivo" = "Criação do Primeiro Site Oficial (Modern Organic Editorial • Catalão / Davinópolis)"
    "status" = "redesenhado"
    "urlNova" = "sites/rayson-mendes-nutri/index.html"
    "dataProposta" = "2026-08-30"
    "valor" = 1800.0
    "manutencao" = 150.0
    "pago" = 0
    "contratoStatus" = "pendente"
    "contratoEm" = $null
    "docCliente" = $null
    "endCliente" = "Catalão - GO / Davinópolis - GO"
    "obs" = "Nutrição Esportiva Personalizada, Emagrecimento, Hipertrofia, BJJ e Performance. Atendimento presencial e online. Instagram @raysonmendesnutri com 4.8k seguidores."
    "direcaoCriativa" = @{
        "presetId" = "modern-organic-editorial"
        "presetNome" = "Modern Organic Editorial"
        "composicao" = "warm-editorial-lifestyle"
        "tipografia" = @{
            "display" = "Plus Jakarta Sans 800 + Playfair Display Itálico"
            "body" = "Plus Jakarta Sans 400"
        }
        "paleta" = @{
            "estilo" = "dark-moss-olive-warm-sand"
            "sugestoes" = @{
                "fundo" = "#0D140F"
                "superficie" = "#15201A"
                "texto" = "#F4F6F0"
                "acento" = "#22C55E"
                "acento_secundario" = "#84CC16"
            }
        }
        "justificativa" = "Design editorial moderno e acolhedor para nutrição esportiva e alta performance com fotos reais do consultório, bio do Instagram e integração WhatsApp direta."
        "data" = "2026-08-30"
        "status" = "direcao_definida"
    }
    "versoes" = @(
        @{
            "numero" = 1
            "nome_estilo" = "Modern Organic Editorial"
            "descricao" = "Layout lifestyle de alta conversão para nutrição esportiva com fotos reais do Instagram/Maps, seções de metodologia, planos e WhatsApp"
            "arquivo" = "sites/rayson-mendes-nutri/index.html"
            "criado_em" = "2026-08-30 15:04"
            "ativo" = 1
        }
    )
}

foreach ($f in @("dashboard.html", "index.html")) {
    $raw = [System.IO.File]::ReadAllText("$PSScriptRoot\..\$f", [System.Text.Encoding]::UTF8)
    $pattern = '(?s)<script id="dados" type="application/json">(.*?)</script>'
    if ($raw -match $pattern) {
        $data = $matches[1] | ConvertFrom-Json
        $filtered = @($data.leads | Where-Object { $_.slug -ne "rayson-mendes-nutri" })
        $data.leads = $filtered + (ConvertTo-Json $leadDash -Depth 10 | ConvertFrom-Json)
        $data.atualizado = (Get-Date).ToString("yyyy-MM-dd HH:mm")
        $newJson = $data | ConvertTo-Json -Depth 10 -Compress
        $replacement = '<script id="dados" type="application/json">' + $newJson + '</script>'
        $newRaw = [System.Text.RegularExpressions.Regex]::Replace($raw, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ return $replacement })
        [System.IO.File]::WriteAllText("$PSScriptRoot\..\$f", $newRaw, [System.Text.Encoding]::UTF8)
        Write-Host "✅ Arquivo $f atualizado com sucesso!" -ForegroundColor Green
    }
}
