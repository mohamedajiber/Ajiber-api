from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid

app = Flask(__name__)

@app.route("/")
def home():
    return "🔥 YT Downloader API Running!"

@app.route("/info", methods=["POST"])
def video_info():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL missing"}), 400

    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            video_formats = [
                {
                    "format_id": f["format_id"],
                    "format_note": f.get("format_note"),
                    "ext": f["ext"],
                    "resolution": f.get("resolution") or f.get("height"),
                    "filesize": f.get("filesize") or 0
                }
                for f in formats if f.get("vcodec") != "none"
            ]
            audio_formats = [
                {
                    "format_id": f["format_id"],
                    "ext": f["ext"],
                    "abr": f.get("abr"),
                    "filesize": f.get("filesize") or 0
                }
                for f in formats if f.get("vcodec") == "none"
            ]
            return jsonify({
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration_string") or info.get("duration"),
                "channel": info.get("uploader"),
                "is_playlist": info.get("_type") == "playlist",
                "video_formats": video_formats,
                "audio_formats": audio_formats,
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")
    format_id = data.get("format_id")
    ext = data.get("ext", "mp4")  # default extension

    if not url or not format_id:
        return jsonify({"error": "URL and format_id are required"}), 400

    filename = f"{uuid.uuid4()}.{ext}"
    ydl_opts = {
        "format": format_id,
        "outtmpl": filename,
        "quiet": True,
        "noplaylist": True,
        "merge_output_format": ext
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
