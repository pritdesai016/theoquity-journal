import streamlit as st
import pandas as pd
from datetime import datetime, date, time

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
# ---------- Journal State & Helpers ----------
def _init_journal_state():
    if "trades_df" not in st.session_state:
        st.session_state.trades_df = pd.DataFrame(columns=[
            "TradeID","LegID","Exchange","Symbol","Multiplier","TradeType","Direction",
            "EntryDate","EntryTime","EntryStrategy","BuyQty","BuyPrice","StopPriceInitial",
            "T1","T2","T3","SellQty","ExitPrice","ExitDate","ExitTime","TotalCharges",
            "Catalyst","Conviction","Notes","Status"
        ])
    if "stops_df" not in st.session_state:
        st.session_state.stops_df = pd.DataFrame(columns=[
            "TradeID","LegID","StopType","StopPrice","Timestamp"
        ])

def _next_trade_id():
    if st.session_state.trades_df.empty:
        return 1
    return int(st.session_state.trades_df["TradeID"].max()) + 1

def _active_stop_for(trade_id, leg_id, default_sl):
    df = st.session_state.stops_df
    df = df[(df.TradeID == trade_id) & (df.LegID == leg_id)]
    if df.empty: 
        return default_sl
    latest = df.sort_values("Timestamp").iloc[-1]
    return float(latest["StopPrice"])

def _derived_metrics(row):
    mult = float(row["Multiplier"] or 1)
    buy_qty = float(row["BuyQty"] or 0)
    buy_price = float(row["BuyPrice"] or 0)
    sell_qty = float(row.get("SellQty") or 0)
    exit_price = float(row.get("ExitPrice") or 0)
    charges = float(row.get("TotalCharges") or 0)
    entry_dt = row.get("EntryDate")
    exit_dt  = row.get("ExitDate")

    total_buy  = buy_qty * buy_price * mult
    total_sell = sell_qty * exit_price * mult
    gross_pnl  = total_sell - total_buy
    net_pnl    = gross_pnl - charges

    sl_initial = float(row.get("StopPriceInitial") or 0)
    active_sl = _active_stop_for(row["TradeID"], row["LegID"], sl_initial)

    original_r_per_share = buy_price - sl_initial if sl_initial else None
    active_r_per_share   = buy_price - active_sl if active_sl else None

    r_multiple = None
    locked_r = None
    if original_r_per_share and original_r_per_share > 0:
        if exit_price > 0:
            r_multiple = (exit_price - buy_price) / original_r_per_share
        if active_sl and active_sl >= buy_price:
            locked_r = (active_sl - buy_price) / original_r_per_share

    holding_days = None
    if entry_dt and exit_dt:
        start = datetime.combine(entry_dt, time.min) if isinstance(entry_dt, date) else entry_dt
        end   = datetime.combine(exit_dt, time.min)  if isinstance(exit_dt, date)  else exit_dt
        holding_days = max((end - start).days, 0)

    return {
        "TotalBuy": total_buy,
        "TotalSell": total_sell,
        "GrossPnL": gross_pnl,
        "NetPnL": net_pnl,
        "ActiveSL": active_sl,
        "OriginalR_per_share": original_r_per_share,
        "ActiveR_per_share": active_r_per_share,
        "R_multiple": r_multiple,
        "Locked_R_from_TSL": locked_r,
        "HoldingDays": holding_days
    }

# --- Routing ---
if menu == "Dashboard":
    st.title("📊 Dashboard")
    st.write("KPIs, Portfolio Snapshots, BM Console quick view.")

