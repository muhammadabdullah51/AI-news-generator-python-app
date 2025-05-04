AIzaSyDfZG5sFwMm4o9k6IkTtwVb0nnfkEPDvtU

pip install fastapi uvicorn sqlalchemy python-multipart bcrypt python-jose[cryptography] requests
pip install jinja2
pip install google-generativeai
pip install --upgrade google-generativeai


#for migrations
alembic init migrations
# Edit alembic.ini to use your database URL
alembic revision --autogenerate -m "Add generation_count"
alembic upgrade head