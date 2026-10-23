param([switch]$NoOpen)
$ErrorActionPreference = 'Stop'
$webRoot = Join-Path $PSScriptRoot 'assets\open-cowart-canvas'
$runtime = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (!(Test-Path -LiteralPath $runtime)) {
    $runtime = (Get-Command python -ErrorAction Stop).Source
}
if (!(Test-Path -LiteralPath (Join-Path $webRoot 'nine-grid.html'))) { throw '九宫格页面文件缺失。' }
$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
$listener.Start()
$port = $listener.LocalEndpoint.Port
$listener.Stop()
$url = "http://127.0.0.1:$port/nine-grid.html"
$server = Start-Process -FilePath $runtime -ArgumentList @('-m','http.server',"$port",'--bind','127.0.0.1','--directory',('"' + $webRoot + '"')) -WindowStyle Hidden -PassThru
$ready = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    if ($server.HasExited) { throw '九宫格本地服务启动失败。' }
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Milliseconds 150 }
}
if (!$ready) { Stop-Process -Id $server.Id; throw '九宫格本地服务未能就绪。' }
Write-Output $url
if (!$NoOpen) { Start-Process $url }
