# 🤖 Telegram Collage Maker Bot  
**Create beautiful photo collages directly from Telegram using a webhook-based bot**

---

## 📌 Overview  
This project is a Telegram bot that allows users to create photo collages by uploading multiple images. The bot provides layout options and automatically generates a collage using image processing techniques.

It is built using **Flask (webhook-based architecture)** and leverages the **Telegram Bot API** for real-time interaction.

---

## 🎯 Key Features  
- 📸 Upload multiple images (3 or 4 photos)  
- 🎨 Choose from multiple collage layouts  
- 🧠 Smart image resizing and cropping  
- ⚡ Real-time collage generation  
- 🔄 Reuse last configuration (/new command)  
- 📤 Supports both image and document uploads  

---

## 🏗️ System Architecture  

The bot follows a webhook-based architecture:

- **Telegram API:** Receives user messages and callbacks  
- **Flask Server:** Handles webhook requests  
- **State Management:** Tracks user interaction flow  
- **Image Processing Engine:** Uses PIL for collage creation  
- **Temporary Storage:** Stores images during processing  

---

## 🛠️ Tech Stack  
- **Backend:** Python (Flask)  
- **API:** Telegram Bot API  
- **Image Processing:** Pillow (PIL)  
- **HTTP Requests:** Requests library  
- **Storage:** Temporary file system  

---

## ⚙️ Key Technical Highlights  
- Webhook-based bot (low latency, real-time response)  
- Inline keyboard interaction using Telegram callbacks  
- Smart image cropping with aspect ratio preservation  
- Dynamic collage layout engine (3 & 4 image support)  
- Temporary file handling and cleanup for efficiency  

---

## 📊 Functional Flow  
1. User starts bot using `/start`  
2. Selects number of images (3 or 4)  
3. Chooses a collage layout  
4. Uploads required images  
5. Bot processes images and generates collage  
6. Collage is sent back to the user  

---

## 🧠 Image Processing Logic  
- Images are resized using **scale + center crop**  
- Maintains aspect ratio without distortion  
- Supports multiple layout configurations  
- Uses high-quality resampling (LANCZOS)  

---

## 🧪 Challenges  
- Handling multiple user states simultaneously  
- Managing temporary files efficiently  
- Supporting different input formats (photo/document)  
- Ensuring consistent layout rendering  

---

## 📚 Learnings  
- Webhook-based bot development  
- State management in stateless HTTP systems  
- Image processing techniques using PIL  
- Handling real-time user interaction  

---

## 🔐 Security  
- Bot token stored using environment variables  
- Temporary files cleaned after processing  
- No persistent user data storage  

---

## 🚀 Setup & Deployment  

### 1. Clone Repository  
```bash
git clone https://github.com/agr0303-sys/Collagemaker_BOT.git
cd collage-bot  
