

import csv
import hashlib
import html
import io
import random
import string
from decimal import Decimal, InvalidOperation

import streamlit as st

from Database import connect_to_database


st.set_page_config(
    page_title="Banking Management System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_custom_css():
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(140deg, #07111f 0%, #081a31 46%, #050d19 100%);
                color: #e5edf7;
            }

            .block-container {
                padding-top: 1.4rem;
                padding-bottom: 2rem;
                max-width: 1280px;
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #07111f 0%, #0b1d33 100%);
                border-right: 1px solid rgba(148, 163, 184, 0.22);
            }

            [data-testid="stSidebar"] * {
                color: #e5edf7;
            }

            h1, h2, h3, p, label, span {
                font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }

            .brand-card {
                border: 1px solid rgba(56, 189, 248, 0.25);
                background: linear-gradient(180deg, rgba(14, 116, 144, 0.28), rgba(15, 23, 42, 0.55));
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1rem;
            }

            .brand-title {
                font-size: 1.05rem;
                font-weight: 800;
                margin-bottom: 0.18rem;
            }

            .brand-subtitle {
                color: #94a3b8;
                font-size: 0.82rem;
                line-height: 1.35;
            }

            .page-hero {
                border: 1px solid rgba(56, 189, 248, 0.24);
                background: linear-gradient(135deg, rgba(13, 27, 46, 0.96), rgba(14, 116, 144, 0.28));
                border-radius: 8px;
                padding: 1.45rem 1.55rem;
                margin-bottom: 1.1rem;
            }

            .hero-badge {
                display: inline-flex;
                color: #bae6fd;
                background: rgba(14, 165, 233, 0.14);
                border: 1px solid rgba(125, 211, 252, 0.24);
                border-radius: 999px;
                padding: 0.28rem 0.65rem;
                font-size: 0.78rem;
                font-weight: 700;
                margin-bottom: 0.7rem;
            }

            .page-hero h1 {
                margin: 0;
                font-size: clamp(2rem, 4vw, 3.2rem);
                line-height: 1.05;
                font-weight: 850;
            }

            .page-hero p {
                color: #94a3b8;
                max-width: 800px;
                margin: 0.7rem 0 0 0;
                font-size: 1rem;
                line-height: 1.6;
            }

            .metric-card, .info-card, .success-card {
                border: 1px solid rgba(148, 163, 184, 0.22);
                background: linear-gradient(180deg, rgba(15, 35, 60, 0.96), rgba(8, 19, 35, 0.96));
                border-radius: 8px;
                padding: 1rem;
                min-height: 132px;
                box-shadow: 0 16px 40px rgba(0, 0, 0, 0.20);
            }

            .metric-top {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.8rem;
            }

            .metric-icon {
                width: 2.35rem;
                height: 2.35rem;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background: rgba(56, 189, 248, 0.12);
                border: 1px solid rgba(56, 189, 248, 0.24);
                border-radius: 8px;
                font-size: 1.1rem;
            }

            .metric-caption {
                color: #94a3b8;
                font-size: 0.78rem;
            }

            .metric-value {
                font-size: 1.75rem;
                font-weight: 850;
                line-height: 1.15;
                color: #f8fafc;
                word-break: break-word;
            }

            .metric-title {
                margin-top: 0.25rem;
                color: #94a3b8;
                font-size: 0.9rem;
            }

            .section-label {
                color: #dbeafe;
                font-weight: 800;
                margin: 1.3rem 0 0.65rem 0;
                font-size: 1.05rem;
            }

            .success-card {
                border-color: rgba(34, 197, 94, 0.35);
                background: linear-gradient(180deg, rgba(20, 83, 45, 0.42), rgba(8, 19, 35, 0.96));
            }

            .account-number {
                display: inline-flex;
                margin-top: 0.7rem;
                padding: 0.55rem 0.75rem;
                border-radius: 8px;
                background: rgba(2, 6, 23, 0.42);
                border: 1px solid rgba(148, 163, 184, 0.25);
                color: #f8fafc;
                font-weight: 800;
                letter-spacing: 0.04em;
            }

            .stTextInput input, .stNumberInput input, .stTextArea textarea {
                background-color: rgba(15, 23, 42, 0.78) !important;
                color: #f8fafc !important;
                border: 1px solid rgba(148, 163, 184, 0.24) !important;
                border-radius: 8px !important;
            }

            .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
                border-radius: 8px !important;
                border: 1px solid rgba(125, 211, 252, 0.28) !important;
                background: linear-gradient(135deg, #1d4ed8, #0ea5e9) !important;
                color: white !important;
                font-weight: 800 !important;
                min-height: 2.75rem;
            }

            [data-testid="stDataFrame"] {
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 8px;
                overflow: hidden;
            }

            div[data-testid="stAlert"], div[data-testid="stExpander"] {
                border-radius: 8px !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def clean_text(value):
    return html.escape(str(value))


def format_money(value):
    try:
        amount = Decimal(str(value or 0))
    except Exception:
        amount = Decimal("0")
    return f"Rs. {amount:,.2f}"


def parse_money(value, field_name="Amount", allow_zero=False):
    text_value = str(value).replace(",", "").strip()

    if not text_value:
        return None, f"{field_name} is required."

    try:
        amount = Decimal(text_value).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None, f"{field_name} must be numeric."

    if allow_zero and amount < 0:
        return None, f"{field_name} cannot be negative."

    if not allow_zero and amount <= 0:
        return None, f"{field_name} must be greater than zero."

    return amount, None


def validate_pin(pin, confirm_pin=None):
    pin = str(pin).strip()

    if not pin:
        return "PIN is required."

    if not pin.isdigit():
        return "PIN must contain only numbers."

    if len(pin) != 4:
        return "PIN must be exactly 4 digits."

    if confirm_pin is not None and pin != str(confirm_pin).strip():
        return "PIN and confirm PIN do not match."

    return None


def format_timestamp(value):
    if hasattr(value, "strftime"):
        return value.strftime("%d %b %Y, %I:%M %p")
    return str(value or "-")


def rerun_app():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun() # pyright: ignore[reportAttributeAccessIssue]


def open_connection():
    try:
        return connect_to_database()
    except Exception as error:
        st.error(f"Database connection error: {error}")
        return None


def initialize_tables():
    connection = open_connection()
    if not connection:
        return False

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                account_number VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                pin VARCHAR(64) NOT NULL,
                balance DECIMAL(15, 2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit (
                id SERIAL PRIMARY KEY,
                account_number VARCHAR(50),
                holder_name VARCHAR(100),
                action VARCHAR(100) NOT NULL,
                amount DECIMAL(15, 2) DEFAULT 0.00,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_number) REFERENCES accounts(account_number)
            );
            """
        )
        cursor.execute("ALTER TABLE audit ADD COLUMN IF NOT EXISTS holder_name VARCHAR(100);")
        connection.commit()
        cursor.close()
        return True
    except Exception as error:
        connection.rollback()
        st.error(f"Database setup failed: {error}")
        return False
    finally:
        connection.close()


def pin_column_allows_hash():
    connection = open_connection()
    if not connection:
        return False

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'accounts'
              AND column_name = 'pin';
            """
        )
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return True

        max_length = result[0]
        return max_length is None or max_length >= 64
    except Exception:
        return False
    finally:
        connection.close()


def hash_pin(pin):
    return hashlib.sha256(str(pin).encode()).hexdigest()


def pin_for_storage(pin):
    if pin_column_allows_hash():
        return hash_pin(pin)
    return str(pin).strip()


def verify_pin(input_pin, stored_pin):
    input_pin = str(input_pin).strip()
    stored_pin = str(stored_pin or "").strip()
    return stored_pin == input_pin or stored_pin == hash_pin(input_pin)


def generate_account_number():
    return "BNK" + "".join(random.choices(string.digits, k=9))


def create_new_account(name, pin, opening_balance):
    stored_pin = pin_for_storage(pin)
    connection = open_connection()

    if not connection:
        return False, "Database connection failed.", None

    try:
        cursor = connection.cursor()

        account_number = None
        for _ in range(30):
            candidate = generate_account_number()
            cursor.execute("SELECT 1 FROM accounts WHERE account_number = %s", (candidate,))
            if not cursor.fetchone():
                account_number = candidate
                break

        if not account_number:
            raise RuntimeError("Could not generate a unique account number.")

        cursor.execute(
            """
            INSERT INTO accounts (account_number, name, pin, balance)
            VALUES (%s, %s, %s, %s)
            """,
            (account_number, name, stored_pin, opening_balance),
        )
        cursor.execute(
            """
            INSERT INTO audit (account_number, holder_name, action, amount)
            VALUES (%s, %s, %s, %s)
            """,
            (account_number, name, "Account Created", Decimal("0.00")),
        )

        if opening_balance > 0:
            cursor.execute(
                """
                INSERT INTO audit (account_number, holder_name, action, amount)
                VALUES (%s, %s, %s, %s)
                """,
                (account_number, name, "Amount deposited", opening_balance),
            )

        connection.commit()
        cursor.close()

        return True, "Account created successfully.", {
            "account_number": account_number,
            "name": name,
            "balance": opening_balance,
        }
    except Exception as error:
        connection.rollback()
        return False, f"Account creation failed: {error}", None
    finally:
        connection.close()


def authenticate_account(account_number, pin):
    connection = open_connection()
    if not connection:
        return False, "Database connection failed.", None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT account_number, name, pin, balance
            FROM accounts
            WHERE account_number = %s
            """,
            (account_number,),
        )
        result = cursor.fetchone()

        if not result or not verify_pin(pin, result[2]):
            cursor.close()
            return False, "Login failed. Invalid account number or PIN.", None

        account = {
            "account_number": result[0],
            "name": result[1],
            "balance": Decimal(str(result[3] or 0)),
        }

        cursor.execute(
            """
            INSERT INTO audit (account_number, holder_name, action, amount)
            VALUES (%s, %s, %s, %s)
            """,
            (account["account_number"], account["name"], "Balance checked", Decimal("0.00")),
        )
        connection.commit()
        cursor.close()
        return True, "Login successful.", account
    except Exception as error:
        connection.rollback()
        return False, f"Login failed: {error}", None
    finally:
        connection.close()


def fetch_account(account_number):
    connection = open_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT account_number, name, balance
            FROM accounts
            WHERE account_number = %s
            """,
            (account_number,),
        )
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return None

        return {
            "account_number": result[0],
            "name": result[1],
            "balance": Decimal(str(result[2] or 0)),
        }
    except Exception:
        return None
    finally:
        connection.close()


