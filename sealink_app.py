import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import date

st.set_page_config(page_title="harborcore — Port Management", page_icon="⚓", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Source+Sans+3:wght@300;400;600&display=swap');
html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    background-color: #0b1120; color: #d4e4f7;
}
h1, h2, h3 { font-family: 'Bebas Neue', sans-serif; letter-spacing: 2px; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2e, #091528);
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] * { color: #a8c4e0 !important; }
div[data-testid="metric-container"] {
    background: #112240; border: 1px solid #1e3a5f; border-radius: 8px; padding: 12px;
}
.stButton > button {
    background: #0a6ec7; color: white; border: none; border-radius: 5px;
    font-family: 'Bebas Neue', sans-serif; letter-spacing: 1px;
    font-size: 1rem; padding: 0.4rem 1.2rem;
}
.stButton > button:hover { background: #0d8cf0; }
.info-box {
    background: #0d1f35; border-left: 3px solid #1e6aab;
    border-radius: 0 6px 6px 0; padding: 10px 14px; margin: 8px 0;
    font-size: 0.9rem;
}
.tx-box {
    background: #0d1f35; border-left: 3px solid #22c55e;
    border-radius: 0 6px 6px 0; padding: 10px 14px; margin: 8px 0;
    font-size: 0.9rem;
}
.tx-box-warn {
    background: #1f1505; border-left: 3px solid #f59e0b;
    border-radius: 0 6px 6px 0; padding: 10px 14px; margin: 8px 0;
    font-size: 0.9rem;
}
.tx-box-danger {
    background: #1f0505; border-left: 3px solid #ef4444;
    border-radius: 0 6px 6px 0; padding: 10px 14px; margin: 8px 0;
    font-size: 0.9rem;
}
.section-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.4rem; letter-spacing: 2px; color: #4da3ff;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 4px; margin-top: 1rem; margin-bottom: 0.5rem;
}
.tx-label {
    font-family: 'Bebas Neue'; font-size: 1.1rem; letter-spacing: 2px;
    color: #22c55e; margin-bottom: 4px;
}
.tx-label-warn { color: #f59e0b; }
.tx-label-danger { color: #ef4444; }
</style>
""", unsafe_allow_html=True)


# ── DB ──────────────────────────────────────────────────────
@st.cache_resource
def get_connection():
    try:
        return mysql.connector.connect(
            host='127.0.0.1', database='harborcore',
            user='root', password='eshaan1306', autocommit=False
        )
    except Error:
        return None
    

def get_conn():
    c = get_connection()
    if c is None or not c.is_connected():
        st.error("❌ Cannot connect to MySQL.")
        st.stop()
    return c

def run_query(sql, params=None):
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1', database='harborcore',
            user='root', password='eshaan1306', autocommit=True
        )
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    except Error as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()

def run_write(sql, params=None):
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1', database='harborcore',
            user='root', password='eshaan1306', autocommit=False
        )
        cur = conn.cursor()
        try:
            cur.execute(sql, params or ())
            conn.commit()
            return True, "OK"
        except Error as e:
            conn.rollback()
            return False, str(e)
        finally:
            cur.close() 
            conn.close()
    except Error as e:
        return False, f"Connection failed: {e}"

def run_transaction(statements):
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1', database='harborcore',
            user='root', password='eshaan1306', autocommit=False
        )
        cur = conn.cursor()
        try:
            conn.start_transaction()
            total_rows = 0
            for sql, params in statements:
                cur.execute(sql, params or ())
                total_rows += cur.rowcount
            conn.commit()
            return True, total_rows
        except Error as e:
            try:
                conn.rollback()
            except:
                pass
            return False, str(e)
        finally:
            cur.close()
            conn.close()  # always close fresh connections
    except Error as e:
        return False, f"Connection failed: {e}"

def get_options(sql):
    df = run_query(sql)
    if df.empty:
        return []
    return df.iloc[:, 0].tolist()


# ── SIDEBAR ─────────────────────────────────────────────────
st.sidebar.markdown("## ⚓ harborcore")
st.sidebar.markdown("**Port Management · Tasks 5 & 6**")
st.sidebar.markdown("---")

page = st.sidebar.radio("Go to", [
    "🏠 Dashboard",
    "⚙️ Feature 1 — Log Equipment Hours",
    "🚢 Feature 2 — Schedule a Voyage",
    "🛳️ Vessels & Voyages",
    "📦 Container & Customs",
    "🪝 Berth Management",
    "💰 Invoices & Billing",
    "👤 Agents & Officers",
    "🔁 Task 6 — Transactions",
], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Triggers (Task 5)**

**F1 — Equipment**
`before_equip_usage_insert`  
`after_equip_usage_insert`

**F2 — Voyage**
`before_voyage_insert`  
`after_voyage_insert`
""")
st.sidebar.caption("harborcore · DBMS Tasks 5 & 6")


# ══════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.markdown("# ⚓ harborcore PORT MANAGEMENT")
    st.markdown("---")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Vessels",
              run_query("SELECT COUNT(*) AS c FROM vessel").iloc[0]['c'])
    c2.metric("Vessels at Port",
              run_query("SELECT COUNT(*) AS c FROM voyage WHERE departure_date IS NULL").iloc[0]['c'])
    c3.metric("Equipment Needing Service",
              run_query("SELECT COUNT(*) AS c FROM equipment WHERE status='Needs_Service'").iloc[0]['c'])
    c4.metric("Available Berths",
              run_query("SELECT COUNT(*) AS c FROM berth WHERE status='Available'").iloc[0]['c'])
    c5.metric("Containers On Hold",
              run_query("SELECT COUNT(*) AS c FROM container WHERE status='Held'").iloc[0]['c'])

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⚙️ Equipment Status")
        df = run_query("SELECT equip_id, type, engine_hours, status FROM equipment ORDER BY engine_hours DESC")
        if not df.empty:
            def color_eq(val):
                return 'color: #f87171' if val == 'Needs_Service' else 'color: #4ade80'
            st.dataframe(df.style.applymap(color_eq, subset=['status']),
                         use_container_width=True, hide_index=True)

    with col2:
        st.markdown("### 🪝 Berth Status")
        df = run_query("SELECT berth_id, length_cap, status FROM berth ORDER BY berth_id")
        if not df.empty:
            def color_berth(val):
                c = {'Available':'color:#4ade80','Occupied':'color:#fb923c',
                     'Maintenance':'color:#f87171','Weather_Closed':'color:#facc15'}
                return c.get(val, '')
            st.dataframe(df.style.applymap(color_berth, subset=['status']),
                         use_container_width=True, hide_index=True)

    st.markdown('<div class="section-header">VESSELS CURRENTLY AT PORT</div>', unsafe_allow_html=True)
    df = run_query("""
        SELECT v.name AS vessel_name, v.imo_number, v.type,
               voy.voyage_no, voy.arrival_date, voy.berth_id
        FROM vessel v
        JOIN voyage voy ON v.imo_number = voy.imo_number
        WHERE voy.departure_date IS NULL
        ORDER BY voy.arrival_date
    """)
    if df.empty:
        st.info("No vessels currently at port.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
#  FEATURE 1 — LOG EQUIPMENT HOURS
# ══════════════════════════════════════════════════════════════
elif page == "⚙️ Feature 1 — Log Equipment Hours":
    st.markdown("# ⚙️ FEATURE 1 — LOG EQUIPMENT HOURS")
    st.markdown("---")

    st.markdown("""
<div class="info-box">
<strong>Trigger 1 — before_equip_usage_insert (BEFORE INSERT)</strong><br>
Blocks the insert if equipment status is already <code>Needs_Service</code>.
<br><br>
<strong>Trigger 2 — after_equip_usage_insert (AFTER INSERT)</strong><br>
Adds the logged hours to <code>engine_hours</code>. If the total hits 500h or more, auto-flags the equipment as <code>Needs_Service</code>.
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Current Equipment")
    eq_df = run_query("SELECT equip_id, type, engine_hours, status FROM equipment ORDER BY engine_hours DESC")
    if not eq_df.empty:
        def color_status(val):
            return 'color: #f87171' if val == 'Needs_Service' else 'color: #4ade80'
        st.dataframe(eq_df.style.applymap(color_status, subset=['status']),
                     use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Log Hours")

    voy_df = run_query("""
        SELECT v.name, voy.imo_number, voy.voyage_no
        FROM voyage voy JOIN vessel v ON voy.imo_number = v.imo_number
        WHERE voy.departure_date IS NULL
    """)

    if voy_df.empty:
        st.warning("No active voyages at port.")
    else:
        voy_opts   = [f"{r['name']} — VOY {r['voyage_no']}" for _, r in voy_df.iterrows()]
        equip_opts = [f"{r['equip_id']} ({r['type']}) — {r['engine_hours']}h [{r['status']}]"
                      for _, r in eq_df.iterrows()]

        with st.form("log_form"):
            sel_voy   = st.selectbox("Voyage", voy_opts)
            sel_equip = st.selectbox("Equipment", equip_opts)
            hours     = st.number_input("Hours Used", min_value=0.5, max_value=100.0, step=0.5, value=10.0)
            submitted = st.form_submit_button("Log Hours")

        if submitted:
            voy_row  = voy_df.iloc[voy_opts.index(sel_voy)]
            equip_id = sel_equip.split(" (")[0]
            eq_row   = eq_df[eq_df['equip_id'] == equip_id].iloc[0]
            old_h    = float(eq_row['engine_hours'])
            old_st   = eq_row['status']

            ok, msg = run_write(
                "INSERT INTO equipment_usage (imo_number, voyage_no, equip_id, hours_used) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE hours_used = hours_used + VALUES(hours_used)",
                (voy_row['imo_number'], int(voy_row['voyage_no']), equip_id, hours)
            )

            if ok:
                new_row = run_query(f"SELECT engine_hours, status FROM equipment WHERE equip_id='{equip_id}'").iloc[0]
                new_h   = float(new_row['engine_hours'])
                new_st  = new_row['status']

                st.success(f"✅ Logged {hours}h for {equip_id}.")
                c1, c2 = st.columns(2)
                c1.metric("Engine Hours", f"{new_h}h", delta=f"+{hours}h")
                c2.metric("Status", new_st, delta="⚠️ Auto-flagged by trigger" if new_st == 'Needs_Service' and old_st == 'Active' else "No change")

                if new_st == 'Needs_Service' and old_st == 'Active':
                    st.warning(f"⚠️ **Trigger fired:** {equip_id} crossed 500h and was automatically flagged as `Needs_Service`.")
            else:
                if "45000" in msg or "Needs_Service" in msg or "servicing" in msg.lower():
                    st.error(f"🚫 **Trigger blocked the insert:** {msg}")
                elif "Duplicate entry" in msg:
                    st.error("❌ Hours already logged for this equipment on this voyage.")
                else:
                    st.error(f"❌ {msg}")


# ══════════════════════════════════════════════════════════════
#  FEATURE 2 — SCHEDULE A VOYAGE
# ══════════════════════════════════════════════════════════════
elif page == "🚢 Feature 2 — Schedule a Voyage":
    st.markdown("# 🚢 FEATURE 2 — SCHEDULE A VOYAGE")
    st.markdown("---")

    st.markdown("""
<div class="info-box">
<strong>Trigger 3 — before_voyage_insert (BEFORE INSERT)</strong><br>
Blocks the insert if the selected berth is <code>Occupied</code>, <code>Maintenance</code>, or <code>Weather_Closed</code>.
<br><br>
<strong>Trigger 4 — after_voyage_insert (AFTER INSERT)</strong><br>
Once the voyage is inserted successfully, auto-sets the berth status to <code>Occupied</code>.
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Current Berths")
    berth_df = run_query("SELECT berth_id, length_cap, status FROM berth ORDER BY berth_id")
    if not berth_df.empty:
        def color_berth(val):
            c = {'Available':'color:#4ade80','Occupied':'color:#fb923c',
                 'Maintenance':'color:#f87171','Weather_Closed':'color:#facc15'}
            return c.get(val, '')
        st.dataframe(berth_df.style.applymap(color_berth, subset=['status']),
                     use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Schedule New Voyage")

    vessel_df = run_query("SELECT imo_number, name FROM vessel ORDER BY name")

    if vessel_df.empty:
        st.warning("No vessels registered.")
    else:
        v_map  = dict(zip(vessel_df['name'], vessel_df['imo_number']))
        b_opts = [f"{r['berth_id']} — {r['status']}" for _, r in berth_df.iterrows()]

        with st.form("voyage_form"):
            sel_vessel = st.selectbox("Vessel", list(v_map.keys()))
            voy_no = st.number_input("Voyage Number", min_value=1, step=1, value=1001)
            arrival = st.date_input("Arrival Date", value=date.today())
            sel_berth = st.selectbox("Berth", b_opts)
            submitted = st.form_submit_button("Schedule Voyage")

        if submitted:
            berth_id = sel_berth.split(" — ")[0]
            berth_status = berth_df[berth_df['berth_id'] == berth_id]['status'].values[0]

            ok, msg = run_write(
                "INSERT INTO voyage (imo_number, voyage_no, arrival_date, berth_id) VALUES (%s,%s,%s,%s)",
                (v_map[sel_vessel], voy_no, arrival, berth_id)
            )

            if ok:
                new_status = run_query(f"SELECT status FROM berth WHERE berth_id='{berth_id}'").iloc[0]['status']
                st.success(f"✅ Voyage {voy_no} scheduled for {sel_vessel} at Berth {berth_id}.")
                c1, c2 = st.columns(2)
                c1.metric("Berth Before", berth_status)
                c2.metric("Berth After",  new_status, delta="Auto-updated by trigger ✓")
            else:
                if "45000" in msg or "unavailable" in msg.lower():
                    st.error(f"🚫 **Trigger blocked the insert:** {msg}")
                elif "Duplicate entry" in msg:
                    st.error(f"❌ Voyage number {voy_no} already exists for this vessel.")
                else:
                    st.error(f"❌ {msg}")


# ══════════════════════════════════════════════════════════════
#  VESSELS & VOYAGES
# ══════════════════════════════════════════════════════════════
elif page == "🛳️ Vessels & Voyages":
    st.markdown("# 🛳️ VESSELS & VOYAGES")
    tab1, tab2, tab3 = st.tabs(["View All Vessels", "Voyage History", "Add New Vessel"])

    with tab1:
        st.markdown('<div class="section-header">ALL REGISTERED VESSELS</div>', unsafe_allow_html=True)
        df = run_query("""
            SELECT v.imo_number, v.name, v.type, v.draft, sa.name AS agent
            FROM vessel v
            JOIN shipping_agent sa ON v.agent_license_no = sa.license_no
            ORDER BY v.name
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown('<div class="section-header">FULL VOYAGE LOG</div>', unsafe_allow_html=True)
        df = run_query("""
            SELECT voy.imo_number, v.name AS vessel, voy.voyage_no,
                   voy.arrival_date, voy.departure_date, voy.berth_id,
                   CASE WHEN voy.departure_date IS NULL THEN 'At Port' ELSE 'Departed' END AS state,
                   DATEDIFF(IFNULL(voy.departure_date, CURDATE()), voy.arrival_date) AS days_in_port
            FROM voyage voy
            JOIN vessel v ON voy.imo_number = v.imo_number
            ORDER BY voy.arrival_date DESC
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown('<div class="section-header">REGISTER NEW VESSEL</div>', unsafe_allow_html=True)
        agents = run_query("SELECT license_no, name FROM shipping_agent ORDER BY name")
        agent_map = dict(zip(agents['name'], agents['license_no'])) if not agents.empty else {}

        with st.form("add_vessel"):
            c1, c2 = st.columns(2)
            imo = c1.text_input("IMO Number*", placeholder="IMO_XXXXXXX")
            name = c2.text_input("Vessel Name*")
            vtype = c1.selectbox("Type*", ["Container","Cargo","Bulk","Feeder","Tanker","RoRo"])
            draft = c2.number_input("Draft (m)*", min_value=1.0, max_value=25.0, value=12.0, step=0.1)
            agent_name = st.selectbox("Shipping Agent*", list(agent_map.keys()))
            sub = st.form_submit_button("Register Vessel")

        if sub:
            if not imo or not name:
                st.error("IMO Number and Vessel Name are required.")
            elif not imo.startswith("IMO_"):
                st.error("IMO Number must start with 'IMO_'")
            else:
                ok, msg = run_write(
                    "INSERT INTO vessel VALUES (%s, %s, %s, %s, %s)",
                    (imo, name, vtype, draft, agent_map[agent_name])
                )
                if ok:
                    st.success(f"✅ Vessel '{name}' registered successfully!")
                elif "Duplicate entry" in msg:
                    st.error(f"❌ IMO Number '{imo}' already exists.")
                else:
                    st.error(f"❌ {msg}")


# ══════════════════════════════════════════════════════════════
#  CONTAINERS & CUSTOMS
# ══════════════════════════════════════════════════════════════
elif page == "📦 Container & Customs":
    st.markdown("# 📦 CONTAINER & CUSTOMS TRACKING")
    tab1, tab2, tab3 = st.tabs(["All Containers", "Clear a Container", "HazMat Locator"])

    with tab1:
        st.markdown('<div class="section-header">FULL CONTAINER MANIFEST</div>', unsafe_allow_html=True)
        df = run_query("""
            SELECT c.container_id, c.type, c.status,
                   CONCAT(c.block,'-',c.row_num,'-',c.tier_num) AS yard_position,
                   c.imo_number, c.voyage_no, co.name AS cleared_by
            FROM container c
            LEFT JOIN customs_officer co ON c.cleared_by_id = co.badge_id
            ORDER BY c.status, c.container_id
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not df.empty:
            st.metric("Containers Currently Held", len(df[df['status'] == 'Held']))

    with tab2:
        st.markdown('<div class="section-header">CUSTOMS CLEARANCE</div>', unsafe_allow_html=True)
        held_ids = get_options("SELECT container_id FROM container WHERE status='Held' ORDER BY container_id")
        officers = run_query("SELECT badge_id, name, rank_title FROM customs_officer ORDER BY name")

        if not held_ids:
            st.success("✅ No containers currently on hold!")
        else:
            off_map = {f"{r['name']} ({r['rank_title']})": r['badge_id'] for _, r in officers.iterrows()}
            with st.form("clear_form"):
                c_id    = st.selectbox("Select Held Container*", held_ids)
                officer = st.selectbox("Clearing Officer*", list(off_map.keys()))
                sub = st.form_submit_button("Clear Container")
            if sub:
                ok, msg = run_write(
                    "UPDATE container SET status='Cleared', cleared_by_id=%s WHERE container_id=%s",
                    (off_map[officer], c_id)
                )
                if ok:
                    st.success(f"✅ Container {c_id} cleared.")
                else:
                    st.error(f"❌ {msg}")

    with tab3:
        st.markdown('<div class="section-header">HAZMAT CONTAINER LOCATOR</div>', unsafe_allow_html=True)
        df = run_query("SELECT container_id, block, row_num, tier_num, status FROM container WHERE type='HazMat' AND status='Held'")
        if df.empty:
            st.success("No HazMat containers currently held.")
        else:
            st.warning("⚠️ HazMat containers currently on hold:")
            st.dataframe(df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
#  BERTH MANAGEMENT
# ══════════════════════════════════════════════════════════════
elif page == "🪝 Berth Management":
    st.markdown("# 🪝 BERTH MANAGEMENT")
    tab1, tab2 = st.tabs(["Berth Overview", "Update Berth Status"])

    with tab1:
        st.markdown('<div class="section-header">BERTH OCCUPANCY MAP</div>', unsafe_allow_html=True)
        df = run_query("""
            SELECT b.berth_id, b.length_cap, b.status,
                   v.name AS vessel_at_berth, voy.arrival_date
            FROM berth b
            LEFT JOIN voyage voy ON b.berth_id = voy.berth_id AND voy.departure_date IS NULL
            LEFT JOIN vessel v ON voy.imo_number = v.imo_number
            ORDER BY b.berth_id
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not df.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Available", len(df[df['status']=='Available']))
            c2.metric("Occupied", len(df[df['status']=='Occupied']))
            c3.metric("Maintenance", len(df[df['status']=='Maintenance']))
            c4.metric("Weather Closed", len(df[df['status']=='Weather_Closed']))

    with tab2:
        st.markdown('<div class="section-header">UPDATE BERTH STATUS</div>', unsafe_allow_html=True)
        with st.form("berth_status_form"):
            berth_id = st.selectbox("Berth*", get_options("SELECT berth_id FROM berth ORDER BY berth_id"))
            new_status = st.selectbox("New Status*", ["Available","Occupied","Maintenance","Weather_Closed"])
            sub = st.form_submit_button("Update Status")
        if sub:
            ok, msg = run_write("UPDATE berth SET status=%s WHERE berth_id=%s", (new_status, berth_id))
            if ok:
                st.success(f"✅ Berth {berth_id} updated to {new_status}.")
            else:
                st.error(f"❌ {msg}")


# ══════════════════════════════════════════════════════════════
#  INVOICES & BILLING
# ══════════════════════════════════════════════════════════════
elif page == "💰 Invoices & Billing":
    st.markdown("# 💰 INVOICES & BILLING")
    tab1, tab2, tab3 = st.tabs(["All Invoices", "Add Invoice", "Apply Overdue Penalty"])

    with tab1:
        st.markdown('<div class="section-header">INVOICE REGISTER</div>', unsafe_allow_html=True)
        df = run_query("""
            SELECT i.invoice_id, sa.name AS agent, i.amount, i.payment_status, i.inv_date
            FROM invoice i
            JOIN shipping_agent sa ON i.agent_license_no = sa.license_no
            ORDER BY i.inv_date DESC
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Invoiced", f"₹ {float(df['amount'].sum()):,.2f}")
            c2.metric("Overdue Amount", f"₹ {float(df[df['payment_status']=='Overdue']['amount'].sum()):,.2f}")
            c3.metric("Pending Count", len(df[df['payment_status']=='Pending']))

    with tab2:
        st.markdown('<div class="section-header">CREATE NEW INVOICE</div>', unsafe_allow_html=True)
        agents = run_query("SELECT license_no, name FROM shipping_agent ORDER BY name")
        a_map  = dict(zip(agents['name'], agents['license_no'])) if not agents.empty else {}

        with st.form("inv_form"):
            c1, c2 = st.columns(2)
            inv_id = c1.text_input("Invoice ID*", placeholder="INV_XXX")
            amount = c2.number_input("Amount (₹)*", min_value=0.01, value=10000.0, step=100.0)
            status = c1.selectbox("Payment Status*", ["Pending","Paid","Overdue"])
            inv_date = c2.date_input("Invoice Date*", value=date.today())
            agent = st.selectbox("Shipping Agent*", list(a_map.keys()))
            sub = st.form_submit_button("Create Invoice")

        if sub:
            if not inv_id:
                st.error("Invoice ID is required.")
            else:
                ok, msg = run_write(
                    "INSERT INTO invoice VALUES (%s, %s, %s, %s, %s)",
                    (inv_id, amount, status, inv_date, a_map[agent])
                )
                if ok:
                    st.success(f"✅ Invoice {inv_id} created for ₹{amount:,.2f}.")
                elif "Duplicate entry" in msg:
                    st.error(f"❌ Invoice ID '{inv_id}' already exists.")
                else:
                    st.error(f"❌ {msg}")

    with tab3:
        st.markdown('<div class="section-header">APPLY 10% LATE PENALTY TO OVERDUE INVOICES</div>', unsafe_allow_html=True)
        overdue_df = run_query("""
            SELECT i.invoice_id, sa.name AS agent, i.amount, i.inv_date
            FROM invoice i
            JOIN shipping_agent sa ON i.agent_license_no = sa.license_no
            WHERE i.payment_status = 'Overdue'
        """)
        if overdue_df.empty:
            st.success("No overdue invoices currently.")
        else:
            st.dataframe(overdue_df, use_container_width=True, hide_index=True)
            if st.button("Apply 10% Penalty to All Overdue"):
                ok, msg = run_write("UPDATE invoice SET amount = amount * 1.10 WHERE payment_status = 'Overdue'")
                if ok:
                    st.success("✅ 10% penalty applied to all overdue invoices.")
                else:
                    st.error(f"❌ {msg}")


# ══════════════════════════════════════════════════════════════
#  AGENTS & OFFICERS
# ══════════════════════════════════════════════════════════════
elif page == "👤 Agents & Officers":
    st.markdown("# 👤 AGENTS & OFFICERS")
    tab1, tab2 = st.tabs(["Shipping Agents", "Customs Officers"])

    with tab1:
        st.markdown('<div class="section-header">REGISTERED SHIPPING AGENTS</div>', unsafe_allow_html=True)
        df = run_query("""
            SELECT sa.license_no, sa.name, sa.contact_email,
                   COUNT(DISTINCT v.imo_number) AS vessels_managed,
                   COUNT(DISTINCT i.invoice_id) AS total_invoices
            FROM shipping_agent sa
            LEFT JOIN vessel v  ON sa.license_no = v.agent_license_no
            LEFT JOIN invoice i ON sa.license_no = i.agent_license_no
            GROUP BY sa.license_no, sa.name, sa.contact_email
            ORDER BY vessels_managed DESC
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown('<div class="section-header">CUSTOMS OFFICERS</div>', unsafe_allow_html=True)
        df = run_query("""
            SELECT co.badge_id, co.name, co.rank_title,
                   COUNT(c.container_id) AS containers_cleared
            FROM customs_officer co
            LEFT JOIN container c ON co.badge_id = c.cleared_by_id AND c.status='Cleared'
            GROUP BY co.badge_id, co.name, co.rank_title
            ORDER BY containers_cleared DESC
        """)
        st.dataframe(df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
#  TASK 6 — TRANSACTIONS
# ══════════════════════════════════════════════════════════════
elif page == "🔁 Task 6 — Transactions":
    st.markdown("# 🔁 TASK 6 — DATABASE TRANSACTIONS")
    st.markdown("Each demo below runs a real transaction on the live database and shows the before/after state.")
    st.markdown("---")

    tabs = st.tabs([
        "T1 · Vessel Arrival",
        "T2 · Invoice Payment",
        "T3 · Batch Clearance",
        "T4 · Berth Conflict",
        "T5 · Lost Update Fix",
    ])

    # ── T1: VESSEL ARRIVAL ──────────────────────────────────
    with tabs[0]:
        st.markdown('<div class="section-header">T1 — VESSEL ARRIVAL (COMMIT)</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="tx-box">
<strong>Scenario:</strong> A new vessel arrives and must be assigned to a berth atomically.<br>
Both the voyage record and the berth status update happen inside one transaction — if either fails, neither is saved.
</div>
""", unsafe_allow_html=True)

        vessel_df = run_query("SELECT imo_number, name FROM vessel ORDER BY name")
        avail_berths = run_query("SELECT berth_id FROM berth WHERE status='Available' ORDER BY berth_id")

        if vessel_df.empty or avail_berths.empty:
            st.warning("No available berths or vessels right now.")
        else:
            v_map = dict(zip(vessel_df['name'], vessel_df['imo_number']))
            with st.form("t1_form"):
                col1, col2 = st.columns(2)
                sel_v = col1.selectbox("Vessel", list(v_map.keys()))
                sel_b = col2.selectbox("Available Berth", avail_berths['berth_id'].tolist())
                voy_num = col1.number_input("Voyage No", min_value=2000, max_value=9999, value=2001, step=1)
                arr = col2.date_input("Arrival Date", value=date.today())
                go = st.form_submit_button("▶️ Execute Transaction")

            if go:
                pre_berth = run_query(f"SELECT status FROM berth WHERE berth_id='{sel_b}'")
                pre_status = pre_berth.iloc[0]['status'] if not pre_berth.empty else "Unknown"

                ok, result = run_transaction([
                    ("INSERT INTO voyage (imo_number, voyage_no, arrival_date, berth_id) VALUES (%s,%s,%s,%s)",
                    (v_map[sel_v], voy_num, arr, sel_b)),
                    ("UPDATE berth SET status='Occupied' WHERE berth_id=%s", (sel_b,)),
                ])

                if ok:
                    post_status = run_query(f"SELECT status FROM berth WHERE berth_id='{sel_b}'").iloc[0]['status']
                    st.success("✅ COMMIT — Transaction succeeded.")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Berth Before", pre_status)
                    c2.metric("Berth After", post_status, delta="Occupied ✓")
                    c3.metric("Voyage Inserted", f"VOY {voy_num}")
                    st.info("Both INSERT and UPDATE committed atomically in one transaction.")

                    # Store cleanup state in session state — only clean up when user clicks
                    st.session_state['t1_cleanup'] = (voy_num, v_map[sel_v], sel_b)
                    st.warning("⚠️ DB is in modified state. Click below to restore for re-runs.")
                    st.rerun()

                else:
                    st.error(f"❌ ROLLBACK — {result}")

            # cleanup button outside the form
            if 't1_cleanup' in st.session_state:
                if st.button("🔄 Restore DB (cleanup for re-run)", key="t1_cleanup_btn"):
                    vno_c, imo_c, b_c = st.session_state['t1_cleanup']
                    run_write("DELETE FROM voyage WHERE voyage_no=%s AND imo_number=%s", (vno_c, imo_c))
                    run_write("UPDATE berth SET status='Available' WHERE berth_id=%s", (b_c,))
                    del st.session_state['t1_cleanup']
                    st.success("🔄 DB restored.")
                    st.rerun()

    # ── T2: INVOICE PAYMENT ─────────────────────────────────
    with tabs[1]:
        st.markdown('<div class="section-header">T2 — INVOICE PAYMENT + PENALTY (COMMIT)</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="tx-box">
<strong>Scenario:</strong> An overdue invoice is being settled. The 10% late penalty is applied AND the status is changed to Paid — both happen atomically. If the payment system crashes mid-way, neither change persists.
</div>
""", unsafe_allow_html=True)

        overdue_df = run_query("""
            SELECT i.invoice_id, sa.name AS agent, i.amount, i.payment_status
            FROM invoice i JOIN shipping_agent sa ON i.agent_license_no = sa.license_no
            WHERE i.payment_status = 'Overdue'
        """)

        if overdue_df.empty:
            st.info("No overdue invoices currently. Reset data or mark one Overdue from the Billing page.")
        else:
            st.markdown("**Overdue Invoices (Pre-Transaction)**")
            st.dataframe(overdue_df, use_container_width=True, hide_index=True)

            inv_opts = overdue_df['invoice_id'].tolist()
            with st.form("t2_form"):
                sel_inv = st.selectbox("Invoice to Settle", inv_opts)
                go = st.form_submit_button("▶️ Apply Penalty & Mark Paid")

            if go:
                pre = run_query(f"SELECT amount, payment_status FROM invoice WHERE invoice_id='{sel_inv}'").iloc[0]

                ok, result = run_transaction([
                    ("UPDATE invoice SET amount = amount * 1.10 WHERE invoice_id=%s AND payment_status='Overdue'", (sel_inv,)),
                    ("UPDATE invoice SET payment_status='Paid' WHERE invoice_id=%s", (sel_inv,)),
                ])

                if ok:
                    post = run_query(f"SELECT amount, payment_status FROM invoice WHERE invoice_id='{sel_inv}'").iloc[0]
                    st.success("✅ COMMIT — Invoice settled.")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Amount Before", f"₹{float(pre['amount']):,.2f}")
                    c2.metric("Amount After (+ 10% penalty)", f"₹{float(post['amount']):,.2f}",
                              delta=f"+₹{float(post['amount'])-float(pre['amount']):,.2f}")
                    c3.metric("Status", post['payment_status'], delta="Paid ✓")
                else:
                    st.error(f"❌ ROLLBACK — {result}")

    # ── T3: BATCH CLEARANCE ─────────────────────────────────
    with tabs[2]:
        st.markdown('<div class="section-header">T3 — BATCH CONTAINER CLEARANCE (COMMIT)</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="tx-box">
<strong>Scenario:</strong> A customs officer clears all containers from a specific voyage in one atomic batch. Either all containers are cleared, or none are — partial clearance is not allowed.
</div>
""", unsafe_allow_html=True)

        voy_df = run_query("""
            SELECT CONCAT(v.name, ' — VOY ', voy.voyage_no) AS label,
                   voy.imo_number, voy.voyage_no
            FROM voyage voy JOIN vessel v ON voy.imo_number = v.imo_number
        """)
        officers = run_query("SELECT badge_id, name FROM customs_officer ORDER BY name")

        if voy_df.empty:
            st.warning("No voyages found.")
        else:
            voy_map = {r['label']: (r['imo_number'], r['voyage_no']) for _, r in voy_df.iterrows()}
            off_map = dict(zip(officers['name'], officers['badge_id'])) if not officers.empty else {}

            with st.form("t3_form"):
                sel_voy = st.selectbox("Voyage", list(voy_map.keys()))
                sel_off = st.selectbox("Clearing Officer", list(off_map.keys()))
                go = st.form_submit_button("▶️ Clear All Held Containers")

            if go:
                imo, vno = voy_map[sel_voy]
                pre_df = run_query(f"""
                    SELECT container_id, status FROM container
                    WHERE imo_number='{imo}' AND voyage_no={vno} AND status='Held'
                """)

                if pre_df.empty:
                    st.info("No held containers on this voyage.")
                else:
                    st.markdown(f"**{len(pre_df)} containers to clear:**")
                    st.dataframe(pre_df, use_container_width=True, hide_index=True)

                    stmts = [
                        ("UPDATE container SET status='Cleared', cleared_by_id=%s WHERE imo_number=%s AND voyage_no=%s AND status='Held'",
                         (off_map[sel_off], imo, vno))
                    ]
                    ok, result = run_transaction(stmts)

                    if ok:
                        post_df = run_query(f"""
                            SELECT container_id, status, cleared_by_id FROM container
                            WHERE imo_number='{imo}' AND voyage_no={vno}
                        """)
                        st.success(f"✅ COMMIT — {len(pre_df)} containers cleared atomically.")
                        st.dataframe(post_df, use_container_width=True, hide_index=True)
                    else:
                        st.error(f"❌ ROLLBACK — {result}")

    # ── T4: BERTH DOUBLE-BOOKING ─────────────────────────────────
    with tabs[3]:
        st.markdown('<div class="section-header">T4 — BERTH DOUBLE-BOOKING CONFLICT (ROLLBACK)</div>', unsafe_allow_html=True)
        st.markdown("""
    <div class="tx-box-warn">
    <strong>Scenario:</strong> Two agents try to book the same berth simultaneously.<br>
    <strong>Session A</strong> commits first — berth becomes Occupied.<br>
    <strong>Session B</strong> attempts the same berth — the <code>before_voyage_insert</code> trigger detects it's now Occupied and fires a SIGNAL, causing Session B's INSERT to fail and the transaction to ROLLBACK.
    </div>
    """, unsafe_allow_html=True)

        avail_berths2 = run_query("SELECT berth_id FROM berth WHERE status='Available' ORDER BY berth_id")
        vessel_df2 = run_query("SELECT imo_number, name FROM vessel ORDER BY name")

        if avail_berths2.empty or vessel_df2.empty:
            st.warning("Need at least one available berth and two vessels.")
        else:
            v_list = vessel_df2['name'].tolist()
            b_list = avail_berths2['berth_id'].tolist()

            with st.form("t4_form"):
                col1, col2 = st.columns(2)
                b_sel  = col1.selectbox("Berth (both agents want this)", b_list)
                v_a = col1.selectbox("Session A Vessel", v_list, index=0)
                v_b = col2.selectbox("Session B Vessel", v_list, index=min(1, len(v_list)-1))
                vno_a = col1.number_input("Session A Voyage No", min_value=3000, max_value=3999, value=3001)
                vno_b = col2.number_input("Session B Voyage No", min_value=4000, max_value=4999, value=4001)
                go = st.form_submit_button("▶️ Simulate Double-Booking")

            if go:
                v_map2 = dict(zip(vessel_df2['name'], vessel_df2['imo_number']))

                pre_status = run_query(f"SELECT status FROM berth WHERE berth_id='{b_sel}'").iloc[0]['status']

                # ── SESSION A: Insert voyage + mark berth Occupied ──
                ok_a, res_a = run_transaction([
                    ("INSERT INTO voyage (imo_number, voyage_no, arrival_date, berth_id) VALUES (%s,%s,%s,%s)",
                    (v_map2[v_a], vno_a, date.today(), b_sel)),
                    ("UPDATE berth SET status='Occupied' WHERE berth_id=%s", (b_sel,)),
                ])

                mid_status = run_query(f"SELECT status FROM berth WHERE berth_id='{b_sel}'").iloc[0]['status']

                # ── SESSION B: Also tries to INSERT into same berth ──
                # The before_voyage_insert trigger will now fire because berth is Occupied
                ok_b, res_b = run_transaction([
                    ("INSERT INTO voyage (imo_number, voyage_no, arrival_date, berth_id) VALUES (%s,%s,%s,%s)",
                    (v_map2[v_b], vno_b, date.today(), b_sel)),
                ])

                final_status = run_query(f"SELECT status FROM berth WHERE berth_id='{b_sel}'").iloc[0]['status']

                # ── Results ──
                st.markdown("### Results")
                c1, c2, c3 = st.columns(3)
                c1.metric("Berth Before", pre_status)
                c2.metric("After Session A", mid_status, delta="Occupied ✓" if mid_status == "Occupied" else "")
                c3.metric("After Session B", final_status)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Session A**")
                    if ok_a:
                        st.success(f"✅ COMMIT — Voyage {vno_a} booked, berth set Occupied.")
                    else:
                        st.error(f"❌ ROLLBACK — {res_a}")
                with col2:
                    st.markdown("**Session B**")
                    if ok_b:
                        st.warning("⚠️ Committed (unexpected — trigger may not have fired)")
                    else:
                        st.error(f"🚫 ROLLBACK — Trigger blocked: {res_b}")

                # Show what's in the voyage table now
                voyages_at_berth = run_query(f"""
                    SELECT voy.voyage_no, v.name AS vessel, voy.arrival_date, voy.berth_id
                    FROM voyage voy JOIN vessel v ON voy.imo_number = v.imo_number
                    WHERE voy.berth_id = '{b_sel}' AND voy.departure_date IS NULL
                """)
                st.markdown(f"**Voyages currently at Berth {b_sel}:**")
                st.dataframe(voyages_at_berth, use_container_width=True, hide_index=True)
                st.info("Only Session A's voyage appears — Session B was blocked by the trigger.")

                # Store cleanup in session state so user can see the state first
                st.session_state['t4_cleanup'] = (vno_a, v_map2[v_a], b_sel)
                st.warning("⚠️ DB is in modified state. Session A's voyage is live. Click below to restore.")
                st.rerun()

        # Cleanup button outside form
        if 't4_cleanup' in st.session_state:
            if st.button("🔄 Restore DB (cleanup for re-run)", key="t4_cleanup_btn"):
                vno_c, imo_c, b_c = st.session_state['t4_cleanup']
                run_write("DELETE FROM voyage WHERE voyage_no=%s AND imo_number=%s", (vno_c, imo_c))
                run_write("UPDATE berth SET status='Available' WHERE berth_id=%s", (b_c,))
                del st.session_state['t4_cleanup']
                st.success("🔄 DB restored — berth is Available again.")
                st.rerun()

    # ── T5: LOST UPDATE FIX ──────────────────────────────────────
    with tabs[4]:
        st.markdown('<div class="section-header">T5 — LOST UPDATE PROBLEM & FIX</div>', unsafe_allow_html=True)
        st.markdown("""
    <div class="tx-box-warn">
    <strong>Scenario:</strong> Two billing clerks both read the same invoice amount and try to add charges to it.<br>
    Without locking, one clerk's update overwrites the other's — a "lost update".<br>
    With <code>SELECT ... FOR UPDATE</code>, the second clerk waits until the first commits, then reads the correct updated value.
    </div>
    """, unsafe_allow_html=True)

        pending_inv = run_query("""
            SELECT i.invoice_id, sa.name AS agent, i.amount
            FROM invoice i JOIN shipping_agent sa ON i.agent_license_no = sa.license_no
            WHERE i.payment_status = 'Pending' LIMIT 5
        """)
        st.dataframe(pending_inv, use_container_width=True, hide_index=True)

        inv_opts5 = pending_inv['invoice_id'].tolist() if not pending_inv.empty else []

        with st.form("t5_form"):
            sel_inv5 = st.selectbox("Select Invoice", inv_opts5) if inv_opts5 else st.text_input("Invoice ID")
            add_a = st.number_input("Clerk A adds (₹)", min_value=100.0, value=5000.0, step=100.0)
            add_b = st.number_input("Clerk B adds (₹)", min_value=100.0, value=2000.0, step=100.0)
            go = st.form_submit_button("▶️ Demonstrate Lost Update → Fix")

        if go and sel_inv5:
            import mysql.connector as _mc

            DB = dict(host='127.0.0.1', database='harborcore', user='root', password='eshaan1306')
            original = float(run_query(f"SELECT amount FROM invoice WHERE invoice_id='{sel_inv5}'").iloc[0]['amount'])

            # ── PART 1: LOST UPDATE (no locking) ──────────────────
            # Both clerks read original simultaneously, each adds their own amount,
            # last writer wins — Clerk A's addition is silently lost.

            # Reset to original first
            run_write("UPDATE invoice SET amount=%s WHERE invoice_id=%s", (original, sel_inv5))

            # Clerk A reads original, adds add_a
            ca = _mc.connect(**DB, autocommit=False)
            cur_a = ca.cursor()
            ca.start_transaction()
            cur_a.execute("SELECT amount FROM invoice WHERE invoice_id=%s", (sel_inv5,))
            read_a = float(cur_a.fetchone()[0]) # reads original
            cur_a.execute("UPDATE invoice SET amount=%s WHERE invoice_id=%s", (read_a + add_a, sel_inv5))
            ca.commit()
            cur_a.close(); ca.close()

            after_a = float(run_query(f"SELECT amount FROM invoice WHERE invoice_id='{sel_inv5}'").iloc[0]['amount'])

            # Clerk B also read original (before A committed), adds add_b — overwrites A
            cb = _mc.connect(**DB, autocommit=False)
            cur_b = cb.cursor()
            cb.start_transaction()
            cur_b.execute("UPDATE invoice SET amount=%s WHERE invoice_id=%s", (original + add_b, sel_inv5))
            cb.commit()
            cur_b.close(); cb.close()

            after_lost = float(run_query(f"SELECT amount FROM invoice WHERE invoice_id='{sel_inv5}'").iloc[0]['amount'])

            st.markdown("#### ❌ Without Locking — Lost Update")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Original", f"₹{original:,.2f}")
            c2.metric("After Clerk A", f"₹{after_a:,.2f}",    delta=f"+₹{add_a:,.0f}")
            c3.metric("After Clerk B (overwrites A)", f"₹{after_lost:,.2f}", delta=f"Clerk A's +₹{add_a:,.0f} LOST!")
            c4.metric("Expected (correct)", f"₹{original+add_a+add_b:,.2f}")
            st.error(f"Clerk A's ₹{add_a:,.0f} addition was silently overwritten — lost update!")

            # ── Reset to original before fix demo ─────────────────
            run_write("UPDATE invoice SET amount=%s WHERE invoice_id=%s", (original, sel_inv5))

            # ── PART 2: FIX with SELECT ... FOR UPDATE ─────────────
            # Clerk A locks the row, reads it, updates it, commits.
            # Clerk B must wait — then reads A's committed value and adds on top.

            ca2 = _mc.connect(**DB, autocommit=False)
            cur_a2 = ca2.cursor()
            ca2.start_transaction()
            cur_a2.execute("SELECT amount FROM invoice WHERE invoice_id=%s FOR UPDATE", (sel_inv5,))
            locked_val = float(cur_a2.fetchone()[0])     # locks the row
            cur_a2.execute("UPDATE invoice SET amount=%s WHERE invoice_id=%s", (locked_val + add_a, sel_inv5))

            ca2.commit() \ # releases lock
            cur_a2.close(); ca2.close()

            after_a_fix = float(run_query(f"SELECT amount FROM invoice WHERE invoice_id='{sel_inv5}'").iloc[0]['amount'])

            # Clerk B now runs — row is unlocked, reads A's committed value
            cb2 = _mc.connect(**DB, autocommit=False)
            cur_b2 = cb2.cursor()
            cb2.start_transaction()
            cur_b2.execute("SELECT amount FROM invoice WHERE invoice_id=%s FOR UPDATE", (sel_inv5,))
            locked_val_b = float(cur_b2.fetchone()[0])   # reads original + add_a
            cur_b2.execute("UPDATE invoice SET amount=%s WHERE invoice_id=%s", (locked_val_b + add_b, sel_inv5))
            cb2.commit()
            cur_b2.close(); cb2.close()

            final_correct = float(run_query(f"SELECT amount FROM invoice WHERE invoice_id='{sel_inv5}'").iloc[0]['amount'])

            st.markdown("#### ✅ With SELECT ... FOR UPDATE — Correct Result")
            c1, c2, c3 = st.columns(3)
            c1.metric("Original", f"₹{original:,.2f}")
            c2.metric("After Clerk A + B", f"₹{final_correct:,.2f}", delta=f"+₹{add_a+add_b:,.0f} ✓")
            c3.metric("Expected", f"₹{original+add_a+add_b:,.2f}")
            st.success("Both additions preserved. FOR UPDATE forced Clerk B to wait for A's commit before reading.")

            live = run_query(f"""
                SELECT i.invoice_id, sa.name AS agent, i.amount, i.payment_status
                FROM invoice i JOIN shipping_agent sa ON i.agent_license_no = sa.license_no
                WHERE i.invoice_id = '{sel_inv5}'
            """)
            st.markdown("**Live DB state (also reflected in Invoices & Billing):**")
            st.dataframe(live, use_container_width=True, hide_index=True)

            st.session_state['t5_cleanup'] = (sel_inv5, original)
            st.warning(f"⚠️ Invoice {sel_inv5} now shows ₹{final_correct:,.2f} in Invoices & Billing. Click below to restore.")
            st.rerun()

        if 't5_cleanup' in st.session_state:
            inv_id_c, orig_c = st.session_state['t5_cleanup']
            if st.button("🔄 Restore Invoice Amount", key="t5_cleanup_btn"):
                run_write("UPDATE invoice SET amount=%s WHERE invoice_id=%s", (orig_c, inv_id_c))
                del st.session_state['t5_cleanup']
                st.success("🔄 Invoice amount restored.")
                st.rerun()
