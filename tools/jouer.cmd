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

rem La racine se deduit de l'emplacement de ce fichier, qui vit dans
rem tools\ : aucun chemin en dur, donc rien qui depende d'un nom
rem d'utilisateur ni d'un dossier d'installation.
pushd "%~dp0.."
set "RACINE=%CD%"
popd
set "AP=%RACINE%\vendor\Archipelago"
set "PYAP=%AP%\venv\Scripts\python.exe"
set "BIZHAWK=%RACINE%\bizhawk-2.10\EmuHawk.exe"
set "ROM=%RACINE%\4171 - Mario & Luigi - Bowser's Inside Story (US)(M3)(XenoPhobia).nds"
set "SESSION=%RACINE%\tools\session_bizhawk.lua"
set "LUA_AP=%AP%\data\lua"
set "SESSION_LANCEE=%LUA_AP%\session_bizhawk.lua"
set "CLAUDE=%USERPROFILE%\Desktop\Claude Code - Projet BIS.lnk"

rem La seed la plus recente, plutot qu'un nom en dur : regenerer une seed
rem ne doit pas casser le raccourci.
set "SEED="
for /f "delims=" %%f in ('dir /b /o-d "%RACINE%\seeds\*.zip" 2^>nul') do (
    if not defined SEED set "SEED=%RACINE%\seeds\%%f"
)

rem Chaque chemin est verifie avant usage : un raccourci qui ouvre trois
rem fenetres dont une vide est plus penible qu'un message clair.
for %%P in ("%PYAP%" "%BIZHAWK%" "%ROM%" "%SESSION%" "%LUA_AP%\connector_bizhawk_generic.lua") do (
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

rem POURQUOI LA SESSION EST COPIEE DANS data\lua AVANT D'ETRE LANCEE.
rem Le connecteur d'Archipelago fait require("lua_5_3_compat"),
rem require("base64"), require("json") et require("socket"), et
rem socket.lua:44-47 construit en plus le chemin de sa DLL a partir du
rem repertoire courant. Ces quatre modules et le dossier x64 vivent tous
rem dans data\lua. Lance depuis tools\, le script ne les trouve pas et le
rem connecteur meurt sur "module 'lua_5_3_compat' not found" pendant que
rem le journal, lui, survit : une session a moitie vivante, ou le client
rem attend BizHawk sans fin. Mesure le 7 aout 2026.
rem
rem La source reste tools\session_bizhawk.lua, seul fichier a maintenir
rem et le seul suivi par git ; la copie est refaite a chaque lancement,
rem donc recloner Archipelago ne casse rien.
copy /Y "%SESSION%" "%SESSION_LANCEE%" >nul
if not exist "%SESSION_LANCEE%" (
    echo Copie impossible vers "%SESSION_LANCEE%".
    echo.
    pause
    exit /b 1
)

rem --lua et --luaconsole sont des options reelles de BizHawk 2.10,
rem relevees dans les chaines UTF-16 de BizHawk.Client.Common.dll.
rem La console ouverte sert a voir le journal defiler.
rem
rem Le /D double la ceinture : rien dans l'erreur mesuree ne dit si le
rem repertoire courant vient du script charge ou du processus qui lance
rem BizHawk. Les deux pointent maintenant sur data\lua.
start "" /D "%LUA_AP%" "%BIZHAWK%" --lua="%SESSION_LANCEE%" --luaconsole "%ROM%"

rem BizHawk met quelques secondes a ouvrir son socket. Le client sait
rem attendre, mais demarrer dans le desordre brouille ses messages.
timeout /t 8 /nobreak >nul

start "Client Archipelago" /D "%AP%" cmd /k ""%PYAP%" BizHawkClient.py"

echo.
echo Lance. Dans le client : /connect localhost:38281 puis le slot TestBIS.
echo Cette fenetre peut etre fermee.
timeout /t 10 /nobreak >nul