def post_transaction(account_number, pin, transaction_type, amount):
    connection = open_connection()
    if not connection:
        return False, "Database connection failed.", None

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT name, pin, balance
            FROM accounts
            WHERE account_number = %s
            FOR UPDATE
            """,
            (account_number,),
        )
        result = cursor.fetchone()

        if not result or not verify_pin(pin, result[1]):
            connection.rollback()
            cursor.close()
            return False, "Session verification failed. Please login again.", None

        holder_name = result[0]
        current_balance = Decimal(str(result[2] or 0))

        if transaction_type == "deposit":
            new_balance = current_balance + amount
            action = "Amount deposited"
            success_message = f"Deposit of {format_money(amount)} completed."
        else:
            if amount > current_balance:
                connection.rollback()
                cursor.close()
                return False, "Insufficient balance for this withdrawal.", current_balance

            new_balance = current_balance - amount
            action = "Amount withdrawn"
            success_message = f"Withdrawal of {format_money(amount)} completed."

        cursor.execute(
            "UPDATE accounts SET balance = %s WHERE account_number = %s",
            (new_balance, account_number),
        )
        cursor.execute(
            """
            INSERT INTO audit (account_number, holder_name, action, amount)
            VALUES (%s, %s, %s, %s)
            """,
            (account_number, holder_name, action, amount),
        )

        connection.commit()
        cursor.close()
        return True, success_message, new_balance
    except Exception as error:
        connection.rollback()
        return False, f"Transaction failed: {error}", None
    finally:
        connection.close()


def delete_customer_account(account_number, pin):
    connection = open_connection()
    if not connection:
        return False, "Database connection failed."

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT name, pin, balance
            FROM accounts
            WHERE account_number = %s
            FOR UPDATE
            """,
            (account_number,),
        )
        result = cursor.fetchone()

        if not result or not verify_pin(pin, result[1]):
            connection.rollback()
            cursor.close()
            return False, "Account deletion failed. Invalid PIN."

        holder_name = result[0]

        # Existing audit rows reference accounts through a foreign key.
        # Set old audit references to NULL before deleting the account record.
        cursor.execute(
            "UPDATE audit SET account_number = NULL WHERE account_number = %s",
            (account_number,),
        )
        cursor.execute(
            "DELETE FROM accounts WHERE account_number = %s",
            (account_number,),
        )
        cursor.execute(
            """
            INSERT INTO audit (account_number, holder_name, action, amount)
            VALUES (%s, %s, %s, %s)
            """,
            (None, holder_name, f"Account Deleted ({account_number})", Decimal("0.00")),
        )

        connection.commit()
        cursor.close()
        return True, "Account deleted successfully."
    except Exception as error:
        connection.rollback()
        return False, f"Account deletion failed: {error}"
    finally:
        connection.close()


