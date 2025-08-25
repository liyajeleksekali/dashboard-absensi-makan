import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# === 1. Konfigurasi Halaman ===
st.set_page_config(
    page_title="Dashboard Absensi Makan", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .section-header {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1.5rem 0 1rem 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .info-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #ff6b6b;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }
    
    .filter-container {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9ff;
        border-radius: 10px;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .upload-area {
        border: 3px dashed #4facfe;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header dengan gradient
st.markdown('<h1 class="main-header">🍽️ Dashboard Absensi Makan Karyawan</h1>', unsafe_allow_html=True)

# === 2. Upload File dengan styling ===
st.markdown('<div class="upload-area">', unsafe_allow_html=True)
st.markdown("### 📂 Upload File Absensi")
uploaded_file = st.file_uploader("Pilih file CSV absensi", type=["csv"], help="Upload file dengan format CSV")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    try:
        # Baca CSV
        df = pd.read_csv(uploaded_file, skiprows=5)
        df = df.drop(columns=[col for col in df.columns if "Unnamed" in col])

        # Cari kolom tanggal (formatnya 08-01, 08-02, dst)
        date_cols = [c for c in df.columns if "-" in c and len(c.split("-")) == 2]

        # Konversi simbol: A = hadir/makan (1), - = tidak (0)
        df[date_cols] = df[date_cols].replace({"A": 1, "-": 0})

        # Sidebar untuk filter
        with st.sidebar:
            st.markdown('<div class="section-header">🎛️ Filter Data</div>', unsafe_allow_html=True)
            
            # Filter Department
            departments = ["Semua Departemen"] + sorted(df["Department"].unique().tolist())
            selected_dept = st.selectbox("🏢 Departemen", departments)

            # Filter Attendance Group
            groups = ["Semua Group"] + sorted(df["Attendance Group"].unique().tolist())
            selected_group = st.selectbox("👥 Attendance Group", groups)

        # Apply filters
        df_filtered = df.copy()
        if selected_dept != "Semua Departemen":
            df_filtered = df_filtered[df_filtered["Department"] == selected_dept]
        if selected_group != "Semua Group":
            df_filtered = df_filtered[df_filtered["Attendance Group"] == selected_group]

        # === Filter Tanggal ===
        st.markdown('<div class="section-header">📅 Periode Analisis</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.selectbox("Tanggal Mulai", date_cols, key="start")
        with col2:
            end_date = st.selectbox("Tanggal Selesai", date_cols, index=len(date_cols)-1, key="end")

        date_range = date_cols[date_cols.index(start_date): date_cols.index(end_date)+1]

        # === 3. Dashboard Metrics ===
        st.markdown('<div class="section-header">📊 Ringkasan Utama</div>', unsafe_allow_html=True)
        
        # Hitung metrics
        total_makan = df_filtered[date_range].sum().sum()
        total_karyawan = len(df_filtered)
        rata_rata_harian = df_filtered[date_range].sum().mean()
        tingkat_partisipasi = (df_filtered[date_range].sum().sum() / (len(df_filtered) * len(date_range)) * 100)

        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <h2>🍽️</h2>
                <h3>{total_makan:,.0f}</h3>
                <p>Total Makan</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <h2>👥</h2>
                <h3>{total_karyawan:,}</h3>
                <p>Total Karyawan</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <h2>📈</h2>
                <h3>{rata_rata_harian:.0f}</h3>
                <p>Rata-rata Harian</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class="metric-container">
                <h2>📊</h2>
                <h3>{tingkat_partisipasi:.1f}%</h3>
                <p>Tingkat Partisipasi</p>
            </div>
            """, unsafe_allow_html=True)

        # === 4. Rekap Harian dengan Plotly ===
        rekap_harian = df_filtered[date_range].sum().reset_index()
        rekap_harian.columns = ["Tanggal", "Jumlah Makan"]
        
        st.markdown('<div class="section-header">📈 Trend Konsumsi Harian</div>', unsafe_allow_html=True)
        
        fig_daily = px.line(rekap_harian, x="Tanggal", y="Jumlah Makan",
                           title="Trend Konsumsi Makan Harian",
                           markers=True)
        fig_daily.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Tanggal",
            yaxis_title="Jumlah Makan",
            font=dict(size=12),
            hovermode='x'
        )
        fig_daily.update_traces(
            line_color='#667eea',
            marker_color='#764ba2',
            marker_size=8
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(fig_daily, use_container_width=True)
        with col2:
            st.dataframe(rekap_harian, use_container_width=True)

        # === 5. Rekap Mingguan ===
        rekap_harian["Tanggal_dt"] = pd.to_datetime("2025-" + rekap_harian["Tanggal"], format="%Y-%m-%d")
        rekap_harian["Minggu"] = rekap_harian["Tanggal_dt"].dt.isocalendar().week
        rekap_mingguan = rekap_harian.groupby("Minggu")["Jumlah Makan"].sum().reset_index()

        st.markdown('<div class="section-header">📅 Analisis Mingguan</div>', unsafe_allow_html=True)
        
        fig_weekly = px.bar(rekap_mingguan, x="Minggu", y="Jumlah Makan",
                           title="Konsumsi Makan per Minggu",
                           color="Jumlah Makan",
                           color_continuous_scale="Viridis")
        fig_weekly.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(fig_weekly, use_container_width=True)
        with col2:
            st.dataframe(rekap_mingguan, use_container_width=True)

        # === 6. Rekap per Departemen dengan donut chart ===
        rekap_departemen = df.groupby("Department")[date_range].sum().sum(axis=1).reset_index()
        rekap_departemen.columns = ["Department", "Total Makan"]
        rekap_departemen = rekap_departemen.sort_values(by="Total Makan", ascending=False)

        st.markdown('<div class="section-header">🏢 Distribusi per Departemen</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_dept_pie = px.pie(rekap_departemen, values="Total Makan", names="Department",
                                 title="Distribusi Konsumsi per Departemen",
                                 hole=0.4)
            fig_dept_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_dept_pie, use_container_width=True)
            
        with col2:
            fig_dept_bar = px.bar(rekap_departemen.head(10), 
                                 x="Total Makan", y="Department",
                                 orientation='h',
                                 title="Top 10 Departemen",
                                 color="Total Makan",
                                 color_continuous_scale="Blues")
            fig_dept_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_dept_bar, use_container_width=True)

        # === 7. Rekap per Karyawan ===
        df_filtered["Total Makan"] = df_filtered[date_range].sum(axis=1)
        rekap_karyawan = df_filtered[["First Name", "Last Name", "ID", "Department", "Attendance Group", "Total Makan"]]
        rekap_karyawan = rekap_karyawan.sort_values("Total Makan", ascending=False)

        st.markdown('<div class="section-header">👤 Detail per Karyawan</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Top 10 karyawan
            top_employees = rekap_karyawan.head(10).copy()
            top_employees["Nama Lengkap"] = top_employees["First Name"] + " " + top_employees["Last Name"]
            
            fig_top_emp = px.bar(top_employees, 
                               x="Total Makan", y="Nama Lengkap",
                               orientation='h',
                               title="Top 10 Karyawan",
                               color="Total Makan",
                               color_continuous_scale="Reds")
            fig_top_emp.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_top_emp, use_container_width=True)
            
        with col2:
            # Searchable dataframe
            search_term = st.text_input("🔍 Cari Karyawan", placeholder="Ketik nama atau ID karyawan...")
            if search_term:
                filtered_employees = rekap_karyawan[
                    (rekap_karyawan["First Name"].str.contains(search_term, case=False, na=False)) |
                    (rekap_karyawan["Last Name"].str.contains(search_term, case=False, na=False)) |
                    (rekap_karyawan["ID"].astype(str).str.contains(search_term, case=False, na=False))
                ]
                st.dataframe(filtered_employees, use_container_width=True)
            else:
                st.dataframe(rekap_karyawan, use_container_width=True)

        # === 8. Rekap per Attendance Group ===
        rekap_group = df.groupby("Attendance Group")[date_range].sum().sum(axis=1).reset_index()
        rekap_group.columns = ["Attendance Group", "Total Makan"]
        rekap_group = rekap_group.sort_values(by="Total Makan", ascending=False)

        st.markdown('<div class="section-header">👥 Analisis Attendance Group</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_group = px.bar(rekap_group, x="Attendance Group", y="Total Makan",
                              title="Total Konsumsi per Group",
                              color="Total Makan",
                              color_continuous_scale="Greens")
            fig_group.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_group, use_container_width=True)
            
        with col2:
            # Trend mingguan per group
            df_melt = df.melt(
                id_vars=["Attendance Group"],
                value_vars=date_range,
                var_name="Tanggal",
                value_name="Makan"
            )
            df_melt["Tanggal_dt"] = pd.to_datetime("2025-" + df_melt["Tanggal"], format="%Y-%m-%d")
            df_melt["Minggu"] = df_melt["Tanggal_dt"].dt.isocalendar().week

            rekap_group_mingguan = df_melt.groupby(["Attendance Group", "Minggu"])["Makan"].sum().reset_index()
            
            fig_group_trend = px.line(rekap_group_mingguan, x="Minggu", y="Makan", 
                                     color="Attendance Group",
                                     title="Trend Mingguan per Group",
                                     markers=True)
            fig_group_trend.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_group_trend, use_container_width=True)

        # === 9. Download Section ===
        st.markdown('<div class="section-header">⬇️ Download Laporan</div>', unsafe_allow_html=True)
        
        download_col1, download_col2, download_col3 = st.columns(3)
        
        with download_col1:
            st.download_button(
                "📊 Download Rekap Harian",
                rekap_harian.to_csv(index=False).encode("utf-8"),
                "rekap_harian.csv",
                "text/csv",
                use_container_width=True
            )
            
            st.download_button(
                "📅 Download Rekap Mingguan",
                rekap_mingguan.to_csv(index=False).encode("utf-8"),
                "rekap_mingguan.csv",
                "text/csv",
                use_container_width=True
            )

        with download_col2:
            st.download_button(
                "👤 Download Rekap Karyawan",
                rekap_karyawan.to_csv(index=False).encode("utf-8"),
                "rekap_karyawan.csv",
                "text/csv",
                use_container_width=True
            )
            
            st.download_button(
                "🏢 Download Rekap Departemen",
                rekap_departemen.to_csv(index=False).encode("utf-8"),
                "rekap_departemen.csv",
                "text/csv",
                use_container_width=True
            )

        with download_col3:
            st.download_button(
                "👥 Download Rekap Group Bulanan",
                rekap_group.to_csv(index=False).encode("utf-8"),
                "rekap_group_bulanan.csv",
                "text/csv",
                use_container_width=True
            )
            
            st.download_button(
                "📈 Download Rekap Group Mingguan",
                rekap_group_mingguan.to_csv(index=False).encode("utf-8"),
                "rekap_group_mingguan.csv",
                "text/csv",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"❌ Terjadi kesalahan dalam memproses file: {str(e)}")
        st.info("💡 Pastikan format file CSV sesuai dengan template yang diharapkan.")

else:
    st.markdown("""
    <div class="info-box">
        <h3>🚀 Selamat Datang di Dashboard Absensi Makan!</h3>
        <p>Untuk memulai analisis, silakan upload file CSV absensi makan karyawan Anda.</p>
        <p><strong>Format yang diharapkan:</strong></p>
        <ul>
            <li>File CSV dengan kolom: First Name, Last Name, ID, Department, Attendance Group</li>
            <li>Kolom tanggal dengan format MM-DD (contoh: 08-01, 08-02)</li>
            <li>Data absensi dengan kode: A (hadir/makan), - (tidak hadir)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>💡 Dashboard Absensi Makan Karyawan v2.0 | Dibuat dengan ❤️ menggunakan Streamlit</p>
</div>
""", unsafe_allow_html=True)