FROM arm32v7/python:3.9-buster
WORKDIR /code
COPY . /code
RUN pip install --upgrade pip && pip install -r config/requirements.txt || pip install -r requirements.txt
CMD ["pytest", "--maxfail=5", "--disable-warnings", "-v"]
