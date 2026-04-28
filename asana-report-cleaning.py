import streamlit as st
import pandas as pd
import io
import re

# ═══════════════════════════════════════════════════════════════════════════════
#  THEME STATE
# ═══════════════════════════════════════════════════════════════════════════════
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

st.set_page_config(
    page_title="CPH Retrofit — CSV Cleaner",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════════════════════════
#  LOGO
# ═══════════════════════════════════════════════════════════════════════════════
LOGO_URL = (
    "https://raw.githubusercontent.com/cphretrofit/cphretrofit/main/"
    "New%20CPH%20Logo_transparent.png"
)

# ═══════════════════════════════════════════════════════════════════════════════
#  THEME CSS
# ═══════════════════════════════════════════════════════════════════════════════
dark = st.session_state.dark_mode

if dark:
    BG_MAIN       = "#060d18"
    BG_CARD       = "rgba(255,255,255,0.04)"
    BG_CARD_HOVER = "rgba(255,255,255,0.06)"
    BORDER        = "rgba(255,255,255,0.09)"
    BORDER_ACCENT = "rgba(0,195,160,0.35)"
    TXT_PRIMARY   = "rgba(255,255,255,0.88)"
    TXT_MUTED     = "rgba(255,255,255,0.38)"
    TAG_BG        = "rgba(13,217,179,0.10)"
    TAG_BORDER    = "rgba(13,217,179,0.28)"
    TAG_TXT       = "rgba(13,217,179,0.90)"
    TAG_BG_B      = "rgba(59,130,246,0.10)"
    TAG_BORDER_B  = "rgba(59,130,246,0.28)"
    TAG_TXT_B     = "rgba(99,168,255,0.90)"
    TAG_BG_P      = "rgba(168,85,247,0.10)"
    TAG_BORDER_P  = "rgba(168,85,247,0.28)"
    TAG_TXT_P     = "rgba(196,140,255,0.90)"
    ALERT_BG      = "rgba(13,217,179,0.07)"
    ALERT_BORDER  = "rgba(13,217,179,0.28)"
    ALERT_TXT     = "rgba(13,217,179,0.92)"
    WARN_BG       = "rgba(251,191,36,0.08)"
    WARN_BORDER   = "rgba(251,191,36,0.28)"
    WARN_TXT      = "rgba(251,191,36,0.92)"
    STAT_BG       = "rgba(255,255,255,0.04)"
    STAT_BORDER   = "rgba(255,255,255,0.07)"
    ORB1          = "rgba(0,195,160,0.17)"
    ORB2          = "rgba(59,130,246,0.13)"
    UPLOAD_HOVER  = "rgba(0,195,160,0.04)"
    BTN_DL_BG     = "rgba(255,255,255,0.06)"
    BTN_DL_HOVER  = "rgba(0,195,160,0.10)"
    INPUT_TXT     = "rgba(255,255,255,0.50)"
    LOGO_FILTER   = "drop-shadow(0 0 18px rgba(0,195,160,0.35))"
    TOGGLE_LABEL  = "☀️  Light mode"
    DIVIDER_COLOR = "rgba(0,195,160,0.35), rgba(59,130,246,0.35)"
else:
    BG_MAIN       = "#eef2f7"
    BG_CARD       = "rgba(255,255,255,0.80)"
    BG_CARD_HOVER = "rgba(255,255,255,0.95)"
    BORDER        = "rgba(0,0,0,0.08)"
    BORDER_ACCENT = "rgba(0,150,120,0.40)"
    TXT_PRIMARY   = "#162030"
    TXT_MUTED     = "#7a8fa8"
    TAG_BG        = "rgba(0,160,130,0.09)"
    TAG_BORDER    = "rgba(0,160,130,0.30)"
    TAG_TXT       = "#007a65"
    TAG_BG_B      = "rgba(37,99,235,0.08)"
    TAG_BORDER_B  = "rgba(37,99,235,0.28)"
    TAG_TXT_B     = "#1d4ed8"
    TAG_BG_P      = "rgba(126,34,206,0.08)"
    TAG_BORDER_P  = "rgba(126,34,206,0.28)"
    TAG_TXT_P     = "#6b21a8"
    ALERT_BG      = "rgba(0,160,130,0.08)"
    ALERT_BORDER  = "rgba(0,160,130,0.30)"
    ALERT_TXT     = "#065f46"
    WARN_BG       = "rgba(180,130,0,0.08)"
    WARN_BORDER   = "rgba(180,130,0,0.30)"
    WARN_TXT      = "#78450a"
    STAT_BG       = "rgba(255,255,255,0.70)"
    STAT_BORDER   = "rgba(0,0,0,0.07)"
    ORB1          = "rgba(0,195,160,0.12)"
    ORB2          = "rgba(59,130,246,0.10)"
    UPLOAD_HOVER  = "rgba(0,160,130,0.04)"
    BTN_DL_BG     = "rgba(0,0,0,0.04)"
    BTN_DL_HOVER  = "rgba(0,160,130,0.08)"
    INPUT_TXT     = "#7a8fa8"
    LOGO_FILTER   = "drop-shadow(0 4px 12px rgba(0,0,0,0.15))"
    TOGGLE_LABEL  = "🌙  Dark mode"
    DIVIDER_COLOR = "rgba(0,160,130,0.35), rgba(37,99,235,0.35)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
.stApp {{
    font-family: 'DM Sans', sans-serif;
    background: {BG_MAIN} !important;
    color: {TXT_PRIMARY};
    transition: background 0.3s, color 0.3s;
}}

/* ── Orbs ── */
.stApp::before {{
    content: '';
    position: fixed;
    top: -140px; right: -90px;
    width: 540px; height: 540px;
    background: radial-gradient(circle, {ORB1} 0%, transparent 70%);
    pointer-events: none; z-index: 0;
}}
.stApp::after {{
    content: '';
    position: fixed;
    bottom: -110px; left: -70px;
    width: 440px; height: 440px;
    background: radial-gradient(circle, {ORB2} 0%, transparent 70%);
    pointer-events: none; z-index: 0;
}}

/* ── Streamlit chrome ── */
#MainMenu, footer, [data-testid="stToolbar"],
[data-testid="collapsedControl"] {{ display: none !important; }}
header {{ visibility: hidden; }}

/* ── Layout ── */
[data-testid="stAppViewContainer"] > .main {{ padding: 0 !important; }}
.block-container {{
    max-width: 660px !important;
    padding: 2.5rem 1.5rem 4rem !important;
    position: relative; z-index: 1;
}}

/* ── Logo ── */
.cph-logo {{
    display: flex;
    justify-content: center;
    margin-bottom: 0.25rem;
}}
.cph-logo img {{
    height: 70px;
    width: auto;
    filter: {LOGO_FILTER};
    transition: filter 0.3s;
}}

/* ── Page subtitle ── */
.cph-subtitle {{
    text-align: center;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: {TXT_MUTED};
    font-family: 'DM Mono', monospace;
    margin-bottom: 2rem;
}}

/* ── Section label ── */
.section-label {{
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: {TXT_MUTED};
    font-family: 'DM Mono', monospace;
    margin-bottom: 0.75rem;
}}

/* ── Gradient divider ── */
.grad-divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, {DIVIDER_COLOR}, transparent);
    margin: 1.5rem 0;
    border: none;
}}