def fetch_summary_metrics():
    metrics = {
        "accounts": 0,
        "total_balance": Decimal("0.00"),
        "audit_logs": 0,
        "deposits": Decimal("0.00"),
        "withdrawals": Decimal("0.00"),
    }

    connection = open_connection()
    if not connection:
        return metrics

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(balance), 0) FROM accounts")
        account_row = cursor.fetchone() or (0, 0)
        metrics["accounts"] = account_row[0]
        metrics["total_balance"] = Decimal(str(account_row[1] or 0))

        cursor.execute(
            """
            SELECT
                COUNT(*),
                COALESCE(SUM(CASE WHEN action = 'Amount deposited' THEN amount ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN action = 'Amount withdrawn' THEN amount ELSE 0 END), 0)
            FROM audit
            """
        )
        audit_row = cursor.fetchone() or (0, 0, 0)
        metrics["audit_logs"] = audit_row[0]
        metrics["deposits"] = Decimal(str(audit_row[1] or 0))
        metrics["withdrawals"] = Decimal(str(audit_row[2] or 0))

        cursor.close()
        return metrics
    except Exception:
        return metrics
    finally:
        connection.close()


def fetch_audit_logs(account_number=None, limit=None):
    connection = open_connection()
    if not connection:
        return []

    try:
        cursor = connection.cursor()
        query = """
            SELECT id, account_number, holder_name, action, amount, timestamp
            FROM audit
        """
        params = []

        if account_number:
            query += " WHERE account_number = %s"
            params.append(account_number)

        query += " ORDER BY timestamp DESC"

        if limit:
            query += " LIMIT %s"
            params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        cursor.close()

        logs = []
        for row in rows:
            logs.append(
                {
                    "id": row[0],
                    "account_number": row[1],
                    "holder_name": row[2],
                    "action": row[3],
                    "amount": row[4],
                    "timestamp": row[5],
                }
            )
        return logs
    except Exception:
        return []
    finally:
        connection.close()


