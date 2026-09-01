$destDir = ".\sites\daldali-coffee-paris\assets"
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir -Force
}

$photos = @(
    @{ Name = "hero-cafe.jpg"; Url = "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1200&q=85" },
    @{ Name = "matcha-latte.jpg"; Url = "https://images.unsplash.com/photo-1536256263959-770b48d82b0a?auto=format&fit=crop&w=1000&q=85" },
    @{ Name = "yakgwa-pastry.jpg"; Url = "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1000&q=85" },
    @{ Name = "specialty-coffee.jpg"; Url = "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1000&q=85" },
    @{ Name = "interior-cozy.jpg"; Url = "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1000&q=85" },
    @{ Name = "barista-pour.jpg"; Url = "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=1000&q=85" },
    @{ Name = "ceramics.jpg"; Url = "https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=1000&q=85" }
)

foreach ($item in $photos) {
    $dest = Join-Path $destDir $item.Name
    Write-Host "Baixando $($item.Name)..."
    try {
        Invoke-WebRequest -Uri $item.Url -OutFile $dest -UserAgent "Mozilla/5.0"
        Write-Host "OK: $($item.Name)"
    } catch {
        Write-Host "Erro ao baixar $($item.Name)"
    }
}

Get-ChildItem $destDir | Select-Object Name, Length