/* ── Tag pills ── */
.tag-row {{ display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.5rem; }}
.tag {{
    font-size: 0.73rem;
    font-family: 'DM Mono', monospace;
    padding: 0.28rem 0.65rem;
    border-radius: 8px;
    background: {TAG_BG};
    border: 1px solid {TAG_BORDER};
    color: {TAG_TXT};
    white-space: nowrap;
    transition: background 0.2s;
}}
.tag.blue  {{ background: {TAG_BG_B};  border-color: {TAG_BORDER_B};  color: {TAG_TXT_B}; }}
.tag.purple{{ background: {TAG_BG_P};  border-color: {TAG_BORDER_P};  color: {TAG_TXT_P}; }}

/* ── Alert boxes ── */
.alert {{
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    margin: 1rem 0;
    font-size: 0.87rem;
    line-height: 1.65;
}}
.alert-success {{
    background: {ALERT_BG};
    border: 1px solid {ALERT_BORDER};
    color: {ALERT_TXT};
}}
.alert-warn {{
    background: {WARN_BG};
    border: 1px solid {WARN_BORDER};
    color: {WARN_TXT};
}}

/* ── Stat grid ── */
.stat-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.7rem;
    margin: 1.4rem 0 1rem;
}}
.stat-box {{
    background: {STAT_BG};
    border: 1px solid {STAT_BORDER};
    border-radius: 14px;
    padding: 1.1rem 0.75rem;
    text-align: center;
    backdrop-filter: blur(12px);
}}
.stat-val {{
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, #0dd9b3, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-family: 'DM Mono', monospace;
    line-height: 1.2;
}}
.stat-lbl {{
    font-size: 0.64rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {TXT_MUTED};
    margin-top: 0.3rem;
    font-family: 'DM Mono', monospace;
}}

/* ── File uploader ── */
[data-testid="stFileUploaderDropzone"] {{
    background: {BG_CARD} !important;
    border: 1.5px dashed {BORDER_ACCENT} !important;
    border-radius: 14px !important;
    transition: border-color 0.25s, background 0.25s;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: rgba(0,195,160,0.65) !important;
    background: {UPLOAD_HOVER} !important;
}}
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small {{
    color: {INPUT_TXT} !important;
}}
[data-testid="stFileUploader"] label {{ display: none; }}

