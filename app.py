from flask import Flask, request
import requests
from PIL import Image
import os
import tempfile

TOKEN = os.getenv("BOT_TOKEN")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
SEND_MSG = f"{BASE_URL}/sendMessage"
SEND_PHOTO = f"{BASE_URL}/sendPhoto"
SEND_MEDIA = f"{BASE_URL}/sendMediaGroup"
GET_FILE = f"{BASE_URL}/getFile"
FILE_DL = f"https://api.telegram.org/file/bot{TOKEN}/"

app = Flask(__name__)
user_state = {}

# =========================
# 🔧 HELPERS
# =========================

def send_message(chat_id, text, inline_keyboard=None):
    payload = {"chat_id": chat_id, "text": text}

    if inline_keyboard:
        payload["reply_markup"] = {"inline_keyboard": inline_keyboard}

    requests.post(SEND_MSG, json=payload)


def send_layout_preview(chat_id, count):
    paths = [
        f"static/layouts/layout_{count}_1.jpg",
        f"static/layouts/layout_{count}_2.jpg",
        f"static/layouts/layout_{count}_3.jpg",
    ]

    media = []
    files = {}

    for i, path in enumerate(paths, start=1):
        files[f"file{i}"] = open(path, "rb")
        media.append({
            "type": "photo",
            "media": f"attach://file{i}"
        })

    requests.post(
        SEND_MEDIA,
        data={"chat_id": chat_id, "media": str(media).replace("'", '"')},
        files=files
    )

    send_message(
        chat_id,
        "👇 Select layout",
        inline_keyboard=[
            [{"text": "Layout 1", "callback_data": f"{count}_1"}],
            [{"text": "Layout 2", "callback_data": f"{count}_2"}],
            [{"text": "Layout 3", "callback_data": f"{count}_3"}],
        ]
    )


def download_image(file_id):
    file_res = requests.get(GET_FILE, params={"file_id": file_id}).json()
    file_path = file_res["result"]["file_path"]

    img_data = requests.get(FILE_DL + file_path).content

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    tmp.write(img_data)
    return tmp.name


# =========================
# 🧠 SMART CROP
# =========================
def resize_crop(img, target_size):
    target_w, target_h = target_size
    img_w, img_h = img.size

    scale = max(target_w / img_w, target_h / img_h)
    new_size = (int(img_w * scale), int(img_h * scale))
    img = img.resize(new_size, Image.LANCZOS)

    left = (img.width - target_w) // 2
    top = (img.height - target_h) // 2
    right = left + target_w
    bottom = top + target_h

    return img.crop((left, top, right, bottom))


