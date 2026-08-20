import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date, datetime, timedelta

# Konfigurasi Halaman Dashboard
st.set_page_config(
    page_title="Monitoring Bahan Baku - PT Solusi Bangun Indonesia",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stApp { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    .header-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 24px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .header-title { font-size: 26px; font-weight: 700; margin: 0; }
    .header-subtitle { font-size: 14px; opacity: 0.85; margin-top: 6px; }
    
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 18px 20px;
        border-left: 5px solid #2a5298;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .metric-card-flyash { border-left-color: #4A5568; }
    .metric-card-gypsum { border-left-color: #319795; }
    .metric-card-batubara { border-left-color: #DD6B20; }
    .metric-card-total { border-left-color: #3182CE; }
    
    .metric-label { font-size: 13px; color: #718096; font-weight: 600; text-transform: uppercase; }
    .metric-value { font-size: 24px; font-weight: 700; color: #1A202C; margin: 6px 0; }
    .metric-sub { font-size: 12px; color: #A0AEC0; }
    
    .badge-dummy {
        background-color: #FEECDC;
        color: #9C4221;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Data TIS
if "tis_data" not in st.session_state:
    np.random.seed(42)
    start_date = date(2026, 8, 1)
    end_date = date(2026, 8, 20)
    delta = (end_date - start_date).days + 1
    
    materials = ["Fly Ash", "Gypsum", "Batu Bara"]
    suppliers = {
        "Fly Ash": ["PT PLN Nusantara Power", "PT Indonesia Power"],
        "Gypsum": ["PT Petrokimia Gresik", "PT Siam-Gypsum Indonesia"],
        "Batu Bara": ["PT Bukit Asam Tbk", "PT Adaro Indonesia", "PT Kaltim Prima Coal"]
    }
    truck_prefixes = ["B 91", "B 92", "B 93", "F 80", "F 81", "D 88"]
    
    records = []
    trx_id = 1001
    
    for day in range(delta):
        curr_date = start_date + timedelta(days=day)
        num_trucks = np.random.randint(12, 26)
        
        for _ in range(num_trucks):
            mat = np.random.choice(materials, p=[0.3, 0.25, 0.45])
            supp = np.random.choice(suppliers[mat])
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

TARGET_HARIAN = {"Fly Ash": 200.0, "Gypsum": 150.0, "Batu Bara": 350.0}

# Header Section
st.markdown("""
<div class="header-box">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 class="header-title">🏭 Real-Time Raw Material Incoming Dashboard</h1>
            <p class="header-subtitle">Divisi Production Planning — PT Solusi Bangun Indonesia</p>
        </div>
        <div>
            <span class="badge-dummy">⚠️ Mode Data Dummy (Simulasi TIS)</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Filter
st.sidebar.title("🔍 Control Panel")
selected_date = st.sidebar.date_input(
    "📅 Pilih Tanggal Monitoring:",
    value=date(2026, 8, 20),
    min_value=date(2026, 8, 1),
    max_value=date(2026, 8, 20)
)

selected_materials = st.sidebar.multiselect(
    "📦 Filter Bahan Baku:",
    options=["Fly Ash", "Gypsum", "Batu Bara"],
    default=["Fly Ash", "Gypsum", "Batu Bara"]
)

# Form Input Manual Transaksi
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Tambah Transaksi Manual")
with st.sidebar.form("add_transaction_form", clear_on_submit=True):
    new_time = st.time_input("Jam Masuk", value=datetime.now().time())
    new_mat = st.selectbox("Bahan Baku", ["Fly Ash", "Gypsum", "Batu Bara"])
    new_supp = st.text_input("Supplier", value="PT Vendor Utama")
    new_truck = st.text_input("No. Kendaraan", value="B 9999 SBI")
    new_po = st.text_input("No. PO", value="PO-SBI-2026-9999")
    new_weight = st.number_input("Berat Netto (Ton)", min_value=1.0, max_value=60.0, value=30.0, step=0.5)
    
    if st.form_submit_button("💾 Simpan Transaksi Baru"):
        new_row = {
            "ID Transaksi": f"TIS-MANUAL-{np.random.randint(100, 999)}",
            "Tanggal": selected_date,
            "Jam Masuk": new_time.strftime("%H:%M"),
            "Bahan Baku": new_mat,
            "Supplier": new_supp,
            "No. Kendaraan": new_truck,
            "No. PO": new_po,
            "Berat Netto (Ton)": new_weight,
            "Status Jembatan Timbang": "Selesai (Manual)",
            "Catatan": "Input Manual Operator PP"
        }
        st.session_state.tis_data = pd.concat([st.session_state.tis_data, pd.DataFrame([new_row])], ignore_index=True)
        st.sidebar.success("✅ Transaksi berhasil ditambahkan!")
        st.rerun()

# Filter Data
df_all = st.session_state.tis_data
df_filtered_date = df_all[df_all["Tanggal"] == selected_date]
df_filtered = df_filtered_date[df_filtered_date["Bahan Baku"].isin(selected_materials)]

st.subheader(f"📊 Summary Kedatangan Material — Tanggal: {selected_date.strftime('%d %B %Y')}")

if df_filtered.empty:
    st.warning(f"⚠️ Tidak ada data transaksi kedatangan material untuk tanggal {selected_date.strftime('%d-%m-%Y')}.")
else:
    # Summary Cards
    total_tonnage = df_filtered["Berat Netto (Ton)"].sum()
    total_trucks = len(df_filtered)
    
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        st.markdown(f"""
        <div class="metric-card metric-card-total">
            <div class="metric-label">Total All Material</div>
            <div class="metric-value">{total_tonnage:,.2f} <span style="font-size:14px;">Ton</span></div>
            <div class="metric-sub">🚚 Total {total_trucks} Truk/Ritase</div>
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
                <div class="metric-value">{mat_ton:,.2f} <span style="font-size:14px;">Ton</span></div>
                <div class="metric-sub">🎯 Target: {target} Ton ({pct:.1f}%) | {mat_trucks} Truk</div>
            </div>""", unsafe_allow_html=True)

    # Charts
    st.markdown("<br>", unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns([6, 4])

    with col_chart1:
        st.markdown("##### 📈 Akumulasi Tonase Kedatangan per Jam")
        df_hourly = df_filtered.copy()
        df_hourly["Jam"] = df_hourly["Jam Masuk"].apply(lambda x: str(x).split(":")[0] + ":00")
        hourly_summary = df_hourly.groupby(["Jam", "Bahan Baku"])["Berat Netto (Ton)"].sum().reset_index()
        
        fig_bar = px.bar(
            hourly_summary, x="Jam", y="Berat Netto (Ton)", color="Bahan Baku",
            color_discrete_map={"Fly Ash": "#4A5568", "Gypsum": "#319795", "Batu Bara": "#DD6B20"},
            barmode="stack", height=300
        )
        fig_bar.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        st.markdown("##### 🍕 Proporsi Komposisi Bahan Baku")
        pie_summary = df_filtered.groupby("Bahan Baku")["Berat Netto (Ton)"].sum().reset_index()
        fig_pie = px.pie(
            pie_summary, values="Berat Netto (Ton)", names="Bahan Baku", color="Bahan Baku",
            color_discrete_map={"Fly Ash": "#4A5568", "Gypsum": "#319795", "Batu Bara": "#DD6B20"},
            hole=0.45, height=300
        )
        fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

    # Data Editor
    st.markdown("---")
    st.subheader("📝 Live Data Feed TIS Jembatan Timbang")
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
        height=350
    )

    col_btn1, col_btn2 = st.columns([3, 7])
    with col_btn1:
        if st.button("💾 Simpan Perubahan Tabel", type="primary", use_container_width=True):
            df_all.update(edited_df)
            st.session_state.tis_data = df_all
            st.success("✅ Perubahan berhasil disimpan!")
            st.rerun()

    with col_btn2:
        csv_data = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data Hari Ini (CSV)",
            data=csv_data,
            file_name=f"TIS_Incoming_{selected_date.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
