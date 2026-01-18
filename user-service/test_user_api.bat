@echo off
set URL=http://localhost:8080/api/users
set TOTAL=30

echo Sending %TOTAL% requests to %URL%
echo ----------------------------------------

for /L %%i in (1,1,%TOTAL%) do (
    echo Request #%%i
    curl -i %URL%
    echo.
    echo ----------------------------------------
)

pause
