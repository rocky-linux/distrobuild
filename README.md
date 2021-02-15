# distrobuild

### Development

#### UI
```
cd ui
yarn
yarn start
```

#### Server
```
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn distrobuild.app:app --reload --port 8090
```