def clear_audit_logs():
    connection = open_connection()
    if not connection:
        return False, "Database connection failed."

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM audit")
        connection.commit()
        cursor.close()
        return True, "All audit logs cleared successfully."
    except Exception as error:
        connection.rollback()
        return False, f"Could not clear audit logs: {error}"
    finally:
        connection.close()


def logs_to_rows(logs, include_account=True):
    rows = []

    for log in logs:
        row = {
            "ID": log["id"],
            "Holder Name": log["holder_name"] or "-",
            "Action": log["action"] or "-",
            "Amount": format_money(log["amount"]),
            "Timestamp": format_timestamp(log["timestamp"]),
        }
        if include_account:
            row = {"Account Number": log["account_number"] or "-", **row}
        rows.append(row)

    return rows


def rows_to_csv(rows):
    if not rows:
        return b""

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


HOME_PAGE = "🏠 Dashboard Home"
CREATE_PAGE = "➕ New Account Creation"
LOGIN_PAGE = "🔐 Customer Login"
ACCOUNT_PAGE = "💳 Account Dashboard"
ADMIN_PAGE = "🛡️ Admin Audit Logs"

NAV_ITEMS = [
    HOME_PAGE,
    CREATE_PAGE,
    LOGIN_PAGE,
    ACCOUNT_PAGE,
    ADMIN_PAGE,
]


def init_session_state():
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = HOME_PAGE
    if "customer" not in st.session_state:
        st.session_state.customer = None
    if "customer_pin" not in st.session_state:
        st.session_state.customer_pin = ""
    if "last_created_account" not in st.session_state:
        st.session_state.last_created_account = None
    if "flash_success" not in st.session_state:
        st.session_state.flash_success = ""


def change_page(page_name):
    st.session_state.selected_page = page_name
    rerun_app()


def logout_customer():
    st.session_state.customer = None
    st.session_state.customer_pin = ""
    st.session_state.selected_page = LOGIN_PAGE
    rerun_app()


