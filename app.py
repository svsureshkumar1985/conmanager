import streamlit as st
from streamlit_option_menu import option_menu
# import streamlit_antd_components as sac

from utilities.nav_utils import render_header_enhanced, get_connection_status
from pages import get_page_renderer


st.set_page_config(
    layout="wide",
    page_title="Enterprise Rule Manager",
    initial_sidebar_state="expanded"
)

# Load base CSS
try:
    from pathlib import Path
    css_path = Path(__file__).with_name("css") / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
except Exception:
    pass


# Initialize session state
if "active_connection" not in st.session_state:
    st.session_state.active_connection = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Connection Manager"

def app():
    # Render top header
    render_header_enhanced()

    # Check if user is connected
    is_connected = bool(st.session_state.get("active_connection"))

    if not is_connected:
        # User not connected - hide sidebar completely with CSS
        st.markdown(
            """
            <style>
                section[data-testid="stSidebar"] {
                    display: none !important;
                }
                [data-testid="stMainBlockContainer"] {
                    margin-left: 0 !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
        # Show only Connection Manager, no sidebar
        renderer = get_page_renderer("Connection Manager")
        renderer()
    else:
        # User is connected - show sidebar with navigation
        with st.sidebar:
            # Main navigation menu (without Connection Manager)
            nav_options = ["Dashboard", "Configure Rule", "Edit Rules", "Export Rules", "Monitor Batch"]
            nav_icons = ["speedometer2", "sliders2", "pencil-square", "box-arrow-down", "speedometer2"]

            selected = option_menu(
                menu_title=None,
                options=nav_options,
                icons=nav_icons,
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "#F9FAFB"},
                    "icon": {"color": "#0F62FE", "font-size": "18px"},
                    "nav-link": {
                        "font-size": "15px",
                        "text-align": "left",
                        "margin": "6px 0",
                        "padding": "12px 15px",
                        "border-radius": "8px",
                        "transition": "all 0.3s",
                    },
                    "nav-link-selected": {
                        "background-color": "#0F62FE",
                        "color": "white",
                        "font-weight": "600",
                        "border-radius": "8px",
                        "box-shadow": "0 2px 8px rgba(15, 98, 254, 0.2)"
                    },
                }
            )

            st.session_state.current_page = selected

            st.divider()

            # Logout button
            if st.button("Logout", use_container_width=True, key="logout_btn"):
                st.session_state.active_connection = None
                st.session_state.current_page = "Connection Manager"
                st.rerun()

            st.divider()

            # Footer info in sidebar
            st.markdown(
                """
                <div style="padding: 10px 0; margin-top: 30px; font-size: 11px; color: #9CA3AF; text-align: center; border-top: 1px solid #E5E7EB; padding-top: 15px;">
                    <p style="margin: 0;">Enterprise Rule Manager</p>
                    <p style="margin: 4px 0 0 0;">v1.0.0</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Main content area - only show pages that require connection
        current_page = st.session_state.current_page

        # Route to the appropriate page renderer
        renderer = get_page_renderer(current_page)
        renderer()


if __name__ == "__main__":
    app()
