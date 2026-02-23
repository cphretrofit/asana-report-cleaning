import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(
    page_title="CSV Cleaner",
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
    
    .main > div:first-child {
        display: none;
    }
    
    .block-container {
        padding-top: 1rem !important;
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
    
    .stFileUploader > div > div > div {
        background: transparent !important;
    }
    
    .stFileUploader label {
        display: none !important;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 0.875rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.35);
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

def normalize_address(value):
    if pd.isna(value) or str(value).strip() == "":
        return None
    addr = str(value).strip().lower()
    addr = addr.replace('.', '').replace(',', '').replace('#', '').replace('\n', ' ')
    addr = ' '.join(addr.split())
    return addr

def looks_like_address(value):
    if pd.isna(value):
        return False
    
    val = str(value).strip()
    val_lower = val.lower()
    
    if not val or val == "":
        return False
    
    address_patterns = [
        r'\b(street|st|avenue|ave|road|rd|boulevard|blvd|drive|dr|lane|ln|court|ct|place|pl|way|terrace|ter)\b',
        r'\b(suite|ste|floor|unit|building|bldg|apartment|apt|house)\b',
        r'\b(po box|pobox|box)\b',
        r'\b(north|south|east|west|n\.?|s\.?|e\.?|w\.?)\b',
        r'\b(city|state|zip|postal)\b',
        r'\d+\s+(street|avenue|road|drive|lane|boulevard|way|place)',
    ]
    
    for pattern in address_patterns:
        if re.search(pattern, val_lower):
            return True
    
    if re.search(r'#\s*\d+', val):
        return True
    
    parts = val.split()
    if len(parts) >= 3:
        if re.match(r'^\d+', val) and any(x in val_lower for x in ['street', 'avenue', 'road', 'drive', 'lane', 'court', 'way', 'place', 'blvd', 'ave', 'st', 'rd']):
            return True
    
    return False

st.markdown('<div class="container"><div class="card">', unsafe_allow_html=True)
st.markdown('<div class="title">🧹 CSV Cleaner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Clean your Asana exports by removing subtasks and duplicates</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, dtype=str)
    
    parent_col = 'Parent task'
    
    if parent_col not in df.columns:
        st.error(f"Column '{parent_col}' not found in the CSV. Please ensure your file has this column.")
    else:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        st.markdown(f'<p class="info-text">Only rows with valid addresses in "{parent_col}" will be kept. All other rows will be removed.</p>', unsafe_allow_html=True)
        
        if st.button("Clean CSV"):
            original_count = len(df)
            
            mask = df[parent_col].apply(looks_like_address)
            filtered_df = df[mask].copy()
            
            filtered_df['__normalized_addr__'] = filtered_df[parent_col].apply(normalize_address)
            filtered_df = filtered_df.drop_duplicates(subset='__normalized_addr__', keep='first')
            filtered_df = filtered_df.drop(columns=['__normalized_addr__'])
            
            cols_to_keep = [col for col in filtered_df.columns if col.lower() != 'name']
            filtered_df = filtered_df[cols_to_keep]
            
            if parent_col in filtered_df.columns:
                cols = list(filtered_df.columns)
                parent_idx = cols.index(parent_col)
                cols.remove(parent_col)
                cols.insert(1, parent_col)
                filtered_df = filtered_df[cols]
            
            final_count = len(filtered_df)
            removed_count = original_count - final_count
            
            buffer = io.StringIO()
            filtered_df.to_csv(buffer, index=False)
            buffer.seek(0)
            
            st.markdown(f"""
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-value">{original_count}</div>
                    <div class="stat-label">Original</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{final_count}</div>
                    <div class="stat-label">Kept</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{removed_count}</div>
                    <div class="stat-label">Removed</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f'<div class="success-box">✅ Cleaned file ready with {final_count} addresses</div>', unsafe_allow_html=True)
            
            st.download_button(
                label="Download Cleaned CSV",
                data=buffer.getvalue(),
                file_name="cleaned_" + uploaded_file.name,
                mime="text/csv"
            )

st.markdown('</div></div>', unsafe_allow_html=True)