def render_sidebar():
    st.sidebar.markdown(
        """
        <div class="brand-card">
            <div class="brand-title">🏦 BlueVault Bank</div>
            <div class="brand-subtitle">PostgreSQL powered banking operations dashboard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### Navigation")

    for page in NAV_ITEMS:
        button_label = page

        if page == st.session_state.selected_page:
            button_label = "✓ " + page

        if st.sidebar.button(button_label, key=f"nav_{page}", use_container_width=True):
            change_page(page)

    if st.session_state.customer:
        customer = st.session_state.customer
        st.sidebar.markdown(
            f"""
            <div class="brand-card">
                <div class="brand-title">Signed in</div>
                <div class="brand-subtitle">
                    {clean_text(customer['name'])}<br>
                    {clean_text(customer['account_number'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout_customer()


def render_page_header(title, subtitle, badge):
    st.markdown(
        f"""
        <div class="page-hero">
            <div class="hero-badge">{clean_text(badge)}</div>
            <h1>{clean_text(title)}</h1>
            <p>{clean_text(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(title, value, caption, icon):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-top">
                <span class="metric-icon">{clean_text(icon)}</span>
                <span class="metric-caption">{clean_text(caption)}</span>
            </div>
            <div class="metric-value">{clean_text(value)}</div>
            <div class="metric-title">{clean_text(title)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_logs_table(logs, include_account=True):
    if not logs:
        st.info("No audit logs found.")
        return

    rows = logs_to_rows(logs, include_account=include_account)
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_home_page():
    metrics = fetch_summary_metrics()

    render_page_header(
        "Banking Management System",
        "A professional Streamlit banking dashboard for account onboarding, secure customer access, and audit monitoring.",
        "Live database: BankData",
    )

    cols = st.columns(4)

    with cols[0]:
        render_metric_card("Total Accounts", metrics["accounts"], "Customer records", "👥")
    with cols[1]:
        render_metric_card("Total Balance", format_money(metrics["total_balance"]), "Across all accounts", "💰")
    with cols[2]:
        render_metric_card("Audit Logs", metrics["audit_logs"], "Tracked actions", "📋")
    with cols[3]:
        render_metric_card("Total Deposits", format_money(metrics["deposits"]), "Logged deposits", "📈")

    st.markdown('<div class="section-label">Quick Actions</div>', unsafe_allow_html=True)

    action_cols = st.columns(4)

    with action_cols[0]:
        if st.button("➕ Create Account", use_container_width=True):
            change_page(CREATE_PAGE)
    with action_cols[1]:
        if st.button("🔐 Customer Login", use_container_width=True):
            change_page(LOGIN_PAGE)
    with action_cols[2]:
        if st.button("💳 Account Dashboard", use_container_width=True):
            change_page(ACCOUNT_PAGE)
    with action_cols[3]:
        if st.button("🛡️ Audit Logs", use_container_width=True):
            change_page(ADMIN_PAGE)

    st.markdown('<div class="section-label">Recent System Activity</div>', unsafe_allow_html=True)
    show_logs_table(fetch_audit_logs(limit=8), include_account=True)


def render_create_account_page():
    render_page_header(
        "Create New Account",
        "Open a new customer account with validation, secure PIN handling, opening balance, and automatic audit tracking.",
        "Customer onboarding",
    )

    left, right = st.columns([1.25, 0.75])

    with left:
        with st.form("create_account_form"):
            name = st.text_input("Full Name", placeholder="Enter customer full name")

            col_pin, col_confirm = st.columns(2)

            with col_pin:
                pin = st.text_input("4-digit PIN", type="password", max_chars=4)

            with col_confirm:
                confirm_pin = st.text_input("Confirm PIN", type="password", max_chars=4)

            opening_balance_text = st.text_input("Opening Balance", value="0.00")
            submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            name = name.strip()

            if not name:
                st.error("Empty name is not allowed.")
            else:
                pin_error = validate_pin(pin, confirm_pin)
                opening_balance, balance_error = parse_money(
                    opening_balance_text,
                    field_name="Balance",
                    allow_zero=True,
                )

                if pin_error:
                    st.error(pin_error)
                elif balance_error:
                    st.error(balance_error)
                else:
                    success, message, account = create_new_account(name, pin, opening_balance)

                    if success:
                        st.session_state.last_created_account = account
                        st.success(message)
                    else:
                        st.error(message)

    with right:
        st.markdown(
            """
            <div class="info-card">
                <h3>Account setup checks</h3>
                <p>Name cannot be empty, PIN is required, and balance must be numeric.
                Every successful account creation is written to the audit table.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.last_created_account:
        account = st.session_state.last_created_account

        st.markdown('<div class="section-label">Created Account</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="success-card">
                <h3>Account ready for customer login</h3>
                <p>Share this account number with the customer and ask them to keep their PIN private.</p>
                <div class="account-number">{clean_text(account['account_number'])}</div>
                <p style="margin-top: 0.8rem;">
                    Holder: {clean_text(account['name'])} · Opening Balance: {clean_text(format_money(account['balance']))}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_login_page():
    render_page_header(
        "Customer Login",
        "Authenticate customers by account number and PIN. Failed logins show a clear error message.",
        "Secure account access",
    )

    if st.session_state.flash_success:
        st.success(st.session_state.flash_success)
        st.session_state.flash_success = ""

    if st.session_state.customer:
        st.success("You are already logged in.")

        if st.button("Open Account Dashboard", use_container_width=True):
            change_page(ACCOUNT_PAGE)

        return

    with st.form("customer_login_form"):
        account_number = st.text_input("Account Number", placeholder="Example: BNK123456789")
        pin = st.text_input("PIN", type="password", max_chars=4)
        submitted = st.form_submit_button("Login to Account", use_container_width=True)

    if submitted:
        account_number = account_number.strip().upper()

        if not account_number:
            st.error("Account number is required.")
            return

        pin_error = validate_pin(pin)

        if pin_error:
            st.error(pin_error)
            return

        success, message, account = authenticate_account(account_number, pin)

        if not success:
            st.error(message)
            return

        st.session_state.customer = account
        st.session_state.customer_pin = pin
        st.session_state.selected_page = ACCOUNT_PAGE
        rerun_app()


def render_account_dashboard_page():
    render_page_header(
        "Account Dashboard",
        "View customer balance, make deposits or withdrawals, and review account audit history.",
        "Customer workspace",
    )

    if not st.session_state.customer:
        st.warning("Please login before opening the account dashboard.")

        if st.button("Go to Customer Login", use_container_width=True):
            change_page(LOGIN_PAGE)

        return

    latest_account = fetch_account(st.session_state.customer["account_number"])

    if not latest_account:
        st.session_state.customer = None
        st.session_state.customer_pin = ""
        st.error("This account could not be found. Please login again.")
        return

    st.session_state.customer = latest_account
    customer = st.session_state.customer

    cols = st.columns(3)

    with cols[0]:
        render_metric_card("Account Holder", customer["name"], "Verified customer", "👤")
    with cols[1]:
        render_metric_card("Account Number", customer["account_number"], "Primary identifier", "💳")
    with cols[2]:
        render_metric_card("Current Balance", format_money(customer["balance"]), "Available funds", "💰")

    st.markdown('<div class="section-label">Banking Actions</div>', unsafe_allow_html=True)

    deposit_col, withdraw_col = st.columns(2)

    with deposit_col:
        with st.form("deposit_form"):
            deposit_amount_text = st.text_input("Deposit Amount", placeholder="Example: 5000")
            deposit_submitted = st.form_submit_button("📈 Deposit Funds", use_container_width=True)

        if deposit_submitted:
            amount, error = parse_money(deposit_amount_text, field_name="Deposit amount")

            if error:
                st.error(error)
            else:
                success, message, new_balance = post_transaction(
                    customer["account_number"],
                    st.session_state.customer_pin,
                    "deposit",
                    amount,
                )

                if success:
                    st.session_state.customer["balance"] = new_balance
                    st.success(message)
                else:
                    st.error(message)

    with withdraw_col:
        with st.form("withdraw_form"):
            withdraw_amount_text = st.text_input("Withdrawal Amount", placeholder="Example: 2500")
            withdraw_submitted = st.form_submit_button("📉 Withdraw Funds", use_container_width=True)

        if withdraw_submitted:
            amount, error = parse_money(withdraw_amount_text, field_name="Withdrawal amount")

            if error:
                st.error(error)
            else:
                success, message, new_balance = post_transaction(
                    customer["account_number"],
                    st.session_state.customer_pin,
                    "withdraw",
                    amount,
                )

                if success:
                    st.session_state.customer["balance"] = new_balance
                    st.success(message)
                else:
                    st.error(message)

    st.markdown('<div class="section-label">Account Activity</div>', unsafe_allow_html=True)
    show_logs_table(fetch_audit_logs(account_number=customer["account_number"]), include_account=False)

    st.markdown('<div class="section-label">Account Management</div>', unsafe_allow_html=True)

    with st.expander("Delete account permanently"):
        st.warning("This will permanently delete your account from the accounts table.")

        with st.form("delete_account_form"):
            confirm_checkbox = st.checkbox("I understand this account will be permanently deleted.")
            account_number_confirm = st.text_input("Type your account number to confirm")
            delete_pin = st.text_input("Enter PIN", type="password", max_chars=4)
            delete_submitted = st.form_submit_button("Delete Account", use_container_width=True)

        if delete_submitted:
            if not confirm_checkbox:
                st.error("Please tick the confirmation checkbox.")
            elif account_number_confirm.strip().upper() != customer["account_number"]:
                st.error("Account number confirmation does not match.")
            else:
                pin_error = validate_pin(delete_pin)

                if pin_error:
                    st.error(pin_error)
                else:
                    success, message = delete_customer_account(customer["account_number"], delete_pin)

                    if success:
                        st.session_state.customer = None
                        st.session_state.customer_pin = ""
                        st.session_state.flash_success = message
                        st.session_state.selected_page = LOGIN_PAGE
                        rerun_app()
                    else:
                        st.error(message)


def render_admin_audit_page():
    render_page_header(
        "Admin Audit Logs",
        "Monitor all account activity in a clean audit table and clear logs only after confirmation.",
        "Admin controls",
    )

    metrics = fetch_summary_metrics()
    cols = st.columns(4)

    with cols[0]:
        render_metric_card("Audit Logs", metrics["audit_logs"], "Total entries", "📋")
    with cols[1]:
        render_metric_card("Deposits", format_money(metrics["deposits"]), "Total deposited", "📈")
    with cols[2]:
        render_metric_card("Withdrawals", format_money(metrics["withdrawals"]), "Total withdrawn", "📉")
    with cols[3]:
        render_metric_card("Accounts", metrics["accounts"], "Customer records", "👥")

    st.markdown('<div class="section-label">Clear Audit Logs</div>', unsafe_allow_html=True)

    with st.expander("Danger zone: permanently delete audit records"):
        st.warning("This action deletes every row from the audit table. It cannot be undone from this app.")

        with st.form("clear_audit_form"):
            confirm_checkbox = st.checkbox("I understand this will permanently clear all audit logs.")
            confirmation_text = st.text_input("Type CLEAR to confirm")
            clear_submitted = st.form_submit_button("Clear Audit Logs", use_container_width=True)

        if clear_submitted:
            if not confirm_checkbox or confirmation_text.strip() != "CLEAR":
                st.error("Please tick the checkbox and type CLEAR before deleting audit logs.")
            else:
                success, message = clear_audit_logs()

                if success:
                    st.success(message)
                else:
                    st.error(message)

    st.markdown('<div class="section-label">All Audit Logs</div>', unsafe_allow_html=True)

    logs = fetch_audit_logs()
    show_logs_table(logs, include_account=True)

    if logs:
        rows = logs_to_rows(logs, include_account=True)

        st.download_button(
            "⬇️ Download Audit CSV",
            data=rows_to_csv(rows),
            file_name="bank_audit_logs.csv",
            mime="text/csv",
            use_container_width=True,
        )


def main():
    load_custom_css()
    init_session_state()
    render_sidebar()

    database_ready = initialize_tables()

    if not database_ready:
        render_page_header(
            "Database Connection Required",
            "The app could not connect to PostgreSQL. Please check Database.py, PostgreSQL service, database name BankData, user, password, and psycopg2 installation.",
            "Connection status",
        )
        st.stop()

    selected_page = st.session_state.selected_page

    if selected_page == HOME_PAGE:
        render_home_page()
    elif selected_page == CREATE_PAGE:
        render_create_account_page()
    elif selected_page == LOGIN_PAGE:
        render_login_page()
    elif selected_page == ACCOUNT_PAGE:
        render_account_dashboard_page()
    elif selected_page == ADMIN_PAGE:
        render_admin_audit_page()


if __name__ == "__main__":
    main()
