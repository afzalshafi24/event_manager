
@echo off 

:: Create Python Virtual Environment
echo Creating Python Virtual Environment
python -m venv venv
echo Python Virtual Environment Created

:: Activate Python Environment
echo Activating Python Environment
call .\venv\Scripts\activate.bat

:: Install Required Libraries
echo Installing Python Libraries
pip install -r .\requirements.txt

:: Install Internal Libraries
echo Installing Internal Libraries
pip install .\internal_libaries\eureka_client-0.1.5-py3-none-any.whl

:: Install Pyinstaller
echo Installing Pyinstaller
pip install pyinstaller

:: Build EventManagerAPI with Pyinstaller
echo Building EventManager_API with Pyinstaller
cd API 
mkdir pyinstaller
cd .\pyinstaller\
pyinstaller --add-data "..\api_config.json;." --add-data "..\README.md;." ..\EventManagerMain.py
move .\dist\EventManagerMain\_internal\api_config.json .\dist\EventManagerMain\
move .\dist\EventManagerMain\_internal\README.md .\dist\EventManagerMain\

