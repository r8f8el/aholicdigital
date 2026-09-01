$destDir = ".\sites\lucas-aguiar-nutri\assets"
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir -Force
}

$photos = @(
    @{ Name = "avatar.jpg"; Url = "https://pixel-p1.s3.sa-east-1.amazonaws.com/doctor/avatar/e85250a6/e85250a6-aa23-4e35-b2b8-d01265369c9a_large.jpg" },
    @{ Name = "foto-1.jpg"; Url = "https://pixel-p1.s3.sa-east-1.amazonaws.com/doctor/photos/82a26673/82a26673-d756-454a-8903-5f094e7c3e94_large.jpg" },
    @{ Name = "foto-2.jpg"; Url = "https://pixel-p1.s3.sa-east-1.amazonaws.com/doctor/photos/7ea91123/7ea91123-36a4-4801-9bf3-2e29c0da737f_large.jpg" },
    @{ Name = "foto-3.jpg"; Url = "https://pixel-p1.s3.sa-east-1.amazonaws.com/doctor/photos/c1773e64/c1773e64-3d1f-4fe5-8840-fce845983a03_large.jpg" },
    @{ Name = "foto-4.jpg"; Url = "https://pixel-p1.s3.sa-east-1.amazonaws.com/doctor/photos/2497d2b3/2497d2b3-00a6-463e-8745-e4be04c39c6c_large.jpg" },
    @{ Name = "foto-5.jpg"; Url = "https://pixel-p1.s3.sa-east-1.amazonaws.com/doctor/photos/5c875386/5c875386-783e-4def-b050-7553699550a9_large.jpg" },
    @{ Name = "foto-6.jpg"; Url = "https://pixel-p1.s3.sa-east-1.amazonaws.com/doctor/photos/d776f10b/d776f10b-b089-4b94-ac60-59be3a898503_large.jpg" },
    @{ Name = "foto-7.jpg"; Url = "https://pixel-p1.s3.sa-east-1.amazonaws.com/doctor/photos/be3f11ff/be3f11ff-d280-4cf5-a930-b41287657a57_large.jpg" }
)

foreach ($item in $photos) {
    $dest = Join-Path $destDir $item.Name
    Write-Host "Baixando $($item.Name)..."
    Invoke-WebRequest -Uri $item.Url -OutFile $dest -UserAgent "Mozilla/5.0"
    Write-Host "Salvo: $dest"
}

Get-ChildItem $destDir | Select-Object Name, Length
