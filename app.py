"""
app.py
=======
EHV Transformer Under-Impedance (Backup Impedance / Mho) Protection
Setting Calculator — Streamlit App

Structure mirrors app.py (line distance protection) exactly:
  Sidebar inputs → Section 1 (Base Impedances & CT/VT)
                 → Section 2 (Zone Reaches — Z1/Z2/Z3/Z4)
                 → Section 3 (SEF — Standby Earth Fault / DEF-equivalent)
                 → Section 4 (Load Encroachment / Blinder)
                 → Section 5 (Power Swing Block)
                 → Complete Settings Summary

Theme: Light blue — background #e8f4fa, cards #ffffff, panel #f0f8fc,
       borders #7ab8d4, text deep navy #03223a, dark blue #0a2a42
       Active nav: solid dark blue #0a2a42 with white text

Run:
    pip install streamlit plotly
    streamlit run app.py
"""

import streamlit as st
import math
import sys, os
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(__file__))
from calculations import calculate_tx, TX_VECTOR_GROUPS

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EHV Transformer Backup Impedance Calculator",
    page_icon="🔰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── THEME CSS — LIGHT BLUE ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background: #e8f4fa !important;
    color: #03223a !important;
}

.stApp { background: #e8f4fa !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #f0f8fc !important;
    border-right: 2px solid #7ab8d4 !important;
}
section[data-testid="stSidebar"] * { color: #0a2a42 !important; }
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stNumberInput input,
section[data-testid="stSidebar"] .stSelectbox select {
    background: #ffffff !important;
    border: 1px solid #7ab8d4 !important;
    color: #03223a !important;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
}

/* ── TITLES ── */
.main-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 26px; font-weight: 700;
    color: #0a2a42;
    letter-spacing: -0.5px; margin-bottom: 4px;
}
.sub-title {
    font-size: 12px; color: #4a7fa0;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 24px; letter-spacing: 0.8px;
}

