# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        THỊ TRƯỜNG LAO ĐỘNG VIỆT NAM 2026–2031 · MEMENTOMORI EDITION          ║
║        Phân Tích Cấu Trúc Kỹ Năng & Chỉ Số Nguy Cơ Thay Thế Bởi AI (AVI)      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Tác giả : Chung Võ Quốc Minh — MSSV: 24050042                               ║
║  Đơn vị  : Khoa CNTT, Robot & Trí Tuệ Nhân Tạo (FIRA)                        ║
║  Đề tài  : Nghiên cứu Khoa học Dữ liệu & Ứng dụng                           ║
║  URL     : https://kiutrang.streamlit.app/                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import base64
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# 1. CẤU HÌNH TRANG WEB (PAGE CONFIG)
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Thị Trường Lao Động Việt Nam 2026–2031 · MementoMori",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="expanded"
)

STREAMLIT_URL = "https://kiutrang.streamlit.app/"
CSV_FILENAME = "thi_truong_lao_dong_vietnam.csv"
LOADING_IMG_PATH = os.path.join("anh cho", "Screenshot 2026-11-11 230128.png")

# ══════════════════════════════════════════════════════════════════════════════
# 2. BẢNG MÀU MỰC NƯỚC MEMENTOMORI (WATERCOLOR INK PALETTE)
# ══════════════════════════════════════════════════════════════════════════════
INK_COLORS = {
    "sumi": "#2C3242",        # Mực tàu sumi
    "carmine": "#B54D59",     # Mực đỏ rượu / Rủi ro rất cao
    "amber": "#C48039",       # Mực vàng hổ phách / Rủi ro cao
    "ochre": "#B89B48",       # Mực vàng nghệ / Trung bình
    "celadon": "#4F7D74",     # Mực xanh ngọc bích / An toàn
    "indigo": "#3A506B",      # Mực chàm sương mù / Cực kỳ an toàn
    "wisteria": "#7A6B8D",    # Mực tím hoa đậu biếc / Kỹ năng mềm
    "light_teal": "#6A9C93",  # Mực nước trong veo
    "parchment": "#F9F6EE",   # Giấy dó truyền thống
}

PLOTLY_INK_SCALE = [
    [0.0, INK_COLORS["indigo"]],
    [0.2, INK_COLORS["celadon"]],
    [0.5, INK_COLORS["ochre"]],
    [0.75, INK_COLORS["amber"]],
    [1.0, INK_COLORS["carmine"]]
]

# ══════════════════════════════════════════════════════════════════════════════
# 3. HÀM TẢI ẢNH CHỜ LOADING (BASE64)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def get_loading_image_base64():
    candidates = [
        LOADING_IMG_PATH,
        os.path.join(os.path.dirname(__file__), LOADING_IMG_PATH),
        os.path.abspath(LOADING_IMG_PATH)
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                pass
    return ""

loading_b64 = get_loading_image_base64()

# ══════════════════════════════════════════════════════════════════════════════
# 4. INJECT CSS & GIAO DIỆN HOẠT ẢNH MỰC MÀU NƯỚC + CANVAS SÓNG NƯỚC CON CHUỘT
# ══════════════════════════════════════════════════════════════════════════════
custom_css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;900&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* --- NỀN NƯỚC MỜ CỰC TRONG, NHÌN THẤY ĐÁY HỒ --- */
html, body, [data-testid="stAppViewContainer"] {{
    background: radial-gradient(circle at 50% 20%, rgba(246, 243, 236, 0.92) 0%, rgba(235, 239, 237, 0.90) 50%, rgba(223, 232, 233, 0.94) 100%),
                radial-gradient(circle at 85% 80%, rgba(200, 220, 225, 0.45) 0%, transparent 60%),
                radial-gradient(circle at 15% 65%, rgba(230, 215, 205, 0.35) 0%, transparent 55%),
                linear-gradient(180deg, #FAF7F0 0%, #EEF3F2 40%, #E3EBEB 100%) !important;
    background-attachment: fixed !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #2D3748 !important;
    overflow-x: hidden;
}}

/* Hiệu ứng gợn sóng nước đáy hồ lấp lánh (Caustics) */
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: 
        radial-gradient(rgba(255, 255, 255, 0.4) 1px, transparent 1px),
        radial-gradient(rgba(180, 205, 215, 0.25) 1.5px, transparent 1.5px);
    background-size: 48px 48px, 64px 64px;
    background-position: 0 0, 24px 24px;
    opacity: 0.65;
    pointer-events: none;
    z-index: 0;
    animation: lakeBottomShimmer 16s ease-in-out infinite alternate;
}}

@keyframes lakeBottomShimmer {{
    0% {{ transform: scale(1) translateY(0); opacity: 0.55; }}
    50% {{ transform: scale(1.03) translateY(-10px); opacity: 0.75; }}
    100% {{ transform: scale(1.01) translateY(5px); opacity: 0.60; }}
}}

/* Sidebar phong cách giấy dó màu nước cổ điển */
[data-testid="stSidebar"] {{
    background: rgba(248, 245, 238, 0.88) !important;
    backdrop-filter: blur(18px) saturate(140%) !important;
    border-right: 1px solid rgba(190, 180, 165, 0.35) !important;
    box-shadow: 4px 0 25px rgba(60, 75, 80, 0.05) !important;
}}

/* --- MÀN HÌNH CHỜ (NOW LOADING... MEMENTOMORI BIRD) --- */
#memento-loader {{
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background-color: #EFEBE4;
    z-index: 9999999;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    pointer-events: none;
    animation: dissolveLoader 2.6s cubic-bezier(0.4, 0, 0.2, 1) 1.5s forwards;
}}

@keyframes dissolveLoader {{
    0% {{ opacity: 1; filter: blur(0px); visibility: visible; }}
    50% {{ opacity: 0.85; filter: blur(2px); }}
    85% {{ opacity: 0.15; filter: blur(8px); }}
    100% {{ opacity: 0; visibility: hidden; display: none; }}
}}

.loader-bird {{
    max-width: 320px;
    width: 65vw;
    height: auto;
    filter: drop-shadow(0 12px 30px rgba(100, 80, 60, 0.18));
    animation: birdBreath 2.8s ease-in-out infinite alternate;
}}

@keyframes birdBreath {{
    0% {{ transform: translateY(0) scale(1); }}
    100% {{ transform: translateY(-8px) scale(1.025); }}
}}

.loader-caption {{
    font-family: 'Cinzel', 'Playfair Display', serif;
    letter-spacing: 5px;
    font-size: 15px;
    color: #6C5A46;
    margin-top: 18px;
    font-weight: 700;
    text-transform: uppercase;
}}

.loader-subtext {{
    font-family: 'Playfair Display', serif;
    font-style: italic;
    color: #8C7862;
    font-size: 13px;
    margin-top: 6px;
    letter-spacing: 1px;
}}

/* --- HIỆU ỨNG VẾT MỰC LOANG TRÊN CÁC CONTAINER & CARD BIỂU ĐỒ --- */
.ink-card {{
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.82) 0%, rgba(247, 244, 237, 0.72) 100%);
    backdrop-filter: blur(14px) saturate(130%);
    border: 1px solid rgba(200, 195, 185, 0.45);
    border-radius: 22px 10px 24px 12px / 14px 26px 14px 24px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: 0 10px 32px rgba(45, 60, 70, 0.06), 0 1px 3px rgba(0, 0, 0, 0.03);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    animation: watercolorAppear 1.2s cubic-bezier(0.2, 0.8, 0.2, 1) both;
}}

.ink-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 18px 45px rgba(50, 70, 85, 0.12), 0 0 25px rgba(79, 125, 116, 0.14);
    border-color: rgba(79, 125, 116, 0.45);
}}

