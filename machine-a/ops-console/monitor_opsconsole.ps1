# monitor_opsconsole.ps1
# Plays the "legitimate admin" role for testing Machine A's network vuln.
# Run this on your Windows host (already on the same host-only network as
# the VMs) -- it periodically logs into OpsConsole over the real network,
# generating traffic an ARP-spoofing attacker can actually intercept.
#
# Usage: powershell -ExecutionPolicy Bypass -File monitor_opsconsole.ps1

$targetIP = "192.168.241.3"
$targetPort = 2222
$intervalSeconds = 15

function Read-Until {
    param($Stream, [string]$Marker)
    $bytes = New-Object System.Collections.Generic.List[byte]
    $markerBytes = [System.Text.Encoding]::ASCII.GetBytes($Marker)
    $one = New-Object byte[] 1
    while ($true) {
        $n = $Stream.Read($one, 0, 1)
        if ($n -le 0) { break }
        $bytes.Add($one[0])
        if ($bytes.Count -ge $markerBytes.Length) {
            $tail = $bytes.GetRange($bytes.Count - $markerBytes.Length, $markerBytes.Length).ToArray()
            $match = $true
            for ($i = 0; $i -lt $markerBytes.Length; $i++) {
                if ($tail[$i] -ne $markerBytes[$i]) { $match = $false; break }
            }
            if ($match) { break }
        }
    }
    return [System.Text.Encoding]::ASCII.GetString($bytes.ToArray())
}

function Send-Line {
    param($Stream, [string]$Text)
    $bytes = [System.Text.Encoding]::ASCII.GetBytes("$Text`r`n")
    $Stream.Write($bytes, 0, $bytes.Length)
    $Stream.Flush()
}

function Invoke-CheckIn {
    $client = New-Object System.Net.Sockets.TcpClient
    $client.Connect($targetIP, $targetPort)
    $stream = $client.GetStream()

    Read-Until $stream "username: " | Out-Null
    Send-Line $stream "sysadmin"

    Read-Until $stream "password: " | Out-Null
    Send-Line $stream "R00tR0b0tics#99"

    Read-Until $stream "> " | Out-Null
    Send-Line $stream "status"

    Start-Sleep -Milliseconds 400
    $buf = New-Object byte[] 4096
    $n = $stream.Read($buf, 0, $buf.Length)
    $resp = [System.Text.Encoding]::ASCII.GetString($buf, 0, $n)

    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] check-in ok:`n$resp"

    $stream.Close()
    $client.Close()
}

Write-Host "Monitoring OpsConsole at ${targetIP}:${targetPort} every ${intervalSeconds}s. Ctrl+C to stop."
while ($true) {
    try {
        Invoke-CheckIn
    } catch {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] check-in failed: $_"
    }
    Start-Sleep -Seconds $intervalSeconds
}
