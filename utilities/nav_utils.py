"""Navigation and layout utilities for the enterprise app.

Provides:
- render_header_enhanced(): responsive top bar with connection status
- get_connection_status(): returns connection status info
"""
import streamlit as st


def render_header_enhanced(title: str = "Enterprise Rule Manager") -> None:
    """Render a professional top header with connection status badge."""
    active = st.session_state.get("active_connection")

    # Status badge HTML
    if active:
        status_html = f"""
        <div style='display:inline-flex;align-items:center;gap:6px;
                    background:#E6F6EE;color:#1F8A70;padding:6px 12px;
                    border-radius:16px;font-weight:600;font-size:13px;'>
            <span style='width:8px;height:8px;border-radius:50%;background:#1F8A70;display:inline-block;'></span>
            Active: {active}
        </div>
        """
    else:
        status_html = """
        <div style='display:inline-flex;align-items:center;gap:6px;
                    background:#FFF4E5;color:#B7791F;padding:6px 12px;
                    border-radius:16px;font-weight:600;font-size:13px;'>
            <span style='width:8px;height:8px;border-radius:50%;background:#B7791F;display:inline-block;'></span>
            No Active Connection
        </div>
        """

    # Enhanced header with gradient background
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    background: linear-gradient(135deg, #0F62FE 0%, #0053D6 100%);
                    padding:16px 24px;margin:-10px -10px 20px -10px;
                    border-bottom: 3px solid #0053D6;box-shadow: 0 2px 8px rgba(15, 98, 254, 0.15);
                    position:relative;z-index:50;">
            <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:32px;height:32px;border-radius:8px;background:rgba(255,255,255,0.2);
                           display:flex;align-items:center;justify-content:center;
                           font-size:18px;font-weight:bold;color:white;box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    ⚙️
                </div>
                <div>
                    <h1 style="color:white;margin:0;font-size:20px;font-weight:700;letter-spacing:.5px;">
                        {title}
                    </h1>
                    <p style="color:rgba(255,255,255,0.85);margin:2px 0 0 0;font-size:11px;letter-spacing:.3px;">
                        Secure Rule Management & Configuration
                    </p>
                </div>
            </div>
            <div>{status_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_connection_status() -> dict:
    """Return connection status information."""
    active = st.session_state.get("active_connection")
    return {
        "connected": bool(active),
        "name": active,
        "status": "Connected" if active else "Disconnected",
    }


def render_metric_card(title: str, value: str, icon: str = "📊", color: str = "#0F62FE") -> None:
    """Render a metric card with icon, title, and value."""
    st.markdown(
        f"""
        <div style="background:white;border:1px solid #E5E7EB;border-radius:12px;
                    padding:16px;text-align:center;box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                    transition: all 0.3s ease;">
            <div style="font-size:32px;margin-bottom:8px;">{icon}</div>
            <p style="color:#6B7280;font-size:13px;font-weight:500;margin:0 0 4px 0;text-transform:uppercase;letter-spacing:0.5px;">
                {title}
            </p>
            <p style="color:{color};font-size:28px;font-weight:700;margin:0;">
                {value}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

