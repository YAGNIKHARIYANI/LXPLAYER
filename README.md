# LX-PLAYER - Ultra Cinematic Streaming Engine

An ultra high-speed, private, ad-free streaming web application featuring real-time movie catalogs, a fully responsive dashboard, multi-language audio track selectors, and hardware-accelerated HLS video playback.

---

## ⚡ Features

### 🎬 Cinematic UI/UX (Jio Hotstar Style)
- **Ambient Header Banner**: A floating, rounded featured banner card (`rounded-2xl sm:rounded-3xl`) with high-definition original poster images centered and left-aligned (`object-contain md:object-left`), complete with rich drop shadows and high contrast text styling.
- **Unified Sidebar Navigation**: Desktop-hover expandable sidebar showing Home, Bollywood (New Movies), and Hollywood.
- **Responsive Footer**: Tightly aligned footer text fitting perfectly across all screen sizes.

### 📱 Responsive Mobile Adjustments
- **Toggle Drawer Sidebar**: A fixed sidebar that transforms into a slide-out drawer on mobile devices, triggered by a hamburger menu, with backdrop overlays and a dedicated close (`X`) button.
- **Legible Labels**: Sidebar categories display text labels next to icons instantly on mobile.
- **Two-Column Mobile Grid**: Catalog items automatically stack into exactly 2 columns (`grid-cols-2`) on mobile viewports with tight spacing to maximize display efficiency.
- **Optimized Carousel Dots**: Carousel indicators are scaled down to tiny dots (`w-1` / `w-1.5` active) on mobile to fit the layout.
- **Non-Wrapping Pagination**: Page controllers are compressed on mobile screens to fit all buttons in a single row without wrapping.

### ⚙️ Private Performance Engine
- **100% Ad-Free Playback**: Direct streaming without raw source links exposed, protecting user privacy.
- **HD Quality Upscaling**: Integrated automatic URL processing to upgrade low-resolution thumbnail links (TMDB `/w185/` and `/340-500/` paths) to their original high-definition HD quality (`/t/p/original/` and `/1000-1500/`).
- **Local Network / Wi-Fi Streaming**: Fully configured to bind to `0.0.0.0`, allowing instant private streaming access across all phones, tablets, and smart TVs on the same Wi-Fi network.

---

## 🛠️ Technology Stack

- **Backend**: Python 3, Flask, CORS, Socket-based Local Network Discovery.
- **Frontend**: HTML5, Tailwind CSS, FontAwesome, JavaScript (ES6+).
- **Video Engine**: Hls.js (HTTP Live Streaming), HTML5 Native Video.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
- **Local Host**: `http://127.0.0.1:5100`
- **Local Network / Wi-Fi**: `http://<your-computer-ip>:5100`

---

## 📄 License
MIT License - Created by Yagnik & Vaidehi Hariyani.

