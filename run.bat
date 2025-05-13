cd /d %~dp0
uv run main.py
echo Finished at %DATE% %TIME% >> task_log.txt

@REM $sname = "arcanumpw"
@REM schtasks /Create /TN $sname /TR "`"$PWD\run.bat`"" /SC ONCE /ST 23:59 /F
@REM schtasks /Run /TN $sname
@REM schtasks /End /TN "arcanumpw"

@REM Get-CimInstance Win32_Process | Where-Object {
@REM     $_.Name -eq "python.exe" -and $_.CommandLine -like "*arcanum-pw*"
@REM } | ForEach-Object {
@REM     taskkill /PID $_.ProcessId /T /F
@REM }