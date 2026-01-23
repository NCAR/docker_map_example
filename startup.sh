git clone https://github.com/NCAR/docker_map_example.git
git log -1 --pretty=format:"%h" -- ./docker_map_example
cp -r docker_map_example/flask-app/* .
python wsgi.py
