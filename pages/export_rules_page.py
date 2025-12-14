import streamlit as st
import streamlit_antd_components as sac


def render() -> None:
    # Enhanced page header
    st.markdown(
        """
        <div style="margin-bottom: 30px;">
            <h2 style="margin: 0; color: #1F2937; font-weight: 700;">Export Rules</h2>
            <p style="margin: 8px 0 0 0; color: #6B7280; font-size: 14px;">
                Export your rules in various formats for backup, sharing, or integration.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    rules = st.session_state.get("rules", [])
    if not rules:
        st.info("📭 No rules to export. Create some rules first in **Configure Rule**.")
        return

    # Export options section
    st.markdown(
        """
        <div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:24px;
                    margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <h3 style="margin: 0 0 20px 0; color: #1F2937; font-weight: 600; font-size: 16px;">
                📤 Export Options
            </h3>
        """,
        unsafe_allow_html=True,
    )

    fmt = sac.segmented(
        items=[
            sac.SegmentedItem(label='📄 JSON', icon='filetype-json'),
            sac.SegmentedItem(label='📊 CSV', icon='filetype-csv'),
            sac.SegmentedItem(label='📋 YAML', icon='filetype-yml'),
        ],
        align='start',
        size='lg'
    )

    st.markdown(
        """
        <div style="background:#F9FAFB;border-radius:8px;padding:12px;margin-top:12px;">
            <p style="margin: 0; color: #6B7280; font-size: 13px;">
        """,
        unsafe_allow_html=True,
    )

    if "JSON" in fmt:
        st.write("**JSON** - Human-readable with full fidelity. Best for backups and integrations.")
    elif "CSV" in fmt:
        st.write("**CSV** - Tabular format for spreadsheets and data pipelines.")
    else:
        st.write("**YAML** - Configuration-friendly format for DevOps workflows.")

    st.markdown("</p></div>", unsafe_allow_html=True)

    st.divider()

    # File naming
    st.markdown(
        """
        <p style="margin: 16px 0 12px 0; font-size: 13px; font-weight: 600; color: #374151; text-transform: uppercase; letter-spacing: 0.5px;">
            File Configuration
        </p>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        filename = st.text_input(
            "Filename (without extension)",
            value="rules_export",
            placeholder="rules_export",
            help="Name for your exported file"
        )

    with col2:
        st.metric("Rules", len(rules))

    st.divider()

    # Preview section
    with st.expander("👀 Preview", expanded=False):
        st.markdown(
            """
            <p style="margin: 0 0 12px 0; font-size: 12px; color: #6B7280; font-weight: 500;">
                Preview of data to be exported:
            </p>
            """,
            unsafe_allow_html=True,
        )

        if "JSON" in fmt:
            import json
            st.code(json.dumps(rules[:2], indent=2), language="json")
        elif "CSV" in fmt:
            import pandas as pd
            df = pd.DataFrame(rules[:5])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            import yaml
            st.code(yaml.dump(rules[:2], default_flow_style=False), language="yaml")

    st.divider()

    # Download buttons
    st.markdown(
        """
        <p style="margin: 16px 0 12px 0; font-size: 13px; font-weight: 600; color: #374151; text-transform: uppercase; letter-spacing: 0.5px;">
            Download
        </p>
        """,
        unsafe_allow_html=True,
    )

    if "JSON" in fmt:
        import json
        data = json.dumps(rules, indent=2).encode("utf-8")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"✅ Ready to export {len(rules)} rules as JSON")
        with col2:
            st.download_button(
                "⬇️ Download JSON",
                data=data,
                file_name=f"{filename}.json",
                mime="application/json",
                use_container_width=True
            )
    elif "CSV" in fmt:
        import csv
        import io
        output = io.StringIO()
        if rules:
            fieldnames = sorted({k for r in rules for k in r.keys()})
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for r in rules:
                writer.writerow(r)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"✅ Ready to export {len(rules)} rules as CSV")
        with col2:
            st.download_button(
                "⬇️ Download CSV",
                data=output.getvalue(),
                file_name=f"{filename}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        try:
            import yaml
            data = yaml.dump(rules, default_flow_style=False).encode("utf-8")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"✅ Ready to export {len(rules)} rules as YAML")
            with col2:
                st.download_button(
                    "⬇️ Download YAML",
                    data=data,
                    file_name=f"{filename}.yaml",
                    mime="application/x-yaml",
                    use_container_width=True
                )
        except ImportError:
            st.warning("⚠️ YAML support requires 'pyyaml' package. Please install it with: pip install pyyaml")

    st.markdown("</div>", unsafe_allow_html=True)
