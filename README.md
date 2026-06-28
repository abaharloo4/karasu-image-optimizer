# Karasu Image Optimizer | بهینه‌ساز تصویر کاراسو

[English](#english) | [فارسی](#fa)

---

<a name="fa"></a>
## 🇮🇷 راهنمای فارسی

برنامه **Karasu Image Optimizer** یک ابزار پیشرفته و حرفه‌ای برای بهینه‌سازی و فشرده‌سازی تصاویر است که در دو نسخه **اپلیکیشن دسکتاپ** و **وب اپلیکیشن مدرن** توسعه یافته است. این پروژه مجهز به شتاب‌دهنده سخت‌افزاری GPU، الگوریتم‌های هوشمند فشرده‌سازی و پیش‌نمایش مقایسه‌ای زنده است.

---

### 📋 پیش‌نیازهای سیستم

قبل از شروع نصب پروژه، مطمئن شوید ابزارهای زیر روی سیستم شما نصب هستند:
- **پایتون (Python 3.11 یا بالاتر)**
- **نود جی‌اس (Node.js نسخه 20 یا بالاتر)**
- **داکر (Docker Desktop)** - اختیاری، اما برای دیتابیس یا اجرای کانتینری پیشنهاد می‌شود.

---

### 🛠️ مراحل نصب و راه‌اندازی پروژه

#### ۱. شبیه‌سازی (Clone) پروژه
ابتدا پروژه را از گیت‌هاب شبیه‌سازی کرده و وارد فولدر پروژه شوید:
```bash
git clone https://github.com/abaharloo4/karasu-image-optimizer.git
cd image-optimizer
```

#### ۲. نصب وابستگی‌های پایتون (بک‌اند)
یک محیط مجازی (Virtual Environment) ایجاد کرده و پکیج‌های مورد نیاز بک‌اند را نصب کنید:
```bash
# ایجاد محیط مجازی پایتون
python -m venv .venv

# فعال‌سازی محیط مجازی
# در ویندوز:
.venv\Scripts\activate
# در مک یا لینوکس:
source .venv/bin/activate

# نصب پکیج‌های پایتون
pip install -r backend/requirements.txt
```

#### ۳. نصب وابستگی‌های فرانت‌اند (React)
وارد فولدر `frontend` شده و پکیج‌های مربوط به نود را نصب کنید:
```bash
cd frontend
npm install
cd ..
```

---

### 🚦 روش‌های اجرای پروژه

#### روش اول: اجرای آسان و خودکار (ویندوز - پیشنهادی)
ساده‌ترین راه برای اجرای کامل پروژه در ویندوز، استفاده از اسکریپت آماده است. کافیست در ریشه پروژه فایل زیر را اجرا کنید:
```bash
run_project.bat
```
*این اسکریپت به صورت خودکار دیتابیس PostgreSQL را در داکر بالا می‌آورد (در صورت عدم دسترسی به داکر، برنامه به صورت خودکار روی حافظه موقت In-Memory سوئیچ می‌کند)، سرور فلاسک بک‌اند را روی پورت `5001` اجرا می‌کند، سرور ری‌اکت را روی پورت `5173` باز می‌کند و مرورگر شما را به صورت خودکار روی آدرس فرانت‌اند بالا می‌آورد.*

برای متوقف کردن کامل سرویس‌ها و بستن پنجره‌ها، اسکریپت زیر را اجرا کنید:
```bash
stop_project.bat
```

#### روش دوم: اجرای کانتینری با داکر کامپوز (Docker Compose)
بدون نیاز به نصب دستی پایتون و نود، کل پروژه را در چند ثانیه اجرا کنید:
```bash
docker compose up -d
```
پس از اتمام پروسه، وب اپلیکیشن روی آدرس `http://localhost:5173` در دسترس خواهد بود.

#### روش سوم: اجرای دستی سرویس‌ها
در صورتی که می‌خواهید هر سرویس را در خط فرمان جداگانه کنترل کنید:

1. **مرحله اول (دیتابیس)**:
   یک کانتینر دیتابیس PostgreSQL روی پورت `5432` بالا بیاورید:
   ```bash
   docker run --name postgres -p 5432:5432 -e POSTGRES_DB=image_optimizer -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -d postgres:15-alpine
   ```
2. **مرحله دوم (سرور بک‌اند پایتون)**:
   در ریشه پروژه، محیط مجازی را فعال کرده و بک‌اند را استارت بزنید:
   ```bash
   .venv\Scripts\activate      # فعال‌سازی محیط مجازی
   python -m backend.app
   ```
   *بک‌اند روی آدرس `http://127.0.0.1:5001` اجرا می‌شود.*
3. **مرحله سوم (سرور فرانت‌اند)**:
   وارد فولدر فرانت‌اند شده و سرور توسعه ویت را اجرا کنید:
   ```bash
   cd frontend
   npm run dev
   ```
   *فرانت‌اند روی آدرس `http://127.0.0.1:5173` اجرا شده و درخواست‌های `/api` را به بک‌اند پروکسی می‌کند.*

---

### 🖥️ اجرای نسخه دسکتاپ (GUI پایتون)

برنامه دارای یک نسخه دسکتاپ محلی با رابط کاربری زیبا است. برای اجرا:
1. مطمئن شوید محیط مجازی فعال است.
2. دستور زیر را در ریشه پروژه بزنید:
   ```bash
   python app.py
   ```
3. برای ساخت فایل خروجی تک‌فایله قابل حمل ویندوز (`.exe`):
   ```bash
   pyinstaller app.spec
   ```
   فایل خروجی نهایی در مسیر `dist/KarasuImageOptimizer.exe` ذخیره خواهد شد.

---

<a name="english"></a>
## 🇬🇧 English Guide

**Karasu Image Optimizer** is an advanced, ultra-professional image optimization tool supporting both a **Desktop GUI Application** and a **Modern Web Application**. It features GPU acceleration, smart compression algorithms, and real-time comparison previews.

---

### 📋 Prerequisites

Make sure you have the following installed on your machine:
- **Python (3.11 or higher)**
- **Node.js (v20 or higher)**
- **Docker Desktop** (Optional, but highly recommended for database & compose setups)

---

### 🛠️ Installation Steps

#### 1. Clone the Repository
Clone this repository to your local machine and navigate into the directory:
```bash
git clone https://github.com/abaharloo4/karasu-image-optimizer.git
cd image-optimizer
```

#### 2. Install Python Dependencies (Backend)
Create a Python virtual environment and install the required packages:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

#### 3. Install Frontend Dependencies (React)
Navigate to the frontend directory and install the required npm packages:
```bash
cd frontend
npm install
cd ..
```

---

### 🚦 Running the Application

#### Method 1: Easy Automatic Script (Windows - Recommended)
The easiest way to start all services locally is by executing the manager script in the root directory:
```bash
run_project.bat
```
*This script automatically starts the PostgreSQL database container (or falls back to In-Memory mode if Docker is missing), launches the Flask backend on port `5001`, launches the Vite frontend on port `5173`, and opens your web browser.*

To stop all active services and close their command prompt windows, run:
```bash
stop_project.bat
```

#### Method 2: Docker Compose (Multiplatform)
Launch the entire stack (PostgreSQL, Backend, Frontend) with a single command:
```bash
docker compose up -d
```
Access the application by navigating to `http://localhost:5173` in your browser.

#### Method 3: Manual Startup
If you want to run each service manually in separate terminals:

1. **Step 1 (Database)**:
   Run a PostgreSQL container on port `5432`:
   ```bash
   docker run --name postgres -p 5432:5432 -e POSTGRES_DB=image_optimizer -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -d postgres:15-alpine
   ```
2. **Step 2 (Flask Backend)**:
   Activate your virtual environment and run the backend app:
   ```bash
   .venv\Scripts\activate
   python -m backend.app
   ```
   *The backend will run on port `5001`.*
3. **Step 3 (Vite Frontend)**:
   Navigate to the frontend directory and start the Vite dev server:
   ```bash
   cd frontend
   npm run dev
   ```
   *The frontend will run on port `5173` and proxy API calls to port `5001`.*

---

### 🖥️ Running the Desktop GUI App

To launch the native desktop application:
1. Ensure your virtual environment is active.
2. Run the entrypoint script in the root directory:
   ```bash
   python app.py
   ```
3. To package the desktop app into a standalone Windows executable (`.exe`):
   ```bash
   pyinstaller app.spec
   ```
   *The compiled executable will be located in the `dist/` directory.*

---

## 🛠️ Project Structure | ساختار پروژه

```
image-optimizer/
│
├── backend/                  # Flask REST API Backend | بک‌اند پروژه
│   ├── api/                  # API Controllers (Upload, Process, History, Preview, etc.)
│   ├── core/                 # Optimization core logic, database wrapper, and cache
│   ├── uploads/              # Temporary storage for uploaded images
│   ├── outputs/              # Storage for optimized output images
│   └── app.py                # Flask entrypoint
│
├── frontend/                 # Vite + React Frontend | فرانت‌اند پروژه
│   ├── src/                  # React components, hooks, assets, i18n
│   ├── package.json          # Node dependencies and scripts
│   └── vite.config.js        # Vite & dev-server proxy configuration
│
├── fonts/                    # Font assets (YekanBakh) | فونت‌های پروژه
├── app.py                    # Python Desktop GUI entrypoint | اجرای دسکتاپ پایتون
├── docker-compose.yml        # Docker compose configuration
├── run_project.bat           # Windows script to launch local services
└── stop_project.bat          # Windows script to stop all services safely
```
