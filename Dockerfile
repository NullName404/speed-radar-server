FROM tailscale/tailscale:latest
RUN apt-get update && apt-get install -y python3 python3-pip
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock & tailscale up --authkey=$TS_AUTHKEY --hostname=render-server && gunicorn app:app
