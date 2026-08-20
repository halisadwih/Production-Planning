import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date, datetime, timedelta

# 1. Konfigurasi Halaman Dashboard
st.set_page_config(
    page_title="Raw Material Incoming Dashboard - PT Solusi Bangun Indonesia",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom Corporate CSS Styling
st.markdown("""
<style>
    .main { background-color: #f4f6f9; }
    .stApp { font-family: 'Segoe UI', Arial, sans-serif; }
    
    /* Header Box Styling */
    .header-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 20px 28px;
        border-radius: 8px;
        color: #ffffff;
        margin-bottom: 24px;
        border-bottom: 4px solid #2563eb;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .header-title { 
        font-size: 22px; 
        font-weight: 700; 
        margin: 0; 
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .header-subtitle { 
        font-size: 13px; 
        color: #94a3b8; 
        margin-top: 4px; 
        font-weight: 400;
    }
    
    /* Metric Cards Styling */
    .metric-card {
        background-color: #ffffff;
        border-radius: 6px;
        padding: 16px 20px;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #2563eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .metric-card-flyash { border-left-color: #475569; }
    .metric-card-gypsum { border-left-color: #0d9488; }
    .metric-card-batubara { border-left-color: #d97706; }
    .metric-card-total { border-left-color: #2563eb; }
    
    .metric-label { font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 22px; font-weight: 700; color: #0f172a; margin: 4px 0; }
    .metric-sub { font-size: 12px; color: #64748b; }
    
    /* Auto Info Preview Box */
    .system-preview-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 12px;
        font-size: 12px;
        color: #334155;
        margin-bottom: 15px;
    }
    .system-preview-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
    }
    .system-preview-label { font-weight: 600; color: #64748b; }
    
    /* Status Badge */
    .badge-status {
        background-color: #e2e8f0;
        color: #334155;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Master Data Supplier & Inisialisasi State
SUPPLIER_MAPPING = {
    "Fly Ash": ["PT PLN Nusantara Power", "PT Indonesia Power"],
    "Gypsum": ["PT Petrokimia Gresik", "PT Siam-Gypsum Indonesia"],
    "Batu Bara": ["PT Bukit Asam Tbk", "PT Adaro Indonesia", "PT Kaltim Prima Coal"]
}

TARGET_HARIAN = {"Fly Ash": 200.0, "Gypsum": 150.0, "Batu Bara": 350.0}

if "tis_data" not in st.session_state:
    np.random.seed(42)
    start_date = date(2026, 8, 1)
    end_date = date(2026, 8, 20)
    delta = (end_date - start_date).days + 1
    
    materials = ["Fly Ash", "Gypsum", "Batu Bara"]
    truck_prefixes = ["B 91", "B 92", "B 93", "F 80", "F 81", "D 88"]
    
    records = []
    trx_id = 1001
    
    for day in range(delta):
        curr_date = start_date + timedelta(days=day)
        num_trucks = np.random.randint(12, 26)
        
        for _ in range(num_trucks):
            mat = np.random.choice(materials, p=[0.3, 0.25, 0.45])
            supp = np.random.choice(SUPPLIER_MAPPING[mat])
            weight = round(np.random.uniform(22.0, 38.5), 2)
            hour = np.random.randint(6, 22)
            minute = np.random.randint(0, 60)
            time_str = f"{hour:02d}:{minute:02d}"
            truck_no = f"{np.random.choice(truck_prefixes)}{np.random.randint(100, 999)} SBI"
            po_number = f"PO-SBI-2026-{np.random.randint(1000, 9999)}"
            
            records.append({
                "ID Transaksi": f"TIS-{trx_id}",
                "Tanggal": curr_date,
                "Jam Masuk": time_str,
                "Bahan Baku": mat,
                "Supplier": supp,
                "No. Kendaraan": truck_no,
                "No. PO": po_number,
                "Berat Netto (Ton)": weight,
                "Status Jembatan Timbang": "Selesai",
                "Catatan": "QC Passed"
            })
            trx_id += 1
            
    st.session_state.tis_data = pd.DataFrame(records)

# 4. Header Section
st.markdown("""
<div class="header-box">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 class="header-title">RAW MATERIAL INCOMING MONITORING SYSTEM</h1>
            <p class="header-subtitle">Division of Production Planning — PT Solusi Bangun Indonesia Tbk</p>
        </div>
        <div>
            <span class="badge-status">MODE SIMULASI TIS</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. Control Panel (Sidebar Filter & Quick Entry)
st.sidebar.markdown("### PANEL KONTROL")

# Filter Utama (Otomatis memutakhirkan tampilan tanpa tombol action)
selected_date = st.sidebar.date_input(
    "Tanggal Monitoring",
    value=date(2026, 8, 20),
    min_value=date(2026, 8, 1),
    max_value=date(2026, 8, 20)
)

selected_materials = st.sidebar.multiselect(
    "Filter Bahan Baku",
    options=["Fly Ash", "Gypsum", "Batu Bara"],
    default=["Fly Ash", "Gypsum", "Batu Bara"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### INPUT TRANSAKSI MANUAL")

# Pilihan Bahan Baku & Supplier
manual_mat = st.sidebar.selectbox("Bahan Baku", ["Fly Ash", "Gypsum", "Batu Bara"])
available_suppliers = SUPPLIER_MAPPING.get(manual_mat, [])
manual_supp = st.sidebar.selectbox("Nama Supplier", available_suppliers)

# Generasi Nilai Otomatis oleh Sistem
auto_time = datetime.now().strftime("%H:%M")
auto_truck = f"B 9{np.random.randint(10, 99)} SBI"
auto_po = f"PO-SBI-2026-{np.random.randint(1000, 9999)}"
auto_weight = 30.0  # Standar muatan rata-rata truk

# Preview Informasi Sistem Sebelum Ditambahkan
st.sidebar.markdown("""
<div class="system-preview-box">
    <div class="system-preview-item">
        <span class="system-preview-label">Jam Masuk (Auto):</span>
        <span>{}</span>
    </div>
    <div class="system-preview-item">
        <span class="system-preview-label">No. Kendaraan (Auto):</span>
        <span>{}</span>
    </div>
    <div class="system-preview-item">
        <span class="system-preview-label">No. PO (Auto):</span>
        <span>{}</span>
    </div>
    <div class="system-preview-item">
        <span class="system-preview-label">Estimasi Berat:</span>
        <span>{} Ton</span>
    </div>
</div>
""".format(auto_time, auto_truck, auto_po, auto_weight), unsafe_allow_html=True)

if st.sidebar.button("Tambah Kedatangan Material", type="primary", use_container_width=True):
    new_row = {
        "ID Transaksi": f"TIS-MANUAL-{np.random.randint(100, 999)}",
        "Tanggal": selected_date,
        "Jam Masuk": auto_time,
        "Bahan Baku": manual_mat,
        "Supplier": manual_supp,
        "No. Kendaraan": auto_truck,
        "No. PO": auto_po,
        "Berat Netto (Ton)": auto_weight,
        "Status Jembatan Timbang": "Selesai (Manual)",
        "Catatan": "Input Manual Operator PP"
    }
    st.session_state.tis_data = pd.concat([st.session_state.tis_data, pd.DataFrame([new_row])], ignore_index=True)
    st.sidebar.success("Transaksi berhasil ditambahkan ke sistem.")
    st.rerun()

# 6. Pemrosesan Data Berdasarkan Filter
df_all = st.session_state.tis_data
df_filtered_date = df_all[df_all["Tanggal"] == selected_date]
df_filtered = df_filtered_date[df_filtered_date["Bahan Baku"].isin(selected_materials)]

st.markdown(f"#### Summary Kedatangan Material — Tanggal: {selected_date.strftime('%d %B %Y')}")

if df_filtered.empty:
    st.info(f"Tidak ditemukan transaksi kedatangan material untuk tanggal {selected_date.strftime('%d-%m-%Y')}.")
else:
    # Summary Metric Cards
    total_tonnage = df_filtered["Berat Netto (Ton)"].sum()
    total_trucks = len(df_filtered)
    
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        st.markdown(f"""
        <div class="metric-card metric-card-total">
            <div class="metric-label">Total Volume Kedatangan</div>
            <div class="metric-value">{total_tonnage:,.2f} <span style="font-size:13px; font-weight:normal;">Ton</span></div>
            <div class="metric-sub">Total Ritase: {total_trucks} Truk</div>
        </div>""", unsafe_allow_html=True)
        
    for mat_name, card_class, col_obj in [
        ("Fly Ash", "metric-card-flyash", col_t2),
        ("Gypsum", "metric-card-gypsum", col_t3),
        ("Batu Bara", "metric-card-batubara", col_t4)
    ]:
        with col_obj:
            mat_df = df_filtered[df_filtered["Bahan Baku"] == mat_name]
            mat_ton = mat_df["Berat Netto (Ton)"].sum()
            mat_trucks = len(mat_df)
            target = TARGET_HARIAN.get(mat_name, 0)
            pct = (mat_ton / target * 100) if target > 0 else 0
            
            st.markdown(f"""
            <div class="metric-card {card_class}">
                <div class="metric-label">{mat_name}</div>
                <div class="metric-value">{mat_ton:,.2f} <span style="font-size:13px; font-weight:normal;">Ton</span></div>
                <div class="metric-sub">Target: {target:.0f} Ton ({pct:.1f}%) | {mat_trucks} Rit</div>
            </div>""", unsafe_allow_html=True)

    # Charts Section
    st.markdown("<br>", unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns([6, 4])

    with col_chart1:
        st.markdown("##### Akumulasi Tonase Kedatangan per Jam")
        df_hourly = df_filtered.copy()
        df_hourly["Jam"] = df_hourly["Jam Masuk"].apply(lambda x: str(x).split(":")[0] + ":00")
        hourly_summary = df_hourly.groupby(["Jam", "Bahan Baku"])["Berat Netto (Ton)"].sum().reset_index()
        
        fig_bar = px.bar(
            hourly_summary, x="Jam", y="Berat Netto (Ton)", color="Bahan Baku",
            color_discrete_map={"Fly Ash": "#475569", "Gypsum": "#0d9488", "Batu Bara": "#d97706"},
            barmode="stack", height=280
        )
        fig_bar.update_layout(
            margin=dict(l=10, r=10, t=10, b=10), 
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        st.markdown("##### Proporsi Material Incoming")
        pie_summary = df_filtered.groupby("Bahan Baku")["Berat Netto (Ton)"].sum().reset_index()
        fig_pie = px.pie(
            pie_summary, values="Berat Netto (Ton)", names="Bahan Baku", color="Bahan Baku",
            color_discrete_map={"Fly Ash": "#475569", "Gypsum": "#0d9488", "Batu Bara": "#d97706"},
            hole=0.45, height=280
        )
        fig_pie.update_layout(
            margin=dict(l=10, r=10, t=10, b=10), 
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Data Feed Table Section
    st.markdown("---")
    st.markdown("##### Live Data Feed TIS Jembatan Timbang")

    edited_df = st.data_editor(
        df_filtered,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "ID Transaksi": st.column_config.TextColumn("ID Transaksi", disabled=True),
            "Tanggal": st.column_config.DateColumn("Tanggal", disabled=True),
            "Bahan Baku": st.column_config.SelectboxColumn("Bahan Baku", options=["Fly Ash", "Gypsum", "Batu Bara"]),
            "Berat Netto (Ton)": st.column_config.NumberColumn("Berat Netto (Ton)", format="%.2f ton"),
            "Status Jembatan Timbang": st.column_config.SelectboxColumn("Status", options=["Selesai", "Progres Timbang", "Pending QC"])
        },
        height=320
    )

    col_btn1, col_btn2 = st.columns([3, 7])
    with col_btn1:
        if st.button("Simpan Perubahan Tabel", type="secondary", use_container_width=True):
            df_all.update(edited_df)
            st.session_state.tis_data = df_all
            st.success("Perubahan data tersimpan.")
            st.rerun()

    with col_btn2:
        csv_data = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export Data Kedatangan (CSV)",
            data=csv_data,
            file_name=f"TIS_Incoming_{selected_date.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