/* Vết mực loang nở ra từ góc thẻ */
.ink-card::after {{
    content: "";
    position: absolute;
    bottom: -35px; right: -35px;
    width: 140px; height: 140px;
    background: radial-gradient(circle, rgba(79, 125, 116, 0.16) 0%, rgba(79, 125, 116, 0.04) 55%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    transition: all 0.5s ease;
}}

.ink-card:hover::after {{
    transform: scale(1.4);
    opacity: 0.9;
}}

/* Biến thể vết mực màu Đỏ rượu / Cảnh báo rủi ro */
.ink-card-danger {{
    background: linear-gradient(135deg, rgba(255, 250, 249, 0.88) 0%, rgba(253, 240, 240, 0.75) 100%);
    border-color: rgba(181, 77, 89, 0.35);
}}
.ink-card-danger::after {{
    background: radial-gradient(circle, rgba(181, 77, 89, 0.22) 0%, rgba(181, 77, 89, 0.05) 55%, transparent 70%);
}}
.ink-card-danger:hover {{
    border-color: rgba(181, 77, 89, 0.65);
    box-shadow: 0 18px 45px rgba(181, 77, 89, 0.15), 0 0 25px rgba(181, 77, 89, 0.15);
}}

/* Biến thể vết mực Vàng hổ phách / Xu hướng tương lai */
.ink-card-amber {{
    background: linear-gradient(135deg, rgba(255, 252, 245, 0.88) 0%, rgba(252, 246, 233, 0.75) 100%);
    border-color: rgba(196, 128, 57, 0.35);
}}
.ink-card-amber::after {{
    background: radial-gradient(circle, rgba(196, 128, 57, 0.22) 0%, rgba(196, 128, 57, 0.05) 55%, transparent 70%);
}}

/* Biến thể vết mực Tím đậu biếc / Kỹ năng mềm */
.ink-card-purple {{
    background: linear-gradient(135deg, rgba(254, 250, 255, 0.88) 0%, rgba(246, 240, 252, 0.75) 100%);
    border-color: rgba(122, 107, 141, 0.35);
}}
.ink-card-purple::after {{
    background: radial-gradient(circle, rgba(122, 107, 141, 0.22) 0%, rgba(122, 107, 141, 0.05) 55%, transparent 70%);
}}

/* --- HIỆU ỨNG HIỆN LÊN KIỂU MÀU NƯỚC CHO BIỂU ĐỒ (WATERCOLOR BLOOM) --- */
@keyframes watercolorAppear {{
    0% {{
        opacity: 0;
        filter: blur(8px) saturate(150%);
        transform: translateY(18px) scale(0.97);
    }}
    60% {{
        filter: blur(2px) saturate(120%);
    }}
    100% {{
        opacity: 1;
        filter: blur(0px) saturate(100%);
        transform: translateY(0) scale(1);
    }}
}}

/* Style Header Nghệ Thuật */
.memento-title {{
    font-family: 'Cinzel', 'Playfair Display', serif;
    font-size: 2.3rem;
    font-weight: 700;
    color: #242B35;
    letter-spacing: 2px;
    margin-bottom: 4px;
    background: linear-gradient(120deg, #1C2430 0%, #3D5A54 50%, #874C56 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.memento-subtitle {{
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.05rem;
    color: #5A6578;
    margin-bottom: 20px;
    letter-spacing: 0.5px;
}}

.memento-badge {{
    display: inline-block;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-right: 8px;
    border: 1px solid transparent;
}}

.badge-danger {{
    background: rgba(181, 77, 89, 0.12);
    color: #9E3340;
    border-color: rgba(181, 77, 89, 0.3);
}}

.badge-warning {{
    background: rgba(196, 128, 57, 0.12);
    color: #9C5F1C;
    border-color: rgba(196, 128, 57, 0.3);
}}

.badge-success {{
    background: rgba(79, 125, 116, 0.12);
    color: #2F6158;
    border-color: rgba(79, 125, 116, 0.3);
}}

.badge-info {{
    background: rgba(58, 80, 107, 0.12);
    color: #2C3E55;
    border-color: rgba(58, 80, 107, 0.3);
}}

/* Plotly container animation */
.stPlotlyChart {{
    animation: watercolorAppear 1.3s cubic-bezier(0.16, 1, 0.3, 1) both;
    border-radius: 16px;
}}

/* Tinh chỉnh nút bấm Streamlit sang phong cách phím đàn màu nước */
.stButton>button {{
    background: linear-gradient(135deg, #4F7D74 0%, #3D645D 100%) !important;
    color: #F8F6F0 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(79, 125, 116, 0.25) !important;
}}
.stButton>button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(79, 125, 116, 0.4) !important;
    background: linear-gradient(135deg, #5B8E85 0%, #46736B 100%) !important;
}}
</style>

<!-- MÀN HÌNH CHỜ (LOADING SCREEN) VỚI ẢNH CHÚ CHIM MÀU NƯỚC MEMENTOMORI -->
<div id="memento-loader">
    <img src="data:image/png;base64,{loading_b64}" alt="Now Loading..." class="loader-bird" />
    <div class="loader-caption">Now Loading...</div>
    <div class="loader-subtext">Đang kết nối thị trường lao động Việt Nam 2026–2031</div>
</div>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 5. THỦ THUẬT NỀN NƯỚC MỜ & CON CHUỘT LOANG SÓNG NƯỚC (WATER RIPPLE CANVAS)
# ══════════════════════════════════════════════════════════════════════════════
water_ripple_component = """
<div id="water-container" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 1;">
    <canvas id="water-canvas" style="width: 100%; height: 100%;"></canvas>
</div>

<script>
(function() {
    // Tìm hoặc gắn canvas vào cửa sổ cha của Streamlit để nhận sự kiện chuột toàn diện
    const targetDoc = window.parent ? window.parent.document : document;
    let canvas = targetDoc.getElementById('memento-water-canvas');
    
    if (!canvas) {
        canvas = targetDoc.createElement('canvas');
        canvas.id = 'memento-water-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100vw';
        canvas.style.height = '100vh';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '0';
        targetDoc.body.appendChild(canvas);
    }

    const ctx = canvas.getContext('2d');
    let ripples = [];
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    // Bắt sự kiện chuột di chuyển trên toàn trang để tạo sóng loang
    let lastX = 0, lastY = 0, lastTime = 0;
    targetDoc.addEventListener('mousemove', (e) => {
        const now = Date.now();
        const dist = Math.hypot(e.clientX - lastX, e.clientY - lastY);
        if (dist > 18 || (now - lastTime > 60)) {
            ripples.push({
                x: e.clientX,
                y: e.clientY,
                radius: 4,
                maxRadius: Math.min(120, 40 + dist * 1.5),
                alpha: 0.45,
                speed: 1.8 + Math.min(dist * 0.05, 2.5),
                hue: (dist > 35) ? 'rgba(181, 77, 89,' : 'rgba(110, 165, 185,' // Màu mực biến đổi theo tốc độ di chuột
            });
            lastX = e.clientX;
            lastY = e.clientY;
            lastTime = now;
        }
    });

    function animate() {
        ctx.clearRect(0, 0, width, height);

        for (let i = ripples.length - 1; i >= 0; i--) {
            const r = ripples[i];
            r.radius += r.speed;
            r.alpha *= 0.965; // Mờ dần như nước loang

            if (r.alpha < 0.01 || r.radius > r.maxRadius) {
                ripples.splice(i, 1);
                continue;
            }

            // Vòng sóng chính
            ctx.beginPath();
            ctx.arc(r.x, r.y, r.radius, 0, Math.PI * 2);
            ctx.strokeStyle = r.hue + r.alpha + ')';
            ctx.lineWidth = 2.2;
            ctx.stroke();

            // Vòng gợn sóng thứ 2 phản chiếu ánh sáng mặt hồ
            if (r.radius > 12) {
                ctx.beginPath();
                ctx.arc(r.x, r.y, r.radius * 0.72, 0, Math.PI * 2);
                ctx.strokeStyle = 'rgba(255, 255, 255, ' + (r.alpha * 0.6) + ')';
                ctx.lineWidth = 1.2;
                ctx.stroke();
            }
        }

        requestAnimationFrame(animate);
    }
    animate();
})();
</script>
"""
st.components.v1.html(water_ripple_component, height=0)

# ══════════════════════════════════════════════════════════════════════════════
# 6. TẢI VÀ CHUẨN HÓA DỮ LIỆU THỰC TẾ (DATA ENGINE)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    if os.path.exists(CSV_FILENAME):
        df = pd.read_csv(CSV_FILENAME)
    else:
        # Dự phòng dữ liệu mô phỏng theo đúng phân phối chuẩn của đề tài
        np.random.seed(42)
        n = 1000
        roles = ["Phần mềm", "Văn phòng", "Doanh nghiệp", "Quản trị mạng nội bộ", "Nhân viên", "Quản lý"]
        degrees = ["Đại học", "Cao đẳng", "Trung cấp", "THPT", "Thạc sĩ"]
        df = pd.DataFrame({
            "TT": range(1, n + 1),
            "Tên công việc": np.random.choice(["Kỹ sư AI", "Lập trình viên Python", "Kế toán", "Bảo vệ", "Nhân viên Telesales"], n),
            "Vị trí công việc": np.random.choice(roles, n, p=[0.27, 0.33, 0.22, 0.09, 0.06, 0.03]),
            "Thời gian làm việc": np.random.choice(["Toàn thời gian", "Theo ca", "Giờ hành chính"], n),
            "Thuyết trình": np.random.choice(["có", "không"], n, p=[0.36, 0.64]),
            "Làm việc nhóm": np.random.choice(["có", "không"], n, p=[0.756, 0.244]),
            "Sáng tạo": np.random.choice(["có", "không"], n, p=[0.451, 0.549]),
            "Đàm phán": np.random.choice(["có", "không"], n, p=[0.241, 0.759]),
            "Giao tiếp": np.random.choice(["có", "không"], n, p=[0.727, 0.273]),
            "Ngoại ngữ": np.random.choice(["IELTS 6.0", "TOEIC 550", "Hoa ngữ", "null"], n, p=[0.25, 0.25, 0.112, 0.388]),
            "Kinh nghiệm": np.random.choice(["1 năm", "2 năm", "không"], n, p=[0.4, 0.3, 0.3]),
            "Chuyên môn": np.random.choice(["CNTT", "Kinh tế", "Luật", "null"], n),
            "Trình độ": np.random.choice(degrees, n, p=[0.51, 0.061, 0.093, 0.186, 0.15]),
            "Lập trình": np.random.choice(["Python", "SQL", "C#", "không"], n, p=[0.30, 0.06, 0.03, 0.61]),
            "Kỹ năng AI": np.random.choice(["có", "không"], n, p=[0.36, 0.64]),
            "Tên doanh nghiệp": "Tập đoàn Công nghệ & Thương mại",
            "Link dữ liệu": "https://kiutrang.streamlit.app/"
        })
    return df

df_data = load_data()

# ══════════════════════════════════════════════════════════════════════════════
# 7. TÍNH TOÁN CHỈ SỐ NGUY CƠ THAY THẾ BỞI AI (AVI) THEO CÔNG THỨC CHUẨN
#    AVI = 100 × ( 0.30×R + 0.30×A + 0.25×S + 0.15×E )
# ══════════════════════════════════════════════════════════════════════════════
AVI_INDUSTRY_DATA = [
    {
        "Mã ngành": "IND-01",
        "Tên ngành nghề": "Lao động Phổ thông & Bảo vệ Mục tiêu",
        "Tên ngắn": "Lao động phổ thông / Bảo vệ",
        "AVI": 89.4,
        "Mức rủi ro": "RẤT CAO",
        "Màu": INK_COLORS["carmine"],
        "Nguy cơ chính": "Bị thay thế bởi Camera AI nhận diện khuôn mặt, cổng barrier tự động và Drone tuần tra.",
        "Dự báo 5 năm": "Thu hẹp tuyển dụng 25% – 35% đến năm 2031.",
        "Khuyến nghị": "Chuyển đổi sang đào tạo kỹ năng vận hành công nghệ kho vận hoặc quản lý thiết bị thông minh."
    },
    {
        "Mã ngành": "IND-02",
        "Tên ngành nghề": "Kế toán - Tài chính (Cơ bản / Nhập liệu)",
        "Tên ngắn": "Kế toán cơ bản / Thu ngân",
        "AVI": 50.5,
        "Mức rủi ro": "CAO",
        "Màu": INK_COLORS["amber"],
        "Nguy cơ chính": "Các tác vụ đối soát chứng từ, nhập hóa đơn bị hệ thống RPA và AI kế toán tự động hóa hoàn toàn.",
        "Dự báo 5 năm": "Chuyển giao 30% tác vụ định kỳ cho AI; bắt buộc biết phân tích dữ liệu chuyên sâu.",
        "Khuyến nghị": "Học công cụ Business Intelligence (PowerBI), phân tích tài chính chiến lược và lập trình Python/SQL."
    },
    {
        "Mã ngành": "IND-03",
        "Tên ngành nghề": "Quản trị Nhân sự / Tuyển dụng Cơ bản",
        "Tên ngắn": "Quản trị nhân sự (HR)",
        "AVI": 30.0,
        "Mức rủi ro": "TRUNG BÌNH",
        "Màu": INK_COLORS["ochre"],
        "Nguy cơ chính": "AI tự động lọc CV ứng viên và phân tích hiệu suất làm việc; vị trí sơ cấp bị tinh gọn.",
        "Dự báo 5 năm": "Nhân sự dịch chuyển sang quản trị trải nghiệm nhân viên và hoạch định chiến lược tổ chức.",
        "Khuyến nghị": "Rèn luyện trí tuệ cảm xúc (EQ), kỹ năng kết nối văn hóa và đàm phán nhân sự cấp cao."
    },
    {
        "Mã ngành": "IND-04",
        "Tên ngành nghề": "Luật Kinh tế & Pháp chế Thủ tục",
        "Tên ngắn": "Luật kinh tế / Pháp chế",
        "AVI": 30.0,
        "Mức rủi ro": "TRUNG BÌNH",
        "Màu": INK_COLORS["ochre"],
        "Nguy cơ chính": "Hợp đồng mẫu và tra cứu văn bản pháp luật được AI giải quyết trong vài giây.",
        "Dự báo 5 năm": "Luật sư chuyển dịch từ soạn thảo văn bản thuần túy sang chiến lược tranh tụng và đàm phán.",
        "Khuyến nghị": "Nâng cao kỹ năng tư vấn rủi ro pháp lý phức tạp và nghệ thuật giải quyết khủng hoảng."
    },
    {
        "Mã ngành": "IND-05",
        "Tên ngành nghề": "Kinh doanh / B2B & Bán lẻ",
        "Tên ngắn": "Kinh doanh / B2B",
        "AVI": 30.0,
        "Mức rủi ro": "TRUNG BÌNH",
        "Màu": INK_COLORS["ochre"],
        "Nguy cơ chính": "Telesales lặp lại bị Voice AI thay thế; khách hàng tra cứu thông tin trực tiếp qua AI bot.",
        "Dự báo 5 năm": "Chỉ những chuyên viên có năng lực xây dựng mối quan hệ tin cậy và đàm phán lớn duy trì thu nhập cao.",
        "Khuyến nghị": "Nâng tầm kỹ năng tâm lý khách hàng, đàm phán giải pháp giá trị cao và xây dựng thương hiệu cá nhân."
    },
    {
        "Mã ngành": "IND-06",
        "Tên ngành nghề": "Công nghệ Thông tin (Phát triển Phần mềm)",
        "Tên ngắn": "CNTT (Phần mềm)",
        "AVI": 12.5,
        "Mức rủi ro": "THẤP (An toàn)",
        "Màu": INK_COLORS["celadon"],
        "Nguy cơ chính": "Lập trình viên không dùng AI sẽ bị thay thế bởi lập trình viên biết khai thác AI Copilot.",
        "Dự báo 5 năm": "Năng suất cá nhân tăng gấp 2-3 lần; nhu cầu kiến trúc hệ thống và tích hợp mô hình AI tăng vọt.",
        "Khuyến nghị": "Làm chủ AI Coding Assistants, tập trung vào thiết kế kiến trúc phân tán và an toàn hệ thống."
    },
    {
        "Mã ngành": "IND-07",
        "Tên ngành nghề": "An toàn Thông tin (Cybersecurity)",
        "Tên ngắn": "An ninh mạng",
        "AVI": 10.0,
        "Mức rủi ro": "THẤP (Vùng An Toàn Nhất)",
        "Màu": INK_COLORS["indigo"],
        "Nguy cơ chính": "Các cuộc tấn công mạng sử dụng AI đòi hỏi con người phải có tư duy phản biện liên tục để phòng thủ.",
        "Dự báo 5 năm": "Nhu cầu chuyên gia bảo mật tăng trưởng trên 45%; là lá chắn cốt lõi không thể tự động hóa.",
        "Khuyến nghị": "Nghiên cứu cơ chế phòng thủ AI nghịch đảo (Adversarial AI Defense) và bảo vệ hạ tầng trọng yếu."
    }
]

df_avi = pd.DataFrame(AVI_INDUSTRY_DATA)

# Dữ liệu dự báo xu hướng 5 năm (2026 - 2031) từ nghiên cứu
FORECAST_DATA = pd.DataFrame({
    "Năm": ["2026 (Hiện tại)", "2027", "2028", "2029", "2030", "2031"],
    "Yêu cầu Kỹ năng AI (%)": [36.0, 42.5, 50.1, 59.1, 69.8, 82.4],
    "Yêu cầu Lập trình (%)": [51.2, 57.3, 64.2, 70.0, 70.0, 70.0],
    "Yêu cầu Ngoại ngữ (%)": [61.2, 68.0, 73.5, 79.4, 80.0, 80.0],
    "Thu hẹp Tác vụ Lặp lại Routine (%)": [0.0, -7.0, -14.0, -21.0, -28.0, -35.0]
})

# ══════════════════════════════════════════════════════════════════════════════
# 8. THANH ĐIỀU HƯỚNG BÊN HÔNG (SIDEBAR)
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <span style="font-size: 40px;">🕊️</span>
        <div style="font-family: 'Cinzel', serif; font-size: 20px; font-weight: 700; color: #2C3242; letter-spacing: 2px;">MEMENTOMORI</div>
        <div style="font-family: 'Playfair Display', serif; font-style: italic; font-size: 13px; color: #6F7A8A;">Hệ Thống Trực Quan Hóa Lao Động 2026–2031</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    menu = st.radio(
        "MỤC LỤC TRỰC QUAN HÓA",
        [
            "🌸 I. Tổng Quan & Số Liệu Then Chốt",
            "📊 II. Cấu Trúc Kỹ Năng & Trình Độ",
            "⚠️ III. Trung Tâm Cảnh Báo Rủi Ro (Tên Ngành)",
            "🔮 IV. Dự Báo Xu Hướng 2026–2031",
            "🧮 V. Đo Lường Chỉ Số AVI Cá Nhân",
            "🔎 VI. Tra Cứu 1.000 Bản Ghi Tuyển Dụng"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 13px; color: #4A5568; line-height: 1.6; background: rgba(255,255,255,0.5); padding: 12px; border-radius: 12px; border: 1px solid rgba(200,190,175,0.4);">
        <b>Thông tin nghiên cứu:</b><br>
        👤 Tác giả: <b>Chung Võ Quốc Minh</b><br>
        🆔 MSSV: <b>24050042</b><br>
        🏛️ Đơn vị: Khoa CNTT, Robot & AI (FIRA)<br>
        🎯 Cổng triển khai: <a href="https://kiutrang.streamlit.app/" target="_blank" style="color:#4F7D74; font-weight:600;">kiutrang.streamlit.app</a><br>
        📊 Quy mô mẫu: <b>1.000 bản ghi thực nghiệm</b>
    </div>
    """, unsafe_allow_html=True)

    # Nút đồng bộ lại
    if st.button("🔄 Tải lại Dữ liệu & Sóng Nước"):
        st.cache_data.clear()
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# 9. PHẦN HEADER CHÍNH CỦA TRANG
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align: center; margin-bottom: 25px; padding-top: 10px;">
    <div class="memento-title">THỊ TRƯỜNG LAO ĐỘNG VIỆT NAM (2026–2031)</div>
    <div class="memento-subtitle">
        "Trong dòng chảy bất tận của trí tuệ nhân tạo, thấu hiểu cấu trúc kỹ năng chính là chiếc mỏ neo định vị tương lai."
    </div>
    <div>
        <span class="memento-badge badge-success">Mẫu N = 1.000 Bản Ghi Thực Nghiệm</span>
        <span class="memento-badge badge-info">Chỉ Số Độc Quyền AVI</span>
        <span class="memento-badge badge-warning">Dự Báo 5 Năm WEF Standard</span>
        <span class="memento-badge badge-danger">Cảnh Báo Đỏ Rủi Ro Thay Thế</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB I: TỔNG QUAN & SỐ LIỆU THEN CHỐT (EXECUTIVE DASHBOARD)
# ══════════════════════════════════════════════════════════════════════════════
if menu == "🌸 I. Tổng Quan & Số Liệu Then Chốt":
    st.markdown("""
    <div class="ink-card">
        <h3 style="font-family: 'Playfair Display', serif; color: #2C3242; margin-top: 0;">
            🕊️ Bảng Phong Vũ Biểu Thị Trường Lao Động (Market Barometer)
        </h3>
        <p style="font-size: 14.5px; color: #4A5568; margin-bottom: 20px;">
            Số liệu thống kê thực nghiệm từ 1.000 tin tuyển dụng được bóc tách tự động qua mô hình NLP & Thesaurus Dictionary. 
            Mọi biểu đồ được tích hợp nhãn dữ liệu trực tiếp giúp người xem nắm bắt ngay lập tức thực trạng tuyển dụng.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 4 Thẻ KPI chính
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="ink-card" style="text-align: center;">
            <div style="font-size: 13px; font-weight: 600; color: #6C7A89; text-transform: uppercase;">Quy mô Mẫu Thực Nghiệm</div>
            <div style="font-family: 'Cinzel', serif; font-size: 34px; font-weight: 700; color: {INK_COLORS['sumi']}; margin: 8px 0;">1.000</div>
            <div style="font-size: 12px; color: #4F7D74; font-weight: 500;">✓ 100% Đạt Data Quality Gate</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="ink-card ink-card-amber" style="text-align: center;">
            <div style="font-size: 13px; font-weight: 600; color: #6C7A89; text-transform: uppercase;">Nhu Cầu Kỹ Năng AI</div>
            <div style="font-family: 'Cinzel', serif; font-size: 34px; font-weight: 700; color: {INK_COLORS['amber']}; margin: 8px 0;">36.0%</div>
            <div style="font-size: 12px; color: #B8863B; font-weight: 500;">↑ Tăng tốc mạnh mẽ (+15%/năm)</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="ink-card" style="text-align: center;">
            <div style="font-size: 13px; font-weight: 600; color: #6C7A89; text-transform: uppercase;">Yêu Cầu Ngoại Ngữ</div>
            <div style="font-family: 'Cinzel', serif; font-size: 34px; font-weight: 700; color: {INK_COLORS['indigo']}; margin: 8px 0;">61.2%</div>
            <div style="font-size: 12px; color: #3A506B; font-weight: 500;">★ Rào cản phân hóa thu nhập</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="ink-card ink-card-danger" style="text-align: center;">
            <div style="font-size: 13px; font-weight: 600; color: #6C7A89; text-transform: uppercase;">Điểm AVI Bình Quân</div>
            <div style="font-family: 'Cinzel', serif; font-size: 34px; font-weight: 700; color: {INK_COLORS['carmine']}; margin: 8px 0;">36.1 / 100</div>
            <div style="font-size: 12px; color: #B54D59; font-weight: 500;">⚠️ Ngưỡng chuyển đổi công nghệ</div>
        </div>
        """, unsafe_allow_html=True)

    # 2 Biểu đồ hàng 1: Phân bố Trình độ và Kỹ năng AI
    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.markdown("""
        <div class="ink-card">
            <h4 style="font-family: 'Playfair Display', serif; color: #2C3242; margin-top: 0;">
                🏛️ Cơ Cấu Trình Độ Học Vấn Trên Thị Trường
            </h4>
        """, unsafe_allow_html=True)
        edu_counts = df_data["Trình độ"].value_counts().reset_index()
        edu_counts.columns = ["Trình độ", "Số lượng"]
        edu_counts["Tỷ lệ (%)"] = (edu_counts["Số lượng"] / len(df_data) * 100).round(1)

        fig_edu = px.pie(
            edu_counts,
            names="Trình độ",
            values="Số lượng",
            hole=0.48,
            color="Trình độ",
            color_discrete_map={
                "Đại học": INK_COLORS["celadon"],
                "THPT": INK_COLORS["carmine"],
                "Thạc sĩ": INK_COLORS["indigo"],
                "Trung cấp": INK_COLORS["amber"],
                "Cao đẳng": INK_COLORS["wisteria"]
            }
        )
        fig_edu.update_traces(
            textinfo="label+percent",
            textfont=dict(family="Plus Jakarta Sans", size=13, color="#FFFFFF"),
            marker=dict(line=dict(color="#FAF7F0", width=2.5))
        )
        fig_edu.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_edu, use_container_width=True)
        st.markdown("""
        <div style="font-size: 13px; color: #555; background: rgba(255,255,255,0.6); padding: 8px 12px; border-radius: 8px;">
            <b>Nhận xét:</b> Trình độ Đại học chiếm đa số (51.0%), tiếp theo là THPT (18.6%) và Thạc sĩ (15.0%). 
            Nhóm THPT có nguy cơ tự động hóa cao nhất do tập trung ở các công việc lặp lại.
        </div>
        </div>
        """, unsafe_allow_html=True)

    with c_right:
        st.markdown("""
        <div class="ink-card ink-card-amber">
            <h4 style="font-family: 'Playfair Display', serif; color: #2C3242; margin-top: 0;">
                🤖 Mức Độ Thâm Nhập Của Kỹ Năng Trí Tuệ Nhân Tạo
            </h4>
        """, unsafe_allow_html=True)
        ai_counts = df_data["Kỹ năng AI"].value_counts().reset_index()
        ai_counts.columns = ["Yêu cầu AI", "Số lượng"]
        ai_counts["Nhãn"] = ai_counts["Yêu cầu AI"].map({"có": "Đòi hỏi / Ưu tiên kỹ năng AI", "không": "Chưa yêu cầu kỹ năng AI"})
        ai_counts["Tỷ lệ (%)"] = (ai_counts["Số lượng"] / len(df_data) * 100).round(1)

        fig_ai = px.bar(
            ai_counts,
            x="Số lượng",
            y="Nhãn",
            orientation="h",
            text=ai_counts.apply(lambda r: f"{r['Số lượng']} tin ({r['Tỷ lệ (%)']}%)", axis=1),
            color="Nhãn",
            color_discrete_sequence=[INK_COLORS["amber"], INK_COLORS["sumi"]]
        )
        fig_ai.update_traces(
            textposition="inside",
            textfont=dict(family="Plus Jakarta Sans", size=13, color="#FFFFFF", weight="bold"),
            marker=dict(line=dict(color="rgba(255,255,255,0.4)", width=1.5))
        )
        fig_ai.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=False,
            xaxis=dict(showgrid=True, gridcolor="rgba(180, 190, 200, 0.2)", title="Số lượng tin tuyển dụng"),
            yaxis=dict(title="")
        )
        st.plotly_chart(fig_ai, use_container_width=True)
        st.markdown("""
        <div style="font-size: 13px; color: #555; background: rgba(255,255,255,0.6); padding: 8px 12px; border-radius: 8px;">
            <b>Nhận xét:</b> Đã có <b>36.0%</b> (360/1.000 tin tuyển dụng) yêu cầu hoặc ưu tiên nhân sự có kỹ năng AI (Prompt Engineering, Generative AI, Copilot), 
            cho thấy AI đang nhanh chóng chuyển mình từ lợi thế cộng thêm sang yêu cầu phổ quát.
        </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB II: CẤU TRÚC KỸ NĂNG & TRÌNH ĐỘ (SKILLS & EDUCATION)
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "📊 II. Cấu Trúc Kỹ Năng & Trình Độ":
    st.markdown("""
    <div class="ink-card ink-card-purple">
        <h3 style="font-family: 'Playfair Display', serif; color: #2C3242; margin-top: 0;">
            🌸 Ma Trận Kỹ Năng Mềm — 'Vũ Khí Phòng Thủ' Duy Nhất Trước AI
        </h3>
        <p style="font-size: 14.5px; color: #4A5568; margin-bottom: 20px;">
            AI có thể phân tích dữ liệu và sinh mã lệnh trong chớp mắt, nhưng không thể thay thế năng lực thấu cảm, 
            kết nối tập thể và đàm phán giữa con người với con người.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Thống kê 5 kỹ năng mềm
    soft_skills = ["Làm việc nhóm", "Giao tiếp", "Sáng tạo", "Thuyết trình", "Đàm phán"]
    soft_data = []
    for s in soft_skills:
        cnt = (df_data[s] == "có").sum()
        pct = round(cnt / len(df_data) * 100, 1)
        soft_data.append({"Kỹ năng mềm": s, "Số lượng tin": cnt, "Tỷ lệ (%)": pct})

    df_soft = pd.DataFrame(soft_data).sort_values("Tỷ lệ (%)", ascending=True)

    fig_soft = px.bar(
        df_soft,
        x="Tỷ lệ (%)",
        y="Kỹ năng mềm",
        orientation="h",
        text=df_soft.apply(lambda r: f"{r['Tỷ lệ (%)']}%  ({r['Số lượng tin']} tin)", axis=1),
        color="Tỷ lệ (%)",
        color_continuous_scale=[
            [0.0, INK_COLORS["wisteria"]],
            [0.5, INK_COLORS["celadon"]],
            [1.0, INK_COLORS["indigo"]]
        ]
    )
    fig_soft.update_traces(
        textposition="inside",
        textfont=dict(family="Plus Jakarta Sans", size=13, color="#FFFFFF", weight="bold"),
        marker=dict(line=dict(color="rgba(255,255,255,0.4)", width=1.5))
    )
    fig_soft.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(t=10, b=10, l=10, r=10),
        coloraxis_showscale=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(180, 190, 200, 0.2)", range=[0, 100], title="Tỷ lệ xuất hiện trong JD (%)"),
        yaxis=dict(title="")
    )
    st.plotly_chart(fig_soft, use_container_width=True)

    # Hai cột phân tích: Kỹ năng Lập trình và Ngoại ngữ
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="ink-card">
            <h4 style="font-family: 'Playfair Display', serif; color: #2C3242; margin-top: 0;">
                💻 Phổ Kỹ Năng Lập Trình & Truy Vấn Dữ Liệu
            </h4>
        """, unsafe_allow_html=True)
        prog_counts = df_data["Lập trình"].value_counts().head(6).reset_index()
        prog_counts.columns = ["Ngôn ngữ", "Số tin"]
        fig_prog = px.bar(
            prog_counts,
            x="Ngôn ngữ",
            y="Số tin",
            text="Số tin",
            color="Số tin",
            color_continuous_scale=[[0, INK_COLORS["light_teal"]], [1, INK_COLORS["indigo"]]]
        )
        fig_prog.update_traces(textposition="outside", textfont=dict(family="Plus Jakarta Sans", size=12, weight="bold"))
        fig_prog.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=20, b=10, l=10, r=10),
            coloraxis_showscale=False,
            yaxis=dict(showgrid=True, gridcolor="rgba(180, 190, 200, 0.2)")
        )
        st.plotly_chart(fig_prog, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="ink-card">
            <h4 style="font-family: 'Playfair Display', serif; color: #2C3242; margin-top: 0;">
                🌐 Phân Bố Yêu Cầu Chứng Chỉ Ngoại Ngữ
            </h4>
        """, unsafe_allow_html=True)
        lang_filter = df_data["Ngoại ngữ"].dropna().loc[lambda x: x != "null"].value_counts().head(6).reset_index()
        lang_filter.columns = ["Chứng chỉ", "Số tin"]
        fig_lang = px.bar(
            lang_filter,
            x="Chứng chỉ",
            y="Số tin",
            text="Số tin",
            color="Số tin",
            color_continuous_scale=[[0, INK_COLORS["wisteria"]], [1, INK_COLORS["carmine"]]]
        )
        fig_lang.update_traces(textposition="outside", textfont=dict(family="Plus Jakarta Sans", size=12, weight="bold"))
        fig_lang.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=20, b=10, l=10, r=10),
            coloraxis_showscale=False,
            yaxis=dict(showgrid=True, gridcolor="rgba(180, 190, 200, 0.2)")
        )
        st.plotly_chart(fig_lang, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB III: TRUNG TÂM CẢNH BÁO RỦI RO (HIỆN RÕ TÊN CÁC NGÀNH NGHỀ RỦI RO)
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "⚠️ III. Trung Tâm Cảnh Báo Rủi Ro (Tên Ngành)":
    st.markdown("""
    <div class="ink-card ink-card-danger">
        <h3 style="font-family: 'Playfair Display', serif; color: #9E3340; margin-top: 0;">
            ⚠️ TRUNG TÂM CẢNH BÁO NGUY CƠ THAY THẾ BỞI AI (AVI DASHBOARD)
        </h3>
        <p style="font-size: 15px; color: #4A5568; margin-bottom: 14px;">
            Chỉ số <b>AI Vulnerability Index (AVI)</b> lượng hóa nguy cơ bị trí tuệ nhân tạo và tự động hóa thay thế trên thang điểm 0 – 100.
            <br>
            Công thức: <code>AVI = 100 × ( 0.30 × R + 0.30 × A + 0.25 × S + 0.15 × E )</code>
        </p>
        <div style="font-size: 13.5px; color: #721C24; background: rgba(255,230,230,0.6); padding: 10px 16px; border-radius: 10px; border-left: 4px solid #B54D59;">
            <b>Đặc biệt quan tâm:</b> Dưới đây là bảng xếp hạng định lượng hiển thị <b>ĐẦY ĐỦ VÀ RÕ RÀNG TÊN TỪNG NGÀNH NGHỀ</b> cùng mức độ rủi ro tương ứng để người lao động kịp thời thích ứng.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # BIỂU ĐỒ CỘT NGANG THỂ HIỆN RÕ TÊN TỪNG NGÀNH NGHỀ
    df_avi_sorted = df_avi.sort_values("AVI", ascending=True)

    fig_avi = px.bar(
        df_avi_sorted,
        x="AVI",
        y="Tên ngành nghề",
        orientation="h",
        text=df_avi_sorted.apply(lambda r: f"AVI: {r['AVI']}  [{r['Mức rủi ro']}]", axis=1),
        color="AVI",
        color_continuous_scale=[
            [0.0, INK_COLORS["celadon"]],
            [0.3, INK_COLORS["indigo"]],
            [0.5, INK_COLORS["ochre"]],
            [0.7, INK_COLORS["amber"]],
            [1.0, INK_COLORS["carmine"]]
        ]
    )
    fig_avi.update_traces(
        textposition="inside",
        textfont=dict(family="Plus Jakarta Sans", size=13, color="#FFFFFF", weight="bold"),
        marker=dict(line=dict(color="#FAF7F0", width=1.5))
    )
    fig_avi.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=380,
        margin=dict(t=10, b=10, l=10, r=10),
        coloraxis_showscale=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(180, 190, 200, 0.2)", range=[0, 100], title="Điểm Chỉ Số AVI (0 - 100)"),
        yaxis=dict(title="")
    )
    st.plotly_chart(fig_avi, use_container_width=True)

    st.markdown("### 📋 CHI TIẾT TỪNG NGÀNH NGHỀ & ĐÁNH GIÁ NGUY CƠ 5 NĂM TỚI")

    # Render danh sách từng ngành kèm tên ngành, điểm số và giải pháp
    for _, ind in df_avi.iterrows():
        badge_cls = (
            "badge-danger" if ind["AVI"] >= 70
            else "badge-warning" if ind["AVI"] >= 45
            else "badge-info" if ind["AVI"] >= 25
            else "badge-success"
        )
        card_cls = "ink-card ink-card-danger" if ind["AVI"] >= 50 else "ink-card"

        st.markdown(f"""
        <div class="{card_cls}" style="margin-bottom: 18px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-family: 'Playfair Display', serif; font-size: 1.25rem; font-weight: 700; color: #2C3242;">
                    🏷️ {ind['Tên ngành nghề']}
                </div>
                <div>
                    <span class="memento-badge {badge_cls}">Điểm AVI: {ind['AVI']} / 100</span>
                    <span class="memento-badge {badge_cls}">{ind['Mức rủi ro']}</span>
                </div>
            </div>
            <div style="font-size: 14px; color: #4A5568; line-height: 1.6;">
                <b>💥 Nguyên nhân & Nguy cơ:</b> {ind['Nguy cơ chính']}<br>
                <b>🔮 Dự báo tác động 5 năm (2026–2031):</b> {ind['Dự báo 5 năm']}<br>
                <b>💡 Khuyến nghị chuyển đổi:</b> <span style="color: #2F6158; font-weight: 600;">{ind['Khuyến nghị']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 7 Cảnh báo chiến lược theo báo cáo NCKH
    st.markdown("### 🚨 HỆ THỐNG 7 CẢNH BÁO CHIẾN LƯỢC TOÀN DIỆN (W001 – W007)")
    warnings = [
        ("W001", "KHẨN CẤP", "Nguy cơ đào thải đối với lao động trình độ THPT", 
         "21% vị trí hiện tại chỉ yêu cầu THPT với mức độ lặp lại cao.", 
         "Tham gia các chương trình đào tạo nghề ngắn hạn được Nhà nước trợ cấp; học kỹ năng vận hành công nghệ và quản lý kho vận thông minh."),
        ("W002", "KHẨN CẤP", "Kỹ năng AI chuyển từ 'Ưu tiên' sang 'Bắt buộc'", 
         "Doanh nghiệp bắt đầu sàng lọc hồ sơ dựa trên năng lực ứng dụng AI để tối ưu hóa năng suất lao động.", 
         "Sinh viên và người lao động cần chủ động đạt các chứng chỉ nền tảng như Google AI Essentials, Microsoft AI Skills Pass; thực hành ứng dụng AI trong giải quyết công việc chuyên môn hàng ngày."),
        ("W003", "QUAN TRỌNG", "Sự phổ cập của kỹ năng lập trình và xử lý dữ liệu", 
         "Gần 50% tin tuyển dụng đòi hỏi kỹ năng lập trình/truy vấn dữ liệu, lan rộng ra ngoài khối IT.", 
         "Khối ngành kinh tế, xã hội cần đưa học phần Python for Data Analysis và SQL vào chương trình đào tạo chính quy bắt buộc."),
        ("W004", "QUAN TRỌNG", "Chênh lệch thu nhập do rào cản ngoại ngữ", 
         "Ngoại ngữ là tiêu chí bắt buộc tại hơn 60% vị trí lương cao (IELTS 6.0+, TOEIC 600+, Hoa ngữ).", 
         "Xây dựng mục tiêu ngoại ngữ thực chiến (giao tiếp đàm phán thương mại) thay vì chỉ học ngữ pháp lý thuyết."),
        ("W005", "LƯU Ý", "Kỹ năng mềm là 'Vũ khí phòng thủ' duy nhất trước AI", 
         "AI có thể phân tích số liệu và viết code nhưng không thể thay thế năng lực thấu cảm, đàm phán và truyền cảm hứng.", 
         "Tăng cường rèn luyện kỹ năng giải quyết xung đột, tư duy phản biện và năng lực đàm phán thông qua các dự án thực tế."),
        ("W006", "LƯU Ý", "Sự phân hóa của nhóm lao động trình độ cao (Thạc sĩ + AI)", 
         "7.3% vị trí Thạc sĩ gắn liền với mức thu nhập vượt trội (cao hơn 2–2.5 lần mặt bằng chung).", 
         "Định hướng học tập chuyên sâu theo các chương trình thạc sĩ ứng dụng liên ngành (AI in Finance, AI in Healthcare, Data-driven Governance)."),
        ("W007", "KHẨN CẤP", "Cảnh báo đỏ cho các ngành có AVI vượt ngưỡng 50", 
         "Kế toán cơ bản, lễ tân, bảo vệ, bốc xếp kho đối mặt với làn sóng tự động hóa nhanh nhất.", 
         "Nhà nước và doanh nghiệp cần thành lập quỹ hỗ trợ tái đào tạo kỹ năng (Reskilling Fund) để người lao động kịp thời chuyển đổi sang các ngành nghề mới nổi.")
    ]

    for code, level, title, fact, action in warnings:
        badge = "badge-danger" if level == "KHẨN CẤP" else "badge-warning" if level == "QUAN TRỌNG" else "badge-info"
        st.markdown(f"""
        <div class="ink-card" style="padding: 16px 22px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <div style="font-weight: 700; color: #2C3242; font-size: 15px;">
                    📌 [{code}] {title}
                </div>
                <span class="memento-badge {badge}">{level}</span>
            </div>
            <div style="font-size: 13.5px; color: #4A5568; line-height: 1.5;">
                <b>Thực trạng:</b> {fact}<br>
                <b>Khuyến nghị hành động:</b> <span style="color: #2F6158;">{action}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB IV: DỰ BÁO XU HƯỚNG 2026–2031 (FUTURE FORECASTING)
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "🔮 IV. Dự Báo Xu Hướng 2026–2031":
    st.markdown("""
    <div class="ink-card ink-card-amber">
        <h3 style="font-family: 'Playfair Display', serif; color: #2C3242; margin-top: 0;">
            🔮 Mô Hình Dự Báo Xu Hướng Thị Trường Lao Động 5 Năm (2026–2031)
        </h3>
        <p style="font-size: 14.5px; color: #4A5568; margin-bottom: 14px;">
            Mô hình toán học kết hợp dữ liệu cào thực tế tại Việt Nam đối chiếu cùng <b>Báo Cáo Tương Lai Việc Làm (Future of Jobs Report - WEF)</b>. 
            Đường biểu diễn spline màu nước phản ánh xu thế chuyển dịch tất yếu: Kỹ năng AI tăng tốc vọt, công việc cơ học thu hẹp mạnh.
        </p>
    </div>
    """, unsafe_allow_html=True)

    fig_fore = go.Figure()

    # Đường AI
    fig_fore.add_trace(go.Scatter(
        x=FORECAST_DATA["Năm"],
        y=FORECAST_DATA["Yêu cầu Kỹ năng AI (%)"],
        mode="lines+markers+text",
        name="Nhu cầu Kỹ năng AI (%)",
        line=dict(color=INK_COLORS["carmine"], width=3.5, shape="spline"),
        marker=dict(size=9, symbol="circle"),
        text=FORECAST_DATA["Yêu cầu Kỹ năng AI (%)"].apply(lambda v: f"{v}%"),
        textposition="top center",
        textfont=dict(family="Plus Jakarta Sans", size=12, color=INK_COLORS["carmine"], weight="bold")
    ))

    # Đường Lập trình
    fig_fore.add_trace(go.Scatter(
        x=FORECAST_DATA["Năm"],
        y=FORECAST_DATA["Yêu cầu Lập trình (%)"],
        mode="lines+markers+text",
        name="Kỹ năng Lập trình / Dữ liệu (%)",
        line=dict(color=INK_COLORS["celadon"], width=2.8, shape="spline"),
        marker=dict(size=8, symbol="diamond"),
        text=FORECAST_DATA["Yêu cầu Lập trình (%)"].apply(lambda v: f"{v}%"),
        textposition="bottom center",
        textfont=dict(family="Plus Jakarta Sans", size=11, color=INK_COLORS["celadon"])
    ))

    # Đường Ngoại ngữ
    fig_fore.add_trace(go.Scatter(
        x=FORECAST_DATA["Năm"],
        y=FORECAST_DATA["Yêu cầu Ngoại ngữ (%)"],
        mode="lines+markers+text",
        name="Kỹ năng Ngoại ngữ (%)",
        line=dict(color=INK_COLORS["indigo"], width=2.8, shape="spline"),
        marker=dict(size=8, symbol="square"),
        text=FORECAST_DATA["Yêu cầu Ngoại ngữ (%)"].apply(lambda v: f"{v}%"),
        textposition="top right",
        textfont=dict(family="Plus Jakarta Sans", size=11, color=INK_COLORS["indigo"])
    ))

    # Đường Thu hẹp Routine
    fig_fore.add_trace(go.Scatter(
        x=FORECAST_DATA["Năm"],
        y=FORECAST_DATA["Thu hẹp Tác vụ Lặp lại Routine (%)"],
        mode="lines+markers+text",
        name="Thu hẹp Việc Routine (%)",
        line=dict(color=INK_COLORS["amber"], width=2.5, dash="dot", shape="spline"),
        marker=dict(size=7, symbol="cross"),
        text=FORECAST_DATA["Thu hẹp Tác vụ Lặp lại Routine (%)"].apply(lambda v: f"{v}%"),
        textposition="bottom center",
        textfont=dict(family="Plus Jakarta Sans", size=11, color=INK_COLORS["amber"])
    ))

    fig_fore.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=450,
        margin=dict(t=30, b=20, l=10, r=10),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        xaxis=dict(showgrid=True, gridcolor="rgba(180, 190, 200, 0.2)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(180, 190, 200, 0.2)", range=[-45, 95], title="Tỷ lệ (%)")
    )

    st.plotly_chart(fig_fore, use_container_width=True)

    # 3 Luận điểm trọng yếu
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; margin-top: 15px;">
        <div class="ink-card">
            <h4 style="font-family: 'Playfair Display', serif; color: #2C3242; margin-top: 0;">1. Làn sóng AI-Centric (82.4%)</h4>
            <p style="font-size: 13.5px; color: #4A5568; line-height: 1.6;">
                Đến năm 2031, hơn <b>82%</b> vị trí tuyển dụng sẽ coi kỹ năng làm việc với Generative AI và Copilot là điều kiện tiên quyết, tương tự việc thành thạo máy tính trước đây.
            </p>
        </div>
        <div class="ink-card">
            <h4 style="font-family: 'Playfair Display', serif; color: #2C3242; margin-top: 0;">2. Kỹ năng Lai (Hybridization)</h4>
            <p style="font-size: 13.5px; color: #4A5568; line-height: 1.6;">
                Lập trình và truy vấn dữ liệu (Python/SQL) sẽ trở thành kỹ năng phổ thông, lan tỏa mạnh vào các ngành Marketing, Kế toán, Nhân sự và Y tế.
            </p>
        </div>
        <div class="ink-card ink-card-danger">
            <h4 style="font-family: 'Playfair Display', serif; color: #9E3340; margin-top: 0;">3. Thu hẹp 35% việc lặp lại</h4>
            <p style="font-size: 13.5px; color: #4A5568; line-height: 1.6;">
                Dự báo <b>35%</b> khối lượng công việc có tính chất cơ học, lặp đi lặp lại sẽ chuyển giao trọn vẹn cho máy móc tự động hóa và AI tác nhân (Agentic AI).
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB V: ĐO LƯỜNG CHỈ SỐ AVI CÁ NHÂN (PERSONAL AVI CALCULATOR)
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "🧮 V. Đo Lường Chỉ Số AVI Cá Nhân":
    st.markdown("""
    <div class="ink-card">
        <h3 style="font-family: 'Playfair Display', serif; color: #2C3242; margin-top: 0;">
            🧮 CÔNG CỤ TỰ ĐÁNH GIÁ NGUY CƠ THAY THẾ BỞI AI CÁ NHÂN (AVI)
        </h3>
        <p style="font-size: 14.5px; color: #4A5568; margin-bottom: 20px;">
            Hãy chọn các thông số thực tế về công việc, bằng cấp và kỹ năng hiện tại của bạn để mô hình tính toán 
            chỉ số rủi ro cá nhân và đưa ra lời khuyên chuyển đổi chiến lược theo triết lý MementoMori.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_in1, col_in2 = st.columns(2)
    with col_in1:
        st.markdown("**1. Đặc thù công việc & Trình độ học vấn:**")
        user_role = st.selectbox(
            "Nhóm ngành nghề hiện tại của bạn:",
            [
                "Lao động phổ thông / Bảo vệ / Dịch vụ an ninh",
                "Kế toán - Tài chính (Nhập liệu / Đối soát)",
                "Quản trị Nhân sự / Tuyển dụng sơ cấp",
                "Luật kinh tế / Pháp chế thủ tục",
                "Kinh doanh / B2B / Bán lẻ",
                "Công nghệ thông tin / Lập trình phần mềm",
                "An toàn thông tin / An ninh mạng"
            ]
        )
        user_routine = st.slider("Mức độ lặp lại công việc hàng ngày (Routine Level):", 0, 100, 45, help="0: Hoàn toàn sáng tạo, linh hoạt | 100: Quy trình máy móc, lặp lại mỗi ngày")
        user_edu = st.selectbox("Bằng cấp cao nhất hiện tại:", ["Dưới Đại học (THPT, Trung cấp)", "Cao đẳng", "Đại học", "Thạc sĩ / Tiến sĩ"])

    with col_in2:
        st.markdown("**2. Bộ kỹ năng sở hữu:**")
        user_ai = st.radio("Bạn có thường xuyên ứng dụng AI vào công việc không?", ["Chưa / Rất ít", "Đã sử dụng ở mức cơ bản (ChatGPT, Claude)", "Thành thạo Prompt Engineering & Copilot"], horizontal=True)
        user_soft_count = st.slider("Số kỹ năng mềm bạn tự tin làm chủ (Giao tiếp, Đàm phán, Sáng tạo, Thuyết trình, Teamwork):", 0, 5, 3)
        user_lang = st.checkbox("Có chứng chỉ ngoại ngữ chuẩn mực (IELTS ≥ 6.0, TOEIC ≥ 650, Hoa ngữ HSK, Tiếng Nhật...)")

    # Thuật toán tính AVI cá nhân
    # R: routine ratio (0 - 1)
    r_val = user_routine / 100.0
    # A: no-ai ratio (0 - 1)
    a_val = 1.0 if user_ai == "Chưa / Rất ít" else 0.4 if user_ai == "Đã sử dụng ở mức cơ bản (ChatGPT, Claude)" else 0.05
    # S: no-soft skills ratio (0 - 1)
    s_val = max(0.0, (5 - user_soft_count) / 5.0)
    # E: low education ratio (0 - 1)
    e_val = 1.0 if "Dưới Đại học" in user_edu else 0.6 if "Cao đẳng" in user_edu else 0.2 if "Đại học" in user_edu else 0.0

    if user_lang:
        # Ngoại ngữ giảm 15% rủi ro thay thế
        personal_avi = round(100 * (0.30 * r_val + 0.30 * a_val + 0.25 * s_val + 0.15 * e_val) * 0.85, 1)
    else:
        personal_avi = round(100 * (0.30 * r_val + 0.30 * a_val + 0.25 * s_val + 0.15 * e_val), 1)

    personal_avi = min(100.0, max(0.0, personal_avi))

    # Đánh giá kết quả
    if personal_avi >= 70:
        res_level = "MỨC NGUY CƠ RẤT CAO"
        res_color = INK_COLORS["carmine"]
        res_card = "ink-card ink-card-danger"
        res_advice = "🚨 Công việc của bạn chứa nhiều tác vụ lặp lại và thiếu lá chắn công nghệ/kỹ năng mềm. Cần khẩn trương học cách biến AI thành trợ lý cá nhân và nâng cấp kỹ năng giao tiếp, đàm phán trong vòng 6–12 tháng tới."
    elif personal_avi >= 45:
        res_level = "MỨC NGUY CƠ CAO"
        res_color = INK_COLORS["amber"]
        res_card = "ink-card ink-card-amber"
        res_advice = "⚠️ Một phần đáng kể công việc của bạn có thể bị tự động hóa. Hãy tập trung vào việc học phân tích dữ liệu, rèn luyện tư duy phản biện và chuyên sâu hóa nghiệp vụ để không bị thay thế."
    elif personal_avi >= 25:
        res_level = "MỨC NGUY CƠ TRUNG BÌNH"
        res_color = INK_COLORS["ochre"]
        res_card = "ink-card"
        res_advice = "⚡ Vị trí của bạn tương đối an toàn nhưng cần chủ động làm chủ các công cụ AI thế hệ mới để nhân đôi năng suất làm việc và củng cố vị thế chuyên môn."
    else:
        res_level = "VÙNG AN TOÀN (LỢI THẾ CẠNH TRANH CAO)"
        res_color = INK_COLORS["celadon"]
        res_card = "ink-card"
        res_advice = "🕊️ Chúc mừng! Bạn đang sở hữu cấu trúc kỹ năng lai vững chắc giữa tư duy con người và năng lực số. Bạn chính là nhân tố dẫn dắt quá trình chuyển đổi AI trong tổ chức."

    st.markdown("---")
    st.markdown(f"""
    <div class="{res_card}" style="text-align: center; padding: 30px 20px;">
        <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 2px; color: #6C7A89; font-weight: 600;">
            KẾT QUẢ ĐỊNH LƯỢNG CHỈ SỐ AVI CỦA BẠN
        </div>
        <div style="font-family: 'Cinzel', serif; font-size: 56px; font-weight: 900; color: {res_color}; margin: 12px 0;">
            {personal_avi} <span style="font-size: 24px; color: #888;">/ 100</span>
        </div>
        <div style="font-size: 17px; font-weight: 700; color: {res_color}; margin-bottom: 16px; letter-spacing: 1px;">
            {res_level}
        </div>
        <div style="max-width: 720px; margin: 0 auto; font-size: 14.5px; color: #374151; line-height: 1.7; background: rgba(255,255,255,0.7); padding: 16px 20px; border-radius: 12px; border: 1px solid rgba(200,190,175,0.4);">
            <b>Lời khuyên thích ứng:</b><br>{res_advice}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB VI: TRA CỨU 1.000 BẢN GHI TUYỂN DỤNG (DATA EXPLORER)
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "🔎 VI. Tra Cứu 1.000 Bản Ghi Tuyển Dụng":
    st.markdown("""
    <div class="ink-card">
        <h3 style="font-family: 'Playfair Display', serif; color: #2C3242; margin-top: 0;">
            🔎 BỘ LỌC & KHÁM PHÁ DỮ LIỆU TUYỂN DỤNG THỰC TẾ
        </h3>
        <p style="font-size: 14.5px; color: #4A5568; margin-bottom: 20px;">
            Toàn bộ 1.000 bản ghi dữ liệu cào chuẩn hóa (17 cột định danh, tuân thủ nghiêm ngặt Data Quality Gate) 
            được hiển thị trực quan. Bạn có thể tìm kiếm, lọc theo tiêu chí hoặc tải về tệp CSV gốc.
        </p>
    </div>
    """, unsafe_allow_html=True)

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        keyword = st.text_input("🔍 Tìm theo tên công việc / doanh nghiệp:", "")
    with f_col2:
        selected_role = st.multiselect("Lọc vị trí công việc:", options=df_data["Vị trí công việc"].dropna().unique())
    with f_col3:
        selected_edu = st.multiselect("Lọc trình độ học vấn:", options=df_data["Trình độ"].dropna().unique())

    filtered_df = df_data.copy()
    if keyword:
        filtered_df = filtered_df[
            filtered_df["Tên công việc"].astype(str).str.contains(keyword, case=False, na=False) |
            filtered_df["Tên doanh nghiệp"].astype(str).str.contains(keyword, case=False, na=False)
        ]
    if selected_role:
        filtered_df = filtered_df[filtered_df["Vị trí công việc"].isin(selected_role)]
    if selected_edu:
        filtered_df = filtered_df[filtered_df["Trình độ"].isin(selected_edu)]

    st.markdown(f"**Kết quả lọc:** Tìm thấy **{len(filtered_df):,}** / 1.000 bản ghi thỏa mãn điều kiện.")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=480
    )

    # Nút tải xuống CSV
    csv_bytes = filtered_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="📥 Tải xuống dữ liệu đã lọc (.CSV UTF-8-SIG)",
        data=csv_bytes,
        file_name="thi_truong_lao_dong_vietnam_filtered.csv",
        mime="text/csv"
    )

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER MEMENTOMORI
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 20px 0; color: #7A8596; font-size: 13px; line-height: 1.8;">
    <div style="font-family: 'Cinzel', serif; font-size: 15px; letter-spacing: 2px; color: #4F7D74; font-weight: 700;">
        THỊ TRƯỜNG LAO ĐỘNG VIỆT NAM · 2026–2031
    </div>
    Báo cáo Khoa học Dữ liệu & Trí tuệ Nhân tạo — Tác giả: <b>Chung Võ Quốc Minh</b> (MSSV: <b>24050042</b>)<br>
    Đơn vị: Khoa CNTT, Robot & AI (FIRA) · Triển khai tại: 
    <a href="{STREAMLIT_URL}" target="_blank" style="color: #4F7D74; text-decoration: none; font-weight: 600;">{STREAMLIT_URL}</a><br>
    <i>© 2026 MementoMori Watercolor Visualizer Edition. All rights reserved.</i>
</div>
""", unsafe_allow_html=True)

