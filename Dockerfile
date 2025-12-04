FROM python:3.13-slim

WORKDIR /app

COPY . .
RUN pip install .

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION="0.1.0"

LABEL org.opencontainers.image.title="FlightKit"
LABEL org.opencontainers.image.description="A simple tool to collect and clean Iranian flight price data"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.authors="Reza Ghasemi <syspo8@gmail.com>"
LABEL org.opencontainers.image.vendor="sysp0"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.url="https://github.com/sysp0/FlightKit"
LABEL org.opencontainers.image.documentation="https://github.com/sysp0/FlightKit#readme"
LABEL org.opencontainers.image.source="https://github.com/sysp0/FlightKit"
LABEL org.opencontainers.image.revision="${VCS_REF:-unknown}"
LABEL org.opencontainers.image.created="${BUILD_DATE:-unknown}"

ENTRYPOINT ["python", "src/flightkit/cli/main.py"]
CMD []