/* ── Checkbox ── */
[data-testid="stCheckbox"] label p {{
    color: {TXT_PRIMARY} !important;
    font-size: 0.9rem;
}}

/* ── Toggle (theme switch) ── */
[data-testid="stToggle"] label p {{
    color: {TXT_MUTED} !important;
    font-size: 0.82rem;
    font-family: 'DM Mono', monospace;
}}

/* ── Primary button ── */
.stButton > button {{
    width: 100%;
    background: linear-gradient(135deg, #0dd9b3 0%, #3b82f6 55%, #4ade80 100%) !important;
    color: #050d14 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.06em;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.72rem 2rem !important;
    cursor: pointer !important;
    box-shadow: 0 0 22px rgba(13,217,179,0.28) !important;
    transition: opacity 0.2s, box-shadow 0.2s, transform 0.15s !important;
}}
.stButton > button:hover {{
    opacity: 0.9 !important;
    box-shadow: 0 0 36px rgba(13,217,179,0.42) !important;
    transform: translateY(-1px) !important;
}}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {{
    width: 100%;
    background: {BTN_DL_BG} !important;
    color: {TXT_PRIMARY} !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    border: 1px solid {BORDER_ACCENT} !important;
    border-radius: 12px !important;
    padding: 0.68rem 2rem !important;
    transition: background 0.2s, border-color 0.2s !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
    background: {BTN_DL_HOVER} !important;
    border-color: rgba(0,195,160,0.65) !important;
}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════
UK_POSTCODE = re.compile(r'\b([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\b', re.IGNORECASE)

KNOWN_CUSTOM_FIELDS = [
    "Wave 3 Year 2 Saffron Fields",
    "Watford Low Rise",
    "Dodds Group",
    "Watford Community Housing",
    "GreenHouse Energy Stages",
    "Wave 3 Saffron Stages",
    "Cold Rush Stages",
    "Align Property Stages",
    "North Yorkshire Council Stages",
]

# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def is_address(value):
    if pd.isna(value) or str(value).strip() == "":
        return False
    return bool(UK_POSTCODE.search(str(value)))

def extract_postcode(value):
    if pd.isna(value):
        return ""
    match = UK_POSTCODE.search(str(value))
    if not match:
        return ""
    raw = match.group(1).upper().replace(" ", "")
    return raw[:-3] + " " + raw[-3:]

def extract_uprn_value(notes_value):
    if pd.isna(notes_value):
        return ""
    match = re.search(r'UPRN:\s*(\d+)', str(notes_value))
    return match.group(1) if match else ""

def auto_detect_columns(columns):
    cols_lower = {c.lower().strip(): c for c in columns}
    return (
        cols_lower.get('parent task'),
        cols_lower.get('name'),
        cols_lower.get('notes'),
    )

def detect_custom_fields(columns):
    col_set = {c.strip() for c in columns}
    return [cf for cf in KNOWN_CUSTOM_FIELDS if cf in col_set]

def build_uprn_map(df, name_col, notes_col):
    uprn_map = {}
    if not name_col or not notes_col:
        return uprn_map
    if notes_col not in df.columns or name_col not in df.columns:
        return uprn_map
    for _, row in df.iterrows():
        name  = str(row[name_col]).strip()       if pd.notna(row[name_col])      else ""
        notes = row[notes_col]                   if pd.notna(row.get(notes_col)) else None
        if name and notes:
            uprn = extract_uprn_value(notes)
            if uprn:
                uprn_map[name] = uprn
    return uprn_map

# ═══════════════════════════════════════════════════════════════════════════════
#  HEADER — logo + subtitle + theme toggle
# ═══════════════════════════════════════════════════════════════════════════════
logo_col, toggle_col = st.columns([5, 2])

with logo_col:
    st.markdown(
        f'<div class="cph-logo">'
        f'<img src="{LOGO_URL}" alt="CPH Retrofit"></div>'
        f'<div class="cph-subtitle">Asana CSV Cleaner</div>',
        unsafe_allow_html=True,
    )

with toggle_col:
    st.markdown("<div style='padding-top:1.6rem'></div>", unsafe_allow_html=True)
    new_mode = st.toggle(TOGGLE_LABEL, value=st.session_state.dark_mode)
    if new_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = new_mode
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Upload Asana export</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["csv"])

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN LOGIC
# ═══════════════════════════════════════════════════════════════════════════════
if uploaded_file:
    df             = pd.read_csv(uploaded_file, dtype=str)
    columns        = list(df.columns)
    original_count = len(df)

    parent_col, name_col, notes_col = auto_detect_columns(columns)
    found_custom_fields              = detect_custom_fields(columns)

    # ── Detected columns ──────────────────────────────────────────────────
    st.markdown('<hr class="grad-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Detected Columns</div>', unsafe_allow_html=True)

    tags_html = ""
    if parent_col:
        tags_html += f'<span class="tag">📍 {parent_col}</span>'
    if name_col:
        tags_html += f'<span class="tag blue">📝 {name_col}</span>'
    if notes_col:
        tags_html += f'<span class="tag blue">🗒 {notes_col}</span>'
    if tags_html:
        st.markdown(f'<div class="tag-row">{tags_html}</div>', unsafe_allow_html=True)

    if found_custom_fields:
        st.markdown('<div style="margin-top:1rem;" class="section-label">Custom Fields Found</div>', unsafe_allow_html=True)
        cf_tags = "".join(f'<span class="tag purple">🏷 {cf}</span>' for cf in found_custom_fields)
        st.markdown(f'<div class="tag-row">{cf_tags}</div>', unsafe_allow_html=True)

    if not parent_col:
        st.markdown(
            '<div class="alert alert-warn">⚠️ No "Parent task" column found. '
            'Please check this is a standard Asana CSV export.</div>',
            unsafe_allow_html=True,
        )
    else:
        # ── Options ───────────────────────────────────────────────────────
        st.markdown('<hr class="grad-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Options</div>', unsafe_allow_html=True)
        extract_uprn = st.checkbox(
            "Extract UPRN Number from Notes",
            value=True,
            help="Reads UPRN numbers from parent task Notes and adds a dedicated column.",
        )

        st.markdown('<hr class="grad-divider">', unsafe_allow_html=True)

        if st.button("✦  Clean CSV"):
            # Step 1 — filter to address rows
            address_mask = df[parent_col].apply(is_address)
            filtered_df  = df[address_mask].copy()

            # Step 2 — deduplicate
            before_dedup  = len(filtered_df)
            filtered_df   = filtered_df.drop_duplicates(subset=parent_col, keep='first')
            final_count   = len(filtered_df)
            dupes_removed = before_dedup - final_count
            removed_count = original_count - final_count

            # Step 3 — postcode column
            filtered_df['Postcode'] = filtered_df[parent_col].apply(extract_postcode)

            # Step 4 — UPRN extraction
            uprn_matched = 0
            if extract_uprn and notes_col and notes_col in df.columns:
                uprn_map = build_uprn_map(df, name_col, notes_col)
                filtered_df['UPRN Number'] = filtered_df[parent_col].apply(
                    lambda x: uprn_map.get(str(x).strip(), '') if pd.notna(x) else ''
                )
                uprn_matched = (filtered_df['UPRN Number'] != '').sum()

            # Step 5 — custom fields
            for cf in found_custom_fields:
                if cf in df.columns:
                    filtered_df[cf] = df.loc[filtered_df.index, cf].values

            # Step 6 — rename parent_col → Address
            filtered_df = filtered_df.rename(columns={parent_col: 'Address'})

            # Step 7 — final column order: Task ID | Address | Postcode | UPRN | custom…
            keep_cols = ['Task ID', 'Address', 'Postcode']
            if 'UPRN Number' in filtered_df.columns:
                keep_cols.append('UPRN Number')
            for cf in found_custom_fields:
                if cf in filtered_df.columns:
                    keep_cols.append(cf)
            keep_cols   = [c for c in keep_cols if c in filtered_df.columns]
            filtered_df = filtered_df[keep_cols]

            # ── Results ───────────────────────────────────────────────────
            buffer = io.StringIO()
            filtered_df.to_csv(buffer, index=False)
            buffer.seek(0)

            st.markdown(f"""
            <div class="stat-grid">
                <div class="stat-box">
                    <div class="stat-val">{original_count:,}</div>
                    <div class="stat-lbl">Original Rows</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val">{final_count:,}</div>
                    <div class="stat-lbl">Addresses</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val">{removed_count:,}</div>
                    <div class="stat-lbl">Removed</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            parts = [f"✦ {final_count:,} unique addresses"]
            if dupes_removed > 0:
                parts.append(f"{dupes_removed:,} duplicates removed")
            if extract_uprn and notes_col:
                parts.append(f"{uprn_matched:,} UPRN numbers extracted")
            if found_custom_fields:
                parts.append(f"{len(found_custom_fields)} custom field(s) included")

            st.markdown(
                f'<div class="alert alert-success">{"  ·  ".join(parts)}</div>',
                unsafe_allow_html=True,
            )

            st.download_button(
                label="⬇  Download Cleaned CSV",
                data=buffer.getvalue(),
                file_name="cleaned_" + uploaded_file.name,
                mime="text/csv",
            )
