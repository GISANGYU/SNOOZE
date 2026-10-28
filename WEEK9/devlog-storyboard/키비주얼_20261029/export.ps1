Add-Type -AssemblyName System.Drawing
$taskRoot = $PSScriptRoot
$taskManifest = Get-Content -LiteralPath (Join-Path $taskRoot '제작목록.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$taskSourceDir = Join-Path $taskRoot '생성원본'
New-Item -ItemType Directory -Path $taskSourceDir -Force | Out-Null
$taskChecks = @()
foreach ($entry in $taskManifest.files) {
    $taskOriginal = Join-Path $taskSourceDir $entry.filename
    Copy-Item -LiteralPath $entry.source -Destination $taskOriginal
    $taskImage = [System.Drawing.Image]::FromFile($taskOriginal)
    $taskBitmap = New-Object System.Drawing.Bitmap(1920,1080)
    $taskGraphics = [System.Drawing.Graphics]::FromImage($taskBitmap)
    $taskGraphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
    $taskGraphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $taskGraphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $taskGraphics.DrawImage($taskImage, 0, 0, 1920, 1080)
    $taskTarget = Join-Path $taskRoot $entry.filename
    $taskBitmap.Save($taskTarget, [System.Drawing.Imaging.ImageFormat]::Png)
    $taskChecks += [pscustomobject]@{file=$entry.filename; originalWidth=$taskImage.Width; originalHeight=$taskImage.Height; width=1920; height=1080; bytes=(Get-Item -LiteralPath $taskTarget).Length}
    $taskGraphics.Dispose()
    $taskBitmap.Dispose()
    $taskImage.Dispose()
    $taskVerify = [System.Drawing.Image]::FromFile($taskTarget)
    if ($taskVerify.Width -ne 1920 -or $taskVerify.Height -ne 1080) { throw "Invalid size: $taskTarget" }
    $taskVerify.Dispose()
}
if ($taskChecks.Count -ne 28) { throw 'Expected 28 images' }
$taskChecks | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot '검수결과.json') -Encoding UTF8
Write-Output ('Verified PNG: ' + $taskChecks.Count + ', all 1920x1080')
