@echo off
echo ----------------------------------------
echo SISTEMA PROGETTO "Il Gelato Artigianale"
echo ----------------------------------------

REM Crea la cartella gelato se non esiste
if not exist gelato (
    mkdir gelato
    echo ✓ Cartella "gelato" creata.
) else (
    echo ✓ Cartella "gelato" già presente.
)

REM Sposta i file Python nella cartella gelato
move /Y main.py gelato\__main__.py
move /Y gelato_ui.py gelato\
move /Y gelato_calculations.py gelato\
move /Y traduzioni.py gelato\
move /Y traduzioni2.py gelato\

echo ✓ File spostati nella cartella "gelato":
echo   - __main__.py
echo   - gelato_ui.py
echo   - gelato_calculations.py
echo   - traduzioni.py
echo   - traduzioni2.py

echo ----------------------------------------
echo ✅ Struttura completata. Ora puoi eseguire:
echo   briefcase create android
echo   briefcase build android
echo   briefcase run android
echo ----------------------------------------

pause
