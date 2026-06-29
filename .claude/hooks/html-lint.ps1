$j = [Console]::In.ReadToEnd() | ConvertFrom-Json
$f = $j.tool_input.file_path
if (-not $f) { $f = $j.tool_response.filePath }
if ($f -and $f -match '\.html$') {
    npx html-validate "$f" 2>&1
}
exit 0
