import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(
    page_title="Asana CSV Cleaner",
    page_icon="🧹",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        min-height: 100vh;
        padding: 2rem;
    }
    
    .container {
        max-width: 680px;
        margin: 0 auto;
    }
    
    .card {
        background: white;
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
    }
    
    .title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .subtitle {
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 0.95rem;
    }
    
    .stats {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-box {
        background: #f9fafb;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #6366f1;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .success-box {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1.5rem 0;
        color: #065f46;
    }
    
    .warn-box {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-radius: 10px;
        padding: 1rem;
        margin: 1.5rem 0;
        color: #92400e;
    }
    
    .detected-box {
        background: #f0f4ff;
        border: 1px solid #c7d2fe;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #3730a3;
        font-size: 0.85rem;
        line-height: 1.6;
    }
    
    .divider {
        height: 1px;
        background: #e5e7eb;
        margin: 2rem 0;
    }
    
    .info-text {
        font-size: 0.85rem;
        color: #6b7280;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ── UK postcode regex ────────────────────────────────────────────────────────
UK_POSTCODE = re.compile(r'[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}', re.IGNORECASE)

def is_address(value):
    """Detect a real UK address by looking for a postcode."""
    if pd.isna(value) or str(value).strip() == "":
        return False
    return bool(UK_POSTCODE.search(str(value)))

def extract_uprn_value(notes_value):
    """Pull the UPRN digits out of a Notes cell."""
    if pd.isna(notes_value):
        return ""
    match = re.search(r'UPRN:\s*(\d+)', str(notes_value))
    return match.group(1) if match else ""

def auto_detect_columns(columns):
    """Find the key Asana columns automatically."""
    cols_lower = {c.lower().strip(): c for c in columns}
    parent_col = cols_lower.get('parent task')
    name_col = cols_lower.get('name')
    notes_col = cols_lower.get('notes')
    return parent_col, name_col, notes_col

def build_uprn_map(df, name_col, notes_col):
    """Build address -> UPRN lookup from parent-level rows."""
    uprn_map = {}
    if not name_col or not notes_col:
        return uprn_map
    if notes_col not in df.columns or name_col not in df.columns:
        return uprn_map
    for _, row in df.iterrows():
        name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ""
        notes = row[notes_col] if pd.notna(row.get(notes_col)) else None
        if name and notes:
            uprn = extract_uprn_value(notes)
            if uprn:
                uprn_map[name] = uprn
    return uprn_map


# ── UI ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="container"><div class="card">', unsafe_allow_html=True)
st.markdown('<div class="title">🧹 Asana CSV Cleaner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload an Asana export — subtasks and duplicates are removed automatically</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, dtype=str)
    columns = list(df.columns)
    original_count = len(df)

    # Auto-detect columns
    parent_col, name_col, notes_col = auto_detect_columns(columns)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Show what was detected
    detected_parts = []
    if parent_col:
        detected_parts.append(f"<b>Address column:</b> {parent_col}")
    if name_col:
        detected_parts.append(f"<b>Task name column:</b> {name_col}")
    if notes_col:
        detected_parts.append(f"<b>Notes column:</b> {notes_col}")

    if detected_parts:
        st.markdown(
            f'<div class="detected-box">🔍 Auto-detected:<br>'
            f'{"<br>".join(detected_parts)}</div>',
            unsafe_allow_html=True,
        )

    if not parent_col:
        st.markdown(
            '<div class="warn-box">⚠️ Could not find a "Parent task" column. '
            'Please check your CSV has the standard Asana export format.</div>',
            unsafe_allow_html=True,
        )
    else:
        # ── Options ──────────────────────────────────────────────────────
        extract_uprn = st.checkbox(
            "Extract UPRN Number from Notes",
            value=True,
            help="Extracts the UPRN number from parent task Notes, adds it "
                 "as a column after the address, and removes the Notes column",
        )

        if st.button("Clean CSV"):
            # Step 1: Keep only rows where Parent task is a real address
            address_mask = df[parent_col].apply(is_address)
            filtered_df = df[address_mask].copy()

            # Step 2: Deduplicate — one row per unique address
            before_dedup = len(filtered_df)
            filtered_df = filtered_df.drop_duplicates(
                subset=parent_col, keep='first'
            )
            final_count = len(filtered_df)
            dupes_removed = before_dedup - final_count
            removed_count = original_count - final_count

            # Step 3: Move Parent task to column position 1 (after Task ID)
            cols = list(filtered_df.columns)
            cols.remove(parent_col)
            cols.insert(1, parent_col)
            filtered_df = filtered_df[cols]

            # Step 4: UPRN extraction
            uprn_matched = 0
            if extract_uprn and notes_col and notes_col in df.columns:
                uprn_map = build_uprn_map(df, name_col, notes_col)

                filtered_df['UPRN Number'] = filtered_df[parent_col].apply(
                    lambda x: uprn_map.get(str(x).strip(), '')
                    if pd.notna(x) else ''
                )
                uprn_matched = (filtered_df['UPRN Number'] != '').sum()

                # Place UPRN Number right after address, drop Notes
                cols = list(filtered_df.columns)
                cols.remove('UPRN Number')
                insert_pos = cols.index(parent_col) + 1
                cols.insert(insert_pos, 'UPRN Number')
                if notes_col in cols:
                    cols.remove(notes_col)
                filtered_df = filtered_df[cols]

            # ── Output ───────────────────────────────────────────────────
            buffer = io.StringIO()
            filtered_df.to_csv(buffer, index=False)
            buffer.seek(0)

            st.markdown(f"""
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-value">{original_count:,}</div>
                    <div class="stat-label">Original Rows</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{final_count:,}</div>
                    <div class="stat-label">Addresses</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{removed_count:,}</div>
                    <div class="stat-label">Removed</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Build summary message
            summary = f"✅ {final_count:,} unique addresses"
            if dupes_removed > 0:
                summary += f" ({dupes_removed:,} duplicates removed)"
            if extract_uprn and notes_col:
                summary += f" — {uprn_matched:,} UPRN numbers extracted"
            st.markdown(
                f'<div class="success-box">{summary}</div>',
                unsafe_allow_html=True,
            )

            st.download_button(
                label="Download Cleaned CSV",
                data=buffer.getvalue(),
                file_name="cleaned_" + uploaded_file.name,
                mime="text/csv",
            )

st.markdown('</div></div>', unsafe_allow_html=True)
