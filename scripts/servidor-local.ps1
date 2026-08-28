$port = 8765
$pasta = $PSScriptRoot
if (-not $pasta) { $pasta = (Get-Location).Path }
$pastaRaiz = (Get-Item $pasta).Parent.FullName
if (-not (Test-Path "$pastaRaiz\dashboard.html")) { $pastaRaiz = $pasta }

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
try {
    $listener.Start()
    Write-Host "🚀 Servidor Local Aholic rodando em: http://localhost:$port/" -ForegroundColor Green
    Start-Process "http://localhost:$port/dashboard.html"
} catch {
    Write-Host "⚠️ Erro ao iniciar listener: $($_.Exception.Message)" -ForegroundColor Red
}

$mimeTypes = @{
    ".html" = "text/html; charset=utf-8"
    ".htm"  = "text/html; charset=utf-8"
    ".css"  = "text/css; charset=utf-8"
    ".js"   = "application/javascript; charset=utf-8"
    ".json" = "application/json; charset=utf-8"
    ".png"  = "image/png"
    ".jpg"  = "image/jpeg"
    ".jpeg" = "image/jpeg"
    ".svg"  = "image/svg+xml"
    ".ico"  = "image/x-icon"
}

while ($listener.IsListening) {
    try {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response

        $urlPath = $request.Url.LocalPath.TrimStart('/')
        if (-not $urlPath) { $urlPath = "dashboard.html" }
        $urlPath = [System.Uri]::UnescapeDataString($urlPath)

        $filePath = Join-Path $pastaRaiz $urlPath.Replace('/', '\')

        if (Test-Path $filePath -PathType Leaf) {
            $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
            $mime = $mimeTypes[$ext]
            if (-not $mime) { $mime = "application/octet-stream" }

            $bytes = [System.IO.File]::ReadAllBytes($filePath)
            $response.ContentType = $mime
            $response.ContentLength64 = $bytes.Length
            $response.StatusCode = 200
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        } else {
            $response.StatusCode = 404
            $err = [System.Text.Encoding]::UTF8.GetBytes("<h1>404 - Arquivo não encontrado</h1>")
            $response.OutputStream.Write($err, 0, $err.Length)
        }
        $response.OutputStream.Close()
    } catch {
        # Continua escutando
    }
}
