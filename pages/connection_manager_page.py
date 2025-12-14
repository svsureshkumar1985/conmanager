import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
from datetime import datetime
from typing import Any, List

from utilities.conn_manager import (
    list_connections,
    save_connection,
    get_connection,
    delete_connection,
    decrypt_password,
    test_sql_server_connection,
)

ConnectionRecord = dict[str, Any]


@st.cache_data(ttl=30, show_spinner=False)
def _load_connections_cached(data_version: int) -> List[ConnectionRecord]:
    return list_connections()


def _ensure_cache_version() -> None:
    if "cm_data_version" not in st.session_state:
        st.session_state["cm_data_version"] = 0


def _bump_connections_cache() -> None:
    st.session_state["cm_data_version"] = st.session_state.get("cm_data_version", 0) + 1


def render() -> None:
    # Center the entire Connection Manager content
    _left, _center, _right = st.columns([1, 3, 1])
    with _center:
        st.markdown(
            """
            <style>
            [data-testid="stDataEditor"] input[type="checkbox"] {
                appearance: none;
                width: 8px;
                height: 16px;
                border: 2px solid #9CA3AF;
                border-radius: 0%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            [data-testid="stDataEditor"] input[type="checkbox"]:checked {
                border-color: #D71E28;
                box-shadow: inset 0 0 0 4px #D71E28;
            }

            .cm-hero {
                text-align: center;
                justify-content: center;
                margin-top: -2rem !important;
                margin-bottom: 0.5rem !important;
            }
            
            .cm-hero-text {
                text-align: center;
                justify-content: center;
                margin: 0 !important;
                padding: 0 !important;
            }
            
            .cm-hero-text h2 {
                margin-top: 0 !important;
                margin-bottom: 0.5rem !important;
                padding: 0 !important;
            }
            
            /* Custom button styling with Wells Fargo red #d71e28 */
            /* Target all form submit buttons with primary type */
            div[data-testid="stFormSubmitButton"] button,
            div[data-testid="stFormSubmitButton"] button[kind="primary"],
            .stButton button[kind="primary"],
            button[kind="primary"] {
                background-color: #d71e28 !important;
                border-color: #d71e28 !important;
                color: white !important;
            }
            
            div[data-testid="stFormSubmitButton"] button:hover,
            div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover,
            .stButton button[kind="primary"]:hover,
            button[kind="primary"]:hover {
                background-color: #b81820 !important;
                border-color: #b81820 !important;
            }
            
            div[data-testid="stFormSubmitButton"] button:active,
            div[data-testid="stFormSubmitButton"] button[kind="primary"]:active,
            .stButton button[kind="primary"]:active,
            button[kind="primary"]:active {
                background-color: #9a1419 !important;
                border-color: #9a1419 !important;
            }
            
            div[data-testid="stFormSubmitButton"] button:disabled,
            div[data-testid="stFormSubmitButton"] button[kind="primary"]:disabled,
            .stButton button[kind="primary"]:disabled,
            button[kind="primary"]:disabled {
                background-color: rgba(215, 30, 40, 0.5) !important;
                border-color: rgba(215, 30, 40, 0.5) !important;
                color: rgba(255, 255, 255, 0.7) !important;
            }
            
            /* Additional selector for button text color */
            div[data-testid="stFormSubmitButton"] button p,
            button[kind="primary"] p {
                color: white !important;
            }
            
            /* Minimize spacing between buttons */
            div[data-testid="stFormSubmitButton"] {
                margin: 0 !important;
                padding: 0 !important;
            }
            div[data-testid="column"] {
                padding: 0 0.25rem !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        _render_page_intro()

        connections = list_connections()
        active = st.session_state.get("active_connection")

        if not connections:
            _render_empty_connections_state()
            _render_add_connection_form()
            return

        tab = sac.tabs(
            items=[
                sac.TabsItem(label="Connections", icon="database"),
                sac.TabsItem(label="Add Connection", icon="plus-circle"),
            ],
            align="center",
            size="lg",
            key="cm_tabs",
        )

        if tab == "Connections":
            _render_connections_tab(connections, active)
        else:
            _render_add_connection_form()


def _render_page_intro() -> None:
    st.markdown(
        """
        <section class="cm-hero">
            <div class="cm-hero-text">
                <h2>Login</h2>
            </div>
            <div class="cm-hero-graphic"></div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_connections_tab(connections: List[ConnectionRecord], active_name: str | None) -> None:
    if not connections:
        _render_empty_connections_state()
        return

    selected_name = _ensure_selected_connection(connections, active_name)
    pending_delete = st.session_state.get("cm_pending_delete")

    # Use a container with border to group table and action buttons
    with st.container(border=True):
        # Render table OUTSIDE form so changes are detected immediately
        selected_name = _render_connections_table(connections, selected_name, active_name)

        with st.form("cm_connections_form", clear_on_submit=False, border=False):
            selected = next((c for c in connections if c.get("name") == selected_name), None)
            if not selected:
                st.warning("Select a connection to continue.")
                actions = {"connect": False, "edit": False, "delete_request": False, "delete_confirm": False, "delete_cancel": False}
            else:
                actions = _render_connection_actions(selected, active_name, pending_delete)

    selected = next((c for c in connections if c.get("name") == st.session_state.get("cm_selected_connection")), None)
    if not selected:
        st.warning("Select a connection to continue.")
        return

    if actions["connect"]:
        _handle_connect_action(selected)

    if actions["edit"]:
        st.session_state["cm_edit_mode"] = True
        st.session_state["cm_edit_target"] = selected.get("name", "")

    pending_target = st.session_state.get("cm_pending_delete")
    current_name = selected.get("name", "")
    if actions["delete_request"]:
        st.session_state["cm_pending_delete"] = current_name
        st.rerun()
    if actions["delete_cancel"] and pending_target == current_name:
        st.session_state.pop("cm_pending_delete", None)
        st.rerun()
    if actions["delete_confirm"] and pending_target == current_name:
        _execute_delete(current_name)
        return

    if pending_target and pending_target != current_name:
        st.session_state.pop("cm_pending_delete", None)

    if st.session_state.get("cm_edit_target") != selected.get("name"):
        st.session_state.pop("cm_edit_mode", None)

    if st.session_state.get("cm_edit_mode") and st.session_state.get("cm_edit_target") == selected.get("name"):
        _render_inline_edit_form(selected)


def _render_empty_connections_state() -> None:
    pass
    # st.markdown(
    #     """
    #     <div class="cm-empty-state">
    #         <p>Create a database connection.</p>
    #     </div>
    #     """,
    #     unsafe_allow_html=True,
    # )


def _ensure_selected_connection(connections: List[ConnectionRecord], active_name: str | None) -> str:
    names = [c.get("name", "") for c in connections]
    state_key = "cm_selected_connection"
    stored = st.session_state.get(state_key)
    default = active_name if active_name in names else stored if stored in names else names[0]
    st.session_state[state_key] = default
    return default


def _render_connections_table(
    connections: List[ConnectionRecord],
    selected_name: str,
    active_name: str | None,
) -> str:
    # Build the dataframe with only the selected_name checked
    rows = []
    for conn in connections:
        rows.append(
            {
                "Selected": conn.get("name") == selected_name,
                "Connection Name": conn.get("name", "Unnamed"),
                "Host": conn.get("host", "-"),
                "Username": conn.get("user", "-"),
                "Database": conn.get("database", "-"),
            }
        )

    df = pd.DataFrame(rows)

    # Store the original state before user interaction
    if "cm_prev_selection_state" not in st.session_state:
        st.session_state["cm_prev_selection_state"] = df["Selected"].tolist()

    prev_state = st.session_state["cm_prev_selection_state"]

    # st.markdown('<div class="cm-table-card">', unsafe_allow_html=True)
    edited = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        height="content",
        column_config={
            "Selected": st.column_config.CheckboxColumn(label=""),
            "Connection Name": st.column_config.TextColumn("Connection Name", disabled=True),
            "Host": st.column_config.TextColumn("Host", disabled=True),
            "Username": st.column_config.TextColumn("Username", disabled=True),
            "Database": st.column_config.TextColumn("Database", disabled=True),
        },
        disabled=["Connection Name", "Host", "Username", "Database"],
        key="cm_connections_table",
    )
    # st.markdown('</div>', unsafe_allow_html=True)

    # Detect changes in checkbox state
    new_selection = selected_name
    if isinstance(edited, pd.DataFrame) and "Selected" in edited:
        current_state = edited["Selected"].tolist()

        # Find which checkboxes are currently checked
        selected_indices = [i for i, val in enumerate(current_state) if val]

        # If multiple checkboxes are checked
        if len(selected_indices) > 1:
            # Find which checkbox was newly clicked by comparing with previous state
            newly_clicked_idx = None
            for idx in selected_indices:
                if idx < len(prev_state) and not prev_state[idx]:
                    # This checkbox was unchecked before and is checked now
                    newly_clicked_idx = idx
                    break

            # If we found the newly clicked one, use it; otherwise use the last one
            if newly_clicked_idx is not None:
                new_selection = str(edited.loc[newly_clicked_idx, "Connection Name"]).strip()
            else:
                new_selection = str(edited.loc[selected_indices[-1], "Connection Name"]).strip()

            # Update state and force rerun to show only the new selection
            st.session_state["cm_selected_connection"] = new_selection
            st.session_state["cm_prev_selection_state"] = [False] * len(connections)
            st.session_state["cm_prev_selection_state"][connections.index(next(c for c in connections if c.get("name") == new_selection))] = True
            st.rerun()

        elif len(selected_indices) == 1:
            # Exactly one checkbox is selected - this is good
            idx = selected_indices[0]
            new_selection = str(edited.loc[idx, "Connection Name"]).strip()

            # Update the selection if it changed
            if new_selection != selected_name:
                st.session_state["cm_selected_connection"] = new_selection
                st.session_state["cm_prev_selection_state"] = current_state
                st.rerun()

        elif len(selected_indices) == 0:
            # User tried to uncheck - prevent this by restoring the previous selection
            st.session_state["cm_selected_connection"] = selected_name
            st.session_state["cm_prev_selection_state"] = df["Selected"].tolist()
            st.rerun()

        # Update the stored previous state
        st.session_state["cm_prev_selection_state"] = current_state

    # Ensure we always have a selection
    if not new_selection and connections:
        new_selection = connections[0].get("name", "")
        st.session_state["cm_selected_connection"] = new_selection

    return st.session_state.get("cm_selected_connection", selected_name)


