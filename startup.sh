cat startup.sh
pwd
ls -lrth
git clone https://github.com/NCAR/docker_map_example.git
git -C docker_map_example log -1 --pretty=format:"%h"
cp -r docker_map_example/flask-app/* .
python wsgi.py
