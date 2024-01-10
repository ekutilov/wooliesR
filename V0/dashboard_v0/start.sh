source ./.venv/bin/activate
export YOURAPPLICATION_SETTINGS=./config.py
export STORAGE_BUCKET=myshopdash.appspot.com
python3 main.py

deactivate
