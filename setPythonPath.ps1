Set-Location $PSScriptRoot

function isAdmin {
  $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
  return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

$adm = isAdmin
if (-not $adm) {
  Write-Host "管理者権限が必要"
  return
}

$pythonPath = "PYTHONPATH"
$path = [System.Environment]::GetEnvironmentVariable($pythonPath, "Machine")
if ([string]::IsNullOrEmpty($path)) {
  $path = $PSScriptRoot 
}
else {
  $test = $path -split ";"
  if (-not $test.Contains($PSScriptRoot)) {
    $path += ";" + $PSScriptRoot
    $path = $path -replace ";;", ";"
  }
}
[System.Environment]::SetEnvironmentVariable($pythonPath, $path, "Machine")

$output = [System.Environment]::GetEnvironmentVariable($pythonPath, "Machine") -split ";"
foreach ($data in $output) {
  Write-Host $data
}