elif menu == "Journal":
    st.title("📓 Journal (MVP)")
    _init_journal_state()

    with st.expander("➕ New Trade / Leg", expanded=True):
        colA, colB, colC, colD = st.columns([1,1,1,1])

        # Identity
        with colA:
            exchange = st.selectbox("Exchange", ["NSE","BSE","NYSE","NASDAQ","CME","Other"])
            symbol   = st.text_input("Symbol", placeholder="e.g., RELIANCE, AAPL")
            trade_type = st.selectbox("Trade Type", ["Equity","Futures","Options","Other"])
            direction  = st.selectbox("Direction", ["Long","Short"])

        with colB:
            multiplier = st.number_input("Multiplier (Lot Size)", value=1.0, step=1.0,
                help="For equities keep 1. For F&O use lot size (e.g., Nifty=50).")
            status   = st.selectbox("Status", ["Planned","Open","Closed","Abandoned"])
            entry_dt = st.date_input("Entry Date", value=date.today())
            entry_tm = st.time_input("Entry Time", value=datetime.now().time())
            entry_strategy = st.text_input("Entry Strategy / Setup", placeholder="e.g., Pullback, Breakout")

        with colC:
            buy_qty  = st.number_input("Buy Qty", min_value=0.0, step=1.0)
            buy_price= st.number_input("Buy Price", min_value=0.0, step=0.01)
            stop_initial = st.number_input("Initial Stop Loss", min_value=0.0, step=0.01)
            t1 = st.number_input("T1 (optional)", min_value=0.0, step=0.01)
            t2 = st.number_input("T2 (optional)", min_value=0.0, step=0.01)
            t3 = st.number_input("T3 (optional)", min_value=0.0, step=0.01)

        with colD:
            add_more = st.checkbox("Add more targets (T4–T5)")
            t4 = t5 = 0.0
            if add_more:
                t4 = st.number_input("T4 (optional)", min_value=0.0, step=0.01)
                t5 = st.number_input("T5 (optional)", min_value=0.0, step=0.01)
            sell_qty   = st.number_input("Sell Qty (if exiting)", min_value=0.0, step=1.0)
            exit_price = st.number_input("Exit Price (if exiting)", min_value=0.0, step=0.01)
            exit_dt    = st.date_input("Exit Date (if exiting)", value=date.today())
            exit_tm    = st.time_input("Exit Time (if exiting)", value=datetime.now().time())

        colE, colF = st.columns([1,1])
        with colE:
            total_charges = st.number_input("Total Charges (all-inclusive)", min_value=0.0, step=0.01,
                help="MVP: enter combined brokerage, taxes, fees, etc.")
            catalyst  = st.text_input("Catalyst (optional)", placeholder="e.g., Earnings, Breakout news")
            conviction= st.slider("Conviction (optional)", 0, 100, 50)

        with colF:
            notes     = st.text_area("Comments / Lesson Learned (optional)", height=100)
            # Trade/Leg IDs (auto helpers)
            suggested_trade_id = _next_trade_id()
            colFID1, colFID2 = st.columns(2)
            with colFID1:
                trade_id = st.number_input("Trade ID", value=suggested_trade_id, step=1)
            with colFID2:
                leg_id   = st.number_input("Leg ID", value=1, step=1)

        # Save
        if st.button("Save Trade / Leg"):
            new_row = {
                "TradeID": int(trade_id),
                "LegID": int(leg_id),
                "Exchange": exchange,
                "Symbol": symbol,
                "Multiplier": multiplier,
                "TradeType": trade_type,
                "Direction": direction,
                "EntryDate": entry_dt,
                "EntryTime": entry_tm,
                "EntryStrategy": entry_strategy,
                "BuyQty": buy_qty,
                "BuyPrice": buy_price,
                "StopPriceInitial": stop_initial,
                "T1": t1, "T2": t2, "T3": t3,
                "SellQty": sell_qty,
                "ExitPrice": exit_price,
                "ExitDate": exit_dt if sell_qty > 0 else None,
                "ExitTime": exit_tm if sell_qty > 0 else None,
                "TotalCharges": total_charges,
                "Catalyst": catalyst,
                "Conviction": conviction,
                "Notes": notes,
                "Status": status
            }
            st.session_state.trades_df = pd.concat(
                [st.session_state.trades_df, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.success(f"Saved Trade {trade_id} (Leg {leg_id}).")

            # Show derived metrics immediately
            m = _derived_metrics(new_row)
            st.info(
                f"Active SL: {m['ActiveSL']},  Gross P&L: {m['GrossPnL']:.2f},  Net P&L: {m['NetPnL']:.2f}\n"
                f"Original R/Share: {m['OriginalR_per_share'] if m['OriginalR_per_share'] is not None else '—'}  |  "
                f"Active R/Share: {m['ActiveR_per_share'] if m['ActiveR_per_share'] is not None else '—'}  |  "
                f"R Multiple: {m['R_multiple'] if m['R_multiple'] is not None else '—'}  |  "
                f"Locked R from TSL: {m['Locked_R_from_TSL'] if m['Locked_R_from_TSL'] is not None else '—'}  |  "
                f"Holding Days: {m['HoldingDays'] if m['HoldingDays'] is not None else '—'}"
            )

    with st.expander("🔁 Add Trailing Stop (TSL) to an Existing Trade", expanded=False):
        if st.session_state.trades_df.empty:
            st.warning("No trades yet. Save a trade above first.")
        else:
            # Choose existing trade/leg
            ids = st.session_state.trades_df[["TradeID","LegID","Symbol","EntryDate"]].copy()
            ids["Label"] = ids.apply(lambda r: f"T{int(r.TradeID)}-L{int(r.LegID)} | {r.Symbol} ({r.EntryDate})", axis=1)
            choice = st.selectbox("Select Trade/Leg", ids["Label"])
            pick = ids[ids["Label"] == choice].iloc[0]
            t_trade_id = int(pick["TradeID"])
            t_leg_id   = int(pick["LegID"])

            tsl_price = st.number_input("New Trailing SL Price", min_value=0.0, step=0.01)
            tsl_time  = st.text_input("Timestamp (auto if blank)", "")
            if st.button("Add TSL"):
                ts = tsl_time.strip() or datetime.now().isoformat(timespec="seconds")
                new_sl = {
                    "TradeID": t_trade_id,
                    "LegID": t_leg_id,
                    "StopType": "Trailing",
                    "StopPrice": tsl_price,
                    "Timestamp": ts
                }
                st.session_state.stops_df = pd.concat(
                    [st.session_state.stops_df, pd.DataFrame([new_sl])],
                    ignore_index=True
                )
                st.success(f"Added TSL {tsl_price} to T{t_trade_id}-L{t_leg_id}")

    st.subheader("📄 Trades (MVP View)")
    st.dataframe(st.session_state.trades_df, use_container_width=True)

    st.subheader("🧷 Stop Log (Initial + Trailing)")
    st.dataframe(st.session_state.stops_df, use_container_width=True)

    # Exports
    colX, colY = st.columns(2)
    with colX:
        st.download_button(
            "⬇️ Download Trades CSV",
            st.session_state.trades_df.to_csv(index=False).encode("utf-8"),
            file_name="theoquity_trades.csv",
            mime="text/csv"
        )
    with colY:
        st.download_button(
            "⬇️ Download Stops CSV",
            st.session_state.stops_df.to_csv(index=False).encode("utf-8"),
            file_name="theoquity_stops.csv",
            mime="text/csv"
        )

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