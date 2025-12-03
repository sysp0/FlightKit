FROM python:3.13-slim

WORKDIR /app

COPY . .
RUN pip install .


ENTRYPOINT ["python", "src/flightkit/cli/main.py"]
CMD []