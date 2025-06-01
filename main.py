from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid

app = Flask(__name__)

@app.route("/")
def home():
    return "🔥 YT Downloader API Running!"

@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")
    quality = data.get("quality", "best")

    if not url:
        return jsonify({"error": "URL missing"}), 400

    filename = f"{uuid.uuid4()}.mp4"
    ydl_opts = {
        "format": quality,
        "outtmpl": filename,
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