# =========================
# 🎨 COLLAGE ENGINE
# =========================
def create_collage(paths, count, layout):
    canvas = Image.new("RGB", (600, 600), "white")
    imgs = [Image.open(p) for p in paths]

    if count == 3:

        if layout == 1:
            imgs = [resize_crop(img, (300, 300)) for img in imgs]
            canvas.paste(imgs[0], (0, 0))
            canvas.paste(imgs[1], (300, 0))
            canvas.paste(imgs[2], (150, 300))

        elif layout == 2:
            imgs[0] = resize_crop(imgs[0], (300, 600))
            imgs[1] = resize_crop(imgs[1], (300, 300))
            imgs[2] = resize_crop(imgs[2], (300, 300))

            canvas.paste(imgs[0], (0, 0))
            canvas.paste(imgs[1], (300, 0))
            canvas.paste(imgs[2], (300, 300))

        elif layout == 3:
            imgs = [resize_crop(img, (600, 200)) for img in imgs]
            canvas.paste(imgs[0], (0, 0))
            canvas.paste(imgs[1], (0, 200))
            canvas.paste(imgs[2], (0, 400))

    elif count == 4:

        if layout == 1:
            imgs = [resize_crop(img, (300, 300)) for img in imgs]
            for i, img in enumerate(imgs):
                x = (i % 2) * 300
                y = (i // 2) * 300
                canvas.paste(img, (x, y))

        elif layout == 2:
            imgs[0] = resize_crop(imgs[0], (300, 600))
            imgs[1:] = [resize_crop(img, (300, 200)) for img in imgs[1:]]

            canvas.paste(imgs[0], (0, 0))
            canvas.paste(imgs[1], (300, 0))
            canvas.paste(imgs[2], (300, 200))
            canvas.paste(imgs[3], (300, 400))

        elif layout == 3:
            imgs = [resize_crop(img, (150, 600)) for img in imgs]
            for i, img in enumerate(imgs):
                canvas.paste(img, (i * 150, 0))

    out = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    canvas.save(out.name)
    return out.name


# =========================
# 🌐 HEALTH CHECK
# =========================
@app.route("/")
def home():
    return "✅ Bot is running"


# =========================
# 🌐 WEBHOOK
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "ok"

    # =========================
    # 🔘 CALLBACK
    # =========================
    if "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        data_val = query["data"]

        if data_val.startswith("choose_"):
            count = int(data_val.split("_")[1])
            send_layout_preview(chat_id, count)
            return "ok"

        count, layout = map(int, data_val.split("_"))

        user_state[chat_id] = {
            "step": "upload",
            "count": count,
            "layout": layout,
            "photos": [],
            "last_count": count,
            "last_layout": layout
        }

        send_message(chat_id, f"📤 Upload {count} photos")
        return "ok"

    # =========================
    # 💬 MESSAGE
    # =========================
    if "message" not in data:
        return "ok"

    msg = data["message"]
    chat_id = msg["chat"]["id"]

    if chat_id not in user_state:
        user_state[chat_id] = {}

    state = user_state[chat_id]

    # /start
    if "text" in msg and msg["text"] == "/start":
        send_message(
            chat_id,
            "📸 Choose number of photos",
            inline_keyboard=[
                [{"text": "3 Photos", "callback_data": "choose_3"}],
                [{"text": "4 Photos", "callback_data": "choose_4"}],
            ]
        )
        return "ok"

    # /new
    if "text" in msg and msg["text"] == "/new":
        if "last_count" not in state:
            send_message(chat_id, "⚠️ Use /start first")
            return "ok"

        state["step"] = "upload"
        state["count"] = state["last_count"]
        state["layout"] = state["last_layout"]
        state["photos"] = []

        send_message(chat_id, f"🔁 Upload {state['count']} photos")
        return "ok"

    # =========================
    # 📸 PHOTO + DOCUMENT
    # =========================
    if state.get("step") == "upload" and ("photo" in msg or "document" in msg):

        file_id = None

        if "photo" in msg:
            file_id = msg["photo"][-1]["file_id"]

        elif "document" in msg:
            mime = msg["document"].get("mime_type", "")
            if not mime.startswith("image/"):
                send_message(chat_id, "❌ Send only image files")
                return "ok"

            file_id = msg["document"]["file_id"]

        path = download_image(file_id)
        state["photos"].append(path)

        if len(state["photos"]) == 1:
            send_message(chat_id, f"📥 Receiving images... ({state['count']} needed)")

        if len(state["photos"]) < state["count"]:
            return "ok"

        collage = create_collage(
            state["photos"],
            state["count"],
            state["layout"]
        )

        with open(collage, "rb") as f:
            requests.post(
                SEND_PHOTO,
                files={"photo": f},
                data={"chat_id": chat_id}
            )

        # cleanup
        for p in state["photos"]:
            os.remove(p)
        os.remove(collage)

        # save last config
        state["last_count"] = state["count"]
        state["last_layout"] = state["layout"]

        state.pop("photos", None)
        state.pop("step", None)

        send_message(
            chat_id,
            "✅ Done!\n\n/start → new layout\n/new → reuse last"
        )

    return "ok"
