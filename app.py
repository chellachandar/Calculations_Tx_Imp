import streamlit as st
import math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from calculations_hiref import calculate_hiref, interpolate_imag

st.set_page_config(
    page_title="High Impedance REF Calculator",
    page_icon="⚡", layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif;}
.stApp{background:#e8f4fa;color:#03223a;}
section[data-testid="stSidebar"]{background:#daeef8!important;border-right:2px solid #7ab8d4;}
section[data-testid="stSidebar"] *{color:#0a2a42!important;}
section[data-testid="stSidebar"] input,section[data-testid="stSidebar"] select{
  background:#ffffff!important;border:1px solid #7ab8d4!important;
  color:#03223a!important;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:13px;}
.main-title{font-family:'IBM Plex Mono',monospace;font-size:24px;font-weight:700;color:#03223a;margin-bottom:2px;}
.sub-title{font-family:'IBM Plex Mono',monospace;font-size:11px;color:#1a5570;margin-bottom:20px;letter-spacing:1px;}
.sec-hdr{background:#004d88;color:#ffffff;font-family:'IBM Plex Mono',monospace;
  font-size:13px;font-weight:600;padding:10px 16px;border-radius:4px;margin:20px 0 12px 0;letter-spacing:.5px;}
.sec-hdr.green{background:#005a2a;}.sec-hdr.orange{background:#7a3a00;}
.sec-hdr.purple{background:#4a1f8a;}.sec-hdr.teal{background:#00555a;}
.sec-hdr.red{background:#8b0000;}
.rcard{background:#ffffff;border:1px solid #7ab8d4;border-radius:8px;padding:12px 14px;position:relative;overflow:hidden;}
.rcard::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:#004d88;}
.rcard.green::before{background:#005a2a;}.rcard.orange::before{background:#7a3a00;}
.rcard.red::before{background:#8b0000;}.rcard.purple::before{background:#4a1f8a;}
.rcard.teal::before{background:#00555a;}.rcard.warn::before{background:#b85000;}
.rcard-label{font-family:'IBM Plex Mono',monospace;font-size:10px;color:#1a5570;text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px;}
.rcard-value{font-family:'IBM Plex Mono',monospace;font-size:22px;font-weight:700;color:#03223a;}
.rcard-unit{font-family:'IBM Plex Mono',monospace;font-size:11px;color:#4a7a9b;}
.rcard-sub{font-family:'IBM Plex Mono',monospace;font-size:11px;color:#004d88;margin-top:2px;}
.rcgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(185px,1fr));gap:10px;margin:10px 0;}
.fbox{background:#f0f8fc;border:1px solid #7ab8d4;border-radius:6px;padding:14px 18px;margin:8px 0;
  font-family:'IBM Plex Mono',monospace;font-size:13px;}
.fbox .step{color:#1a5570;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;margin-top:8px;}
.fbox .step:first-child{margin-top:0;}
.fbox .eq{color:#0a2a42;font-size:13px;margin:2px 0;}
.fbox .res{color:#004d88;font-size:15px;font-weight:700;margin-top:6px;padding-top:6px;border-top:1px solid #7ab8d4;}
.fbox .warn{color:#8b0000;font-size:12px;margin-top:4px;font-weight:600;}
.fbox .note{color:#4a7a9b;font-size:11px;margin-top:4px;font-style:italic;}
.settable{width:100%;border-collapse:collapse;font-family:'IBM Plex Mono',monospace;font-size:12px;margin:12px 0;}
.settable th{background:#daeef8;color:#003366;padding:8px 12px;text-align:left;font-size:10px;
  letter-spacing:1px;text-transform:uppercase;border:1px solid #7ab8d4;}
.settable td{padding:8px 12px;border:1px solid #b8d8ea;color:#0a2a42;}
.settable tr:nth-child(even) td{background:#f0f8fc;}
.settable tr:hover td{background:#daeef8;}
.tv{color:#005a2a!important;font-weight:700;}.tw{color:#7a3a00!important;font-weight:700;}
.tr{color:#8b0000!important;font-weight:700;}
.badge{display:inline-block;padding:3px 10px;border-radius:3px;font-family:'IBM Plex Mono',monospace;
  font-size:10px;font-weight:700;text-transform:uppercase;}
.b-green{background:#e8f5ee;color:#005a2a;border:1px solid #7ab8a4;}
.b-red{background:#fde8e8;color:#8b0000;border:1px solid #e8a8a8;}
.b-orange{background:#fef0e0;color:#7a3a00;border:1px solid #e8c080;}
.b-blue{background:#daeef8;color:#003366;border:1px solid #7ab8d4;}
.alert-ok{background:#e8f5ee;border:1px solid #7ab8a4;border-radius:6px;padding:10px 14px;
  font-family:'IBM Plex Mono',monospace;font-size:12px;color:#005a2a;margin:8px 0;}
.alert-warn{background:#fff3e0;border:1px solid #e8c080;border-radius:6px;padding:10px 14px;
  font-family:'IBM Plex Mono',monospace;font-size:12px;color:#7a3a00;margin:8px 0;}
.alert-err{background:#fde8e8;border:1px solid #e8a8a8;border-radius:6px;padding:10px 14px;
  font-family:'IBM Plex Mono',monospace;font-size:12px;color:#8b0000;margin:8px 0;}
.ct-panel{background:#ffffff;border:1px solid #7ab8d4;border-radius:8px;padding:16px;margin-bottom:12px;}
.ct-panel h4{font-family:'IBM Plex Mono',monospace;font-size:11px;color:#004d88;
  text-transform:uppercase;letter-spacing:1px;margin:0 0 12px 0;padding-bottom:8px;border-bottom:1px solid #c8e4f2;}
</style>
""", unsafe_allow_html=True)

CONFIG_NAMES = {
    1: "3-Wire Balanced EF (3 Line CTs)",
    2: "3-Wire + Earth REF (3 LCT + 1 ECT)",
    3: "4-Wire REF (3 LCT + 1 Neutral CT)",
    4: "4-Wire + Earth REF (3 LCT + 1 NCT + 1 ECT)"
}

def rcard(label, value, unit="", sub="", kind=""):
    return f"""<div class="rcard {kind}">
<div class="rcard-label">{label}</div>
<div class="rcard-value">{value}</div>
<div class="rcard-unit">{unit}</div>
{"<div class='rcard-sub'>"+sub+"</div>" if sub else ""}
</div>"""

def sec(title, kind=""):
    return f'<div class="sec-hdr {kind}">⚡ {title}</div>'

def fbox(steps):
    h = ""
    for s in steps:
        if s[0]=="step": h+=f'<div class="step">{s[1]}</div>'
        elif s[0]=="eq":  h+=f'<div class="eq">{s[1]}</div>'
        elif s[0]=="res": h+=f'<div class="res">▶ {s[1]}</div>'
        elif s[0]=="warn":h+=f'<div class="warn">⚠ {s[1]}</div>'
        elif s[0]=="note":h+=f'<div class="note">ℹ {s[1]}</div>'
    return f'<div class="fbox">{h}</div>'

def ct_inputs(label, key, defaults):
    st.markdown(f'<div class="ct-panel"><h4>🔌 {label}</h4>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        T   = st.number_input(f"CT Ratio (1/T) [{key}]", 10, 5000, defaults["T"], 50,
                              help="Enter secondary turns e.g. 600 for 1/600")
        Vk  = st.number_input(f"Vk (V) [{key}]", 10.0, 2000.0, float(defaults["Vk"]), 10.0)
        Imag= st.number_input(f"Imag @ Vk (mA) [{key}]", 1.0, 500.0, float(defaults["Imag"]), 1.0)
    with c2:
        RCT = st.number_input(f"RCT (Ω) [{key}]", 0.1, 50.0, float(defaults["RCT"]), 0.1, format="%.2f")
        RL  = st.number_input(f"RL loop (Ω) [{key}]", 0.01, 10.0, float(defaults["RL"]), 0.01, format="%.3f")
        method = st.selectbox(f"Imag method [{key}]", ["Interpolate from curve","Enter directly"],
                              help="Interpolate: use calibrated CT magnetising curve | Enter: type Imag@Vs directly")
    Imag_vs = None
    if "Enter" in method:
        Imag_vs = st.number_input(f"Imag @ Vs (mA) [{key}]", 0.1, 200.0, float(defaults["Imag"])*0.25, 0.1, format="%.2f")
    st.markdown('</div>', unsafe_allow_html=True)
    return dict(T=T, Vk=Vk, Imag=Imag, RCT=RCT, RL=RL,
                method="interpolate" if "Interp" in method else "enter",
                Imag_vs=Imag_vs)

# ── SIDEBAR ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:IBM Plex Mono;font-size:15px;color:#004d88;font-weight:700;margin-bottom:2px;">⚡ Hi-Z REF</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono;font-size:10px;color:#1a5570;margin-bottom:16px;letter-spacing:1px;">HIGH IMPEDANCE REF CALCULATOR</div>', unsafe_allow_html=True)

    st.markdown("**🏭 Identification**")
    equip_name = st.text_input("Equipment Name", "TX1 — 33/11kV, 10MVA")
    config_sel = st.selectbox("Scheme Configuration",
        list(CONFIG_NAMES.values()), index=0)
    config = [k for k,v in CONFIG_NAMES.items() if v == config_sel][0]

    st.markdown("---")
    st.markdown("**⚡ System Parameters**")
    mva     = st.number_input("Transformer MVA", 0.5, 1000.0, 10.0, 0.5)
    vkv     = st.number_input("Protected Winding Voltage (kV)", 0.4, 765.0, 11.0, 0.5, format="%.1f")
    if_mult = st.number_input("Through Fault Multiplier (×Irated)", 1, 25, 16,
                              help="Typically 16 × Irated per IEC. Or use 1/Zpu × Irated.")
    poc_pct = st.slider("POC — % of Irated", 10.0, 25.0, 10.0, 0.5,
                        help="Primary Operate Current: typically 10–25% of protected winding rated current")

    st.markdown("---")
    st.markdown("**🔧 Relay Setting**")
    relay_is = st.number_input("Relay Is (A)", 0.005, 2.0, 0.05, 0.005, format="%.4f",
                               help="Relay pickup current. Set 0 to auto-calculate from POC.")

    st.markdown("---")
    st.markdown("**📐 Metrosil β**")
    beta = st.number_input("β (Metrosil constant)", 0.20, 0.30, 0.25, 0.01, format="%.2f",
                           help="IEC default: 0.22 to 0.25")

    st.markdown("---")
    calc_btn = st.button("⚡ CALCULATE REF SETTINGS", use_container_width=True, type="primary")

# ── MAIN ────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">⚡ High Impedance REF Protection Calculator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Generic · IEC 60044 Class PX CT · Stability Voltage · Rstab · Metrosil · Primary Operate Current</div>', unsafe_allow_html=True)

# CT INPUTS (shown always, adapt to config)
st.markdown(sec("CT DETAILS — Input Parameters"), unsafe_allow_html=True)

lct_d = dict(T=600, Vk=360, Imag=30, RCT=7.5, RL=0.15)
nct_d = dict(T=600, Vk=450, Imag=20, RCT=4.5, RL=0.50)
ect_d = dict(T=600, Vk=300, Imag=40, RCT=6.0, RL=0.20)

if config == 1:
    col1, col2 = st.columns([1,1])
    with col1: lct = ct_inputs("Line CT (LCT) — 3 phases", "LCT", lct_d)
    with col2:
        st.markdown('<div style="background:#f0f8fc;border:1px solid #7ab8d4;border-radius:8px;padding:20px;margin-top:4px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:IBM Plex Mono;font-size:11px;color:#1a5570;text-transform:uppercase;letter-spacing:1px;">Scheme Diagram</div>', unsafe_allow_html=True)
        st.markdown("""
        <svg viewBox="0 0 300 200" width="100%" xmlns="http://www.w3.org/2000/svg">
          <text x="10" y="20" fill="#004d88" font-family="IBM Plex Mono" font-size="11" font-weight="bold">3-Wire Balanced EF</text>
          <!-- Bus -->
          <line x1="20" y1="40" x2="280" y2="40" stroke="#03223a" stroke-width="2"/>
          <!-- 3 Line CTs -->
          <rect x="50" y="50" width="20" height="30" rx="2" fill="none" stroke="#004d88" stroke-width="1.5"/>
          <rect x="130" y="50" width="20" height="30" rx="2" fill="none" stroke="#004d88" stroke-width="1.5"/>
          <rect x="210" y="50" width="20" height="30" rx="2" fill="none" stroke="#004d88" stroke-width="1.5"/>
          <text x="50" y="47" fill="#004d88" font-family="IBM Plex Mono" font-size="9">A</text>
          <text x="130" y="47" fill="#004d88" font-family="IBM Plex Mono" font-size="9">B</text>
          <text x="210" y="47" fill="#004d88" font-family="IBM Plex Mono" font-size="9">C</text>
          <!-- CT secondaries to relay -->
          <line x1="60" y1="80" x2="60" y2="130" stroke="#7ab8d4" stroke-width="1"/>
          <line x1="140" y1="80" x2="140" y2="130" stroke="#7ab8d4" stroke-width="1"/>
          <line x1="220" y1="80" x2="220" y2="130" stroke="#7ab8d4" stroke-width="1"/>
          <line x1="60" y1="130" x2="220" y2="130" stroke="#7ab8d4" stroke-width="1"/>
          <line x1="140" y1="130" x2="140" y2="150" stroke="#7ab8d4" stroke-width="1.5"/>
          <!-- Relay box -->
          <rect x="100" y="150" width="90" height="35" rx="4" fill="#daeef8" stroke="#004d88" stroke-width="1.5"/>
          <text x="107" y="163" fill="#004d88" font-family="IBM Plex Mono" font-size="9" font-weight="bold">Hi-Z REF</text>
          <text x="108" y="177" fill="#1a5570" font-family="IBM Plex Mono" font-size="8">Relay + Rstab</text>
          <!-- Transformer windings -->
          <text x="75" y="110" fill="#4a7a9b" font-family="IBM Plex Mono" font-size="8">LCT</text>
          <text x="155" y="110" fill="#4a7a9b" font-family="IBM Plex Mono" font-size="8">LCT</text>
        </svg>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    nct, ect = None, None

elif config == 2:
    c1, c2 = st.columns(2)
    with c1: lct = ct_inputs("Line CT (LCT) — 3 phases", "LCT", lct_d)
    with c2: ect = ct_inputs("Earth CT (ECT) — NER/Earth", "ECT", ect_d)
    nct = None

elif config == 3:
    c1, c2 = st.columns(2)
    with c1: lct = ct_inputs("Line CT (LCT) — 3 phases", "LCT", lct_d)
    with c2: nct = ct_inputs("Neutral CT (NCT) — Transformer neutral", "NCT", nct_d)
    ect = None

else:  # config 4
    c1, c2 = st.columns(2)
    with c1: lct = ct_inputs("Line CT (LCT) — 3 phases", "LCT", lct_d)
    with c2: nct = ct_inputs("Neutral CT (NCT)", "NCT", nct_d)
    c3, c4 = st.columns(2)
    with c3: ect = ct_inputs("Earth CT (ECT) — NER/Earth", "ECT", ect_d)
    with c4:
        st.markdown(f"""<div style="background:#f0f8fc;border:1px solid #7ab8d4;border-radius:8px;
        padding:16px;margin-top:4px;font-family:IBM Plex Mono;font-size:11px;color:#1a5570;">
        <div style="font-weight:700;color:#004d88;margin-bottom:8px;">CONFIG 4 — 4 Wire 5CT</div>
        3 × Line CT (LCT) in differential<br>
        1 × Neutral CT (NCT) at transformer star point<br>
        1 × Earth CT (ECT) at NER<br><br>
        <div style="color:#0a2a42;">POC = (3×Imag_LCT + Imag_NCT + Imag_ECT + Is) / T</div>
        </div>""", unsafe_allow_html=True)

if not calc_btn:
    st.markdown("""
    <div style="background:#ffffff;border:1px solid #7ab8d4;border-radius:8px;
         padding:28px;margin-top:20px;text-align:center;">
        <div style="font-family:IBM Plex Mono;font-size:14px;color:#1a5570;margin-bottom:10px;">
            Fill CT parameters above and click CALCULATE REF SETTINGS
        </div>
        <div style="font-family:IBM Plex Mono;font-size:11px;color:#4a7a9b;">
            IEC 60044 Class PX · Stability Voltage · Rstab · Metrosil · POC
        </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── BUILD INPUT DICT ─────────────────────────────────────────────────
inp = dict(
    config=config, mva=mva, voltage_kv=vkv, if_multiplier=if_mult,
    poc_pct=poc_pct, relay_is=relay_is, beta=beta,
    T_lct=lct["T"], Vk_lct=lct["Vk"], Imag_Vk_lct=lct["Imag"],
    RCT_lct=lct["RCT"], RL_lct=lct["RL"],
    imag_method_lct=lct["method"], Imag_Vs_lct=lct["Imag_vs"] or 0,
)
if nct:
    inp.update(T_nct=nct["T"], Vk_nct=nct["Vk"], Imag_Vk_nct=nct["Imag"],
               RCT_nct=nct["RCT"], RL_nct=nct["RL"],
               imag_method_nct=nct["method"], Imag_Vs_nct=nct["Imag_vs"] or 0)
if ect:
    inp.update(T_ect=ect["T"], Vk_ect=ect["Vk"], Imag_Vk_ect=ect["Imag"],
               RCT_ect=ect["RCT"], RL_ect=ect["RL"],
               imag_method_ect=ect["method"], Imag_Vs_ect=ect["Imag_vs"] or 0)

c = calculate_hiref(inp)

# ── HEADER BAR ──────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:#ffffff;border:1px solid #7ab8d4;border-radius:8px;
     padding:14px 20px;display:flex;gap:28px;flex-wrap:wrap;margin:16px 0;">
  <div><span style="font-size:10px;color:#4a7a9b;font-family:IBM Plex Mono">EQUIPMENT</span><br>
       <span style="font-size:14px;color:#03223a;font-family:IBM Plex Mono;font-weight:700">{equip_name}</span></div>
  <div><span style="font-size:10px;color:#4a7a9b;font-family:IBM Plex Mono">CONFIGURATION</span><br>
       <span style="font-size:14px;color:#004d88;font-family:IBM Plex Mono;font-weight:700">{CONFIG_NAMES[config]}</span></div>
  <div><span style="font-size:10px;color:#4a7a9b;font-family:IBM Plex Mono">MVA / kV</span><br>
       <span style="font-size:14px;color:#03223a;font-family:IBM Plex Mono;font-weight:700">{mva} MVA / {vkv} kV</span></div>
  <div><span style="font-size:10px;color:#4a7a9b;font-family:IBM Plex Mono">I_RATED</span><br>
       <span style="font-size:14px;color:#005a2a;font-family:IBM Plex Mono;font-weight:700">{c['I_rated']:.1f} A</span></div>
  <div><span style="font-size:10px;color:#4a7a9b;font-family:IBM Plex Mono">IF ({if_mult}×)</span><br>
       <span style="font-size:14px;color:#8b0000;font-family:IBM Plex Mono;font-weight:700">{c['IF']:.0f} A</span></div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SECTION 1 — SYSTEM PARAMETERS
# ═══════════════════════════════════════════════════════
st.markdown(sec("SECTION 1 — SYSTEM PARAMETERS"), unsafe_allow_html=True)
st.markdown('<div class="rcgrid">' +
    rcard("I_rated", f"{c['I_rated']:.2f}", "A", f"MVA/(√3×{vkv}kV)") +
    rcard("IF (Through Fault)", f"{c['IF']:.1f}", "A", f"{if_mult} × I_rated", "red") +
    rcard("POC (Required)", f"{c['POC']:.2f}", "A", f"{poc_pct:.1f}% × I_rated", "green") +
    rcard("POC Range", f"{c['POC_min']:.1f}–{c['POC_max']:.1f}", "A", "10–25% of I_rated", "teal") +
    rcard("POC (secondary)", f"{c['POC_sec']:.5f}", "A sec", f"POC / T = {c['POC']:.2f}/{lct['T']}") +
'</div>', unsafe_allow_html=True)

with st.expander("📐 Step-by-step — System Parameters"):
    st.markdown(fbox([
        ("step", "Step 1: Rated Current of Protected Winding"),
        ("eq",   f"I_rated = MVA / (√3 × VL) = {mva}×10⁶ / (√3 × {vkv}×10³)"),
        ("res",  f"I_rated = {c['I_rated']:.2f} A"),
        ("step", "Step 2: Assigned Through Fault Current (Rated Stability Limit)"),
        ("eq",   f"IF = {if_mult} × I_rated = {if_mult} × {c['I_rated']:.2f}"),
        ("res",  f"IF = {c['IF']:.1f} A  [IEC: typically 16 × Irated or 1/Zpu × Irated]"),
        ("step", "Step 3: Primary Operate Current (Fault Setting)"),
        ("eq",   f"POC = {poc_pct:.1f}% × {c['I_rated']:.2f} = {c['POC']:.2f} A"),
        ("eq",   f"Acceptable range: 10–25% of Irated = {c['POC_min']:.1f} – {c['POC_max']:.1f} A"),
        ("note", "POC is the minimum primary earth fault current the scheme must operate for."),
    ]), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SECTION 2 — STABILITY VOLTAGE
# ═══════════════════════════════════════════════════════
st.markdown(sec("SECTION 2 — STABILITY VOLTAGE LIMITS", "orange"), unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    vs_status = "green" if c["Vs_ok"] else "warn"
    st.markdown('<div class="rcgrid">' +
        rcard("Vs_min (LCT)", f"{c['Vs_lct_req']:.2f}", "V", f"IF/T × (RCT+RL) = {c['IF']:.0f}/{lct['T']}×({lct['RCT']}+{lct['RL']})") +
        (rcard("Vs_min (NCT)", f"{c['Vs_nct_req']:.2f}", "V", "IF/T × (RCT+RL) NCT") if config in [3,4] else "") +
        (rcard("Vs_min (ECT)", f"{c['Vs_ect_req']:.2f}", "V", "IF/T × (RCT+RL) ECT") if config in [2,4] else "") +
        rcard("Vs_min REQUIRED", f"{c['Vs_min']:.2f}", "V", "Max of all CT requirements", "red") +
    '</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="rcgrid">' +
        rcard("Vk_min", f"{c['Vk_min']:.0f}", "V", "Minimum knee point voltage") +
        rcard("Vs_max ALLOWED", f"{c['Vs_max']:.1f}", "V", "Vk_min / 2", "orange") +
        rcard("Vs_provisional", f"{c['Vs_prov']:.1f}", "V",
              "✓ In range" if c["Vs_ok"] else "⚠ Check!", vs_status) +
    '</div>', unsafe_allow_html=True)

vs_check_html = f'<div class="alert-ok">✓ Vs range valid: {c["Vs_min"]:.2f} V  &lt;  Vs_prov = {c["Vs_prov"]:.1f} V  ≤  Vs_max = {c["Vs_max"]:.1f} V</div>' \
    if c["Vs_ok"] else \
    f'<div class="alert-err">⚠ Vs_prov = {c["Vs_prov"]:.1f} V outside range! Required: {c["Vs_min"]:.2f} V to {c["Vs_max"]:.1f} V. Review CT parameters.</div>'
st.markdown(vs_check_html, unsafe_allow_html=True)

with st.expander("📐 Step-by-step — Stability Voltage"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(fbox([
            ("step", "Minimum Vs — Equation (1) per IEC/Siemens doc"),
            ("eq",   "Vs ≥ IF × (RCT + RL) / T"),
            ("eq",   f"[LCT] Vs ≥ {c['IF']:.1f} × ({lct['RCT']} + {lct['RL']}) / {lct['T']}"),
            ("res",  f"Vs_LCT_min = {c['Vs_lct_req']:.3f} V"),
            ("eq",   f"Worst case Vs_min = {c['Vs_min']:.3f} V"),
            ("note", "Assumes one CT fully saturated — worst case gives highest false differential voltage across relay"),
        ]), unsafe_allow_html=True)
    with col2:
        st.markdown(fbox([
            ("step", "Maximum Vs — Equation (2) per IEC/Siemens doc"),
            ("eq",   "Vs ≤ Vk / 2  (ensures high speed relay operation)"),
            ("eq",   f"Vs ≤ {c['Vk_min']:.0f} / 2 = {c['Vs_max']:.1f} V"),
            ("res",  f"Valid range: {c['Vs_min']:.2f} V  <  Vs  ≤  {c['Vs_max']:.1f} V"),
            ("res",  f"Selected Vs_prov = {c['Vs_prov']:.1f} V"),
            ("note", "Vs must not exceed Vk/2 to ensure relay operates quickly at the set voltage"),
        ]), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SECTION 3 — MAGNETISING CURRENT @ Vs
# ═══════════════════════════════════════════════════════
st.markdown(sec("SECTION 3 — MAGNETISING CURRENT @ Vs", "teal"), unsafe_allow_html=True)

imag_rows = [
    ("LCT (×3)", f"{c['Imag_lct']*1000:.2f}", f"3 × {c['Imag_lct']*1000:.2f} = {3*c['Imag_lct']*1000:.2f} mA", "interpolate" if lct["method"]=="interpolate" else "entered"),
]
if config in [3,4] and nct:
    imag_rows.append(("NCT (×1)", f"{c['Imag_nct']*1000:.2f}", f"{c['Imag_nct']*1000:.2f} mA", "interpolate" if nct["method"]=="interpolate" else "entered"))
if config in [2,4] and ect:
    imag_rows.append(("ECT (×1)", f"{c['Imag_ect']*1000:.2f}", f"{c['Imag_ect']*1000:.2f} mA", "interpolate" if ect["method"]=="interpolate" else "entered"))

table_rows = "".join([f"<tr><td>{r[0]}</td><td class='tv'>{r[1]} mA</td><td>{r[2]}</td><td><span class='badge b-blue'>{r[3]}</span></td></tr>" for r in imag_rows])
st.markdown(f"""
<table class="settable">
<tr><th>CT Type</th><th>Imag @ Vs={c['Vs_prov']:.0f}V</th><th>Contribution to ΣImag</th><th>Method</th></tr>
{table_rows}
<tr style="background:#daeef8"><td><strong>TOTAL ΣImag</strong></td>
<td class="tr"><strong>{c['sum_Imag']*1000:.3f} mA</strong></td>
<td colspan="2">Used in POC calculation</td></tr>
</table>
""", unsafe_allow_html=True)

with st.expander("📐 Imag Interpolation — Calibrated CT Magnetising Curve"):
    st.markdown(fbox([
        ("step", "Calibrated piecewise-linear magnetising curve (IEC 60044 Class PX)"),
        ("eq",   "Factor table: ratio=Vs/Vk → Imag_factor (fraction of Imag@Vk)"),
        ("eq",   "0.0→0%, 0.1→4%, 0.2→10%, 0.3→17%, 0.4→25%, 0.5→38%"),
        ("eq",   "0.6→52%, 0.7→66%, 0.8→80%, 0.9→91%, 1.0→100%"),
        ("eq",   f"[LCT] ratio = {c['Vs_prov']:.1f}/{lct['Vk']:.0f} = {c['Vs_prov']/lct['Vk']:.4f}"),
        ("res",  f"Imag_LCT @ Vs = {c['Imag_lct']*1000:.3f} mA"),
        ("note", "Class PX CT: Vk is the kneepoint where 10% increase in voltage gives 50% increase in excitation current. Curve is non-linear — steeply rising near Vk."),
    ]), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SECTION 4 — RELAY SETTING & RSTAB
# ═══════════════════════════════════════════════════════
st.markdown(sec("SECTION 4 — RELAY SETTING CURRENT & STABILISING RESISTOR", "green"), unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="rcgrid">' +
        rcard("Is (ideal calc)", f"{c['Is_ideal']*1000:.2f}", "mA",
              f"POC_sec − ΣImag = {c['POC_sec']*1000:.2f}−{c['sum_Imag']*1000:.2f}") +
        rcard("Is (applied)", f"{c['Is']*1000:.2f}", "mA",
              "Relay setting current", "green") +
        rcard("Rstab (calculated)", f"{c['Rstab_raw']:.1f}", "Ω",
              f"Vs / Is = {c['Vs_prov']:.1f}/{c['Is']:.5f}") +
        rcard("Rstab (standard)", f"{c['Rstab_std']}", "Ω",
              "Rounded to nearest 50Ω", "green") +
    '</div>', unsafe_allow_html=True)

with col2:
    final_ok = c["Vs_final_ok"]
    st.markdown('<div class="rcgrid">' +
        rcard("Vs (actual)", f"{c['Vs_actual']:.2f}", "V",
              f"Rstab_std × Is = {c['Rstab_std']}×{c['Is']:.5f}",
              "green" if final_ok else "warn") +
        rcard("POC (actual)", f"{c['POC_actual']:.2f}", "A",
              c["poc_formula"], "green") +
        rcard("Vk required", f"{c['Vk_required']:.1f}", "V",
              "2 × Vs_actual", "teal") +
        rcard("Vk_LCT check", f"{'✓ PASS' if c['Vk_check'] else '⚠ FAIL'}",
              f"Vk={lct['Vk']}V, need≥{c['Vk_required']:.0f}V",
              "", "green" if c["Vk_check"] else "red") +
    '</div>', unsafe_allow_html=True)

vs_act_alert = f'<div class="alert-ok">✓ Final Vs = {c["Vs_actual"]:.2f} V — within stability range [{c["Vs_min"]:.2f}V, {c["Vs_max"]:.1f}V]</div>' \
    if final_ok else \
    f'<div class="alert-warn">⚠ Vs_actual = {c["Vs_actual"]:.2f} V may be outside range. Consider adjusting Is or selecting next standard Rstab.</div>'
st.markdown(vs_act_alert, unsafe_allow_html=True)

with st.expander("📐 Step-by-step — Is and Rstab"):
    st.markdown(fbox([
        ("step", "Step 1: Required relay setting current Is"),
        ("eq",   f"POC = {c['poc_formula']}"),
        ("eq",   f"Is = POC × T − ΣImag = {c['POC']:.3f}/{lct['T']}×{lct['T']} − {c['sum_Imag']*1000:.3f}mA"),
        ("eq",   f"Is_ideal = {c['POC_sec']*1000:.3f} mA − {c['sum_Imag']*1000:.3f} mA"),
        ("res",  f"Is_ideal = {c['Is_ideal']*1000:.3f} mA → Applied Is = {c['Is']*1000:.3f} mA"),
        ("step", "Step 2: Stabilising Resistor"),
        ("eq",   f"Rstab = Vs_prov / Is = {c['Vs_prov']:.1f} / {c['Is']:.6f}"),
        ("res",  f"Rstab_calc = {c['Rstab_raw']:.2f} Ω → Standard = {c['Rstab_std']} Ω"),
        ("eq",   f"Vs_actual = {c['Rstab_std']} × {c['Is']:.6f} = {c['Vs_actual']:.3f} V"),
        ("note", "Rstab is in SERIES with relay for 7SR type. For 7PG23 type use shunt Rshunt = Vs/Ishunt."),
    ]), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SECTION 5 — METROSIL
# ═══════════════════════════════════════════════════════
st.markdown(sec("SECTION 5 — METROSIL (NON-LINEAR RESISTOR)", "purple"), unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="rcgrid">' +
        rcard("P1SEC Metrosil", f"{c['P1SEC_metro']:.0f}", "W",
              "(4/π) × IF × (1/T) × Vk_min", "purple") +
        rcard("Metrosil Size", c["metro_size"], "",
              f"Rating: {c['metro_rating']}", "purple") +
        rcard("C value", str(c["C_val"]), "",
              "450 if Vs<100V | 1000 if Vs≥100V", "teal") +
    '</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="rcgrid">' +
        rcard("IFint (secondary)", f"{c['IFint_sec']:.2f}", "A",
              f"IF/T = {c['IF']:.1f}/{lct['T']}") +
        rcard("Vpeak (no Metrosil)", f"{c['VPk']:.0f}" if c['VPk']>0 else "N/A", "V",
              "√(2√(2Vk(IFint×Rstab−Vk)))", "warn") +
        rcard("β (Metrosil)", f"{beta:.2f}", "",
              "IEC: 0.22–0.25 typical") +
    '</div>', unsafe_allow_html=True)

metro_alert = f'<div class="alert-ok">✓ P1SEC = {c["P1SEC_metro"]:.0f} W → {c["metro_size"]} Metrosil ({c["metro_rating"]}) is adequate. C={c["C_val"]}.</div>' \
    if c["P1SEC_metro"] < 8000 else \
    f'<div class="alert-warn">⚠ P1SEC = {c["P1SEC_metro"]:.0f} W > 8kW → 150mm Metrosil (33kJ) required.</div>'
st.markdown(metro_alert, unsafe_allow_html=True)

with st.expander("📐 Step-by-step — Metrosil Specification"):
    st.markdown(fbox([
        ("step", "Step 1: Metrosil 1-Second Power Rating — Equation (10)"),
        ("eq",   "P1SEC = (4/π) × IF × (1/T) × Vk_min"),
        ("eq",   f"P1SEC = (4/π) × {c['IF']:.1f} × (1/{lct['T']}) × {c['Vk_min']:.0f}"),
        ("res",  f"P1SEC = {c['P1SEC_metro']:.1f} W"),
        ("eq",   f"< 8000 W → {c['metro_size']} Metrosil ({c['metro_rating']}) sufficient"),
        ("step", "Step 2: C Value Selection"),
        ("eq",   f"Vs_actual = {c['Vs_actual']:.1f} V  {'< 100V → C = 450' if c['C_val']==450 else '≥ 100V → C = 1000'}"),
        ("res",  f"C = {c['C_val']}"),
        ("step", "Step 3: Voltage Check (Metrosil limits peak to < 3kV)"),
        ("eq",   "VPk = √2 × √(2×Vk×(IFint×Rstab − Vk))  [without Metrosil]"),
        ("res",  f"VPk ≈ {c['VPk']:.0f} V  → Metrosil ALWAYS recommended"),
        ("note", "Metrosil characteristic: V = C × I^β. At Vs the Metrosil current is negligible. At internal fault voltages it clamps the peak below 3kV for safety."),
    ]), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SECTION 6 — STABILISING RESISTOR RATINGS
# ═══════════════════════════════════════════════════════
st.markdown(sec("SECTION 6 — STABILISING RESISTOR THERMAL RATINGS", "red"), unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="rcgrid">' +
        rcard("P_cont (continuous)", f"{c['P_cont']:.2f}", "W",
              f"Is² × Rstab = {c['Is']*1000:.2f}mA² × {c['Rstab_std']}Ω", "orange") +
        rcard("Recommended Prating", f"{max(10, math.ceil(c['P_cont']/10)*10):.0f}", "W",
              "Round up to standard rating", "orange") +
    '</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="rcgrid">' +
        rcard("VFint (internal fault V)", f"{c['VFint']:.1f}", "V",
              "(Vk×Rstab×IFint)^0.75 × 1.3", "red") +
        rcard("P1SEC (1-sec rating)", f"{c['P1SEC_res']:.1f}", "W",
              f"VFint² / Rstab = {c['VFint']:.1f}² / {c['Rstab_std']}", "red") +
    '</div>', unsafe_allow_html=True)

with st.expander("📐 Step-by-step — Resistor Ratings"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(fbox([
            ("step", "Continuous Power Rating"),
            ("eq",   "P_cont = Is² × Rstab"),
            ("eq",   f"P_cont = ({c['Is']:.6f})² × {c['Rstab_std']}"),
            ("res",  f"P_cont = {c['P_cont']:.3f} W"),
            ("eq",   f"Select standard rating ≥ {max(10, math.ceil(c['P_cont']/10)*10)} W"),
        ]), unsafe_allow_html=True)
    with col2:
        st.markdown(fbox([
            ("step", "Short Time (1-second) Power Rating — Equation (11)"),
            ("eq",   "VFint = (Vk × Rstab × IFint)^(3/4) × 1.3"),
            ("eq",   f"IFint = IF/T = {c['IF']:.1f}/{lct['T']} = {c['IFint_sec']:.2f} A"),
            ("eq",   f"VFint = ({c['Vk_min']:.0f} × {c['Rstab_std']} × {c['IFint_sec']:.2f})^0.75 × 1.3"),
            ("res",  f"VFint = {c['VFint']:.2f} V"),
            ("eq",   f"P1SEC = VFint² / Rstab = {c['VFint']:.2f}² / {c['Rstab_std']}"),
            ("res",  f"P1SEC = {c['P1SEC_res']:.1f} W"),
        ]), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SECTION 7 — COMPLETE SETTINGS SUMMARY
# ═══════════════════════════════════════════════════════
st.markdown(sec("SECTION 7 — COMPLETE SETTINGS SUMMARY"), unsafe_allow_html=True)

p_cont_rec = max(10, math.ceil(c['P_cont']/10)*10)
p1sec_rec  = math.ceil(c['P1SEC_res']/100)*100

st.markdown(f"""
<table class="settable">
<tr><th>Parameter</th><th>Value</th><th>Unit</th><th>Notes</th></tr>
<tr><td>Scheme Configuration</td><td class="tv">{CONFIG_NAMES[config]}</td><td>—</td><td>IEC 60044 Class PX CTs</td></tr>
<tr><td>CT Ratio (T)</td><td class="tv">1/{lct['T']}</td><td>—</td><td>All CTs must have same ratio</td></tr>
<tr><td>I_rated (protected winding)</td><td class="tv">{c['I_rated']:.2f}</td><td>A</td><td>{mva} MVA / (√3 × {vkv} kV)</td></tr>
<tr><td>IF (through fault)</td><td class="tw">{c['IF']:.1f}</td><td>A</td><td>{if_mult} × I_rated</td></tr>
<tr><td>POC (Primary Operate Current)</td><td class="tv">{c['POC_actual']:.2f}</td><td>A</td><td>{poc_pct:.1f}% of I_rated, fault setting</td></tr>
<tr><td>Vs_min required</td><td class="tw">{c['Vs_min']:.2f}</td><td>V</td><td>From CT stability requirement</td></tr>
<tr><td>Vs_max allowed</td><td class="tv">{c['Vs_max']:.1f}</td><td>V</td><td>Vk_min / 2 = {c['Vk_min']:.0f}/2</td></tr>
<tr><td><strong>Relay Is (setting)</strong></td><td class="tv"><strong>{c['Is']*1000:.2f}</strong></td><td>mA</td><td>REF function pickup</td></tr>
<tr><td><strong>Vs (actual)</strong></td><td class="tv"><strong>{c['Vs_actual']:.2f}</strong></td><td>V</td><td>Rstab × Is = {c['Rstab_std']}×{c['Is']*1000:.2f}mA</td></tr>
<tr><td><strong>Rstab (standard)</strong></td><td class="tv"><strong>{c['Rstab_std']}</strong></td><td>Ω</td><td>Series stabilising resistor</td></tr>
<tr><td>Rstab continuous rating</td><td class="tw">{p_cont_rec}</td><td>W</td><td>P_cont = {c['P_cont']:.2f} W, round up</td></tr>
<tr><td>Rstab 1-sec rating</td><td class="tw">{p1sec_rec}</td><td>W</td><td>P1SEC = {c['P1SEC_res']:.1f} W (failed CB)</td></tr>
<tr><td><strong>Metrosil (NLR)</strong></td><td class="tv"><strong>C={c['C_val']}, {c['metro_size']}</strong></td><td>—</td><td>β=0.22–0.25, {c['metro_rating']} rating</td></tr>
<tr><td>Vk required (LCT)</td><td class="{'tv' if c['Vk_check'] else 'tr'}">{c['Vk_required']:.1f}</td><td>V</td><td>Actual Vk_LCT={lct['Vk']}V → {'✓ PASS' if c['Vk_check'] else '⚠ FAIL'}</td></tr>
<tr><td>REF Delay</td><td class="tv">0</td><td>s</td><td>Instantaneous — no intentional delay</td></tr>
</table>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="margin-top:16px;padding:12px 16px;background:#ffffff;border:1px solid #7ab8d4;
     border-radius:6px;font-family:IBM Plex Mono;font-size:11px;color:#4a7a9b;line-height:1.8;">
⚡ Hi-Z REF Calculator | {equip_name} | {CONFIG_NAMES[config]} | {mva}MVA {vkv}kV |
Is={c['Is']*1000:.2f}mA | Rstab={c['Rstab_std']}Ω | Vs={c['Vs_actual']:.1f}V |
Metrosil C={c['C_val']} {c['metro_size']} | POC={c['POC_actual']:.1f}A |
Ref: Siemens Reyrolle Technical Guidance Notes — IEC 60044
</div>
""", unsafe_allow_html=True)