/* ── SECTION HEADERS ── */
.sec-header {
    background: linear-gradient(90deg, #d0e9f5 0%, #e8f4fa 100%);
    border-left: 4px solid #0d7bbf;
    padding: 10px 16px; margin: 24px 0 14px 0;
    border-radius: 0 6px 6px 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px; font-weight: 700;
    color: #0a2a42; letter-spacing: 0.5px;
}
.sec-header-sef  { border-left-color: #d97706; color: #7c3a00;
    background: linear-gradient(90deg, #fef3e2 0%, #e8f4fa 100%); }
.sec-header-load { border-left-color: #7c3aed; color: #3b1070;
    background: linear-gradient(90deg, #ede9fe 0%, #e8f4fa 100%); }
.sec-header-psb  { border-left-color: #059669; color: #064e3b;
    background: linear-gradient(90deg, #d1fae5 0%, #e8f4fa 100%); }
.sec-header-sum  { border-left-color: #03223a; color: #03223a;
    background: linear-gradient(90deg, #cfe8f5 0%, #e8f4fa 100%); }

/* ── RESULT CARDS ── */
.result-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px; margin: 10px 0;
}
.rcard {
    background: #ffffff;
    border: 1px solid #7ab8d4;
    border-radius: 8px; padding: 12px 14px;
    position: relative; overflow: hidden;
    box-shadow: 0 1px 4px rgba(10,42,66,0.07);
}
.rcard::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 4px; height: 100%; background: #0d7bbf;
}
.rcard.sef::before   { background: #d97706; }
.rcard.load::before  { background: #7c3aed; }
.rcard.psb::before   { background: #059669; }
.rcard.warn::before  { background: #dc2626; }
.rcard.z1::before    { background: #0d7bbf; }
.rcard.z2::before    { background: #d97706; }
.rcard.z3::before    { background: #dc2626; }

.rcard-label {
    font-size: 10px; color: #4a7fa0;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 3px; text-transform: uppercase; letter-spacing: 0.8px;
}
.rcard-value {
    font-size: 20px; font-weight: 700;
    font-family: 'IBM Plex Mono', monospace; color: #03223a;
}
.rcard-unit  { font-size: 11px; color: #4a7fa0; font-family: 'IBM Plex Mono', monospace; }
.rcard-sub   { font-size: 11px; color: #0d7bbf; margin-top: 2px; font-family: 'IBM Plex Mono', monospace; }

/* ── FORMULA BOXES ── */
.formula-box {
    background: #f0f8fc; border: 1px solid #7ab8d4;
    border-radius: 6px; padding: 14px 18px; margin: 8px 0;
    font-family: 'IBM Plex Mono', monospace; font-size: 13px;
    color: #0a2a42;
}
.formula-box .step {
    color: #4a7fa0; font-size: 10px; text-transform: uppercase;
    letter-spacing: 1.2px; margin-bottom: 4px; margin-top: 8px;
}
.formula-box .step:first-child { margin-top: 0; }
.formula-box .eq   { color: #1565a0; font-size: 13px; margin: 3px 0; }
.formula-box .result {
    color: #0a2a42; font-size: 15px; font-weight: 700;
    margin-top: 6px; padding-top: 6px;
    border-top: 1px solid #7ab8d4;
}
.formula-box .note { color: #4a7fa0; font-size: 11px; margin-top: 4px; font-style: italic; }

/* ── THEORY BOXES ── */
.theory-box {
    background: #ffffff; border: 1px solid #7ab8d4;
    border-radius: 6px; padding: 16px 18px; margin: 8px 0;
    font-size: 13px; color: #0a2a42; line-height: 1.75;
}
.theory-box h4 {
    color: #0a2a42; font-family: 'IBM Plex Mono', monospace;
    font-size: 12px; letter-spacing: 1px; text-transform: uppercase;
    margin-bottom: 10px; margin-top: 0;
    padding-bottom: 6px; border-bottom: 1px solid #b8d8ea;
}
.theory-box .q { color: #0d4f7a; font-weight: 700; margin-top: 10px; }
.theory-box .a { color: #1e3a52; margin-left: 12px; margin-top: 3px; }

/* ── ZONE SUMMARY TABLE ── */
.zone-table {
    width: 100%; border-collapse: collapse;
    font-family: 'IBM Plex Mono', monospace; font-size: 12px; margin: 10px 0;
}
.zone-table th {
    background: #0a2a42; color: #ffffff;
    padding: 9px 12px; text-align: center;
    font-size: 11px; letter-spacing: 0.8px; text-transform: uppercase;
    border: 1px solid #7ab8d4;
}
.zone-table td {
    padding: 8px 12px; border: 1px solid #b8d8ea;
    text-align: center; color: #03223a;
    background: #ffffff;
}
.zone-table tr:nth-child(even) td { background: #f0f8fc; }
.zone-table tr:hover td { background: #d0e9f5; }

/* ── BADGES ── */
.badge {
    display: inline-block; padding: 2px 8px;
    border-radius: 4px; font-size: 11px; font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
}
.badge-blue   { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
.badge-green  { background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }
.badge-orange { background: #ffedd5; color: #9a3412; border: 1px solid #fdba74; }
.badge-red    { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
.badge-warn   { background: #fef9c3; color: #713f12; border: 1px solid #fde047; }
.badge-navy   { background: #0a2a42;   color: #ffffff; border: 1px solid #0a2a42; }

/* ── HEADER INFO BAR ── */
.info-bar {
    background: #ffffff; border: 1px solid #7ab8d4;
    border-radius: 8px; padding: 14px 20px;
    display: flex; gap: 28px; flex-wrap: wrap;
    margin-bottom: 20px;
    box-shadow: 0 1px 4px rgba(10,42,66,0.07);
}
.info-item .lbl { font-size: 10px; color: #4a7fa0; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase; letter-spacing: 1px; }
.info-item .val { font-size: 15px; font-weight: 700; font-family: 'IBM Plex Mono', monospace; color: #0a2a42; }
.info-item .val-blue { color: #0d7bbf; }

/* ── DIVIDER ── */
.hdivider { border: none; border-top: 1px solid #b8d8ea; margin: 14px 0; }

/* ── STREAMLIT OVERRIDES ── */
div[data-testid="metric-container"] {
    background: #ffffff !important; border: 1px solid #7ab8d4 !important;
    border-radius: 8px !important; padding: 10px !important;
}
div[data-testid="metric-container"] label { color: #4a7fa0 !important; }
div[data-testid="metric-container"] div[data-testid="metric-value"] { color: #03223a !important; }

.stExpander {
    background: #f0f8fc !important;
    border: 1px solid #7ab8d4 !important;
    border-radius: 6px !important;
}
.stButton>button {
    background: #0a2a42 !important; color: #ffffff !important;
    border: none !important; border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important; letter-spacing: 1.5px !important;
}
.stButton>button:hover { background: #0d4f7a !important; }

/* ── TABS ── */
div[data-baseweb="tab-list"] { background: #f0f8fc !important; border-bottom: 2px solid #7ab8d4; }
div[data-baseweb="tab"] { color: #4a7fa0 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 12px !important; }
div[data-baseweb="tab"][aria-selected="true"] {
    background: #0a2a42 !important; color: #ffffff !important;
    border-radius: 4px 4px 0 0;
}
</style>
""", unsafe_allow_html=True)

# ── HELPERS (mirrors app.py) ───────────────────────────────────────────────────
def rcard(label, value, unit="", sub="", kind=""):
    cls = f"rcard {kind}".strip()
    return f"""<div class="{cls}">
    <div class="rcard-label">{label}</div>
    <div class="rcard-value">{value}</div>
    <div class="rcard-unit">{unit}</div>
    {"<div class='rcard-sub'>" + sub + "</div>" if sub else ""}
</div>"""

def fbox(steps):
    inner = ""
    for s in steps:
        if   s[0] == "step": inner += f'<div class="step">{s[1]}</div>'
        elif s[0] == "eq":   inner += f'<div class="eq">{s[1]}</div>'
        elif s[0] == "res":  inner += f'<div class="result">▶ {s[1]}</div>'
        elif s[0] == "note": inner += f'<div class="note">ℹ {s[1]}</div>'
    return f'<div class="formula-box">{inner}</div>'

def tbox(title, content):
    return f'<div class="theory-box"><h4>📖 {title}</h4>{content}</div>'

def badge(text, color="blue"):
    return f'<span class="badge badge-{color}">{text}</span>'

def sec(title, kind=""):
    cls = f"sec-header {('sec-header-' + kind) if kind else ''}".strip()
    return f'<div class="{cls}">🔰 {title}</div>'

def mho_points(z_reach, theta_deg, n=360):
    """Return R, X arrays for a Mho circle."""
    theta = math.radians(theta_deg)
    Rc = (z_reach / 2) * math.cos(theta)
    Xc = (z_reach / 2) * math.sin(theta)
    r  = z_reach / 2
    angles = [i * 2 * math.pi / n for i in range(n + 1)]
    R = [Rc + r * math.cos(a) for a in angles]
    X = [Xc + r * math.sin(a) for a in angles]
    return R, X, Rc, Xc

# ── SIDEBAR INPUTS ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="font-family:IBM Plex Mono;font-size:15px;color:#0a2a42;font-weight:700;'
        'margin-bottom:2px;">🔰 EHV TRANSFORMER</div>'
        '<div style="font-family:IBM Plex Mono;font-size:10px;color:#4a7fa0;margin-bottom:16px;'
        'letter-spacing:1.5px;">BACKUP IMPEDANCE PROTECTION</div>',
        unsafe_allow_html=True,
    )

    st.markdown("**🏭 Identification**")
    sub_name  = st.text_input("Substation Name",  "Biswanath Chairali")
    tx_name   = st.text_input("Transformer Tag",  "400/230kV ICT-1")
    voltage   = st.selectbox("HV Voltage (kV)", [220, 400, 765], index=1)

    st.markdown("---")
    st.markdown("**🔌 Transformer Parameters**")
    c1, c2 = st.columns(2)
    with c1:
        vhv = st.number_input("HV kV",  100.0, 800.0, 400.0, 1.0)
        mva = st.number_input("MVA",    10.0,  1200.0, 315.0, 5.0)
        xr  = st.number_input("X/R",    1.0,   60.0,   20.0, 1.0)
    with c2:
        vlv   = st.number_input("LV kV",    10.0,  400.0, 230.0, 1.0)
        pct_z = st.number_input("%Z",        1.0,   50.0,  25.0, 0.1, format="%.1f")
        vg    = st.selectbox("Vector Group", TX_VECTOR_GROUPS, index=1)

    st.markdown("---")
    st.markdown("**🔗 CT & VT (HV Side)**")
    c1, c2 = st.columns(2)
    with c1:
        ct_pri = st.number_input("CT Primary (A)",  100, 5000, 600, 100)
        vt_pri = st.number_input("VT Primary (kV)", 1.0, 400.0, 230.0, 1.0,
                                  help="VT is on LV (230 kV) side")
    with c2:
        ct_sec = st.number_input("CT Secondary (A)", 1, 5, 1, 1)
        vt_sec = st.number_input("VT Secondary (V)", 100, 200, 110, 5)

    st.markdown("---")
    st.markdown("**⚡ System / Fault Data**")
    fault_mva  = st.number_input("3-ph Fault Level at HV Bus (MVA)", 100, 50000, 10000, 500)
    if1_lv     = st.number_input("Min 1-ph Fault at LV Bus — HV referred (A)", 10, 50000, 800, 50,
                                  help="Used for SEF TMS calculation")
    i_nom      = st.number_input("Bay Nominal Current (A)", 100, 5000, 460, 10,
                                  help="FLC at HV side = MVA / (√3 × HV kV)")

    st.markdown("---")
    st.markdown("**🌀 PSB**")
    f_swing = st.number_input("Swing Frequency (Hz)", 0.1, 5.0, 1.5, 0.1)

    st.markdown("---")
    calc_btn = st.button("🔰 CALCULATE", use_container_width=True)

# ── TITLE ──────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="main-title">🔰 EHV Transformer Backup Impedance Protection</div>'
    '<div class="sub-title">UNDER-IMPEDANCE (MHO) · ZONE 1/2/3/4 · SEF · LOAD ENCROACHMENT · PSB '
    '· IEC 60255-121 · CEA 2010</div>',
    unsafe_allow_html=True,
)

if not calc_btn:
    st.markdown("""
    <div style="background:#ffffff;border:1px solid #7ab8d4;border-radius:8px;
         padding:28px;margin-top:20px;text-align:center;
         box-shadow:0 1px 4px rgba(10,42,66,0.08);">
        <div style="font-family:IBM Plex Mono;font-size:15px;color:#0a2a42;
             font-weight:700;margin-bottom:8px;">
            Fill in the parameters in the left panel and click CALCULATE
        </div>
        <div style="font-family:IBM Plex Mono;font-size:11px;color:#4a7fa0;line-height:2;">
            Outputs include: Base Impedances &amp; CT/VT Conversion · Zone Reaches (Z1/Z2/Z3/Z4) ·
            Mho R-X Diagram · Standby Earth Fault (SEF) TMS ·
            Load Encroachment Blinder Check · Power Swing Block (PSB) ·
            Step-by-step formulae with IEC/CEA references in every section ·
            Interview preparation theory with Q&amp;A
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── RUN CALCULATIONS ───────────────────────────────────────────────────────────
inp = dict(
    vhv_kv=vhv, vlv_kv=vlv, mva=mva, pct_z=pct_z, xr_ratio=xr,
    ct_primary=ct_pri, ct_secondary=ct_sec,
    pt_primary_kv=vt_pri, pt_secondary_v=vt_sec,
    fault_mva=fault_mva, fault_1ph_lv=if1_lv,
    nominal_current=i_nom, swing_freq=f_swing, vector_group=vg,
)
c = calculate_tx(inp)

# ── HEADER INFO BAR ────────────────────────────────────────────────────────────
flc_label = f"{c['FLC']:.0f} A"
short_tx = c["Ztx"] < 5.0   # flag if Ztx very small (< 5 Ω primary)
st.markdown(f"""
<div class="info-bar">
  <div class="info-item">
    <div class="lbl">SUBSTATION</div>
    <div class="val">{sub_name}</div>
  </div>
  <div class="info-item">
    <div class="lbl">TRANSFORMER</div>
    <div class="val">{tx_name}</div>
  </div>
  <div class="info-item">
    <div class="lbl">VOLTAGE</div>
    <div class="val val-blue">{vhv:.0f}/{vlv:.0f} kV</div>
  </div>
  <div class="info-item">
    <div class="lbl">RATING</div>
    <div class="val val-blue">{mva:.0f} MVA</div>
  </div>
  <div class="info-item">
    <div class="lbl">%Z / X/R</div>
    <div class="val">{pct_z:.1f}% / {xr:.0f}</div>
  </div>
  <div class="info-item">
    <div class="lbl">CT / VT</div>
    <div class="val">{ct_pri}/{ct_sec} A · {vt_pri:.0f}kV/{vt_sec}V</div>
  </div>
  <div class="info-item">
    <div class="lbl">FLC (HV)</div>
    <div class="val">{flc_label}</div>
  </div>
  <div class="info-item">
    <div class="lbl">VECTOR GRP</div>
    <div class="val">{vg}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — BASE IMPEDANCES & CT/VT CONVERSION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(sec("SECTION 1 — BASE IMPEDANCES & CT / VT CONVERSION"), unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="result-grid">' +
        rcard("Z_base HV", f"{c['Zbase_HV']:.4f}", "Ω primary", f"= V²/MVA = {vhv}²/{mva}") +
        rcard("Z_transformer", f"{c['Ztx']:.4f}", "Ω primary", f"{pct_z}% × {c['Zbase_HV']:.3f} Ω") +
        rcard("Z_tx (R + jX)", f"{c['Ztx_R']:.4f} + j{c['Ztx_X']:.4f}", "Ω", f"∠{c['Z1_ang']:.2f}° (MTA)") +
        rcard("Z_source (Zsys)", f"{c['Zsys']:.4f}", "Ω primary", f"= V²/Fault MVA") +
    '</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="result-grid">' +
        rcard("CTR", f"{c['CTR']:.0f} : 1", "", f"{ct_pri}/{ct_sec} A") +
        rcard("PTR (HV referred)", f"{c['PTR']:.0f} : 1", "", f"VT on LV side → ref'd to {vhv:.0f}kV") +
        rcard("kk = CTR/PTR", f"{c['kk']:.5f}", "conversion factor", "primary Ω → relay sec Ω") +
        rcard("SIR (Zsys/Ztx)", f"{c['SIR']:.4f}", "—", "Source Impedance Ratio") +
    '</div>', unsafe_allow_html=True)

with st.expander("📐 Step-by-step Formulae — Base Impedances & CT/VT"):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(fbox([
            ("step", "Step 1: Base Impedance — HV Side (Primary Ω)"),
            ("eq",   f"Z_base_HV = V_HV² / MVA_rated"),
            ("eq",   f"= ({vhv} × 10³)² / ({mva} × 10⁶)"),
            ("eq",   f"= {vhv**2 * 1e6:.2e} / {mva * 1e6:.2e}"),
            ("res",  f"Z_base_HV = {c['Zbase_HV']:.6f} Ω"),
            ("step", "Step 2: Transformer Leakage Impedance"),
            ("eq",   f"Z_tx = (%Z / 100) × Z_base_HV"),
            ("eq",   f"= ({pct_z} / 100) × {c['Zbase_HV']:.4f}"),
            ("res",  f"Z_tx = {c['Ztx']:.6f} Ω  ∠{c['Z1_ang']:.3f}°"),
            ("step", "Step 3: R and X Components"),
            ("eq",   f"R_tx = Z_tx / √(1 + (X/R)²) = {c['Ztx']:.4f} / √(1+{xr}²)"),
            ("res",  f"R_tx = {c['Ztx_R']:.6f} Ω"),
            ("eq",   f"X_tx = X/R × R_tx = {xr} × {c['Ztx_R']:.4f}"),
            ("res",  f"X_tx = {c['Ztx_X']:.6f} Ω"),
        ]), unsafe_allow_html=True)
    with c2:
        st.markdown(fbox([
            ("step", "Step 4: Source Impedance at HV Bus"),
            ("eq",   f"Z_sys = V_HV² / Fault_MVA"),
            ("eq",   f"= {vhv}² × 10⁶ / ({fault_mva} × 10⁶)"),
            ("res",  f"Z_sys = {c['Zsys']:.6f} Ω"),
            ("step", "Step 5: CT and VT Ratios"),
            ("eq",   f"CTR = CT_primary / CT_secondary = {ct_pri} / {ct_sec} = {c['CTR']:.0f}"),
            ("eq",   f"VT primary referred to HV:"),
            ("eq",   f"  VTP_ref = VT_pri_kV × (V_HV/V_LV) × 1000"),
            ("eq",   f"  = {vt_pri} × ({vhv}/{vlv}) × 1000 = {c['PTR'] * vt_sec:.2f} V"),
            ("eq",   f"PTR = VTP_ref / VT_sec = {c['PTR'] * vt_sec:.2f} / {vt_sec} = {c['PTR']:.2f}"),
            ("res",  f"PTR = {c['PTR']:.4f}"),
            ("step", "Step 6: Relay Conversion Factor"),
            ("eq",   f"kk = CTR / PTR = {c['CTR']:.0f} / {c['PTR']:.2f}"),
            ("res",  f"kk = {c['kk']:.6f}  (primary Ω → relay secondary Ω)"),
            ("note", "All relay settings below in secondary Ω = primary Ω × kk"),
        ]), unsafe_allow_html=True)

with st.expander("📖 Theory & Interview Prep — Transformer Backup Impedance (Under-Impedance)"):
    st.markdown(tbox("Why Under-Impedance / Backup Impedance for Transformers?", """
<div class='q'>Q: What is under-impedance (backup impedance) protection for transformers?</div>
<div class='a'>Under-impedance protection applies a distance/impedance relay on the HV side of the transformer, looking FORWARD into the transformer and LV network. It acts as backup for: (1) transformer internal faults missed by differential protection, (2) LV busbar faults, (3) LV feeder faults where LV protection fails. The relay measures V/I impedance; if it falls inside the Mho circle (i.e. apparent impedance is lower than the reach setting), a trip is issued.</div>

<div class='q'>Q: Why is the relay placed on the HV (400 kV) side?</div>
<div class='a'>Per IEC 60255-121 and CEA 2010 guidelines, the HV side is the standard location because: (1) CT and VT instrumentation is most accurate on the HV side for large EHV transformers, (2) The relay can measure the full transformer + LV network impedance from this vantage point, (3) Tripping the HV CB also de-energises the transformer completely, (4) The HV bus fault current is higher, improving relay sensitivity.</div>

<div class='q'>Q: Why is this called "Mho" characteristic?</div>
<div class='a'>The Mho (admittance) characteristic is a circle on the R-X diagram that passes through the origin. Its diameter equals the zone reach (Z_reach) along the Maximum Torque Angle (MTA) direction. Faults inside the circle → trip. The origin-passing property makes it inherently directional — impedances in the second/third quadrant (behind relay) are always outside the circle.</div>

<div class='q'>Q: What is SIR and how does it affect performance?</div>
<div class='a'>SIR (Source Impedance Ratio) = Z_source / Z_tx. High SIR means a weak source: during faults, relay voltage drops sharply, reducing accuracy. For Z_tx of {:.3f} Ω and Z_sys of {:.3f} Ω, SIR = {:.2f}. Values above 4 indicate a short (weak) TX for the source; values below 0.5 indicate a strong source. High SIR may require VT correction schemes.</div>

<div class='q'>Q: What is the VT location significance?</div>
<div class='a'>The VT is on the LV (230 kV) side for safety and cost reasons on large EHV transformers. For impedance calculations, VT primary is referred to HV base: VTP_ref = VTP_LV × (V_HV / V_LV). This correctly maps measured secondary voltages to primary HV impedances.</div>
""".format(c['Ztx'], c['Zsys'], c['SIR'])), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — ZONE REACH CALCULATIONS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(sec("SECTION 2 — ZONE REACH CALCULATIONS (MHO CHARACTERISTIC)"), unsafe_allow_html=True)

# Zone summary table — Z3 governing label
_z3_gov_short = {
    'Option A (Z_tx + 1.5*Z_sys)': 'A: Z_tx+1.5Zsys',
    'Option B (1.8*Z_tx = 1.5*Z2)': 'B: 1.8×Z_tx',
    'IEC floor (1.2*Z2)':           'IEC floor: 1.2×Z2',
}.get(c['Z3_governing'], c['Z3_governing'])

st.markdown(f"""
<table class="zone-table">
<tr>
  <th>Zone</th><th>Reach %</th><th>Criterion</th>
  <th>Primary (Ω)</th><th>Secondary (Ω)</th>
  <th>Timer (s)</th><th>Direction</th><th>Status</th>
</tr>
<tr>
  <td><b>Z1</b></td>
  <td>{badge("80%","blue")}</td>
  <td>80% × Z_tx (IEC §6.3.2)</td>
  <td>{c['Z1r_pri']:.4f}</td><td><b>{c['Z1r_sec']:.5f}</b></td>
  <td>{c['tZ1']:.1f}</td><td>Forward</td>
  <td>{badge("INSTANTANEOUS","green")}</td>
</tr>
<tr>
  <td><b>Z2</b></td>
  <td>{badge("120%","blue")}</td>
  <td>120% × Z_tx (CEA §4.2.3)</td>
  <td>{c['Z2r_pri']:.4f}</td><td><b>{c['Z2r_sec']:.5f}</b></td>
  <td>{c['tZ2']:.2f}</td><td>Forward</td>
  <td>{badge(f"tZ2 = {c['tZ2']}s","orange")}</td>
</tr>
<tr>
  <td><b>Z3</b></td>
  <td>{badge(f"{c['Z3_pct']*100:.1f}%","blue")}</td>
  <td>MAX(A,B,Floor) — CEA §4.2.4 / IEC §6.3<br>
      <small>A={c['Z3_optA']:.3f} · B={c['Z3_optB']:.3f} · Floor={c['Z3_floor']:.3f} Ω</small></td>
  <td>{c['Z3r_pri']:.4f}</td><td><b>{c['Z3r_sec']:.5f}</b></td>
  <td>{c['tZ3']:.2f}</td><td>Forward</td>
  <td>{badge(f"▶ {_z3_gov_short}","warn")}</td>
</tr>
<tr>
  <td><b>Z4</b></td>
  <td>{badge("20% (Rev)","red")}</td>
  <td>20% × Z_tx — Reverse (CEA §4.3)</td>
  <td>{c['Z4r_pri']:.4f}</td><td><b>{c['Z4r_sec']:.5f}</b></td>
  <td>{c['tZ4']:.2f}</td><td>Reverse</td>
  <td>{badge("REVERSE","red")}</td>
</tr>
</table>
<div style="margin-top:6px;font-size:11px;font-family:IBM Plex Mono;color:#4a7fa0;">
MTA = {c['Z1_ang']:.2f}° = arctan(X/R={xr})  ·  kk = CTR/PTR = {c['kk']:.5f}  ·
Z3 always ≥ Z2 (IEC hard floor = 1.2 × Z2 = {c['Z3_floor']:.4f} Ω)  ·  SIR = {c['SIR']:.3f}
</div>
""", unsafe_allow_html=True)

# ── Mho R-X Plot ──────────────────────────────────────────────────────────────
st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
col_plot, col_steps = st.columns([1.6, 1])

with col_plot:
    st.markdown("**📊 Mho Characteristic — R-X Plane (Primary Ω, HV referred)**")
    z1R, z1X, z1Rc, z1Xc = mho_points(c['Z1r_pri'], c['Z1_ang'])
    z2R, z2X, z2Rc, z2Xc = mho_points(c['Z2r_pri'], c['Z1_ang'])
    z3R, z3X, z3Rc, z3Xc = mho_points(c['Z3r_pri'], c['Z1_ang'])

    tx_ang  = math.radians(c['Z1_ang'])
    lim     = c['Z3r_pri'] * 1.35
    mta_len = c['Z3r_pri'] * 1.2

    traces = [
        go.Scatter(x=z3R, y=z3X, fill='toself', fillcolor='rgba(220,38,38,0.07)',
            line=dict(color='#dc2626', width=2, dash='dash'),
            name=f"Zone 3 — {c['Z3r_pri']:.3f} Ω",
            hovertemplate='R: %{x:.3f} Ω<br>X: %{y:.3f} Ω<extra>Zone 3</extra>'),
        go.Scatter(x=z2R, y=z2X, fill='toself', fillcolor='rgba(217,119,6,0.08)',
            line=dict(color='#d97706', width=2),
            name=f"Zone 2 — {c['Z2r_pri']:.3f} Ω",
            hovertemplate='R: %{x:.3f} Ω<br>X: %{y:.3f} Ω<extra>Zone 2</extra>'),
        go.Scatter(x=z1R, y=z1X, fill='toself', fillcolor='rgba(13,123,191,0.12)',
            line=dict(color='#0d7bbf', width=2.5),
            name=f"Zone 1 — {c['Z1r_pri']:.3f} Ω",
            hovertemplate='R: %{x:.3f} Ω<br>X: %{y:.3f} Ω<extra>Zone 1</extra>'),
        # Transformer impedance vector
        go.Scatter(x=[0, c['Ztx_R']], y=[0, c['Ztx_X']],
            mode='lines+markers',
            line=dict(color='#059669', width=3),
            marker=dict(size=[0, 12], color='#059669', symbol=['circle', 'diamond']),
            name=f"Z_tx = {c['Ztx']:.3f} Ω"),
        # Source impedance (behind relay — negative direction)
        go.Scatter(x=[0, -c['Zsys'] * math.cos(tx_ang)],
                   y=[0, -c['Zsys'] * math.sin(tx_ang)],
            mode='lines+markers',
            line=dict(color='#dc2626', width=2, dash='dot'),
            marker=dict(size=[0, 10], color='#dc2626', symbol=['circle', 'triangle-left']),
            name=f"Z_sys = {c['Zsys']:.3f} Ω (behind)"),
        # MTA line
        go.Scatter(x=[0, mta_len * math.cos(tx_ang)],
                   y=[0, mta_len * math.sin(tx_ang)],
            mode='lines', line=dict(color='rgba(10,42,66,0.18)', width=1, dash='longdash'),
            name=f"MTA = {c['Z1_ang']:.1f}°", hoverinfo='none'),
        # Origin
        go.Scatter(x=[0], y=[0], mode='markers',
            marker=dict(size=12, color='#0a2a42', symbol='cross'),
            name='Relay Point (Origin)'),
    ]

    annotations = [
        dict(x=z1Rc*0.55, y=z1Xc + c['z1_r']*0.5, text='Z1',
             font=dict(color='#0d7bbf', size=13, family='IBM Plex Mono'), showarrow=False),
        dict(x=z2Rc*0.45, y=z2Xc + c['z2_r']*0.55, text='Z2',
             font=dict(color='#d97706', size=13, family='IBM Plex Mono'), showarrow=False),
        dict(x=z3Rc*0.35, y=z3Xc + c['z3_r']*0.6, text='Z3',
             font=dict(color='#dc2626', size=13, family='IBM Plex Mono'), showarrow=False),
    ]

    fig = go.Figure(data=traces)
    fig.update_layout(
        paper_bgcolor='#ffffff', plot_bgcolor='#f8fbfd',
        font=dict(family='IBM Plex Mono', color='#0a2a42', size=11),
        title=dict(
            text=f"Mho Char. — {vhv:.0f}/{vlv:.0f}kV {mva:.0f}MVA | MTA={c['Z1_ang']:.1f}° | HV Side Forward",
            font=dict(color='#0a2a42', size=12), x=0.5),
        xaxis=dict(title=dict(text="R (Ω) — Resistance", font=dict(color='#4a7fa0')),
            range=[-lim*0.55, lim], zeroline=True,
            zerolinecolor='rgba(10,42,66,0.25)', zerolinewidth=1,
            gridcolor='rgba(122,184,212,0.3)', tickfont=dict(color='#4a7fa0')),
        yaxis=dict(title=dict(text="X (Ω) — Reactance", font=dict(color='#4a7fa0')),
            range=[-lim*0.3, lim*1.05], zeroline=True,
            zerolinecolor='rgba(10,42,66,0.25)', zerolinewidth=1,
            gridcolor='rgba(122,184,212,0.3)', tickfont=dict(color='#4a7fa0'),
            scaleanchor='x', scaleratio=1),
        legend=dict(bgcolor='rgba(240,248,252,0.9)', bordercolor='#7ab8d4',
            borderwidth=1, font=dict(color='#0a2a42', size=10), x=1, xanchor='right', y=0),
        annotations=annotations, hovermode='closest',
        margin=dict(l=55, r=10, t=44, b=50), height=480,
    )
    st.plotly_chart(fig, use_container_width=True)

with col_steps:
    st.markdown("**📐 Zone Reach Formulae**")
    t_z1, t_z2, t_z3, t_z4 = st.tabs(["Z1", "Z2", "Z3", "Z4"])

    with t_z1:
        st.markdown(fbox([
            ("step", "Zone-1 — 80% of Transformer Impedance"),
            ("eq",   "Z1_reach = 80% × Z_tx  (IEC 60255-121 §6.3.2)"),
            ("eq",   f"= 0.80 × {c['Ztx']:.6f}"),
            ("res",  f"Z1_primary = {c['Z1r_pri']:.6f} Ω"),
            ("eq",   f"Z1_sec = Z1_pri × kk = {c['Z1r_pri']:.4f} × {c['kk']:.5f}"),
            ("res",  f"Z1_secondary = {c['Z1r_sec']:.6f} Ω"),
            ("note", f"tZ1 = 0.0 s (instantaneous). 20% margin prevents overreach due to CT/VT errors and relay tolerances."),
        ]), unsafe_allow_html=True)

    with t_z2:
        st.markdown(fbox([
            ("step", "Zone-2 — 120% of Transformer Impedance"),
            ("eq",   "Z2_reach = 120% × Z_tx  (CEA §4.2.3)"),
            ("eq",   f"= 1.20 × {c['Ztx']:.6f}"),
            ("res",  f"Z2_primary = {c['Z2r_pri']:.6f} Ω"),
            ("eq",   f"Z2_secondary = {c['Z2r_pri']:.4f} × {c['kk']:.5f}"),
            ("res",  f"Z2_secondary = {c['Z2r_sec']:.6f} Ω"),
            ("eq",   f"tZ2 = {c['tZ2']} s  (≥ 0.4 s grading — CEA §5.1 for {vhv:.0f}kV class)"),
            ("note", "Covers 100% of transformer + 20% margin for LV busbar backup."),
        ]), unsafe_allow_html=True)

    with t_z3:
        st.markdown(fbox([
            ("step", "Zone-3 — Remote Backup: MAX of 3 criteria (CEA §4.2.4 / IEC 60255-121 §6.3)"),
            ("eq",   "Option A: Z3 = Z_tx + 1.5 × Z_sys  (source-impedance reach)"),
            ("eq",   f"= {c['Ztx']:.4f} + 1.5 × {c['Zsys']:.4f} = {c['Z3_optA']:.4f} Ω"),
            ("eq",   "Option B: Z3 = 1.8 × Z_tx  (= 1.5 × Z2; governs when source is strong)"),
            ("eq",   f"= 1.8 × {c['Ztx']:.4f} = {c['Z3_optB']:.4f} Ω"),
            ("eq",   "IEC Hard Floor: Z3 >= 1.2 × Z2  (minimum grading margin)"),
            ("eq",   f"= 1.2 × {c['Z2r_pri']:.4f} = {c['Z3_floor']:.4f} Ω"),
            ("res",  f"Z3 = MAX({c['Z3_optA']:.4f}, {c['Z3_optB']:.4f}, {c['Z3_floor']:.4f})  →  Governed by: {c['Z3_governing']}"),
            ("res",  f"Z3_primary = {c['Z3r_pri']:.6f} Ω"),
            ("eq",   f"Z3_secondary = {c['Z3r_pri']:.4f} × {c['kk']:.5f}"),
            ("res",  f"Z3_secondary = {c['Z3r_sec']:.6f} Ω"),
            ("eq",   f"tZ3 = {c['tZ3']} s  (400kV class — CEA §5.1)"),
            ("note", "Option B governs when fault level is high (strong source, low Z_sys). IEC floor ensures Z3 always exceeds Z2 by minimum 20%."),
        ]), unsafe_allow_html=True)

    with t_z4:
        st.markdown(fbox([
            ("step", "Zone-4 — Reverse Zone (CEA §4.3)"),
            ("eq",   "Z4_reach = 20% × Z_tx  (reverse direction)"),
            ("eq",   f"= 0.20 × {c['Ztx']:.6f}"),
            ("res",  f"Z4_primary = {c['Z4r_pri']:.6f} Ω"),
            ("res",  f"Z4_secondary = {c['Z4r_sec']:.6f} Ω"),
            ("note", "Used for HV busbar backup and current reversal guard in POTT schemes. tZ4 = 0.5 s."),
        ]), unsafe_allow_html=True)

with st.expander("📖 Theory & Interview Prep — Zone Reaches for Transformer"):
    st.markdown(tbox("Distance Zone Philosophy for EHV Transformer", """
<div class='q'>Q: Why is Zone-1 set at 80% of transformer impedance?</div>
<div class='a'>The 20% margin accounts for measurement uncertainties: CT class (0.5–1P), VT class (0.5–1P), relay measurement accuracy (typically ±5%), and transformer impedance variation with tap position (±10% variation is common for on-load tap changers). Setting Zone-1 at 80% ensures it NEVER overreaches beyond the transformer for any combination of these errors — eliminating false trips for through-faults on the LV network.</div>

<div class='q'>Q: Why does Zone-2 set at 120% (not 150%)?</div>
<div class='a'>120% covers the entire transformer (100%) with a 20% overreach into the LV busbar. This ensures Zone-2 backs up the last 20% not covered by Zone-1. Setting higher (150%+) risks encroachment into the LV feeder Zone-1 reach, causing coordination issues. The 0.5 s delay provides time for LV bus protection to clear LV faults first.</div>

<div class='q'>Q: What is the logic behind Zone-3 = Z_tx + 1.5 × Z_sys?</div>
<div class='a'>Zone-3 provides remote backup for faults beyond the LV bus (on LV feeders). Z_tx covers the transformer; 1.5 × Z_sys provides reach into the LV network equivalent to 1.5 times the source impedance. The 1.5 factor ensures coverage even if fault level drops 33% due to system changes (outage of parallel sources), maintaining adequate reach under all system conditions.</div>

<div class='q'>Q: What is the purpose of Zone-4 (reverse zone) for transformers?</div>
<div class='a'>Zone-4 looks backward toward the HV busbar. It is used for: (1) HV busbar backup protection — provides backup trip if busbar protection (BBP) fails, (2) Current reversal guard in PUTT/POTT teleprotection schemes — prevents unwanted tripping when current direction reverses during fault clearance on parallel feeders, (3) Detecting close-in busbar faults that may have very low impedance to the relay.</div>

<div class='q'>Q: How does MTA (Maximum Torque Angle) affect the Mho characteristic?</div>
<div class='a'>MTA defines the direction of maximum sensitivity of the Mho circle on the R-X diagram. For a transformer, MTA is set equal to the impedance angle of the transformer (arctan(X/R)), typically 80–87° for large EHV transformers. This ensures the Mho circle is aligned along the fault impedance direction, maximising coverage for internal faults while minimising the risk of encroachment on load impedances (which lie at 20–30° angles).</div>
"""), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — STANDBY EARTH FAULT (SEF)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(sec("SECTION 3 — STANDBY EARTH FAULT (SEF) / BACKUP DEF SETTINGS", "sef"),
            unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="result-grid">' +
        rcard("IN>1 Pickup (sec)", f"{c['Is_sec']:.4f}", "A secondary",
              f"= {c['Is_pri']:.2f} A primary  ({c['Is_pct']*100:.0f}% FLC)", "sef") +
        rcard("Operating Time", f"{c['t_op']:.2f}", "seconds",
              f"tZ3 ({c['tZ3']}s) + 0.1s grading margin", "sef") +
        rcard("If / Is Ratio", f"{c['ratio']:.4f}", "—",
              f"{if1_lv}A / {c['Is_pri']:.2f}A", "sef") +
        rcard("TMS (IEC S-Inverse)", f"{c['TMS']:.6f}", "",
              "Normal Inverse curve (NI)", "sef") +
    '</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="result-grid">' +
        rcard("Char. Angle",     "-45°", "degrees", "Standard SEF angle", "sef") +
        rcard("Polarisation",   "NEG. SEQ.", "I₂ / V₂",
              "Negative sequence polarisation", "sef") +
        rcard("I2pol Threshold", f"{c['I2pol_ma']}", "mA secondary",
              "Min I₂ for directionality", "sef") +
        rcard("V2pol Threshold", f"{c['V2pol']:.3f}", "V secondary",
              "5% of VT_sec/√3", "sef") +
    '</div>', unsafe_allow_html=True)

with st.expander("📐 Step-by-step Formulae — SEF TMS Calculation"):
    st.markdown(fbox([
        ("step", "Step 1: SEF Pickup Current — 20% of Full Load Current"),
        ("eq",   f"FLC_HV = MVA × 10⁶ / (√3 × V_HV × 10³)"),
        ("eq",   f"= {mva} × 10⁶ / (1.732 × {vhv} × 10³) = {c['FLC']:.2f} A"),
        ("eq",   f"Is_primary = 20% × FLC = 0.20 × {c['FLC']:.2f}"),
        ("res",  f"Is_primary = {c['Is_pri']:.4f} A"),
        ("eq",   f"Is_secondary = Is_pri / CTR = {c['Is_pri']:.4f} / {c['CTR']:.0f}"),
        ("res",  f"Is_secondary = {c['Is_sec']:.6f} A"),
        ("step", "Step 2: Operating Time — Coordinate Above Zone-3"),
        ("eq",   f"t_op = tZ3 + 0.1s = {c['tZ3']} + 0.1"),
        ("res",  f"t_op = {c['t_op']:.2f} s"),
        ("note", "0.1 s margin above Zone-3 ensures SEF does not interfere with impedance zone tripping"),
        ("step", "Step 3: Fault Current Ratio (If / Is)"),
        ("eq",   f"ratio = If_1ph_LV / Is_primary = {if1_lv} / {c['Is_pri']:.4f}"),
        ("res",  f"ratio = {c['ratio']:.6f}"),
        ("step", "Step 4: TMS — IEC Normal Inverse (Standard Inverse) Curve"),
        ("eq",   "t = TMS × 0.14 / [(If/Is)^0.02 − 1]  →  TMS = t × [(If/Is)^0.02 − 1] / 0.14"),
        ("eq",   f"TMS = {c['t_op']} × [{c['ratio']:.4f}^0.02 − 1] / 0.14"),
        ("eq",   f"TMS = {c['t_op']} × [{c['ratio']**0.02:.6f} − 1] / 0.14"),
        ("eq",   f"TMS = {c['t_op']} × {(c['ratio']**0.02 - 1):.6f} / 0.14"),
        ("res",  f"TMS = {c['TMS']:.6f}"),
        ("step", "Step 5: V2pol (Negative Sequence VT Threshold)"),
        ("eq",   f"V2pol = 5% × (VT_sec / √3) = 0.05 × ({vt_sec} / 1.732)"),
        ("res",  f"V2pol = {c['V2pol']:.4f} V"),
    ]), unsafe_allow_html=True)

with st.expander("📖 Theory & Interview Prep — SEF / Standby Earth Fault"):
    st.markdown(tbox("Standby Earth Fault Protection for EHV Transformers", """
<div class='q'>Q: What is the difference between REF (Restricted Earth Fault) and SEF (Standby Earth Fault)?</div>
<div class='a'>REF (Restricted Earth Fault) is a HIGH-SPEED, HIGH-SENSITIVITY differential-type protection using the Merz-Price circulating current principle. It only detects earth faults within the transformer winding — it is "restricted" to the protected zone bounded by CTs. SEF (Standby Earth Fault) is a BACKUP, SLOWER IDMT overcurrent element on the residual (zero-sequence) current. SEF catches faults that REF misses (e.g., faults outside the REF zone, REF CT saturation, REF equipment failure). Both are necessary for complete transformer earth fault protection.</div>

<div class='q'>Q: Why is the SEF pickup set at 20% of FLC?</div>
<div class='a'>Earth fault current magnitude depends on system earthing and fault path resistance. For solidly earthed HV transformers (typical for 400 kV), single-phase-to-earth fault current can reach 50-100% of the 3-phase fault current. Setting pickup at 20% of FLC (full load current) ensures: (1) Detection of relatively low-current HIF (high impedance faults) in windings, (2) Sufficient margin above load unbalance (typically < 5% for balanced loads), (3) Coordination with LV REF element which has higher sensitivity.</div>

<div class='q'>Q: Why use negative sequence polarisation (I2/V2) instead of zero sequence (I0/V0)?</div>
<div class='a'>Negative sequence polarisation has key advantages: (1) Not affected by zero-sequence mutual coupling between parallel transformers sharing the same HV bus, (2) Remains available even during close-in faults where V0 at the relay may be very small (solidly earthed buses), (3) Not corrupted by healthy-state load unbalance in the zero-sequence network, (4) More reliable for transformers with delta-connected windings where zero sequence is blocked.</div>

<div class='q'>Q: What is the significance of the −45° characteristic angle?</div>
<div class='a'>For earth faults on transformer HV windings, the fault current leads the residual voltage by approximately 45–60° (depending on the X/R ratio and earthing impedance). Setting the characteristic angle at −45° (the maximum torque direction) means the relay is most sensitive when IN lags V_polarising by 45° — matching typical transformer earth fault conditions. Incorrect angle setting can cause under-reach (miss faults) or incorrect directionality.</div>

<div class='q'>Q: Explain the IEC Standard Inverse (Normal Inverse) IDMT curve used for TMS.</div>
<div class='a'>Operating time = TMS × 0.14 / [(If/Is)^0.02 − 1]. This is IEC 60255-151 Standard Inverse characteristic. As fault current increases beyond the pickup, operating time decreases with a moderate inverse slope (exponent 0.02). This provides: (1) Faster operation for severe close-in faults, (2) Slower operation for weak distant faults, allowing downstream protections time to operate first. For backup SEF, the Normal Inverse curve gives better coordination margin compared to Very Inverse or Extremely Inverse curves.</div>
"""), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — LOAD ENCROACHMENT / BLINDER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(sec("SECTION 4 — LOAD ENCROACHMENT / BLINDER CHECK", "load"),
            unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="result-grid">' +
        rcard("FLC (HV side)", f"{c['FLC']:.1f}", "A", f"MVA/(√3 × {vhv}kV)", "load") +
        rcard("I_max (1.5× FLC)", f"{c['I_max']:.1f}", "A", f"1.5 × {i_nom}", "load") +
        rcard("Min Load R (Primary)", f"{c['Rload_pri']:.4f}", "Ω primary",
              f"0.85 × Vph / I_max", "load") +
        rcard("Min Load R (Secondary)", f"{c['Rload_sec']:.5f}", "Ω secondary",
              f"Rload_pri × kk", "load") +
    '</div>', unsafe_allow_html=True)

with col2:
    encroach_badge = badge("⚠ RISK", "warn") if c["load_encroach_risk"] else badge("✓ SAFE", "green")
    st.markdown('<div class="result-grid">' +
        rcard("Z< Blinder (secondary)", f"{c['Z_blinder_sec']:.5f}", "Ω secondary",
              "= Min Load R secondary", "load") +
        rcard("Load Angle", "30°", "fixed", "Standard PF angle for transmission", "load") +
        rcard("Z3/Blinder Ratio", f"{c['Z3_vs_load']:.4f}", "—",
              "Z3_sec / Rload_sec",
              "warn" if c["load_encroach_risk"] else "load") +
        rcard("Encroachment Risk", encroach_badge, "",
              f"Ratio {'> 0.8 ⚠ Enable blinder!' if c['load_encroach_risk'] else '≤ 0.8 ✓ No blinder needed'}",
              "warn" if c["load_encroach_risk"] else "load") +
    '</div>', unsafe_allow_html=True)

with st.expander("📐 Step-by-step Formulae — Load Encroachment Check"):
    st.markdown(fbox([
        ("step", "Step 1: Full Load Current (HV side)"),
        ("eq",   f"FLC = MVA × 10⁶ / (√3 × V_HV × 10³)"),
        ("eq",   f"= {mva} × 10⁶ / (1.732 × {vhv} × 10³)"),
        ("res",  f"FLC = {c['FLC']:.4f} A"),
        ("step", "Step 2: Maximum Loading Current (1.5× nominal)"),
        ("eq",   f"I_max = 1.5 × I_nominal = 1.5 × {i_nom}"),
        ("res",  f"I_max = {c['I_max']:.2f} A"),
        ("step", "Step 3: Minimum Phase Voltage (85% depressed voltage)"),
        ("eq",   f"V_ph_min = 0.85 × (V_HV × 10³ / √3) = 0.85 × {vhv*1000:.0f}/1.732"),
        ("res",  f"V_ph_min = {c['V_ph_min']:.2f} V"),
        ("step", "Step 4: Minimum Load Resistance (Primary Ω)"),
        ("eq",   f"R_load_primary = V_ph_min / I_max = {c['V_ph_min']:.2f} / {c['I_max']:.2f}"),
        ("res",  f"R_load_primary = {c['Rload_pri']:.6f} Ω"),
        ("eq",   f"R_load_secondary = R_load_pri × kk = {c['Rload_pri']:.4f} × {c['kk']:.5f}"),
        ("res",  f"R_load_secondary = {c['Rload_sec']:.6f} Ω"),
        ("step", "Step 5: Load Encroachment Check"),
        ("eq",   f"Z3_reach_sec / R_load_sec = {c['Z3r_sec']:.5f} / {c['Rload_sec']:.5f}"),
        ("res",  f"Ratio = {c['Z3_vs_load']:.5f}  →  "
                 f"{'⚠ > 0.8: Z3 MAY ENCROACH on load. Enable quadrilateral blinder!' if c['load_encroach_risk'] else '✓ ≤ 0.8: Z3 safe from load impedance region'}"),
    ]), unsafe_allow_html=True)

with st.expander("📖 Theory & Interview Prep — Load Encroachment for Transformer"):
    st.markdown(tbox("Load Encroachment in Transformer Backup Impedance Protection", """
<div class='q'>Q: How can heavy load cause a transformer backup impedance relay to mal-trip?</div>
<div class='a'>The backup impedance relay measures apparent impedance Z_app = V/I. Under maximum load (high current, low voltage), Z_app = V_phase_min / I_max can fall inside Zone-3 of the Mho characteristic. The relay cannot distinguish heavy load from a high-impedance fault within Zone-3, potentially causing an unwanted trip of the transformer — a very consequential event for the power system.</div>

<div class='q'>Q: Why use 85% voltage and 1.5× nominal current for the load calculation?</div>
<div class='a'>85% voltage represents the minimum allowable system voltage under stressed conditions (post-fault voltage depression, maximum active power transfer). 1.5× nominal current represents transformer overload during emergencies (most transformers are rated for short-term overloads of 120-150% of nameplate). Using these simultaneous worst-case values gives Z_load_min = 0.85 Vph / 1.5 I_nom, which is the true minimum load impedance the relay might see without a fault.</div>

<div class='q'>Q: What is the 0.8 criterion (Z3/Rload ratio)?</div>
<div class='a'>A ratio of Z3/Rload < 0.8 means Zone-3 stays 20% away from the minimum load impedance boundary — providing 20% security margin for measurement errors and unexpected load extremes. If the ratio exceeds 0.8, Zone-3 is at risk of intersecting the load impedance region and a load blinder (resistive boundary) must be enabled on the relay to cut off the Mho circle at the load region boundary.</div>

<div class='q'>Q: What is a load blinder for a Mho relay?</div>
<div class='a'>A load blinder is a straight-line resistive boundary on the R-X diagram, set at R = R_load (the minimum load resistance). Any impedance vector with R > R_blinder is classified as "load" and is excluded from the Mho tripping decision, even if it falls geometrically inside the Mho circle. This is implemented as the "R-reach" parameter in modern numerical relays with quadrilateral or modified Mho characteristics.</div>
"""), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — POWER SWING BLOCK (PSB)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(sec("SECTION 5 — POWER SWING BLOCK (PSB) SETTINGS", "psb"),
            unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="result-grid">' +
        rcard("Zs (Source Imp., sec)", f"{c['Zs_sec']:.5f}", "Ω secondary",
              f"= {c['Zs_pri']:.4f} Ω primary", "psb") +
        rcard("Inner Blinder (RLdInFw)", f"{c['RLdInFw']:.5f}", "Ω secondary",
              "R_load_sec / 2", "psb") +
        rcard("Outer Blinder (RLdOutFw)", f"{c['RLdOutFw']:.5f}", "Ω secondary",
              "From δ_out calculation", "psb") +
        rcard("Delta R (Separation)", f"{c['Delta_R']:.5f}", "Ω secondary",
              "RLdOutFw − RLdInFw", "psb") +
    '</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="result-grid">' +
        rcard("δ_in (Entry angle)", f"{c['delta_in']:.3f}", "degrees",
              "2 × arctan(Zs / 2·RLdInFw)", "psb") +
        rcard("δ_out (Exit angle)", f"{c['delta_out']:.3f}", "degrees",
              "δ_in − tP1 × f_sw × 360", "psb") +
        rcard("Swing Frequency", f"{f_swing}", "Hz", "User input", "psb") +
        rcard("PSB Timer", "50 ms", "milliseconds", "Fixed standard (CEA)", "psb") +
    '</div>', unsafe_allow_html=True)

with st.expander("📐 Step-by-step Formulae — PSB Blinder Calculation"):
    st.markdown(fbox([
        ("step", "Step 1: Source Impedance from 3-ph Fault MVA"),
        ("eq",   f"If_3ph = Fault_MVA × 10⁶ / (√3 × V_HV × 10³)"),
        ("eq",   f"= {fault_mva} × 10⁶ / (1.732 × {vhv} × 10³) = {c['If3_A']:.2f} A"),
        ("eq",   f"V_base = V_HV × 10³ / √3 = {vhv*1000:.0f} / 1.732 = {vhv*1000/math.sqrt(3):.2f} V"),
        ("eq",   f"Zs_primary = V_base / If_3ph = {vhv*1000/math.sqrt(3):.2f} / {c['If3_A']:.2f}"),
        ("res",  f"Zs_primary = {c['Zs_pri']:.6f} Ω"),
        ("eq",   f"Zs_secondary = Zs_pri × kk = {c['Zs_pri']:.4f} × {c['kk']:.5f}"),
        ("res",  f"Zs_secondary = {c['Zs_sec']:.6f} Ω"),
        ("step", "Step 2: Inner Blinder (RLdInFw)"),
        ("eq",   f"RLdInFw = R_load_secondary / 2 = {c['Z_blinder_sec']:.5f} / 2"),
        ("res",  f"RLdInFw = {c['RLdInFw']:.6f} Ω"),
        ("step", "Step 3: Entry Angle δ_in"),
        ("eq",   "δ_in = 2 × arctan(Zs_sec / (2 × RLdInFw))"),
        ("eq",   f"= 2 × arctan({c['Zs_sec']:.5f} / (2 × {c['RLdInFw']:.5f}))"),
        ("res",  f"δ_in = {c['delta_in']:.4f}°"),
        ("step", "Step 4: Exit Angle δ_out (tP1 = 1 s assumed)"),
        ("eq",   "δ_out = δ_in − tP1 × f_swing × 360"),
        ("eq",   f"= {c['delta_in']:.4f} − 1 × {f_swing} × 360"),
        ("res",  f"δ_out = {c['delta_out']:.4f}°"),
        ("step", "Step 5: Outer Blinder (RLdOutFw)"),
        ("eq",   "RLdOutFw = Zs_sec / (2 × tan(|δ_out| / 2))"),
        ("res",  f"RLdOutFw = {c['RLdOutFw']:.6f} Ω"),
        ("step", "Step 6: Blinder Separation ΔR"),
        ("eq",   f"ΔR = RLdOutFw − RLdInFw = {c['RLdOutFw']:.5f} − {c['RLdInFw']:.5f}"),
        ("res",  f"ΔR = {c['Delta_R']:.6f} Ω"),
        ("note", "PSB timer = 50 ms. Impedance crossing both blinders in < 50 ms → FAULT (allow trip). > 50 ms → SWING (block trip)."),
    ]), unsafe_allow_html=True)

with st.expander("📖 Theory & Interview Prep — Power Swing Block for Transformer"):
    st.markdown(tbox("Power Swing Block (PSB) — Transformer Backup Relay", """
<div class='q'>Q: Why is PSB needed for a transformer backup impedance relay?</div>
<div class='a'>During system disturbances (fault clearance, sudden load rejection), the power angle between connected systems oscillates — creating a power swing. The apparent impedance seen by the relay sweeps across the R-X diagram. If this sweep trajectory passes through Zone-2 or Zone-3 of the Mho characteristic, the relay may trip the transformer — disconnecting a healthy power transformer and potentially worsening the disturbance. PSB prevents this by distinguishing fast-moving fault impedance from slow-moving swing impedance.</div>

<div class='q'>Q: How does the PSB detect a swing vs a real fault?</div>
<div class='a'>The key diagnostic is RATE OF IMPEDANCE CHANGE: Real fault: impedance jumps from load region (high R, low X) to fault region (low R, high X) in < 1–2 ms — INSTANTANEOUS. Power swing: impedance moves gradually along a curved locus at 5–100 Ω/s depending on swing frequency. PSB uses TWO concentric blinder lines (outer and inner). If the impedance takes > 50 ms to traverse from outer to inner blinder → SWING classified → zones blocked. If traversal < 50 ms → FAULT classified → tripping allowed.</div>

<div class='q'>Q: Where is the electrical centre of a power swing for a transformer?</div>
<div class='a'>The electrical centre (point of 180° phase angle between two systems) lies on the impedance locus where the voltage is theoretically zero. For a transformer connecting two buses, it lies at Z = Z_source_HV / (Z_source_HV + Z_tx + Z_source_LV) × (Z_tx + Z_source_LV). If Z_source_HV ≈ Z_source_LV, the centre is approximately at Z_tx/2 — inside the transformer impedance. This is why Zone-2 and Zone-3 of the transformer relay are the most vulnerable to swing encroachment.</div>

<div class='q'>Q: What is the significance of swing frequency (1.5 Hz default)?</div>
<div class='a'>Swing frequency (slip frequency) is the oscillation rate of the power angle, typically 0.3–2 Hz for inter-area modes. At 1.5 Hz: one cycle = 667 ms, half-cycle = 333 ms. The PSB timer of 50 ms is much less than 333 ms — ensuring the relay can distinguish a genuine fault (< 5 ms impedance change) from a swing (≥ 50 ms) with good margin. Higher swing frequency → impedance moves faster → if frequency exceeds ~6 Hz, PSB may mis-classify swings as faults.</div>

<div class='q'>Q: What is δ_in and δ_out?</div>
<div class='a'>δ_in (entry angle) is the power angle at which the impedance locus enters the INNER PSB blinder. It is calculated from the geometry of the source impedances and blinder settings. δ_out (exit angle) is the expected power angle when the locus exits the OUTER blinder — accounting for one half-cycle of the swing (tP1 × f_sw × 360°). If δ_out is positive and less than 180°, the system may recover (stable swing). If δ_out exceeds 180°, the swing is unstable (pole slip) and OST (Out-of-Step Tripping) should activate.</div>
"""), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# COMPLETE SETTINGS SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(sec("COMPLETE SETTINGS SUMMARY — EHV TRANSFORMER BACKUP IMPEDANCE", "sum"),
            unsafe_allow_html=True)

st.markdown(f"""
<table class="zone-table">
<tr>
  <th>Parameter</th><th>Primary (Ω)</th><th>Secondary (Ω)</th>
  <th>Timer / Value</th><th>Standard / Clause</th><th>Notes</th>
</tr>
<tr>
  <td><b>Z_base HV</b></td>
  <td>{c['Zbase_HV']:.4f}</td><td>—</td><td>—</td>
  <td>—</td><td>V_HV² / MVA</td>
</tr>
<tr>
  <td><b>Z_transformer</b></td>
  <td>{c['Ztx']:.4f}</td><td>—</td>
  <td>∠{c['Z1_ang']:.2f}° / MTA</td>
  <td>—</td><td>{pct_z}% × Z_base — leakage impedance</td>
</tr>
<tr>
  <td><b>Zone 1</b></td>
  <td>{c['Z1r_pri']:.4f}</td><td><b>{c['Z1r_sec']:.5f}</b></td>
  <td>{c['tZ1']:.1f} s</td>
  <td>IEC 60255-121 §6.3.2</td><td>80% Z_tx — Instantaneous, Forward</td>
</tr>
<tr>
  <td><b>Zone 2</b></td>
  <td>{c['Z2r_pri']:.4f}</td><td><b>{c['Z2r_sec']:.5f}</b></td>
  <td>{c['tZ2']:.2f} s</td>
  <td>CEA §4.2.3</td><td>120% Z_tx — Forward</td>
</tr>
<tr>
  <td><b>Zone 3</b></td>
  <td>{c['Z3r_pri']:.4f}</td><td><b>{c['Z3r_sec']:.5f}</b></td>
  <td>{c['tZ3']:.2f} s</td>
  <td>CEA §4.2.4 / IEC §6.3</td><td>MAX(A/B/floor) — Governing: " + c['Z3_governing'] + " — Forward</td>
</tr>
<tr>
  <td><b>Zone 4 (Reverse)</b></td>
  <td>{c['Z4r_pri']:.4f}</td><td><b>{c['Z4r_sec']:.5f}</b></td>
  <td>{c['tZ4']:.2f} s</td>
  <td>CEA §4.3</td><td>20% Z_tx — Reverse (busbar backup)</td>
</tr>
<tr>
  <td><b>MTA (Char. Angle)</b></td>
  <td colspan="2">{c['Z1_ang']:.3f}°</td>
  <td>—</td><td>IEC 60255-121 §5.2</td>
  <td>arctan(X/R = {xr}) — aligned to Z_tx angle</td>
</tr>
<tr>
  <td><b>CTR</b></td>
  <td colspan="2">{c['CTR']:.0f} : 1</td><td>—</td><td>IEC 61869-2</td><td>{ct_pri}/{ct_sec} A</td>
</tr>
<tr>
  <td><b>PTR (HV referred)</b></td>
  <td colspan="2">{c['PTR']:.2f} : 1</td><td>—</td><td>IEC 61869-3</td>
  <td>VT on LV side, referred to {vhv:.0f} kV</td>
</tr>
<tr>
  <td><b>kk = CTR/PTR</b></td>
  <td colspan="2">{c['kk']:.6f}</td><td>—</td><td>—</td>
  <td>Primary Ω → relay secondary Ω factor</td>
</tr>
<tr>
  <td><b>IN>1 SEF Pickup</b></td>
  <td>{c['Is_pri']:.3f} A</td><td>{c['Is_sec']:.5f} A</td>
  <td>—</td><td>CEA §6.2</td><td>20% FLC — Standby E/F pickup</td>
</tr>
<tr>
  <td><b>SEF TMS</b></td>
  <td colspan="2">{c['TMS']:.6f}</td>
  <td>IEC NI curve</td><td>IEC 60255-151</td><td>Normal Inverse, t_op = {c['t_op']:.2f}s</td>
</tr>
<tr>
  <td><b>Load Blinder (sec)</b></td>
  <td>{c['Rload_pri']:.4f}</td><td>{c['Z_blinder_sec']:.5f}</td>
  <td>30° angle</td><td>—</td>
  <td>{'⚠ Z3/Blinder=' + f"{c['Z3_vs_load']:.3f}" + ' > 0.8 — ENABLE BLINDER' if c['load_encroach_risk'] else '✓ Z3/Blinder=' + f"{c['Z3_vs_load']:.3f}" + ' ≤ 0.8 — Safe'}</td>
</tr>
<tr>
  <td><b>PSB Inner (RLdInFw)</b></td>
  <td>—</td><td>{c['RLdInFw']:.5f}</td>
  <td>50 ms</td><td>CEA §7 / IEC §9</td><td>Inner blinder</td>
</tr>
<tr>
  <td><b>PSB Outer (RLdOutFw)</b></td>
  <td>—</td><td>{c['RLdOutFw']:.5f}</td>
  <td>50 ms</td><td>CEA §7</td><td>ΔR = {c['Delta_R']:.5f} Ω</td>
</tr>
</table>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div style="margin-top:24px;padding:12px 16px;background:#f0f8fc;
     border:1px solid #7ab8d4;border-radius:6px;
     font-family:IBM Plex Mono;font-size:11px;color:#4a7fa0;line-height:1.9;">
🔰 EHV Transformer Backup Impedance Protection | {sub_name} — {tx_name} |
{vhv:.0f}/{vlv:.0f} kV | {mva:.0f} MVA | %Z = {pct_z:.1f}% | X/R = {xr:.0f} | VG = {vg}<br>
CTR={ct_pri}/{ct_sec} · PTR={c['PTR']:.0f} · kk={c['kk']:.5f} |
Z_tx = {c['Ztx']:.4f} Ω primary · FLC = {c['FLC']:.1f} A |
Relay on HV side ({vhv:.0f} kV) — Forward directional Mho |
IEC 60255-121:2014 · CEA Protection Guidelines 2010
</div>
""", unsafe_allow_html=True)
