# ⚓ harborcore — Port Management System

A full-stack database management system that simulates a real-world seaport management platform — tracking vessels, voyages, berths, containers, equipment, customs officers, shipping agents, and invoices, all backed by a live MySQL database with triggers and ACID transactions.

---

## 📸 Features at a Glance

| Module | What it does |
|---|---|
| 🏠 Dashboard | Live port KPIs — vessels at port, equipment health, berth status |
| ⚙️ Log Equipment Hours | Trigger-backed hour logging with auto service-flagging |
| 🚢 Schedule a Voyage | Trigger-guarded berth assignment with auto status updates |
| 🛳️ Vessels & Voyages | Register vessels, view voyage history and turnaround stats |
| 📦 Container & Customs | Full manifest, clearance workflow, HazMat locator |
| 🪝 Berth Management | Occupancy map and manual status control |
| 💰 Invoices & Billing | Invoice register, creation, overdue penalty application |
| 👤 Agents & Officers | Agent vessel portfolios, officer clearance logs |
| 🔁 Transactions | 5 live transaction demos: commit, rollback, lost update fix |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend / UI** | [Streamlit](https://streamlit.io) — Python-native web framework |
| **Database** | [MySQL 8.x](https://dev.mysql.com/) — relational database with InnoDB engine |
| **DB Driver** | `mysql-connector-python` — official MySQL Python connector |
| **Data Handling** | `pandas` — DataFrame display and in-memory transformations |
| **Styling** | Custom CSS injected via `st.markdown` — Bebas Neue + Source Sans 3 (Google Fonts) |
| **Language** | Python 3.10+ |

---

## 🗄️ Database Schema

```
shipping_agent  ←──── vessel ────→ voyage ────→ equipment_usage
                                      │                │
                                  container       equipment
                                      │
                               customs_officer

invoice ────→ shipping_agent
```

**9 tables** with full referential integrity, `CHECK` constraints, cascading deletes, and 5 performance indexes.

### Key Design Decisions
- `voyage` uses a composite primary key `(imo_number, voyage_no)` to allow multiple voyages per vessel
- `container` has a `UNIQUE (block, row_num, tier_num)` constraint enforcing physical yard uniqueness
- `equipment_usage` is the junction table between voyages and equipment, tracking hours per trip

---

## ⚡ Triggers

Four triggers (plus one bonus) enforce business rules automatically at the database level:

### `before_equip_usage_insert` — BEFORE INSERT
Raises `SQLSTATE 45000` if the target equipment's status is `Needs_Service`. Prevents broken equipment from being logged as active.

### `after_equip_usage_insert` — AFTER INSERT
Adds `hours_used` to the equipment's cumulative `engine_hours`. If the total reaches **500 hours**, automatically flips status to `Needs_Service`.

### `before_voyage_insert` — BEFORE INSERT
Raises `SQLSTATE 45000` if the target berth is `Occupied`, `Maintenance`, or `Weather_Closed`. Acts as the database-level gate against double-booking.

### `after_voyage_insert` — AFTER INSERT
After a voyage is successfully inserted, sets the assigned berth's status to `Occupied`. Ensures berth state always reflects reality without needing application-level follow-up queries.

### `after_equip_usage_update` *(bonus)* — AFTER UPDATE
Keeps `engine_hours` in sync if an existing usage record is edited — adjusts by the delta `(NEW.hours_used - OLD.hours_used)`.

---

## 🔁 Transactions 

Five transaction scenarios are demonstrated live in the UI, each showing real before/after database state:

| # | Scenario | Outcome |
|---|---|---|
| T1 | Vessel arrival — voyage INSERT + berth UPDATE atomically | COMMIT |
| T2 | Overdue invoice settlement — penalty + status change atomically | COMMIT |
| T3 | Batch customs clearance — all held containers on a voyage cleared at once | COMMIT |
| T4 | Berth double-booking — Session A commits, Session B is blocked by trigger | ROLLBACK |
| T5 | Lost update problem — demonstrates the bug, then fixes it with `SELECT ... FOR UPDATE` | Both shown |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- MySQL 8.x running locally
- `pip`

### 1. Clone the repository
```bash
git clone https://github.com/your-username/harborcore.git
cd harborcore
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up the database
Open MySQL Workbench or your MySQL shell and run the full setup file:
```sql
source sql/harborcore_schema_and_seed.sql
```
This creates the `harborcore` database, all tables, indexes, seed data, the `available_berths` view, and all triggers.

### 4. Configure your DB credentials
The app currently reads credentials directly from `harborcore_app.py`. Open the file and update the connection block near the top:
```python
conn = mysql.connector.connect(
    host='127.0.0.1',
    database='harborcore',
    user='root',
    password='YOUR_PASSWORD_HERE',  # ← change this
    ...
)
```
> For a more secure setup, move credentials to `.streamlit/secrets.toml` and read them with `st.secrets`.

### 5. Run the app
```bash
streamlit run app.py
```
The app will open at `http://localhost:8501`.

---

## 📁 Project Structure

```
harborcore/
├── app.py                        # Main Streamlit application (all pages)
├── requirements.txt              # Python dependencies
├── .gitignore
├── README.md
└── sql/
    └── harborcore_schema_and_seed.sql   # Full DB setup: schema + data + triggers
```

---

## 🧩 Challenges Faced

Building this project was genuinely one of the more involved things I'd done with SQL and Python together — here's what actually tripped me up:

**Getting triggers to interact correctly with the app layer**  
The trickiest part wasn't writing the triggers — it was making the Python error messages from `SIGNAL SQLSTATE '45000'` bubble up cleanly through `mysql-connector` and render properly in Streamlit. The connector wraps MySQL errors in its own exception class, so I had to dig into the `str(e)` output and check for `"45000"` or keyword substrings to distinguish a trigger block from a constraint violation from a connection failure. It took more trial and error than expected.

**Transaction isolation and the lost update demo (T5)**  
To actually *show* a lost update, I had to deliberately open two separate connections sequentially — one reads the original value and writes `original + add_a`, the other independently reads the original (not the updated value) and writes `original + add_b`. Getting this to be deterministic and not accidentally "fix itself" due to MySQL's default InnoDB isolation required carefully controlling commit timing. The `SELECT ... FOR UPDATE` fix then had to force the second connection to wait, which meant ensuring InnoDB was the engine and that autocommit was off.

**Streamlit's stateless re-run model**  
Every interaction in Streamlit re-runs the entire script from top to bottom. This caused a subtle problem with the transaction demos: after T1 or T4 committed to the DB, the cleanup button needed to persist across re-runs. I solved it with `st.session_state`, but it took a few iterations to get the flow right (form submit → rerun → cleanup button visible → cleanup → rerun again).

**Keeping berth status consistent across concurrent simulations**  
In T4 (double-booking), Session A's `after_voyage_insert` trigger marks the berth as `Occupied` automatically. But then Session B's `before_voyage_insert` trigger fires on the *already-occupied* berth and raises an error. This interaction — two triggers from different INSERTs chained through a shared `berth` row — was the most satisfying thing to get working correctly.

**Schema normalization vs. UI convenience**  
Early on, I stored the vessel name directly in the voyage table to make queries simpler. Normalizing this out and always JOINing through `vessel` made the queries longer but the data consistent. A few of the multi-table JOINs (especially the complex analytical query at the bottom of the SQL file) were genuinely fiddly to write correctly.

---

## 📊 Sample Analytical Queries

The SQL file includes 15+ production-quality queries covering:
- Subqueries (correlated and non-correlated)
- `GROUP BY` with `HAVING`
- `UNION` across heterogeneous tables
- `LEFT OUTER JOIN` for null-aware berth maps
- `NOT EXISTS` for negative set membership
- Window-style aggregations and average comparisons

---

## Author

Built by Deepanshi Ruhil

---

=======
# harborcore
A full-stack DBMS-powered port management system built using Python, Streamlit, and MySQL, designed to simulate real-world seaport operations including vessel scheduling, container tracking, equipment monitoring, and billing.
