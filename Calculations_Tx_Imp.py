"""
calculations.py
===============
EHV Transformer Backup Impedance (Under-Impedance / Mho) Protection
400/230 kV class — HV side relay
IEC 60255-121:2014 & CEA Protection Guidelines 2010

  - Section 1 : Base impedances & CT/VT conversion
  - Section 2 : Zone reaches  (Z1 / Z2 / Z3, forward; Z4 reverse optional)
  - Section 3 : Standby Earth Fault (SEF) / DEF-equivalent
  - Section 4 : Load encroachment / load blinder check
  - Section 5 : Power swing block (PSB)
"""

import math

# ─── TRANSFORMER TYPES ───────────────────────────────────────────────────────
TX_VECTOR_GROUPS = ["YNd1", "YNd11", "YNyn0", "YNyn0d1", "Dyn11", "Dyn1"]

# ─── HELPER ──────────────────────────────────────────────────────────────────
def _safe_tan(deg):
    """Return tan(deg in degrees), guarded against near-90°."""
    rad = math.radians(deg)
    if abs(math.cos(rad)) < 1e-9:
        return 1e9
    return math.tan(rad)


def calculate_tx(inp):
    """
    Master calculation function.

    Parameters (inp dict)
    ---------------------
    vhv_kv          : HV voltage kV
    vlv_kv          : LV voltage kV
    mva             : Transformer MVA rating
    pct_z           : Leakage impedance %
    xr_ratio        : Transformer X/R ratio
    ct_primary      : CT primary current A  (HV side)
    ct_secondary    : CT secondary current A
    pt_primary_kv   : VT primary kV         (LV side)
    pt_secondary_v  : VT secondary V
    fault_mva       : 3-phase fault MVA at HV bus
    fault_1ph_lv    : Min single-phase fault current at LV bus (A, HV referred)
    nominal_current : Bay nominal / rated current A (HV side)
    swing_freq      : Power swing frequency Hz (default 1.5)
    vector_group    : Transformer vector group string
    """

    Vhv        = inp["vhv_kv"]          # kV
    Vlv        = inp["vlv_kv"]          # kV
    MVA        = inp["mva"]
    pct_Z      = inp["pct_z"]
    xr         = inp["xr_ratio"]
    ctp        = inp["ct_primary"]
    cts        = inp["ct_secondary"]
    vtp_kv     = inp["pt_primary_kv"]   # LV side VT primary kV
    vts_v      = inp["pt_secondary_v"]  # VT secondary V
    fault_mva  = inp["fault_mva"]
    If1_lv     = inp["fault_1ph_lv"]    # A (HV referred)
    I_nom      = inp["nominal_current"]
    f_sw       = inp.get("swing_freq", 1.5)
    vg         = inp.get("vector_group", "YNd11")

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — BASE IMPEDANCES & CT/VT CONVERSION
    # ══════════════════════════════════════════════════════════════════════════

    # Base impedance referred to HV side (primary Ω)
    Zbase_HV = (Vhv ** 2 * 1e6) / (MVA * 1e6)          # Ω

    # Transformer leakage impedance (primary Ω)
    Ztx = (pct_Z / 100.0) * Zbase_HV                    # Ω

    # Transformer impedance components using X/R ratio
    # Z = R + jX,  X/R = xr  →  R = Z / √(1 + xr²),  X = xr × R
    Ztx_R = Ztx / math.sqrt(1 + xr ** 2)
    Ztx_X = xr * Ztx_R
    Z1_ang = math.degrees(math.atan2(Ztx_X, Ztx_R))     # MTA angle (degrees)

    # Source impedance at HV bus (primary Ω)
    Zsys = (Vhv ** 2 * 1e6) / (fault_mva * 1e6)         # Ω

    # Full-load current HV side (A)
    FLC = (MVA * 1e6) / (math.sqrt(3) * Vhv * 1e3)

    # ── CT ratio ──
    CTR = ctp / cts

    # ── VT ratio — VT is on LV (230 kV) side; refer to HV for impedance calc ──
    # VT primary referred to HV voltage base:
    #   vtp_hv_V = vtp_kv × (Vhv / Vlv) × 1000
    vtp_hv_V = vtp_kv * 1e3 * (Vhv / Vlv)
    PTR      = vtp_hv_V / vts_v                          # dimensionless ratio

    # Relay impedance conversion factor (primary Ω → relay secondary Ω)
    kk = CTR / PTR

    # ── SIR ──
    SIR = Zsys / Ztx

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — ZONE REACH CALCULATIONS  (IEC 60255-121 / CEA 2010)
    # ══════════════════════════════════════════════════════════════════════════

    # ── Zone 1 — 80% of transformer impedance (instantaneous) ────────────────
    # Basis: IEC 60255-121 §6.3.2 — 20% margin for CT/VT error, relay tolerance
    Z1_pct  = 0.80
    Z1r_pri = Z1_pct * Ztx
    Z1r_sec = Z1r_pri * kk
    tZ1     = 0.0

    # ── Zone 2 — 120% of transformer impedance (time-delayed) ────────────────
    # Basis: CEA §4.2.3 — covers 100% of TX + 20% overreach margin
    # Timer: coordinate with LV bus protection (≥ 0.4 s CEA §5.1)
    Z2_pct  = 1.20
    Z2r_pri = Z2_pct * Ztx
    Z2r_sec = Z2r_pri * kk
    # CEA timer grading: ≥ 0.4 s from Zone 1; use 0.5 s for 400 kV class
    tZ2     = 0.50 if Vhv >= 400 else 0.40

    # ── Zone 3 — Remote backup: Ztx + 1.5 × Zsys  (CEA §4.2.4) ─────────────
    # Also verify against load impedance (see Section 4)
    Z3r_pri = Ztx + 1.5 * Zsys
    Z3_pct  = Z3r_pri / Ztx
    Z3r_sec = Z3r_pri * kk
    if Vhv >= 400:
        tZ3 = 1.00
    elif Vhv >= 220:
        tZ3 = 0.80
    else:
        tZ3 = 0.80

    # ── Zone 4 — Reverse zone (optional, for busbar backup / current reversal) ─
    # Typically 10–20% of Ztx in reverse direction (CEA §4.3)
    Z4_pct  = 0.20
    Z4r_pri = Z4_pct * Ztx
    Z4r_sec = Z4r_pri * kk
    tZ4     = 0.50

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — STANDBY EARTH FAULT (SEF) / DEF-equivalent
    # Mirrors DEF section from line protection.
    # For transformer: Restricted Earth Fault (REF) is primary.
    # The backup SEF is an IDMT overcurrent on residual current.
    # ══════════════════════════════════════════════════════════════════════════

    # Pickup current: 10–20% of FLC (CEA §6.2 for HV side backup SEF)
    Is_pct  = 0.20                        # 20% of FLC
    Is_pri  = Is_pct * FLC               # A primary
    Is_sec  = Is_pri / CTR               # A secondary

    # Operating time: tZ3 + 0.1 s coordination margin
    t_op = tZ3 + 0.1

    # Fault current ratio for TMS
    ratio = If1_lv / Is_pri if Is_pri > 0 else 1.0

    # TMS — IEC Standard Inverse (Normal Inverse) curve
    # t = TMS × 0.14 / [(I/Is)^0.02 − 1]
    if ratio > 1.0:
        TMS = t_op * (ratio ** 0.02 - 1) / 0.14
    else:
        TMS = 1.0   # Default if ratio ≤ 1 (pickup too high)

    # Characteristic angle for SEF element (degrees)
    # For transformer earth faults: −45° (similar to DEF on line)
    SEF_char_angle   = -45
    SEF_polarisation = "Negative Sequence (I2 / V2)"
    I2pol_ma         = 50     # mA threshold (secondary)
    # V2pol: 5% of VT secondary phase voltage
    V2pol = round((vts_v / math.sqrt(3)) * 0.05, 3)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — LOAD ENCROACHMENT / LOAD BLINDER
    # Same philosophy as line protection: verify Zone-3 does not encroach
    # into minimum load impedance region.
    # ══════════════════════════════════════════════════════════════════════════

    load_angle = 30   # degrees — standard power-factor angle

    # Minimum load resistance:
    #   Use 85% Vph (depressed voltage worst case) and 1.5 × FLC (overload)
    I_max      = 1.5 * I_nom
    V_ph_min   = 0.85 * Vhv * 1e3 / math.sqrt(3)        # V (phase)
    Rload_pri  = V_ph_min / I_max                         # Ω primary
    Rload_sec  = Rload_pri * kk                           # Ω secondary

    # Load blinder (simplified — direct Rload)
    Z_blinder_sec = Rload_sec

    # Zone-3 vs load check
    Z3_vs_load       = Z3r_sec / Z_blinder_sec if Z_blinder_sec > 0 else 99.0
    load_encroach_risk = Z3_vs_load > 0.8

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — POWER SWING BLOCK (PSB)
    # For transformer backup relays on 400 kV bus, PSB is applied to prevent
    # mal-operation during system swings (same philosophy as line PSB).
    # IEC 60255-121 §9, CEA §7
    # ══════════════════════════════════════════════════════════════════════════

    # Source impedance (secondary)
    Vbase   = Vhv * 1e3 / math.sqrt(3)          # V (phase)
    Zs_pri  = Vbase / (fault_mva * 1e6 / (math.sqrt(3) * Vhv * 1e3))
    # Re-derive cleanly:
    If3_A   = fault_mva * 1e6 / (math.sqrt(3) * Vhv * 1e3)  # 3-ph fault current A
    Zs_pri  = Vbase / If3_A
    Zs_sec  = Zs_pri * kk

    # Inner blinder = Rload_sec / 2
    R3Ph_sec = Z_blinder_sec
    RLdInFw  = R3Ph_sec / 2.0

    # Power swing angle increment per half-cycle
    delta_ang = f_sw * 0.005 * 180          # degrees per half-cycle (tP1=1 s assumed)

    # Entry angle
    tan_in   = Zs_sec / (2.0 * RLdInFw) if RLdInFw > 0 else 1.0
    delta_in = 2.0 * math.degrees(math.atan(tan_in))

    # Exit angle
    delta_out = delta_in - delta_ang

    # Outer blinder
    t2_half = abs(delta_out) / 2.0
    if t2_half > 0.01:
        RLdOutFw = Zs_sec / (2.0 * math.tan(math.radians(t2_half)))
    else:
        RLdOutFw = RLdInFw * 6.0

    Delta_R   = RLdOutFw - RLdInFw
    PSB_timer = 50    # ms fixed

    # Mho circle parameters (for R-X plot)
    mta_rad  = math.radians(Z1_ang)
    # Zone centres and radii for each zone (primary Ω)
    def _mho(z_reach):
        Rc = (z_reach / 2) * math.cos(mta_rad)
        Xc = (z_reach / 2) * math.sin(mta_rad)
        return Rc, Xc, z_reach / 2

    z1_Rc, z1_Xc, z1_r = _mho(Z1r_pri)
    z2_Rc, z2_Xc, z2_r = _mho(Z2r_pri)
    z3_Rc, z3_Xc, z3_r = _mho(Z3r_pri)

    return {
        # ── identifiers ──
        "Vhv": Vhv, "Vlv": Vlv, "MVA": MVA, "pct_Z": pct_Z, "xr": xr,
        "vector_group": vg,
        # ── section 1 ──
        "Zbase_HV": Zbase_HV, "Ztx": Ztx, "Ztx_R": Ztx_R, "Ztx_X": Ztx_X,
        "Z1_ang": Z1_ang,
        "Zsys": Zsys, "SIR": SIR, "FLC": FLC,
        "CTR": CTR, "PTR": PTR, "kk": kk,
        "vtp_kv": vtp_kv, "vts_v": vts_v,
        # ── section 2 ──
        "Z1_pct": Z1_pct, "Z1r_pri": Z1r_pri, "Z1r_sec": Z1r_sec, "tZ1": tZ1,
        "Z2_pct": Z2_pct, "Z2r_pri": Z2r_pri, "Z2r_sec": Z2r_sec, "tZ2": tZ2,
        "Z3_pct": Z3_pct, "Z3r_pri": Z3r_pri, "Z3r_sec": Z3r_sec, "tZ3": tZ3,
        "Z4_pct": Z4_pct, "Z4r_pri": Z4r_pri, "Z4r_sec": Z4r_sec, "tZ4": tZ4,
        # ── section 3 SEF ──
        "Is_pct": Is_pct, "Is_pri": Is_pri, "Is_sec": Is_sec,
        "t_op": t_op, "If1_lv": If1_lv, "ratio": ratio, "TMS": TMS,
        "SEF_char_angle": SEF_char_angle,
        "SEF_polarisation": SEF_polarisation,
        "I2pol_ma": I2pol_ma, "V2pol": V2pol,
        # ── section 4 load ──
        "I_max": I_max, "V_ph_min": V_ph_min,
        "Rload_pri": Rload_pri, "Rload_sec": Rload_sec,
        "Z_blinder_sec": Z_blinder_sec, "load_angle": load_angle,
        "Z3_vs_load": Z3_vs_load, "load_encroach_risk": load_encroach_risk,
        # ── section 5 PSB ──
        "Zs_pri": Zs_pri, "Zs_sec": Zs_sec, "If3_A": If3_A,
        "RLdInFw": RLdInFw, "RLdOutFw": RLdOutFw,
        "Delta_R": Delta_R, "delta_in": delta_in, "delta_out": delta_out,
        "PSB_timer": PSB_timer, "f_sw": f_sw,
        # ── mho geometry ──
        "z1_Rc": z1_Rc, "z1_Xc": z1_Xc, "z1_r": z1_r,
        "z2_Rc": z2_Rc, "z2_Xc": z2_Xc, "z2_r": z2_r,
        "z3_Rc": z3_Rc, "z3_Xc": z3_Xc, "z3_r": z3_r,
    }
