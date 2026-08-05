@echo off
setlocal enabledelayedexpansion
rem ---------------------------------------------------------------------
rem  Lance tout ce qu'il faut pour une session de jeu instrumentee.
rem
rem  Quatre choses, dans cet ordre :
rem    1. le raccourci Claude Code du projet
rem    2. le serveur Archipelago, sur la seed la plus recente
rem    3. BizHawk avec la ROM et la session Lua, journal + connecteur
rem    4. le client BizHawk d'Archipelago
rem
rem  Le serveur et le client restent ouverts dans leur fenetre, avec
rem  cmd /k : quand quelque chose casse, le message reste lisible au lieu
rem  de disparaitre avec la fenetre.
rem ---------------------------------------------------------------------

set "RACINE=C:\Users\sulyv\Documents\Projet BIS"
set "AP=%RACINE%\vendor\Archipelago"
set "PYAP=%AP%\venv\Scripts\python.exe"
set "BIZHAWK=%RACINE%\bizhawk-2.10\EmuHawk.exe"
set "ROM=%RACINE%\4171 - Mario & Luigi - Bowser's Inside Story (US)(M3)(XenoPhobia).nds"
set "SESSION=%RACINE%\tools\session_bizhawk.lua"
set "CLAUDE=C:\Users\sulyv\Desktop\Claude Code - Projet BIS.lnk"

rem La seed la plus recente, plutot qu'un nom en dur : regenerer une seed
rem ne doit pas casser le raccourci.
set "SEED="
for /f "delims=" %%f in ('dir /b /o-d "%RACINE%\seeds\*.zip" 2^>nul') do (
    if not defined SEED set "SEED=%RACINE%\seeds\%%f"
)

rem Chaque chemin est verifie avant usage : un raccourci qui ouvre trois
rem fenetres dont une vide est plus penible qu'un message clair.
for %%P in ("%PYAP%" "%BIZHAWK%" "%ROM%" "%SESSION%") do (
    if not exist "%%~P" (
        echo INTROUVABLE : %%~P
        echo.
        pause
        exit /b 1
    )
)
if not defined SEED (
    echo Aucune seed dans "%RACINE%\seeds".
    echo En generer une :  venv\Scripts\python.exe tools\seed_de_test.py
    echo.
    pause
    exit /b 1
)

echo seed    : %SEED%
echo journal : %RACINE%\journal_capacites.txt
echo.

if exist "%CLAUDE%" (
    start "" "%CLAUDE%"
) else (
    echo Raccourci Claude Code introuvable, on continue sans.
)

rem Le repertoire de travail passe par /D plutot que par un cd enchaine :
rem imbriquer des guillemets dans un cmd /k est le genre de detail qui
rem casse sans message utile.
start "Serveur Archipelago" /D "%AP%" cmd /k ""%PYAP%" MultiServer.py "%SEED%""

rem --lua et --luaconsole sont des options reelles de BizHawk 2.10,
rem relevees dans les chaines UTF-16 de BizHawk.Client.Common.dll.
rem La console ouverte sert a voir le journal defiler.
start "" "%BIZHAWK%" --lua="%SESSION%" --luaconsole "%ROM%"

rem BizHawk met quelques secondes a ouvrir son socket. Le client sait
rem attendre, mais demarrer dans le desordre brouille ses messages.
timeout /t 8 /nobreak >nul

start "Client Archipelago" /D "%AP%" cmd /k ""%PYAP%" BizHawkClient.py"

echo.
echo Lance. Dans le client : /connect localhost:38281 puis le slot TestBIS.
echo Cette fenetre peut etre fermee.
timeout /t 10 /nobreak >nul
