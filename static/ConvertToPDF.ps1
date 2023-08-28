# Define o caminho da pasta atual como o local de origem
$sourceDirectory = Get-Location

# Define o caminho para o executável do LibreOffice (ajuste conforme o seu sistema)
$libreOfficePath = "C:\Program Files\LibreOffice\program\soffice.exe"

# Verifica se o LibreOffice está instalado no caminho especificado
if (-not (Test-Path $libreOfficePath)) {
    Write-Error "O LibreOffice não foi encontrado no caminho especificado: $libreOfficePath"
    exit
}

# Lista todos os arquivos .doc, .docx e .odt no diretório especificado
$files = Get-ChildItem -Path $sourceDirectory | Where-Object { $_.Extension -match "docx?$|odt" }

# Loop para converter cada arquivo para PDF
foreach ($file in $files) {
    $fullPath = $file.FullName
    Write-Host "Convertendo $fullPath para PDF..."

    # Comando de conversão usando o LibreOffice
    & $libreOfficePath --headless --convert-to pdf --outdir $sourceDirectory $fullPath

    Write-Host "$fullPath convertido com sucesso!"

    # Aguarda 5 segundo antes de processar o próximo arquivo
    Start-Sleep -Seconds 5
}

Write-Host "Operação concluída!"
Start-Sleep -Seconds 5