def _format_connection_option(conn: ConnectionRecord, active_name: str | None) -> str:
    name = conn.get("name", "Unnamed")
    created = _format_date(conn.get("created_date"))
    status = "🟢 Active" if active_name == name else "⚪ Available"
    return f"{name}  |  {status}\nCreated {created}"


def _render_connection_actions(selected: ConnectionRecord, active_name: str | None, pending_delete: str | None) -> dict[str, bool]:
    name = selected.get("name", "Unnamed")
    # Minimal spacing between buttons by not specifying gap (uses default minimal spacing)
    col1, col2, col3,pad1 = st.columns([1, 1, 1,4])
    cols = [col1, col2, col3]
    connect_clicked = cols[0].form_submit_button(
        "Connect",
        key="cm_action_connect",
        type="primary",
        use_container_width=True,
        disabled=active_name == name,
    )
    edit_clicked = cols[1].form_submit_button(
        "Edit",
        key="cm_action_edit",
        type="primary",
        use_container_width=True,
    )

    delete_request_clicked = delete_confirm_clicked = delete_cancel_clicked = False
    with cols[2]:
        if pending_delete == name:
            action_cols = st.columns(2)
            delete_confirm_clicked = action_cols[0].form_submit_button(
                "Yes",
                key="cm_delete_yes",
                type="primary",
                use_container_width=True,
            )
            delete_cancel_clicked = action_cols[1].form_submit_button(
                "No",
                key="cm_delete_no",
                type="primary",
                use_container_width=True,
            )
        else:
            delete_request_clicked = st.form_submit_button(
                "Delete",
                key="cm_action_delete",
                type="primary",
                use_container_width=True,
            )

    return {
        "connect": connect_clicked,
        "edit": edit_clicked,
        "delete_request": delete_request_clicked,
        "delete_confirm": delete_confirm_clicked,
        "delete_cancel": delete_cancel_clicked,
    }


