# distrobuild

### Development

### Kerberos
```
kinit -R -kt {PATH_TO_KEYTAB} koji/distrobuild@ROCKYLINUX.ORG -S HTTP/koji.rockylinux.org@ROCKYLINUX.org
```

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
# set database settings in distrobuild/settings.py
aerich upgrade
uvicorn distrobuild.app:app --reload --port 8090
```

#### Scheduler
```
virtualenv .venv
source .venv/bin/activate
python3 run_scheduler.py
```
