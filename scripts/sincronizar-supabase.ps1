$supabaseUrl = "https://gpignxwsxfbkelckrebd.supabase.co"
$supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdwaWdueHdzeGZia2VsY2tyZWJkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc4NjQ3OTcsImV4cCI6MjEwMzQ0MDc5N30.Ex2iAC0VoW9svg2rMKNwWU9rYz5FNTQaz6qa9GL97tU"

$headers = @{
    "apikey" = $supabaseKey
    "Authorization" = "Bearer $supabaseKey"
    "Content-Type" = "application/json"
    "Prefer" = "resolution=merge-duplicates"
}

# 1. Inserir Lead Patrícia Margotti com nomes de colunas exatos do SQL
$leadPayload = @{
    "slug" = "patricia-margotti-psi"
    "nome" = "Patrícia Margotti | Psicóloga TCC"
    "nicho" = "Psicologia & TCC"
    "cidade" = "Florianópolis"
    "nota" = 5.0
    "avaliacoes" = 30
    "whatsapp" = "5548999999999"
    "email" = "contato@patriciamargotti.com"
    "site_antigo" = ""
    "motivo" = "Criação do Primeiro Site Oficial (Design Softly Digital Wellness • Trindade / Floripa)"
    "status" = "redesenhado"
    "url_nova" = "sites/patricia-margotti-psi/patricia-margotti-psi.html"
    "valor" = 1800.0
    "manutencao" = 150.0
    "pago" = 0
    "obs" = "Atendimento presencial na Trindade e Online. Instagram @psi.patricia.margotti."
} | ConvertTo-Json

try {
    $resLead = Invoke-RestMethod -Uri "$supabaseUrl/rest/v1/leads" -Method Post -Headers $headers -Body $leadPayload
    Write-Host "✅ Lead Patricia Margotti inserido no Supabase Nuvem com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao inserir lead no Supabase: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Inserir Versão do Site
$versaoPayload = @{
    "lead_slug" = "patricia-margotti-psi"
    "numero" = 1
    "nome_estilo" = "Softly Digital Wellness"
    "descricao" = "Digital Living Room com paleta pastel quente (#FDFCF8, coral, sage e lavanda), grão analógico e tipografia Outfit + Cursive"
    "arquivo" = "sites/patricia-margotti-psi/patricia-margotti-psi.html"
    "criado_em" = "2026-08-27 23:25"
    "ativo" = 1
} | ConvertTo-Json

try {
    $resVersao = Invoke-RestMethod -Uri "$supabaseUrl/rest/v1/versoes_site" -Method Post -Headers $headers -Body $versaoPayload
    Write-Host "✅ Versão do site registrada no Supabase Nuvem com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao inserir versão no Supabase: $($_.Exception.Message)" -ForegroundColor Red
}
