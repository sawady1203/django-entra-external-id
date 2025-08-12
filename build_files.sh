echo "BUILD START"

# create a virtual environment named 'venv' if it doesn't already exist
python3.12 -m venv venv

# activate the virtual environment
source venv/bin/activate

# upgrade pip to the latest version
pip install --upgrade pip

# install all deps in the venv
pip install -r requirements.txt

# collect static files using the Python interpreter from venv
python manage.py collectstatic --noinput

# run migrations using the Python interpreter from venv
python manage.py migrate

echo "BUILD END"