def _render_inline_edit_form(selected: ConnectionRecord) -> None:
    current = get_connection(selected.get("name", ""))
    if not current:
        st.error("Connection record not found. Please refresh and try again.")
        return

    name = current.get("name", "")
    host = current.get("host", "")
    user = current.get("user", "")
    database = current.get("database", "")
    stash_key = "cm_edit_cached_pw"
    if stash_key not in st.session_state:
        pw_plain = decrypt_password(current)
        st.session_state[stash_key] = pw_plain or ""
    cached_pw = st.session_state.get(stash_key, "")

    with st.form("cm_inline_edit", clear_on_submit=False, border=True):
        st.markdown('<div class="cm-inline-edit">', unsafe_allow_html=True)
        st.subheader("Edit connection")
        name_input = st.text_input("Connection Name", value=name, key="cm_edit_name")
        host_input = st.text_input("Host / Server", value=host, key="cm_edit_host")
        database_input = st.text_input("Database Name", value=database, key="cm_edit_database")
        user_input = st.text_input("Username", value=user, key="cm_edit_user")
        password_input = st.text_input("Password", value=cached_pw, type="password", key="cm_edit_pw")
        col_test, col_save,pad = st.columns([1,1,4], gap="small")

        with col_test:
            submit_test = st.form_submit_button("Test", type="primary", use_container_width=True)
        with col_save:
            submit_save = st.form_submit_button("Save", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if submit_test:
        _handle_test_action(host_input, user_input, password_input, database_input)
    if submit_save:
        # Clear edit mode flags BEFORE calling save action (which triggers rerun)
        st.session_state.pop("cm_edit_mode", None)
        st.session_state.pop("cm_edit_target", None)
        st.session_state.pop(stash_key, None)
        _handle_save_action(name_input, host_input, user_input, password_input, database_input)


def _execute_delete(target: str) -> None:
    try:
        delete_connection(target)
        if st.session_state.get("active_connection") == target:
            st.session_state.pop("active_connection", None)
        st.session_state.pop("cm_pending_delete", None)
        st.session_state.pop("cm_selected_connection", None)
        st.success(f"Deleted {target}.")
        st.rerun()
    except Exception as exc:
        st.error(f"Failed to delete: {exc}")
        st.session_state.pop("cm_pending_delete", None)


def _render_add_connection_form() -> None:
    default_name = st.session_state.pop("_edit_name", "")
    default_host = st.session_state.pop("_edit_host", "")
    default_user = st.session_state.pop("_edit_user", "")
    default_database = st.session_state.pop("_edit_database", "")

    left_pad, center_col, right_pad = st.columns([1, 2, 1])

    with center_col:
        with st.form("cm_add_connection", clear_on_submit=False, border=True):
            name = st.text_input("Connection Name", value=default_name, placeholder="e.g., DEV,SIT,UAT")
            host = st.text_input("Host Name", value=default_host, placeholder="e.g SERVER\\INSTANCE")
            database = st.text_input("Database Name", value=default_database, placeholder="e.g., master")

            user = st.text_input("Username", value=default_user, placeholder="service-account")
            password = st.text_input("Password", type="password", placeholder="••••••••")

            btn_test, btn_save, btn_connect = st.columns(3, gap="small")
            with btn_test:
                submit_test = st.form_submit_button("Test", type="primary", use_container_width=True)
            with btn_save:
                submit_save = st.form_submit_button("Save", type="primary", use_container_width=True)
            with btn_connect:
                submit_connect = st.form_submit_button("Connect", type="primary", use_container_width=True)

        if submit_test:
            _handle_test_action(host, user, password, database)
        if submit_save:
            _handle_save_action(name, host, user, password, database)
        if submit_connect:
            _handle_test_and_save(name, host, user, password, database)



def _handle_test_action(host: str, user: str, password: str, database: str) -> None:
    if not host or not user or not password or not database:
        st.error("Host, database, username, and password are required before testing.")
        return
    with st.spinner("Testing connection..."):
        ok, msg = test_sql_server_connection(host, user, password, database)
    if ok:
        st.success(f"✅ {msg}")
    else:
        _show_connection_error(msg)


def _handle_save_action(name: str, host: str, user: str, password: str, database: str = "", is_new: bool = False) -> None:
    if not all([name, host, user, password, database]):
        st.error("Name, host, database, username, and password are required.")
        return
    try:
        if not is_new and get_connection(name):
            st.info(f"Updating existing connection '{name}'.")
        save_connection(name, host, user, password, database)
        st.success("Connection saved.")
        st.rerun()
    except Exception as exc:
        st.error(f"Error: {exc}")


def _handle_test_and_save(name: str, host: str, user: str, password: str, database: str) -> None:
    if not all([name, host, user, password, database]):
        st.error("Complete all fields, including database, before testing and saving.")
        return
    with st.spinner("Testing credentials..."):
        ok, msg = test_sql_server_connection(host, user, password, database)
    if not ok:
        _show_connection_error(msg)
        return
    try:
        if get_connection(name):
            st.info(f"Updating existing connection '{name}'.")
        save_connection(name, host, user, password, database)
        st.session_state["active_connection"] = name
        st.success("Connection verified and saved.")
        st.session_state["current_page"] = "Dashboard"
        st.rerun()
    except Exception as exc:
        st.error(f"Error: {exc}")


def _format_date(raw: Any) -> str:
    if not raw:
        return "N/A"
    if isinstance(raw, datetime):
        return raw.strftime("%b %d, %Y %I:%M %p")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(str(raw), fmt)
            return dt.strftime("%b %d, %Y %I:%M %p")
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(str(raw))
        return dt.strftime("%b %d, %Y %I:%M %p")
    except Exception:
        return str(raw)


def _test_connection(conn: ConnectionRecord) -> None:
    if not conn.get("enc_password") and conn.get("name"):
        refreshed = get_connection(conn["name"])  # type: ignore[index]
        if refreshed:
            conn = refreshed
    pw = decrypt_password(conn)
    if pw is None:
        st.error("Stored password is missing or invalid. Please re-save this connection.")
        return
    with st.spinner("Testing connection..."):
        ok, msg = test_sql_server_connection(conn.get("host", ""), conn.get("user", ""), pw, conn.get("database", ""))
    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")


def _set_active_connection(conn_name: str) -> None:
    st.session_state["active_connection"] = conn_name
    st.success(f"Connected to {conn_name}.")
    st.session_state["current_page"] = "Dashboard"
    st.rerun()


def _show_connection_error(details: str) -> None:
    st.error("Unable to connect. Please confirm the host, username, and password, then try again.")
    with st.expander("Technical details", expanded=False):
        st.code(str(details))


def _handle_connect_action(selected: ConnectionRecord) -> None:
    name = selected.get("name")
    if not name:
        st.error("Selected connection is missing a name.")
        return

    record = get_connection(name) or selected
    host = record.get("host", "")
    user = record.get("user", "")
    pw = decrypt_password(record)
    database = record.get("database", "")

    if not all([host, user, pw, database]):
        st.error("Stored credentials are incomplete. Please edit and save this connection before connecting.")
        return

    with st.spinner(f"Connecting to {name}..."):
        ok, msg = test_sql_server_connection(host, user, pw, database)

    if not ok:
        _show_connection_error(msg)
        return

    _set_active_connection(name)
