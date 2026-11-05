# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          DASHBOARD THỊ TRƯỜNG LAO ĐỘNG VIỆT NAM 2026–2031                   ║
║          Automated Lightweight AI Pipeline — Module 3: Dashboard            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Yêu cầu 4: Dashboard cảnh báo & dự báo thị trường lao động Việt Nam       ║
║  Framework : Streamlit + Plotly                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Cài đặt: pip install streamlit plotly pandas
Chạy   : streamlit run dashboard.py
"""

import os, sys, json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Đường dẫn tương đối (hoạt động cả local lẫn Streamlit Cloud) ─────────────
BASE_DIR    = Path(__file__).parent
DATA_CSV    = str(BASE_DIR / "thi_truong_lao_dong_vietnam.csv")
REPORT_JSON = str(BASE_DIR / "analysis_report.json")

def _ensure_report():
    """Tự động sinh CSV + JSON nếu chưa tồn tại (hỗ trợ Cloud deploy)."""
    if not os.path.exists(DATA_CSV):
        st.info("⏳ Lần đầu khởi động — đang tạo dữ liệu (~5 giây)...")
        try:
            import subprocess
            subprocess.run(
                [sys.executable, str(BASE_DIR / "job_crawler.py"),
                 "--target", "1000", "--output", DATA_CSV],
                check=False, cwd=str(BASE_DIR)
            )
        except Exception:
            # Fallback: gọi trực tiếp module nếu subprocess không khả dụng
            sys.path.insert(0, str(BASE_DIR))
            from job_crawler import MasterJobCrawler
            MasterJobCrawler(target_count=1000, output_path=DATA_CSV).run()

    if not os.path.exists(REPORT_JSON):
        st.info("📊 Đang phân tích dữ liệu, vui lòng chờ ...")
        sys.path.insert(0, str(BASE_DIR))
        from analysis import run_analysis
        run_analysis(DATA_CSV, REPORT_JSON)

# ── Hằng số màu sắc thương hiệu ───────────────────────────────────────────────
CLR_PRIMARY   = "#1a56db"
CLR_DANGER    = "#e02424"
CLR_WARNING   = "#ff5a1f"
CLR_SUCCESS   = "#057a55"
CLR_NEUTRAL   = "#6b7280"
CLR_BG        = "#f8fafc"

RISK_COLOR = {
    "RẤT CAO":    CLR_DANGER,
    "CAO":        CLR_WARNING,
    "TRUNG BÌNH": "#faca15",
    "THẤP":       CLR_SUCCESS,
}
SEVERITY_ICON = {
    "KHẨN CẤP":   "🔴",
    "QUAN TRỌNG": "🟠",
    "LƯU Ý":      "🟡",
}

# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load_report(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(show_spinner=False)
def load_df(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def kpi_card(col, label: str, value: str, delta: str = "", color: str = CLR_PRIMARY):
    col.markdown(
        f"""
        <div style="background:{color}11;border-left:4px solid {color};
                    padding:14px 18px;border-radius:8px;margin-bottom:8px">
          <p style="margin:0;font-size:12px;color:{CLR_NEUTRAL};font-weight:600;
                    text-transform:uppercase;letter-spacing:.6px">{label}</p>
          <p style="margin:4px 0 0;font-size:28px;font-weight:700;color:{color}">{value}</p>
          {"<p style='margin:2px 0 0;font-size:12px;color:#6b7280'>"+delta+"</p>" if delta else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

def section_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div style="border-bottom:2px solid {CLR_PRIMARY}22;padding-bottom:8px;margin:24px 0 16px">
          <h3 style="margin:0;color:#1e293b">{title}</h3>
          {"<p style='margin:4px 0 0;color:#64748b;font-size:14px'>"+subtitle+"</p>" if subtitle else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

def warning_card(w: dict):
    icon = SEVERITY_ICON.get(w["muc_do"], "⚪")
    colors = {"KHẨN CẤP": "#fef2f2", "QUAN TRỌNG": "#fff7ed", "LƯU Ý": "#fefce8"}
    borders = {"KHẨN CẤP": CLR_DANGER, "QUAN TRỌNG": CLR_WARNING, "LƯU Ý": "#faca15"}
    bg  = colors.get(w["muc_do"], "#f9fafb")
    bdr = borders.get(w["muc_do"], CLR_NEUTRAL)

    khuyen_nghi_html = "".join(
        f"<li style='margin:4px 0;color:#374151'>{k}</li>"
        for k in w.get("khuyen_nghi", [])
    )
    st.markdown(
        f"""
        <div style="background:{bg};border-left:5px solid {bdr};padding:16px 20px;
                    border-radius:0 10px 10px 0;margin-bottom:16px">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
            <span style="font-size:22px">{icon}</span>
            <div>
              <span style="background:{bdr};color:white;font-size:10px;font-weight:700;
                           padding:2px 8px;border-radius:12px;text-transform:uppercase">
                {w["muc_do"]}
              </span>
              <span style="margin-left:8px;font-size:11px;color:#6b7280">
                Đối tượng: {w.get("doi_tuong","Chung")}
              </span>
            </div>
          </div>
          <p style="font-weight:700;font-size:16px;color:#111827;margin:0 0 8px">{w["tieu_de"]}</p>
          <p style="color:#374151;font-size:14px;line-height:1.6;margin:0 0 12px">{w["noi_dung"]}</p>
          <div style="background:white;border-radius:6px;padding:10px 14px">
            <p style="margin:0 0 6px;font-weight:600;font-size:13px;color:#1f2937">💡 Khuyến nghị:</p>
            <ul style="margin:0;padding-left:18px">{khuyen_nghi_html}</ul>
          </div>
          <p style="margin:8px 0 0;font-size:11px;color:#9ca3af">📌 Nguồn: {w.get("nguon_so_lieu","")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Thị Trường Lao Động Việt Nam 2026–2031",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS tùy chỉnh
st.markdown("""
<style>
  .stApp { background:#f8fafc; }
  .block-container { padding-top: 1.5rem; }
  div[data-testid="stMetricValue"] { font-size: 2rem !important; }
  .stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: 600; }
  .stSidebar { background: #1e293b; }
  .stSidebar * { color: white !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# LOAD & INIT
# ══════════════════════════════════════════════════════════════════════════════
_ensure_report()

report = load_report(REPORT_JSON)
df     = load_df(DATA_CSV)

desc     = report["thong_ke_mo_ta"]
avi      = report["ai_vulnerability_index"]
heatmap  = report["skill_heatmap"]
forecast = report["du_bao_5_nam"]
warnings = report["canh_bao_va_goi_y"]
meta     = report["metadata"]
insights = report["summary_insights"]


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📊 Thị Trường Lao Động VN")
    st.markdown(f"**Ngày phân tích:** {meta.get('ngay_phan_tich','N/A')}")
    st.markdown(f"**Tổng bản ghi:** {meta.get('tong_ban_ghi',0):,}")
    st.markdown("**Nguồn dữ liệu:**")
    for s in meta.get("nguon_du_lieu", []):
        st.markdown(f"  • {s}")
    st.markdown("---")
    st.markdown("### 🔍 Bộ lọc dữ liệu")
    filter_trinh_do = st.multiselect(
        "Trình độ học vấn",
        options=df["Trình độ"].unique().tolist(),
        default=[]
    )
    filter_chuyen_mon = st.multiselect(
        "Chuyên môn / Ngành",
        options=[c for c in df["Chuyên môn"].unique() if c != "null"],
        default=[]
    )
    filter_ai = st.radio("Yêu cầu Kỹ năng AI?", ["Tất cả", "Có", "Không"], index=0)
    st.markdown("---")
    st.markdown("**Phiên bản hệ thống:** v2.0.0")

# Áp dụng bộ lọc
df_filtered = df.copy()
if filter_trinh_do:
    df_filtered = df_filtered[df_filtered["Trình độ"].isin(filter_trinh_do)]
if filter_chuyen_mon:
    df_filtered = df_filtered[df_filtered["Chuyên môn"].isin(filter_chuyen_mon)]
if filter_ai == "Có":
    df_filtered = df_filtered[df_filtered["Kỹ năng AI"] == "có"]
elif filter_ai == "Không":
    df_filtered = df_filtered[df_filtered["Kỹ năng AI"] == "không"]


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="background:linear-gradient(135deg,#1a56db 0%,#0e7490 100%);
            padding:28px 32px;border-radius:16px;margin-bottom:24px;color:white">
  <h1 style="margin:0;font-size:28px;font-weight:800">
    🇻🇳 Phân Tích Thị Trường Lao Động Việt Nam
  </h1>
  <p style="margin:8px 0 0;font-size:16px;opacity:.9">
    Khoa học dữ liệu và ứng dụng · Lớp 26TH01, 26TH02, 26TH03
  </p>
  <p style="margin:4px 0 0;font-size:13px;opacity:.75">
    Nguồn: TopCV.vn · CareerViet.vn · Vieclam24h.vn · Phân tích bởi AI Pipeline
  </p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# KPI ROW
# ══════════════════════════════════════════════════════════════════════════════
c1, c2, c3, c4, c5 = st.columns(5)
n_filtered = len(df_filtered)
kpi_card(c1, "Tổng bản ghi", f"{n_filtered:,}", f"/{meta['tong_ban_ghi']:,} tổng")
kpi_card(c2, "Yêu cầu AI (%)",
         f"{round((df_filtered['Kỹ năng AI']=='có').mean()*100,1)}%",
         "Tỷ lệ trong bộ lọc", CLR_DANGER)
kpi_card(c3, "Yêu cầu Lập trình",
         f"{round((df_filtered['Lập trình']!='không').mean()*100,1)}%",
         "", CLR_WARNING)
kpi_card(c4, "Yêu cầu Ngoại ngữ",
         f"{round((df_filtered['Ngoại ngữ']!='null').mean()*100,1)}%",
         "", "#7c3aed")
kpi_card(c5, "Nhóm rủi ro cao",
         str(sum(1 for v in avi.values() if v['risk_level'] in ('RẤT CAO','CAO'))),
         "ngành theo AVI Index", CLR_DANGER)


# ══════════════════════════════════════════════════════════════════════════════
# TABS CHÍNH
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Tổng quan thị trường",
    "🧠 Bản đồ kỹ năng",
    "⚠️ Trạm Cảnh báo",
    "🔮 Dự báo 2027–2031",
    "🔍 Tự đánh giá bản thân",
])


# ════════════════════════════════════════
# TAB 1 — TỔNG QUAN THỊ TRƯỜNG
# ════════════════════════════════════════
with tab1:
    section_header("📊 Phân phối thị trường lao động",
                   f"Dựa trên {n_filtered:,} bản ghi tuyển dụng (đã lọc)")

    col_a, col_b = st.columns(2)

    # Biểu đồ trình độ học vấn
    with col_a:
        td_data = df_filtered["Trình độ"].value_counts().reset_index()
        td_data.columns = ["Trình độ", "Số lượng"]
        edu_order = ["THPT", "Trung cấp", "Cao đẳng", "Đại học", "Thạc sĩ", "Tiến sĩ", "null"]
        td_data["sort"] = td_data["Trình độ"].map(
            lambda x: edu_order.index(x) if x in edu_order else 99
        )
        td_data = td_data.sort_values("sort")
        fig = px.bar(td_data, x="Trình độ", y="Số lượng",
                     title="Phân bố theo Trình độ học vấn",
                     color="Số lượng",
                     color_continuous_scale=["#dbeafe","#1a56db"],
                     text="Số lượng")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, coloraxis_showscale=False,
                          plot_bgcolor="white", paper_bgcolor="white",
                          font=dict(family="Arial"), margin=dict(t=50,b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Biểu đồ thời gian làm việc
    with col_b:
        tg_data = df_filtered["Thời gian làm việc"].value_counts().reset_index()
        tg_data.columns = ["Thời gian", "Số lượng"]
        fig = px.pie(tg_data, names="Thời gian", values="Số lượng",
                     title="Phân bố theo Hình thức làm việc",
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     hole=0.42)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(paper_bgcolor="white", font=dict(family="Arial"),
                          margin=dict(t=50,b=20))
        st.plotly_chart(fig, use_container_width=True)

    col_c, col_d = st.columns(2)

    # Top chuyên môn
    with col_c:
        cm_data = df_filtered[df_filtered["Chuyên môn"] != "null"]["Chuyên môn"].value_counts().head(10).reset_index()
        cm_data.columns = ["Chuyên môn", "Số lượng"]
        fig = px.bar(cm_data, x="Số lượng", y="Chuyên môn", orientation="h",
                     title="Top 10 Chuyên môn được tuyển dụng nhiều nhất",
                     color="Số lượng",
                     color_continuous_scale=["#d1fae5","#057a55"],
                     text="Số lượng")
        fig.update_traces(textposition="outside")
        fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False,
                          plot_bgcolor="white", paper_bgcolor="white",
                          font=dict(family="Arial"), margin=dict(t=50,l=10))
        st.plotly_chart(fig, use_container_width=True)

    # Vị trí công việc
    with col_d:
        vt_data = df_filtered["Vị trí công việc"].value_counts().reset_index()
        vt_data.columns = ["Vị trí", "Số lượng"]
        fig = px.treemap(vt_data, path=["Vị trí"], values="Số lượng",
                         title="Phân bố theo Vị trí / Môi trường làm việc",
                         color="Số lượng",
                         color_continuous_scale=["#ede9fe","#5b21b6"])
        fig.update_layout(paper_bgcolor="white", margin=dict(t=50,b=5))
        st.plotly_chart(fig, use_container_width=True)

    # Bảng dữ liệu gốc
    section_header("📋 Dữ liệu gốc (có thể lọc và tải xuống)")
    st.dataframe(df_filtered, use_container_width=True, height=320)
    csv_bytes = df_filtered.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button("⬇️ Tải CSV đã lọc", data=csv_bytes,
                       file_name="data_filtered.csv", mime="text/csv")


# ════════════════════════════════════════
# TAB 2 — BẢN ĐỒ KỸ NĂNG
# ════════════════════════════════════════
with tab2:
    section_header("🧠 Bản đồ kỹ năng thị trường lao động",
                   "Phân tích tương quan giữa Trình độ học vấn và Yêu cầu kỹ năng")

    col_e, col_f = st.columns([3, 2])

    # Heatmap kỹ năng × trình độ
    with col_e:
        matrix_data = heatmap["matrix"]
        edu_order   = [e for e in heatmap["order"] if e in matrix_data]
        skills      = heatmap["skills"]
        z = [[matrix_data[edu][s] for s in skills] for edu in edu_order]
        fig = go.Figure(go.Heatmap(
            z=z, x=skills, y=edu_order,
            colorscale=[[0,"#dbeafe"],[0.5,"#3b82f6"],[1,"#1e3a8a"]],
            text=[[f"{v}%" for v in row] for row in z],
            texttemplate="%{text}",
            hovertemplate="Trình độ: %{y}<br>Kỹ năng: %{x}<br>Tỷ lệ: %{z}%<extra></extra>"
        ))
        fig.update_layout(
            title="Ma trận tỷ lệ yêu cầu kỹ năng theo Trình độ (%)",
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Arial", size=12),
            xaxis=dict(tickangle=-30),
            margin=dict(t=60, b=80)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Radar chart kỹ năng mềm
    with col_f:
        soft_skills = ["Thuyết trình","Làm việc nhóm","Sáng tạo","Đàm phán","Giao tiếp"]
        soft_vals = [
            round((df_filtered[s] == "có").mean() * 100, 1)
            for s in soft_skills
        ]
        fig = go.Figure(go.Scatterpolar(
            r=soft_vals + [soft_vals[0]],
            theta=soft_skills + [soft_skills[0]],
            fill="toself",
            line_color=CLR_PRIMARY,
            fillcolor=f"{CLR_PRIMARY}33",
            name="Tỷ lệ yêu cầu (%)"
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="Radar Chart: Tỷ lệ yêu cầu Kỹ năng mềm (%)",
            paper_bgcolor="white", font=dict(family="Arial"),
            margin=dict(t=60)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Biểu đồ AI Vulnerability Index theo ngành
    section_header("🤖 Chỉ số Nguy cơ Tự động hóa AI (AVI Index) theo Ngành")
    avi_df = pd.DataFrame([
        {"Ngành": k, "AVI Score": v["avi_score"], "Mức rủi ro": v["risk_level"],
         "Số việc": v["so_viec"]}
        for k, v in avi.items()
    ]).sort_values("AVI Score", ascending=False)

    fig = px.bar(avi_df, x="AVI Score", y="Ngành", orientation="h",
                 color="Mức rủi ro",
                 color_discrete_map=RISK_COLOR,
                 hover_data=["Số việc"],
                 title="AVI Index theo Ngành (0=An toàn — 100=Rủi ro cao nhất)",
                 text="AVI Score")
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(yaxis=dict(autorange="reversed"), plot_bgcolor="white",
                      paper_bgcolor="white", font=dict(family="Arial"),
                      margin=dict(t=60, l=10), legend_title="Mức rủi ro")
    st.plotly_chart(fig, use_container_width=True)

    # Lập trình ngôn ngữ phổ biến
    col_g, col_h = st.columns(2)
    with col_g:
        lang_df = df_filtered[df_filtered["Lập trình"].notna()]
        lang_df = lang_df[~lang_df["Lập trình"].isin(["không", "null", ""])]
        all_langs = []
        for cell in lang_df["Lập trình"]:
            all_langs.extend([x.strip() for x in str(cell).split(",")])
        from collections import Counter
        lang_counts = Counter(all_langs).most_common(10)
        if lang_counts:
            lc_df = pd.DataFrame(lang_counts, columns=["Ngôn ngữ", "Số lượng"])
            fig = px.bar(lc_df, x="Ngôn ngữ", y="Số lượng",
                         title="Top ngôn ngữ lập trình được yêu cầu",
                         color="Số lượng",
                         color_continuous_scale=["#fef3c7","#d97706"],
                         text="Số lượng")
            fig.update_traces(textposition="outside")
            fig.update_layout(coloraxis_showscale=False, plot_bgcolor="white",
                              paper_bgcolor="white", font=dict(family="Arial"),
                              margin=dict(t=50))
            st.plotly_chart(fig, use_container_width=True)

    with col_h:
        nn_df = df_filtered[~df_filtered["Ngoại ngữ"].isin(["null",""])]["Ngoại ngữ"].value_counts().head(10).reset_index()
        nn_df.columns = ["Ngoại ngữ", "Số lượng"]
        fig = px.bar(nn_df, x="Ngoại ngữ", y="Số lượng",
                     title="Phân bố yêu cầu Ngoại ngữ / Chứng chỉ",
                     color="Số lượng",
                     color_continuous_scale=["#fce7f3","#9d174d"],
                     text="Số lượng")
        fig.update_traces(textposition="outside", textangle=0)
        fig.update_layout(coloraxis_showscale=False, plot_bgcolor="white",
                          paper_bgcolor="white", font=dict(family="Arial"),
                          xaxis=dict(tickangle=-30), margin=dict(t=50,b=70))
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════
# TAB 3 — TRẠM CẢNH BÁO
# ════════════════════════════════════════
with tab3:
    section_header("⚠️ Trạm Cảnh báo & Khuyến nghị Người lao động",
                   "Dựa trên phân tích dữ liệu thực tế + AI Vulnerability Index + WEF Future of Jobs 2025")

    # Tóm tắt nhanh
    urgent = [w for w in warnings if w["muc_do"] == "KHẨN CẤP"]
    important = [w for w in warnings if w["muc_do"] == "QUAN TRỌNG"]
    note = [w for w in warnings if w["muc_do"] == "LƯU Ý"]

    c1, c2, c3 = st.columns(3)
    kpi_card(c1, "🔴 Cảnh báo Khẩn cấp", str(len(urgent)), "", CLR_DANGER)
    kpi_card(c2, "🟠 Quan trọng", str(len(important)), "", CLR_WARNING)
    kpi_card(c3, "🟡 Lưu ý", str(len(note)), "", "#faca15")

    st.markdown("---")

    # Filter theo mức độ
    filter_sev = st.radio(
        "Hiển thị theo mức độ:", ["Tất cả", "Khẩn cấp", "Quan trọng", "Lưu ý"],
        horizontal=True
    )
    filtered_warnings = warnings
    if filter_sev == "Khẩn cấp":
        filtered_warnings = urgent
    elif filter_sev == "Quan trọng":
        filtered_warnings = important
    elif filter_sev == "Lưu ý":
        filtered_warnings = note

    for w in filtered_warnings:
        warning_card(w)

    # Thêm: Top ngành rủi ro bảng
    section_header("📊 Bảng chi tiết Chỉ số AVI theo Ngành")
    avi_detail = pd.DataFrame([
        {
            "Ngành nghề": k,
            "Điểm AVI (0-100)": v["avi_score"],
            "Mức rủi ro": v["risk_level"],
            "Số vị trí": v["so_viec"],
            "Việc lặp lại (%)": v["routine_ratio_pct"],
            "Không cần AI (%)": v["no_ai_demand_pct"],
            "Thiếu kỹ năng mềm (%)": v["no_soft_pct"],
            "Dưới Đại học (%)": v["low_edu_pct"],
        }
        for k, v in avi.items()
    ]).sort_values("Điểm AVI (0-100)", ascending=False).reset_index(drop=True)

    def highlight_risk(row):
        color_map = {
            "RẤT CAO": "background-color:#fef2f2;color:#991b1b",
            "CAO": "background-color:#fff7ed;color:#c2410c",
            "TRUNG BÌNH": "background-color:#fefce8;color:#a16207",
            "THẤP": "background-color:#f0fdf4;color:#166534",
        }
        return [color_map.get(row["Mức rủi ro"], "")] * len(row)

    st.dataframe(
        avi_detail.style.apply(highlight_risk, axis=1),
        use_container_width=True, height=350
    )


# ════════════════════════════════════════
# TAB 4 — DỰ BÁO 2027–2031
# ════════════════════════════════════════
with tab4:
    section_header("🔮 Dự báo xu hướng thị trường lao động 2027–2031",
                   "Mô hình dựa trên dữ liệu thực tế + WEF Future of Jobs 2025 + tốc độ AI adoption 18%/năm")

    years = list(forecast.keys())
    ai_proj  = [forecast[y]["ti_le_yeu_cau_ai_pct"] for y in years]
    cod_proj = [forecast[y]["ti_le_yeu_cau_lap_trinh_pct"] for y in years]
    lan_proj = [forecast[y]["ti_le_yeu_cau_ngoai_ngu_pct"] for y in years]
    rtn_proj = [forecast[y]["du_bao_thu_hep_viec_routine_pct"] for y in years]

    # Thêm điểm gốc 2026
    years_full = ["2026"] + years
    ai_full    = [desc["has_ai_skill_pct"]] + ai_proj
    cod_full   = [desc["has_coding_pct"]] + cod_proj
    lan_full   = [desc["has_foreign_lang_pct"]] + lan_proj
    rtn_full   = [0] + rtn_proj

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years_full, y=ai_full, mode="lines+markers+text",
                             name="Yêu cầu Kỹ năng AI (%)",
                             line=dict(color=CLR_DANGER, width=3, dash="solid"),
                             marker=dict(size=10), text=[f"{v:.1f}%" for v in ai_full],
                             textposition="top center"))
    fig.add_trace(go.Scatter(x=years_full, y=cod_full, mode="lines+markers+text",
                             name="Yêu cầu Lập trình (%)",
                             line=dict(color=CLR_WARNING, width=3),
                             marker=dict(size=10), text=[f"{v:.1f}%" for v in cod_full],
                             textposition="top center"))
    fig.add_trace(go.Scatter(x=years_full, y=lan_full, mode="lines+markers+text",
                             name="Yêu cầu Ngoại ngữ (%)",
                             line=dict(color="#7c3aed", width=3),
                             marker=dict(size=10), text=[f"{v:.1f}%" for v in lan_full],
                             textposition="top center"))
    fig.add_trace(go.Bar(x=years_full, y=rtn_full, name="Thu hẹp việc Routine (%)",
                         marker_color="#e5e7eb", opacity=0.6, yaxis="y2"))

    fig.add_annotation(
        x="2026", y=ai_full[0],
        text="Hiện tại (2026)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowcolor="#94a3b8",
        ax=0, ay=-35,
        font=dict(color="#475569", size=12, family="Arial")
    )

    fig.update_layout(
        title="Dự báo xu hướng kỹ năng thị trường lao động Việt Nam 2026–2031",
        xaxis_title="Năm",
        yaxis_title="Tỷ lệ yêu cầu (%)",
        yaxis2=dict(title="Thu hẹp việc Routine (%)", overlaying="y", side="right", showgrid=False),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Arial", size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=80, b=60), height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # Bảng dự báo
    section_header("📋 Bảng số liệu dự báo chi tiết")
    fc_df = pd.DataFrame([
        {
            "Năm": y,
            "Yêu cầu AI (%)": forecast[y]["ti_le_yeu_cau_ai_pct"],
            "Yêu cầu Lập trình (%)": forecast[y]["ti_le_yeu_cau_lap_trinh_pct"],
            "Yêu cầu Ngoại ngữ (%)": forecast[y]["ti_le_yeu_cau_ngoai_ngu_pct"],
            "Thu hẹp việc Routine (%)": forecast[y]["du_bao_thu_hep_viec_routine_pct"],
        }
        for y in years
    ])
    st.dataframe(fc_df, use_container_width=True, hide_index=True)

    # Biểu đồ waterfall ngành tăng/giảm
    section_header("📊 Dự báo tác động theo Ngành (2026 → 2031)")
    impact_data = []
    for nghanh, v in avi.items():
        if v["so_viec"] < 5:
            continue
        avi_score = v["avi_score"]
        growth = -avi_score * 0.35   # Ngành AVI cao → dự báo co lại
        impact_data.append({
            "Ngành": nghanh,
            "Dự báo thay đổi (%)": round(growth, 1),
            "Xu hướng": "Giảm" if growth < 0 else "Tăng"
        })

    # Thêm ngành tăng trưởng thủ công từ insights
    for ng in insights.get("nganh_tang_truong_cao", []):
        impact_data.append({"Ngành": ng, "Dự báo thay đổi (%)": 25.0, "Xu hướng": "Tăng"})

    impact_df = pd.DataFrame(impact_data).drop_duplicates("Ngành").sort_values("Dự báo thay đổi (%)")
    fig = px.bar(impact_df, x="Dự báo thay đổi (%)", y="Ngành", orientation="h",
                 color="Xu hướng",
                 color_discrete_map={"Giảm": CLR_DANGER, "Tăng": CLR_SUCCESS},
                 title="Dự báo thay đổi quy mô ngành nghề đến 2031 (%)",
                 text="Dự báo thay đổi (%)")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(yaxis=dict(autorange="reversed"), plot_bgcolor="white",
                      paper_bgcolor="white", font=dict(family="Arial"),
                      margin=dict(t=60, l=10))
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════
# TAB 5 — TỰ ĐÁNH GIÁ BẢN THÂN
# ════════════════════════════════════════
with tab5:
    section_header("🔍 Công cụ Tự đánh giá Cơ hội việc làm cá nhân",
                   "Nhập hồ sơ của bạn → Hệ thống phân tích độ phù hợp & cảnh báo rủi ro")

    with st.form("self_assessment"):
        c1, c2 = st.columns(2)
        with c1:
            inp_trinh_do = st.selectbox("Trình độ học vấn của bạn:",
                ["THPT", "Trung cấp", "Cao đẳng", "Đại học", "Thạc sĩ", "Tiến sĩ"])
            inp_chuyen_mon = st.selectbox("Chuyên môn chính:",
                ["null", "Công nghệ thông tin", "Kế toán - Tài chính", "Luật kinh tế",
                 "Marketing", "Thiết kế đồ họa", "An toàn thông tin",
                 "Quản trị nhân sự", "Kinh doanh", "Giáo dục - Đào tạo",
                 "Y tế - Dược", "Xây dựng - Kiến trúc"])
            inp_kinh_nghiem = st.selectbox("Số năm kinh nghiệm:",
                ["không", "1 năm", "2 năm", "3 năm", "4-5 năm", "5+ năm"])
        with c2:
            inp_ngoaingu = st.selectbox("Ngoại ngữ bạn có:",
                ["null", "Tiếng Anh", "Toeic 350", "Toeic 500", "Toeic 600",
                 "IELTS 5.0", "IELTS 6.0", "IELTS 6.5", "IELTS 7.0",
                 "Hoa ngữ", "Tiếng Nhật N3", "Tiếng Nhật N2", "Tiếng Hàn"])
            inp_coding = st.selectbox("Kỹ năng lập trình:",
                ["không", "SQL", "Python", "C#", "Java", "JavaScript", "PHP", "Khác"])
            inp_ai = st.radio("Có kỹ năng AI / Prompt Engineering?", ["Không", "Có"],
                              horizontal=True)

        st.markdown("**Kỹ năng mềm bạn có:**")
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        s_tt = sc1.checkbox("Thuyết trình")
        s_nk = sc2.checkbox("Làm việc nhóm")
        s_st = sc3.checkbox("Sáng tạo")
        s_dp = sc4.checkbox("Đàm phán")
        s_gt = sc5.checkbox("Giao tiếp")

        submitted = st.form_submit_button("🔍 Phân tích hồ sơ của tôi", use_container_width=True)

    if submitted:
        st.markdown("---")
        # Tính điểm phù hợp
        profile = {
            "Trình độ": inp_trinh_do,
            "Chuyên môn": inp_chuyen_mon,
            "Ngoại ngữ": inp_ngoaingu,
            "Lập trình": inp_coding,
            "Kỹ năng AI": "có" if inp_ai == "Có" else "không",
            "Thuyết trình": "có" if s_tt else "không",
            "Làm việc nhóm": "có" if s_nk else "không",
            "Sáng tạo": "có" if s_st else "không",
            "Đàm phán": "có" if s_dp else "không",
            "Giao tiếp": "có" if s_gt else "không",
        }

        # Khớp với bộ dữ liệu
        matched = df[df["Trình độ"] == inp_trinh_do]
        if inp_chuyen_mon != "null":
            matched_cm = df[df["Chuyên môn"] == inp_chuyen_mon]
            match_pct = round(len(matched_cm) / len(df) * 100, 1)
        else:
            match_pct = round(len(matched) / len(df) * 100, 1)

        # Điểm hồ sơ
        score = 0
        edu_scores = {"THPT": 10, "Trung cấp": 20, "Cao đẳng": 30,
                      "Đại học": 50, "Thạc sĩ": 70, "Tiến sĩ": 85}
        score += edu_scores.get(inp_trinh_do, 10)
        if inp_ngoaingu != "null":
            score += 15
        if inp_coding != "không":
            score += 15
        if inp_ai == "Có":
            score += 20
        soft_count = sum([s_tt, s_nk, s_st, s_dp, s_gt])
        score += soft_count * 4
        score = min(score, 100)

        # AVI của ngành người dùng
        user_avi = avi.get(inp_chuyen_mon, {})
        user_avi_score = user_avi.get("avi_score", 50)
        user_risk = user_avi.get("risk_level", "TRUNG BÌNH")

        # Hiển thị kết quả
        rc1, rc2, rc3 = st.columns(3)
        kpi_card(rc1, "Điểm cạnh tranh hồ sơ", f"{score}/100",
                 "Dựa trên trình độ, kỹ năng", CLR_SUCCESS if score >= 60 else CLR_WARNING)
        kpi_card(rc2, "Phù hợp với thị trường",
                 f"{match_pct}%",
                 f"số vị trí tương ứng trình độ của bạn", CLR_PRIMARY)
        kpi_card(rc3, "Rủi ro ngành của bạn",
                 user_risk if user_avi else "N/A",
                 f"AVI = {user_avi_score}" if user_avi else "Chưa đủ dữ liệu",
                 RISK_COLOR.get(user_risk, CLR_NEUTRAL))

        st.markdown("---")

        # Phân tích điểm mạnh / yếu
        col_str, col_weak = st.columns(2)
        with col_str:
            st.markdown("### ✅ Điểm mạnh của bạn")
            strengths = []
            if inp_ai == "Có":
                strengths.append("🤖 Có kỹ năng AI — lợi thế cạnh tranh hàng đầu")
            if inp_coding != "không":
                strengths.append(f"💻 Biết lập trình {inp_coding} — kỹ năng được săn đón")
            if inp_ngoaingu != "null":
                strengths.append(f"🌍 Có ngoại ngữ ({inp_ngoaingu}) — mở ra cơ hội lương cao")
            if soft_count >= 3:
                strengths.append(f"🤝 Có {soft_count}/5 kỹ năng mềm — bảo vệ trước AI tốt")
            if inp_trinh_do in ("Thạc sĩ", "Tiến sĩ"):
                strengths.append("🎓 Trình độ cao — phù hợp vị trí chuyên sâu và quản lý")
            if not strengths:
                strengths.append("Hãy bổ sung kỹ năng để tăng sức cạnh tranh!")
            for s in strengths:
                st.markdown(f"- {s}")

        with col_weak:
            st.markdown("### ⚠️ Cần cải thiện")
            weaknesses = []
            if inp_ai == "Không":
                weaknesses.append("⚠️ Chưa có kỹ năng AI — nguy cơ tụt hậu trong 2-3 năm tới")
            if inp_coding == "không":
                weaknesses.append("⚠️ Chưa biết lập trình — học Python/SQL ngay")
            if inp_ngoaingu == "null":
                weaknesses.append("⚠️ Chưa có ngoại ngữ — đây là rào cản lương cao lớn nhất")
            if soft_count < 3:
                weaknesses.append(f"⚠️ Chỉ có {soft_count}/5 kỹ năng mềm — cần rèn luyện thêm")
            if inp_trinh_do in ("THPT", "Trung cấp"):
                weaknesses.append("⚠️ Trình độ thấp — nguy cơ bị tự động hóa thay thế cao")
            if not weaknesses:
                weaknesses.append("✓ Hồ sơ của bạn khá tốt! Tiếp tục duy trì và cập nhật")
            for w in weaknesses:
                st.markdown(f"- {w}")

        # Lộ trình đề xuất
        st.markdown("---")
        st.markdown("### 🗺️ Lộ trình phát triển được đề xuất (3–12 tháng)")
        roadmap_items = []
        if inp_ai == "Không":
            roadmap_items.append(("🤖 Tháng 1-2", "Hoàn thành khóa Google AI Essentials (miễn phí)",
                                  "https://grow.google/intl/vi_vn/courses-and-tools/"))
        if inp_coding == "không":
            roadmap_items.append(("💻 Tháng 2-4", "Học Python for Everybody trên Coursera",
                                  "https://www.coursera.org/specializations/python"))
        if inp_ngoaingu == "null":
            roadmap_items.append(("🌍 Tháng 1-6", "Học Tiếng Anh + luyện Toeic 500",
                                  "https://www.duolingo.com/"))
        if soft_count < 3:
            roadmap_items.append(("🤝 Tháng 3-6", "Tham gia Toastmasters để rèn kỹ năng mềm",
                                  "https://www.toastmasters.org/"))
        roadmap_items.append(("🎯 Tháng 6-12", "Xây dựng 2-3 dự án thực tế và đưa lên GitHub/Portfolio", ""))

        for time_label, action, link in roadmap_items:
            st.markdown(
                f"""<div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:12px;
                                background:#f0f9ff;padding:12px 16px;border-radius:8px;
                                border-left:3px solid {CLR_PRIMARY}">
                       <span style="font-weight:700;color:{CLR_PRIMARY};min-width:100px">{time_label}</span>
                       <span style="color:#1e293b">{action}
                         {"&nbsp;<a href='"+link+"' target='_blank'>→ Link</a>" if link else ""}
                       </span>
                     </div>""",
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align:center;color:#9ca3af;font-size:13px;padding:16px 0">
      📊 <strong>Hệ thống Phân tích Thị trường Lao động Việt Nam v2.0</strong><br>
      Môn: Khoa học dữ liệu và ứng dụng · Lớp 26TH01, 26TH02, 26TH03<br>
      Nguồn dữ liệu: TopCV.vn · CareerViet.vn · Vieclam24h.vn<br>
      Cập nhật: {meta.get('ngay_phan_tich', 'N/A')} · Tổng bản ghi: {meta.get('tong_ban_ghi', 0):,}
    </div>
    """,
    unsafe_allow_html=True,
)

