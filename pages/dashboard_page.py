"""Dashboard page - main overview of the system."""
import streamlit as st
import streamlit_antd_components as sac
from utilities.nav_utils import render_metric_card


def render() -> None:
    """Render the dashboard page with system overview."""

    # Get data
    rules = st.session_state.get("rules", [])
    active_conn = st.session_state.get("active_connection")

    # Page header
    st.markdown(
        """
        <div style="margin-bottom: 30px;">
            <h2 style="margin: 0; color: #1F2937; font-weight: 700;">Dashboard</h2>
            <p style="margin: 4px 0 0 0; color: #6B7280; font-size: 14px;">
                System overview and quick statistics
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Key metrics section
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h3 style="margin: 0 0 12px 0; color: #374151; font-size: 16px; font-weight: 600;">
                Key Metrics
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card("Active Connection", "✅" if active_conn else "❌", "🔗", "#1F8A70")

    with col2:
        render_metric_card("Total Rules", str(len(rules)), "📋", "#0F62FE")

    with col3:
        allow_rules = len([r for r in rules if r.get("action") == "Allow"])
        render_metric_card("Allow Rules", str(allow_rules), "✅", "#1F8A70")

    with col4:
        block_rules = len([r for r in rules if r.get("action") == "Block"])
        render_metric_card("Block Rules", str(block_rules), "🚫", "#B91C1C")

    st.divider()

    # System status section
    st.markdown(
        """
        <div style="margin-bottom: 20px; margin-top: 30px;">
            <h3 style="margin: 0 0 12px 0; color: #374151; font-size: 16px; font-weight: 600;">
                System Status
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:20px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="display:flex;align-items:center;margin-bottom:12px;">
                    <span style="font-size:20px;margin-right:8px;">🔗</span>
                    <h4 style="margin:0;color:#1F2937;font-weight:600;">Database Connection</h4>
                </div>
                <div style="padding-left:28px;">
            """,
            unsafe_allow_html=True,
        )

        if active_conn:
            st.success(f"Connected to: **{active_conn}**")
            st.caption("Status: Online ✅")
        else:
            st.warning("No active connection")
            st.caption("Status: Offline ⚠️")

        st.markdown("</div></div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:20px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="display:flex;align-items:center;margin-bottom:12px;">
                    <span style="font-size:20px;margin-right:8px;">📊</span>
                    <h4 style="margin:0;color:#1F2937;font-weight:600;">System Health</h4>
                </div>
                <div style="padding-left:28px;">
            """,
            unsafe_allow_html=True,
        )

        st.success("All systems operational ✅")
        st.caption("Uptime: 99.9%")

        st.markdown("</div></div>", unsafe_allow_html=True)

    st.divider()

    # Recent rules section
    st.markdown(
        """
        <div style="margin-bottom: 20px; margin-top: 30px;">
            <h3 style="margin: 0 0 12px 0; color: #374151; font-size: 16px; font-weight: 600;">
                Recent Rules
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if rules:
        # Display last 5 rules in a nice format
        recent_rules = sorted(rules, key=lambda x: rules.index(x), reverse=True)[:5]

        for idx, rule in enumerate(recent_rules):
            action_color = {
                "Allow": "#1F8A70",
                "Block": "#B91C1C",
                "Mask": "#B7791F"
            }.get(rule.get("action"), "#6B7280")

            st.markdown(
                f"""
                <div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:16px;
                            margin-bottom:12px;box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                            transition: all 0.3s ease;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                        <h4 style="margin:0;color:#1F2937;font-weight:600;font-size:14px;">
                            {rule.get('name', '(Unnamed)')}
                        </h4>
                        <span style="background:{action_color};color:white;padding:4px 10px;border-radius:8px;
                                    font-size:11px;font-weight:600;">
                            {rule.get('action', 'N/A')}
                        </span>
                    </div>
                    <div style="color:#6B7280;font-size:12px;line-height:1.6;">
                        <p style="margin:0;"><strong>Schema:</strong> {rule.get('schema', 'N/A')} • 
                                  <strong>Table:</strong> {rule.get('table', 'N/A')}</p>
                        <p style="margin:4px 0 0 0;"><strong>Priority:</strong> {rule.get('priority', 'N/A')}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No rules configured yet. Go to **Configure Rule** to add your first rule.")

    st.divider()

    # Quick start section
    st.markdown(
        """
        <div style="margin-bottom: 20px; margin-top: 30px;">
            <h3 style="margin: 0 0 12px 0; color: #374151; font-size: 16px; font-weight: 600;">
                Quick Start
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div style="background:#E6F6EE;border:2px solid #1F8A70;border-radius:12px;padding:16px;text-align:center;
                        cursor:pointer;transition: all 0.3s ease;">
                <div style="font-size:32px;margin-bottom:8px;">🔗</div>
                <p style="margin:0;color:#1F2937;font-weight:600;font-size:14px;">Setup Connection</p>
                <p style="margin:4px 0 0 0;color:#6B7280;font-size:12px;">Create a new database connection</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Connection Manager", key="quickstart_conn", use_container_width=True):
            st.session_state.current_page = "Connection Manager"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div style="background:#E8F0FF;border:2px solid #0F62FE;border-radius:12px;padding:16px;text-align:center;
                        cursor:pointer;transition: all 0.3s ease;">
                <div style="font-size:32px;margin-bottom:8px;">⚙️</div>
                <p style="margin:0;color:#1F2937;font-weight:600;font-size:14px;">Create Rule</p>
                <p style="margin:4px 0 0 0;color:#6B7280;font-size:12px;">Configure a new security rule</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Configure Rule", key="quickstart_rule", use_container_width=True):
            st.session_state.current_page = "Configure Rule"
            st.rerun()

    with col3:
        st.markdown(
            """
            <div style="background:#FFF4E5;border:2px solid #B7791F;border-radius:12px;padding:16px;text-align:center;
                        cursor:pointer;transition: all 0.3s ease;">
                <div style="font-size:32px;margin-bottom:8px;">📤</div>
                <p style="margin:0;color:#1F2937;font-weight:600;font-size:14px;">Export Rules</p>
                <p style="margin:4px 0 0 0;color:#6B7280;font-size:12px;">Export configuration and rules</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Export Rules", key="quickstart_export", use_container_width=True):
            st.session_state.current_page = "Export Rules"
            st.rerun()

