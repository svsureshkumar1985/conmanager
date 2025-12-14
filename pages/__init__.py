"""Pages registry for the Enterprise Rule Manager Streamlit app.

Each page module exposes a `render()` function. This package provides
`get_page_renderer(name)` to resolve a page by its display name from the
left sidebar menu.
"""
from typing import Callable, Dict


# Import page modules and expose a registry mapping
from . import dashboard_page
from . import connection_manager_page
from . import configure_rule_page
from . import edit_rules_page
from . import export_rules_page
from . import monitor_batch_page


PAGE_REGISTRY: Dict[str, Callable[[], None]] = {
    "Dashboard": dashboard_page.render,
    "Connection Manager": connection_manager_page.render,
    "Configure Rule": configure_rule_page.render,
    "Edit Rules": edit_rules_page.render,
    "Export Rules": export_rules_page.render,
    "Monitor Batch": monitor_batch_page.render,
}


def get_page_renderer(name: str) -> Callable[[], None]:
    """Return the renderer for a page label, or a no-op if unknown."""
    def _noop():
        import streamlit as st
        st.warning(f"Page '{name}' not found.")

    return PAGE_REGISTRY.get(name, _noop)
