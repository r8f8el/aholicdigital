param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Alvo
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " [Auditor Web & Scanner de Leads]" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Alvo pesquisado: $Alvo"

$Url = $Alvo.Trim()
if (-not ($Url.StartsWith('http://') -or $Url.StartsWith('https://'))) {
    $Url = 'https://' + $Url
}

Write-Host "Site Alvo: $Url" -ForegroundColor Green
Write-Host "Inspecionando codigo HTML, UX, WhatsApp, SEO e Responsividade..." -ForegroundColor Gray

$sw = [System.Diagnostics.Stopwatch]::StartNew()
$score = 100
$falhas = @()
$positivos = @()
$html = ''

try {
    $req = [System.Net.HttpWebRequest]::Create($Url)
    $req.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36'
    $req.Timeout = 12000
    $resp = $req.GetResponse()
    $stream = $resp.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($stream)
    $html = $reader.ReadToEnd()
    $reader.Close()
    $resp.Close()
    $sw.Stop()
} catch {
    $sw.Stop()
    Write-Host "Erro ao acessar o site: $($_.Exception.Message)" -ForegroundColor Red
    $falhas += "Site inacessivel ou com lentidao critica de conexao."
    $score = 15
}

if ($html.Length -gt 0) {
    # 1. Identificar Plataforma
    $tec = 'HTML Customizado / Proprio'
    if ($html.Contains('wp-content') -or $html.Contains('wordpress')) {
        if ($html.Contains('elementor')) { $tec = 'WordPress + Elementor' } else { $tec = 'WordPress' }
        $positivos += 'Plataforma WordPress identificada.'
    } elseif ($html.Contains('wix.com') -or $html.Contains('_wix')) {
        $tec = 'Wix (Construtor Generico)'
        $falhas += 'Desenvolvido em Wix: carregamento pesado e perda de autoridade.'
        $score -= 25
    } elseif ($html.Contains('sites.google.com')) {
        $tec = 'Google Sites Gratuito'
        $falhas += 'Usa Google Sites gratuito: sem autoridade para servicos particulares.'
        $score -= 35
    }

    # 2. Viewport Mobile
    $temMobile = $false
    if ($html -match 'name="viewport"' -or $html -match "name='viewport'") {
        $temMobile = $true
        $positivos += 'Meta viewport mobile configurada.'
    } else {
        $falhas += 'SEM meta tag de viewport: pagina quebra ou desalinha no smartphone!'
        $score -= 30
    }

    # 3. WhatsApp
    $temWhats = $false
    $numWhats = ''
    if ($html -match 'api\.whatsapp\.com' -or $html -match 'wa\.me') {
        $temWhats = $true
        $positivos += 'Botao de WhatsApp direto detectado.'
    } else {
        $falhas += 'SEM botao de WhatsApp de 1 clique: o paciente precisa digitar o telefone manualmente.'
        $score -= 30
    }

    # 4. Instagram
    $insta = 'Nao detectado'
    if ($html -match 'instagram\.com/([a-zA-Z0-9_\.\-]+)') {
        $insta = '@' + $matches[1].TrimEnd('/')
    }

    # 5. Performance
    $tempoMs = $sw.ElapsedMilliseconds
    if ($tempoMs -gt 2500) {
        $falhas += "Carregamento lento ($tempoMs ms) - pacientes em 4G desistem da espera."
        $score -= 15
    }

    # Motivo do Redesign
    $motivo = 'Site funcional, porem com layout desatualizado e sem padrao visual premium.'
    if (-not $temWhats) {
        $motivo = 'Site sem botao direto de WhatsApp; perda critica de agendamentos no celular.'
    } elseif (-not $temMobile) {
        $motivo = 'Site nao otimizado para celular (sem viewport responsivo).'
    } elseif ($falhas.Count -gt 0) {
        $motivo = $falhas[0]
    }

    $score = [Math]::Max(10, [Math]::Min(100, $score))

    Write-Host ''
    Write-Host '============================================================' -ForegroundColor DarkCyan
    Write-Host "RELATORIO DE AUDITORIA TECNICA - $Url" -ForegroundColor Cyan
    Write-Host '============================================================' -ForegroundColor DarkCyan
    Write-Host "Score de Conversao: $score / 100" -ForegroundColor Yellow
    Write-Host "Tecnologia Base: $tec"
    Write-Host "Tempo de Resposta: $tempoMs ms"
    Write-Host "Mobile Ready: $(if($temMobile){'SIM'}else{'NAO'})"
    Write-Host "Botao WhatsApp Direto: $(if($temWhats){'SIM'}else{'NAO (Perda de Leads)'})"
    Write-Host "Instagram: $insta"

    Write-Host ''
    Write-Host 'PONTOS FRACOS & FALHAS OBJETIVAS (Para usar na abordagem):' -ForegroundColor Magenta
    if ($falhas.Count -gt 0) {
        foreach ($f in $falhas) {
            Write-Host "  * $f" -ForegroundColor Red
        }
    } else {
        Write-Host '  * Nenhuma falha estrutural grave encontrada.' -ForegroundColor Gray
    }

    Write-Host ''
    Write-Host 'MOTIVO PARA PROPOSTA / REDESIGN:' -ForegroundColor Yellow
    Write-Host "  -> `"$motivo`"" -ForegroundColor White
    Write-Host '============================================================' -ForegroundColor DarkCyan
    Write-Host ''
}
