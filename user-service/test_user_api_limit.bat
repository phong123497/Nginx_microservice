@echo off
set URL=http://localhost:8080/api/users

echo Sending multiple parallel requests...
echo ----------------------------------------

for /L %%i in (1,1,32) do (
    start "" cmd /c curl -s -o nul -w "Request %%i -> HTTP %%{http_code}\n" %URL%
)

pause
