import streamlit as st
import streamlit_antd_components as sac


def render() -> None:
    # Enhanced page header
    st.markdown(
        """
        <div style="margin-bottom: 30px;">
            <h2 style="margin: 0; color: #1F2937; font-weight: 700;">Configure Rule</h2>
            <p style="margin: 8px 0 0 0; color: #6B7280; font-size: 14px;">
                Create new security rules for data access and manipulation control.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "rules" not in st.session_state:
        st.session_state["rules"] = []

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(
            """
            <div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:24px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <h3 style="margin: 0 0 20px 0; color: #1F2937; font-weight: 600; font-size: 16px;">
                    ⚙️ Rule Definition
                </h3>
            """,
            unsafe_allow_html=True,
        )

        with st.form("rule_form", clear_on_submit=False, border=False):
            st.markdown("<div style='padding: 10px 0;'>", unsafe_allow_html=True)

            # Rule metadata
            st.markdown(
                """
                <p style="margin: 0 0 12px 0; font-size: 13px; font-weight: 600; color: #374151; text-transform: uppercase; letter-spacing: 0.5px;">
                    📋 Rule Information
                </p>
                """,
                unsafe_allow_html=True,
            )

            rule_name = st.text_input(
                "Rule Name",
                placeholder="e.g. Mask SSN on Customers",
                help="Descriptive name for this rule"
            )

            st.divider()

            # Scope
            st.markdown(
                """
                <p style="margin: 16px 0 12px 0; font-size: 13px; font-weight: 600; color: #374151; text-transform: uppercase; letter-spacing: 0.5px;">
                    🎯 Target Scope
                </p>
                """,
                unsafe_allow_html=True,
            )

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                scope_schema = st.text_input(
                    "Schema",
                    placeholder="dbo",
                    help="Database schema name"
                )
            with col_s2:
                scope_table = st.text_input(
                    "Table",
                    placeholder="Customers",
                    help="Table name"
                )

            st.divider()

            # Condition
            st.markdown(
                """
                <p style="margin: 16px 0 12px 0; font-size: 13px; font-weight: 600; color: #374151; text-transform: uppercase; letter-spacing: 0.5px;">
                    ⚡ Condition
                </p>
                """,
                unsafe_allow_html=True,
            )

            condition = st.text_area(
                "SQL WHERE Clause",
                placeholder="e.g. ssn IS NOT NULL AND role = 'customer'",
                height=80,
                help="SQL condition that triggers this rule"
            )

            st.divider()

            # Action and Priority
            st.markdown(
                """
                <p style="margin: 16px 0 12px 0; font-size: 13px; font-weight: 600; color: #374151; text-transform: uppercase; letter-spacing: 0.5px;">
                    🎛️ Action & Priority
                </p>
                """,
                unsafe_allow_html=True,
            )

            act = sac.segmented(
                items=[
                    sac.SegmentedItem(label='✅ Allow', icon='check-circle'),
                    sac.SegmentedItem(label='🚫 Block', icon='x-circle'),
                    sac.SegmentedItem(label='🎭 Mask', icon='eye-slash'),
                ],
                align='start',
            )

            colp1, colp2 = st.columns([1, 2])
            with colp1:
                priority = st.number_input(
                    "Priority",
                    min_value=1,
                    max_value=100,
                    value=10,
                    help="Lower numbers execute first"
                )
            with colp2:
                st.caption("⚠️ Lower numbers run first; use smaller values for critical rules.")

            st.markdown("</div>", unsafe_allow_html=True)
            st.divider()

            submitted = st.form_submit_button("💾 Save Rule", use_container_width=True)

        if submitted:
            if not rule_name:
                st.error("❌ Please provide a Rule Name.")
            else:
                rule = {
                    "name": rule_name,
                    "schema": scope_schema,
                    "table": scope_table,
                    "condition": condition,
                    "action": act,
                    "priority": int(priority),
                    "connection": st.session_state.get("active_connection"),
                }
                st.session_state["rules"].append(rule)
                st.success(f"✅ Rule '{rule_name}' saved successfully!")
                st.toast("Rule created!", icon="✅")

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:24px;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <h3 style="margin: 0 0 20px 0; color: #1F2937; font-weight: 600; font-size: 16px;">
                    📊 Preview & Summary
                </h3>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <p style="margin: 0 0 12px 0; font-size: 12px; color: #6B7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">
                Total Rules Created
            </p>
            """,
            unsafe_allow_html=True,
        )

        st.metric("Rules", len(st.session_state.get("rules", [])))

        st.divider()

        # Rules statistics
        st.markdown(
            """
            <p style="margin: 0 0 12px 0; font-size: 12px; color: #6B7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">
                Rules by Action
            </p>
            """,
            unsafe_allow_html=True,
        )

        rules = st.session_state.get("rules", [])

        col_a1, col_a2, col_a3 = st.columns(3)

        with col_a1:
            allow_count = len([r for r in rules if "Allow" in str(r.get("action", ""))])
            st.metric("Allow", allow_count)

        with col_a2:
            block_count = len([r for r in rules if "Block" in str(r.get("action", ""))])
            st.metric("Block", block_count)

        with col_a3:
            mask_count = len([r for r in rules if "Mask" in str(r.get("action", ""))])
            st.metric("Mask", mask_count)

        st.divider()

        # Recent rules
        st.markdown(
            """
            <p style="margin: 16px 0 12px 0; font-size: 12px; color: #6B7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">
                Recent Rules
            </p>
            """,
            unsafe_allow_html=True,
        )

        if rules:
            for rule in rules[-3:]:
                action_color = {
                    "✅ Allow": "#1F8A70",
                    "🚫 Block": "#B91C1C",
                    "🎭 Mask": "#B7791F"
                }.get(str(rule.get("action", "")), "#6B7280")

                st.markdown(
                    f"""
                    <div style="background:#F9FAFB;border-left:4px solid {action_color};border-radius:4px;
                                padding:12px;margin-bottom:8px;">
                        <p style="margin: 0; color: #1F2937; font-weight: 600; font-size: 13px;">
                            {rule.get('name', '(Unnamed)')}
                        </p>
                        <p style="margin: 4px 0 0 0; color: #6B7280; font-size: 11px;">
                            {rule.get('schema', 'N/A')}.{rule.get('table', 'N/A')} • Priority: {rule.get('priority', 'N/A')}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("📭 No rules created yet. Create your first rule on the left!")

        st.markdown("</div>", unsafe_allow_html=True)
