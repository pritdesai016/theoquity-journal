import streamlit as st

# --- Page Config ---
st.set_page_config(
    page_title="Theoquity",
    layout="wide",
    page_icon="🌌"
)

# --- Colors (from earlier selection: softer white, sage green, deep violet) ---
PRIMARY_COLOR = "#5D3FD3"   # deep violet
SECONDARY_COLOR = "#4CAF50" # sage green
BG_COLOR = "#FAFAFA"        # soft white
TEXT_COLOR = "#222222"

# --- Custom Styling ---
st.markdown(f"""
    <style>
        body {{
            background-color: {BG_COLOR};
            color: {TEXT_COLOR};
        }}
        .stSidebar {{
            background-color: {PRIMARY_COLOR}20;
        }}
        .stButton>button {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border-radius: 8px;
        }}
        h1, h2, h3 {{
            color: {PRIMARY_COLOR};
        }}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Menu ---
menu = st.sidebar.radio(
    "Main Menu",
    [
        "Dashboard",
        "Journal",
        "Analysis",
        "Config",
        "Reports",
        "Games",
        "AI Node",     # (AI Coach, codename)
        "News & Blogs",
        "LE Console",  # (Gamification, codename)
        "Notes",
        "Help",
        "Admin"
    ]
)

# --- Routing ---
if menu == "Dashboard":
    st.title("📊 Dashboard")
    st.write("KPIs, Portfolio Snapshots, BM Console quick view.")

elif menu == "Journal":
    st.title("📓 Journal")
    st.subheader("Planned Trades")
    st.write("PTC, Templates, Abandoned reasons.")
    st.subheader("Actual Trades")
    st.write("Planned → Executed, TWOP (Trade Without Plan).")
    st.subheader("Open/Closed Trades")
    st.write("Tracking states, review scores.")

elif menu == "Analysis":
    st.title("📈 Analysis")
    st.write("Performance, Portfolio Compare, BM Deep Dive, RL Suite.")

elif menu == "Config":
    st.title("⚙️ Configuration")
    st.write("Brokers, Labels, Strategies, Checklists, Templates, Risk.")

elif menu == "Reports":
    st.title("📑 Reports")
    st.write("P&L reports, Bias Impact, Narrative Exports.")

elif menu == "Games":
    st.title("🎮 Games")
    st.write("Anchoring, FOMO Gate, LA Lab, Stop Drill, etc.")

elif menu == "AI Node":
    st.title("🤖 AI Node")
    st.write("Seshat (Lite), NC Node (Full). Forecasting, Coaching.")

elif menu == "News & Blogs":
    st.title("📰 News & Blogs")
    st.write("Feeds, Blogs, TradingView widgets.")

elif menu == "LE Console":
    st.title("🏅 Leveling Engine (LE)")
    st.write("Ranks, Sub-levels, Badges, Leaderboards, Challenges.")

elif menu == "Notes":
    st.title("📝 Notes")
    st.write("Rich-text notes, attach to trades/portfolios.")

elif menu == "Help":
    st.title("❓ Help & Account")
    st.write("Tutorials, API Guides, Billing, Support.")

elif menu == "Admin":
    st.title("🔐 Admin Panel")
    st.write("Client Master, User Mgmt, CMS, Logs, Settings.")