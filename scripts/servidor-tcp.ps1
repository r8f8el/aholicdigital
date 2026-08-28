param([int]$Port = 8765)

$pasta = Split-Path -Parent $MyInvocation.MyCommand.Path
$raiz = Split-Path -Parent $pasta
Set-Location $raiz

$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
$listener.Start()
Write-Host "🚀 Servidor Local rodando em: http://localhost:$Port" -ForegroundColor Green
Start-Process "http://localhost:$Port/dashboard.html"

$mimes = @{
    '.html' = 'text/html; charset=utf-8'
    '.htm'  = 'text/html; charset=utf-8'
    '.css'  = 'text/css; charset=utf-8'
    '.js'   = 'application/javascript; charset=utf-8'
    '.json' = 'application/json; charset=utf-8'
    '.png'  = 'image/png'
    '.jpg'  = 'image/jpeg'
    '.jpeg' = 'image/jpeg'
    '.svg'  = 'image/svg+xml'
    '.ico'  = 'image/x-icon'
}

while ($true) {
    $client = $listener.AcceptTcpClient()
    [System.Threading.ThreadPool]::QueueUserWorkItem({
        param($cli)
        try {
            $stream = $cli.GetStream()
            $reader = [System.IO.StreamReader]::new($stream)
            $writer = [System.IO.StreamWriter]::new($stream, [System.Text.Encoding]::UTF8)
            
            $reqLine = $reader.ReadLine()
            if ($reqLine) {
                $parts = $reqLine.Split(' ')
                $path = $parts[1].TrimStart('/')
                if (-not $path -or $path -eq '/') { $path = 'dashboard.html' }
                $path = [System.Uri]::UnescapeDataString($path)
                $file = Join-Path (Get-Location) $path.Replace('/', '\')

                if (Test-Path $file -PathType Leaf) {
                    $ext = [System.IO.Path]::GetExtension($file).ToLower()
                    $mime = $mimes[$ext]
                    if (-not $mime) { $mime = 'application/octet-stream' }
                    $bytes = [System.IO.File]::ReadAllBytes($file)

                    $writer.WriteLine("HTTP/1.1 200 OK")
                    $writer.WriteLine("Content-Type: $mime")
                    $writer.WriteLine("Content-Length: $($bytes.Length)")
                    $writer.WriteLine("Connection: close")
                    $writer.WriteLine()
                    $writer.Flush()
                    $stream.Write($bytes, 0, $bytes.Length)
                } else {
                    $body = [System.Text.Encoding]::UTF8.GetBytes("<h1>404 Not Found</h1>")
                    $writer.WriteLine("HTTP/1.1 404 Not Found")
                    $writer.WriteLine("Content-Type: text/html; charset=utf-8")
                    $writer.WriteLine("Content-Length: $($body.Length)")
                    $writer.WriteLine("Connection: close")
                    $writer.WriteLine()
                    $writer.Flush()
                    $stream.Write($body, 0, $body.Length)
                }
            }
            $cli.Close()
        } catch {}
    }, $client) | Out-Null
}
