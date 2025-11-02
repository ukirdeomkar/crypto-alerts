# Input file path
$filePath = ".\raw-data\futures-coins.txt"

# Optional: Output file (uncomment the overwrite line below if you want to replace the same file)
$outputFile = ".\data\futures-coins-filtered.txt"

# Read, filter, and clean lines
Get-Content $filePath |
    Where-Object { $_ -match "•USDT" } |         # keep only lines containing •USDT
    ForEach-Object { $_ -replace "•USDT", "" } | # remove •USDT from those lines
    Set-Content $outputFile

# --- If you prefer overwriting the same file instead, use this line instead of Set-Content above ---
# (Get-Content $filePath | Where-Object { $_ -match "•USDT" } | ForEach-Object { $_ -replace "•USDT", "" }) | Set-Content $filePath
