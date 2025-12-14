import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
from datetime import datetime, timedelta


def render() -> None:
    # Enhanced page header
    st.markdown(
        """
        <div style="margin-bottom: 30px;">
            <h2 style="margin: 0; color: #1F2937; font-weight: 700;">Monitor Batch</h2>
            <p style="margin: 8px 0 0 0; color: #6B7280; font-size: 14px;">
                Track the status of batch operations and rule enforcement jobs.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "_batches" not in st.session_state:
        st.session_state["_batches"] = [
            {"id": 1, "job": "Nightly enforcement", "status": "Success", "progress": 100, "duration": "5m 23s", "timestamp": datetime.now() - timedelta(hours=2)},
            {"id": 2, "job": "PII scan", "status": "Running", "progress": 65, "duration": "2m 15s", "timestamp": datetime.now()},
            {"id": 3, "job": "Weekly export", "status": "Pending", "progress": 0, "duration": "-", "timestamp": datetime.now() + timedelta(hours=1)},
            {"id": 4, "job": "Mask audit check", "status": "Success", "progress": 100, "duration": "3m 45s", "timestamp": datetime.now() - timedelta(days=1)},
        ]

    # Control panel
    st.markdown(
        """
        <div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:20px;
                    margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <h3 style="margin: 0 0 16px 0; color: #1F2937; font-weight: 600; font-size: 15px;">
                🎮 Monitoring Controls
            </h3>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status = sac.segmented(
            items=[
                sac.SegmentedItem(label='All'),
                sac.SegmentedItem(label='⏳ Pending'),
                sac.SegmentedItem(label='▶️ Running'),
                sac.SegmentedItem(label='✅ Success'),
                sac.SegmentedItem(label='❌ Failed'),
            ],
            align='start',
            size='sm'
        )

    with col2:
        auto = st.toggle("🔄 Auto-refresh", value=False)

    with col3:
        if auto:
            interval = st.select_slider("Interval", options=[5, 10, 15, 30, 60], value=15)
        else:
            st.write("")

    with col4:
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.toast("✅ Data refreshed!", icon="🔄")

    st.markdown("</div>", unsafe_allow_html=True)

    # Filter batches
    data = st.session_state["_batches"]

    status_filter = None
    if "All" not in status and status:
        # Extract status from segmented value (e.g., "⏳ Pending" -> "Pending")
        status_filter = status.split()[-1] if ' ' in status else status
        data = [b for b in data if b["status"] == status_filter]

    # Summary stats
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        success_count = len([b for b in st.session_state["_batches"] if b["status"] == "Success"])
        st.metric("✅ Successful", success_count)

    with col2:
        running_count = len([b for b in st.session_state["_batches"] if b["status"] == "Running"])
        st.metric("▶️ Running", running_count)

    with col3:
        pending_count = len([b for b in st.session_state["_batches"] if b["status"] == "Pending"])
        st.metric("⏳ Pending", pending_count)

    with col4:
        failed_count = len([b for b in st.session_state["_batches"] if b["status"] == "Failed"])
        st.metric("❌ Failed", failed_count)

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # Display batches
    st.markdown(
        """
        <p style="margin: 16px 0 12px 0; font-size: 13px; font-weight: 600; color: #374151; text-transform: uppercase; letter-spacing: 0.5px;">
            📊 Batch Jobs
        </p>
        """,
        unsafe_allow_html=True,
    )

    if data:
        for batch in data:
            status_badge = batch["status"]
            status_color = {
                "Success": "#1F8A70",
                "Running": "#0F62FE",
                "Pending": "#B7791F",
                "Failed": "#B91C1C"
            }.get(status_badge, "#6B7280")

            status_icon = {
                "Success": "✅",
                "Running": "▶️",
                "Pending": "⏳",
                "Failed": "❌"
            }.get(status_badge, "❓")

            st.markdown(
                f"""
                <div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:16px;
                            margin-bottom:12px;box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                        <div>
                            <h4 style="margin:0 0 4px 0;color:#1F2937;font-weight:600;font-size:15px;">
                                #{batch['id']} - {batch['job']}
                            </h4>
                            <p style="margin:0;color:#6B7280;font-size:12px;">
                                Started: {batch['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                            </p>
                        </div>
                        <span style="background:{status_color};color:white;padding:6px 14px;border-radius:8px;
                                    font-size:12px;font-weight:600;display:flex;align-items:center;gap:4px;">
                            {status_icon} {status_badge}
                        </span>
                    </div>
                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                            <span style="font-size:12px;color:#6B7280;font-weight:500;">Progress</span>
                            <span style="font-size:12px;color:#1F2937;font-weight:600;">{batch['progress']}%</span>
                        </div>
                        <div style="background:#F3F4F6;border-radius:8px;height:6px;overflow:hidden;">
                            <div style="background:{status_color};height:100%;width:{batch['progress']}%;
                                       transition: width 0.3s ease;"></div>
                        </div>
                    </div>
                    <div style="display:flex;justify-content:space-between;color:#6B7280;font-size:12px;">
                        <span>⏱️ Duration: {batch['duration']}</span>
                        <span>ID: {batch['id']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("📭 No batches match your filter.")
