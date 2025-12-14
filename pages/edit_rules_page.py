import streamlit as st
import streamlit_antd_components as sac


def _rules_df():
    import pandas as pd
    return pd.DataFrame(st.session_state.get("rules", []))


def render() -> None:
    # Enhanced page header
    st.markdown(
        """
        <div style="margin-bottom: 30px;">
            <h2 style="margin: 0; color: #1F2937; font-weight: 700;">Edit Rules</h2>
            <p style="margin: 8px 0 0 0; color: #6B7280; font-size: 14px;">
                View, filter, and manage existing rules.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    rules = st.session_state.get("rules", [])
    if not rules:
        st.info("📭 No rules yet. Go to **Configure Rule** to add one.")
        return

    # Filters section
    st.markdown(
        """
        <div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:20px;
                    margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <h3 style="margin: 0 0 16px 0; color: #1F2937; font-weight: 600; font-size: 15px;">
                🔍 Filters & Search
            </h3>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        q = st.text_input("Search rules", placeholder="Filter by name, schema, table, or action")

    with col2:
        action_filter = sac.segmented(
            items=[
                sac.SegmentedItem(label='All'),
                sac.SegmentedItem(label='✅ Allow'),
                sac.SegmentedItem(label='🚫 Block'),
                sac.SegmentedItem(label='🎭 Mask'),
            ],
            align='end',
            size='sm',
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Filter data
    data = rules
    if q:
        ql = q.lower()
        data = [r for r in data if any(str(r.get(k, "")).lower().find(ql) >= 0 for k in ("name", "schema", "table", "action"))]

    if action_filter != 'All':
        # Handle both old format and new with icons
        action_key = action_filter.split()[-1] if ' ' in action_filter else action_filter
        data = [r for r in data if action_key in str(r.get("action", ""))]

    # Display rules
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <p style="margin: 0; color: #6B7280; font-size: 12px;">
                Showing <strong>{}</strong> of <strong>{}</strong> rules
            </p>
        </div>
        """.format(len(data), len(rules)),
        unsafe_allow_html=True,
    )

    if data:
        df = _rules_df()
        if data != rules:
            import pandas as pd
            df = pd.DataFrame(data)

        # Custom dataframe display
        for idx, rule in enumerate(data):
            action_color = {
                "✅ Allow": "#1F8A70",
                "🚫 Block": "#B91C1C",
                "🎭 Mask": "#B7791F"
            }.get(str(rule.get("action", "")), "#6B7280")

            st.markdown(
                f"""
                <div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:16px;
                            margin-bottom:12px;box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                        <div>
                            <h4 style="margin:0 0 4px 0;color:#1F2937;font-weight:600;font-size:15px;">
                                {rule.get('name', '(Unnamed)')}
                            </h4>
                            <p style="margin:0;color:#6B7280;font-size:12px;">
                                {rule.get('schema', 'N/A')}.{rule.get('table', 'N/A')}
                            </p>
                        </div>
                        <div style="display:flex;gap:8px;">
                            <span style="background:{action_color};color:white;padding:4px 12px;border-radius:8px;
                                        font-size:11px;font-weight:600;">
                                {rule.get('action', 'N/A')}
                            </span>
                            <span style="background:#F3F4F6;color:#6B7280;padding:4px 12px;border-radius:8px;
                                        font-size:11px;font-weight:600;">
                                P{rule.get('priority', 'N/A')}
                            </span>
                        </div>
                    </div>
                    <div style="background:#F9FAFB;border-radius:8px;padding:10px;margin-bottom:12px;
                                border-left:3px solid {action_color};">
                        <p style="margin:0;color:#6B7280;font-size:12px;font-family:monospace;">
                            {rule.get('condition', '(No condition)')}
                        </p>
                    </div>
                """,
                unsafe_allow_html=True,
            )

            col_d1, col_d2, col_d3 = st.columns(3)

            with col_d1:
                if st.button("🔍 View", key=f"view_{idx}", use_container_width=True):
                    st.info(
                        f"""
                        **Rule Name:** {rule.get('name')}
                        
                        **Schema:** {rule.get('schema')}
                        
                        **Table:** {rule.get('table')}
                        
                        **Action:** {rule.get('action')}
                        
                        **Priority:** {rule.get('priority')}
                        
                        **Condition:** {rule.get('condition')}
                        """
                    )

            with col_d2:
                if st.button("✏️ Edit", key=f"edit_{idx}", use_container_width=True):
                    st.info("Edit functionality coming soon!")

            with col_d3:
                if st.button("🗑️ Delete", key=f"del_{idx}", use_container_width=True):
                    st.session_state["_confirm_delete_idx"] = idx

            # Confirmation dialog
            if st.session_state.get("_confirm_delete_idx") == idx:
                st.warning(f"⚠️ Are you sure you want to delete '{rule.get('name')}'?")
                cc1, cc2 = st.columns(2)
                with cc1:
                    if st.button("Cancel", key=f"cancel_{idx}"):
                        st.session_state.pop("_confirm_delete_idx", None)
                with cc2:
                    if st.button("Confirm Delete", type="primary", key=f"confirm_{idx}"):
                        st.session_state["rules"].pop(idx)
                        st.session_state.pop("_confirm_delete_idx", None)
                        st.success(f"✅ Rule '{rule.get('name')}' deleted!")
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("🔍 No rules match your filters. Try adjusting your search or filters.")
