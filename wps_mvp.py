import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="WPS Disaster Prioritization", layout="wide")

# -------------------------
# Custom CSS for better styling
# -------------------------
st.markdown("""
<style>
    .priority-card {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .high-priority {
        border-left: 5px solid #ff4444;
        background-color: #fff5f5;
    }
    .medium-priority {
        border-left: 5px solid #ffaa44;
        background-color: #fffbf0;
    }
    .low-priority {
        border-left: 5px solid #44ff44;
        background-color: #f0fff0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Initialize session state for storing multiple entries
# -------------------------
if 'lgu_entries' not in st.session_state:
    st.session_state.lgu_entries = []

# -------------------------
# Helper function for normalization
# -------------------------
def normalize_single(column):
    """Normalize a single column of data"""
    if len(column) == 0:
        return column
    if column.max() == column.min():
        return column * 0
    return (column - column.min()) / (column.max() - column.min())

def calculate_priorities(entries_df):
    """Calculate priority scores for all entries"""
    if len(entries_df) == 0:
        return entries_df
    
    # Normalize each criterion
    entries_df['Norm_Casualties'] = normalize_single(entries_df['Casualties'])
    entries_df['Norm_Affected'] = normalize_single(entries_df['Affected Families'])
    entries_df['Norm_Damaged'] = normalize_single(entries_df['Damaged Houses'])
    
    # Equal weighting (WSM)
    weight = 1/3
    entries_df['Priority Score'] = (
        entries_df['Norm_Casualties'] * weight +
        entries_df['Norm_Affected'] * weight +
        entries_df['Norm_Damaged'] * weight
    )
    
    return entries_df

# -------------------------
# Title
# -------------------------
st.title("🏥 Weighted Priority Scheduler (WPS)")
st.subheader("Disaster Response Prioritization System")

# Create tabs for the two interfaces
tab1, tab2 = st.tabs(["📝 LGU Data Entry & Queue", "📊 Results & Analysis"])

# ==================== TAB 1: LGU DATA ENTRY & QUEUE ====================
with tab1:
    st.header("LGU Disaster Impact Assessment")
    st.markdown("---")
    
    # Input form for LGU data
    with st.form("lgu_input_form"):
        st.subheader("Enter Disaster Impact Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            region_name = st.text_input("Region/Municipality Name", placeholder="e.g., Region A, Manila City")
            casualties = st.number_input("Number of Casualties", min_value=0, step=1, value=0)
            affected_families = st.number_input("Number of Affected Families", min_value=0, step=1, value=0)
        
        with col2:
            damaged_houses = st.number_input("Number of Damaged Houses", min_value=0, step=1, value=0)
            additional_notes = st.text_area("Additional Notes (Optional)", placeholder="Any special circumstances...")
        
        submitted = st.form_submit_button("Generate Priority Score & Add to Queue")
        
        if submitted:
            if region_name:
                # Create temporary entry
                new_entry = {
                    'Region': region_name,
                    'Casualties': casualties,
                    'Affected Families': affected_families,
                    'Damaged Houses': damaged_houses,
                    'Timestamp': datetime.now(),
                    'Notes': additional_notes
                }
                
                # Add to session state
                st.session_state.lgu_entries.append(new_entry)
                
                # Recalculate all priorities
                df_temp = pd.DataFrame(st.session_state.lgu_entries)
                df_temp = calculate_priorities(df_temp)
                
                # Update session state with calculated scores
                st.session_state.lgu_entries = df_temp.to_dict('records')
                
                st.success(f"✅ Added {region_name} to the queue")
                st.balloons()
            else:
                st.error("Please enter a Region/Municipality name")
    
    # Display current queue
    st.markdown("---")
    st.subheader("📍 Current Response Queue")
    
    if st.session_state.lgu_entries:
        queue_df = pd.DataFrame(st.session_state.lgu_entries)
        queue_df_sorted = queue_df.sort_values('Priority Score', ascending=False).reset_index(drop=True)
        
        # Display queue with priority indicators
        for idx, row in queue_df_sorted.iterrows():
            # Determine priority level and class
            if row['Priority Score'] >= 0.66:
                priority_level = "🔴 HIGH PRIORITY"
                priority_class = "high-priority"
            elif row['Priority Score'] >= 0.33:
                priority_level = "🟡 MEDIUM PRIORITY"
                priority_class = "medium-priority"
            else:
                priority_level = "🟢 LOW PRIORITY"
                priority_class = "low-priority"
            
            with st.container():
                st.markdown(f"""
                <div class="info-box {priority_class}" style="padding: 15px; margin: 10px 0;">
                    <h3>#{idx + 1} - {row['Region']}</h3>
                    <p><strong>Priority Score:</strong> {row['Priority Score']:.3f} - {priority_level}</p>
                    <p><strong>Impact Data:</strong> {int(row['Casualties'])} casualties, {int(row['Affected Families'])} families affected, {int(row['Damaged Houses'])} houses damaged</p>
                    <p><small>Submitted: {row['Timestamp'].strftime('%Y-%m-%d %H:%M') if isinstance(row['Timestamp'], datetime) else row['Timestamp']}</small></p>
                    {f"<p><small>Notes: {row['Notes']}</small></p>" if row.get('Notes') else ""}
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 1, 4])
                with col1:
                    if st.button(f"⬆️ Move Up", key=f"up_{idx}_{row['Region']}"):
                        if idx > 0:
                            # Swap positions
                            current_idx = queue_df_sorted.index[queue_df_sorted['Region'] == row['Region']].tolist()[0]
                            if current_idx > 0:
                                # This is a simplified version - in practice, you might want to implement reordering
                                st.info("Manual reordering is disabled as priority is calculated automatically")
                
                with col2:
                    if st.button(f"🗑️ Remove", key=f"remove_{idx}_{row['Region']}"):
                        st.session_state.lgu_entries = [e for e in st.session_state.lgu_entries if e['Region'] != row['Region']]
                        st.rerun()
        
        # Add clear all button
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🗑️ Clear All Entries", type="secondary"):
                st.session_state.lgu_entries = []
                st.rerun()
        
        # Show queue statistics
        st.markdown("---")
        st.subheader("Queue Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            high_count = len(queue_df_sorted[queue_df_sorted['Priority Score'] >= 0.66])
            st.metric("High Priority Areas", high_count)
        with col2:
            medium_count = len(queue_df_sorted[(queue_df_sorted['Priority Score'] >= 0.33) & (queue_df_sorted['Priority Score'] < 0.66)])
            st.metric("Medium Priority Areas", medium_count)
        with col3:
            low_count = len(queue_df_sorted[queue_df_sorted['Priority Score'] < 0.33])
            st.metric("Low Priority Areas", low_count)
            
    else:
        st.info("No entries in the queue yet. Use the form above to add disaster-affected areas.")

# ==================== TAB 2: RESULTS & ANALYSIS ====================
with tab2:
    st.header("📊 Priority Analysis & Recommendations")
    st.markdown("---")
    
    if st.session_state.lgu_entries:
        # Prepare data for analysis
        results_df = pd.DataFrame(st.session_state.lgu_entries)
        results_df_sorted = results_df.sort_values('Priority Score', ascending=False).reset_index(drop=True)
        
        # Display prioritized regions with enhanced visualization
        st.subheader("🎯 Prioritized Regions")
        
        # Create a horizontal bar chart for better visualization
        chart_data = results_df_sorted.set_index('Region')['Priority Score']
        
        # Use Streamlit's native bar chart
        st.bar_chart(chart_data, height=400)
        
        # Add a color-coded table
        st.subheader("📋 Priority Ranking Table")
        
        # Create a styled dataframe
        display_df = results_df_sorted[['Region', 'Priority Score', 'Casualties', 'Affected Families', 'Damaged Houses']].copy()
        display_df['Priority Score'] = display_df['Priority Score'].round(3)
        display_df['Priority Level'] = pd.cut(
            display_df['Priority Score'],
            bins=[-float('inf'), 0.33, 0.66, float('inf')],
            labels=['Low', 'Medium', 'High']
        )
        
        # Display the dataframe with styling
        st.dataframe(
            display_df,
            column_config={
                "Region": "Region/Municipality",
                "Priority Score": st.column_config.NumberColumn("Priority Score", format="%.3f"),
                "Casualties": st.column_config.NumberColumn("Casualties", format="%d"),
                "Affected Families": st.column_config.NumberColumn("Affected Families", format="%d"),
                "Damaged Houses": st.column_config.NumberColumn("Damaged Houses", format="%d"),
                "Priority Level": st.column_config.TextColumn("Priority Level"),
            },
            use_container_width=True,
            hide_index=True,
        )
        
        # Create metrics columns
        st.markdown("---")
        st.subheader("📈 Summary Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Areas Assessed", len(results_df_sorted))
        with col2:
            st.metric("Highest Priority Score", f"{results_df_sorted['Priority Score'].max():.3f}")
        with col3:
            st.metric("Average Priority Score", f"{results_df_sorted['Priority Score'].mean():.3f}")
        with col4:
            st.metric("Median Priority Score", f"{results_df_sorted['Priority Score'].median():.3f}")
        
        # Display detailed analysis with estimated response times
        st.markdown("---")
        st.subheader("⏱️ Estimated Response Timeline")
        
        for idx, row in results_df_sorted.iterrows():
            # Determine priority level
            if row['Priority Score'] >= 0.66:
                priority_level = "🔴 HIGH"
                priority_color = "#ff4444"
                response_hours = "0-24"
            elif row['Priority Score'] >= 0.33:
                priority_level = "🟡 MEDIUM"
                priority_color = "#ffaa44"
                response_hours = "24-72"
            else:
                priority_level = "🟢 LOW"
                priority_color = "#44ff44"
                response_hours = "72+"
            
            # Calculate estimated deployment time
            if idx == 0:
                deployment_time = "Immediate (Within 24 hours)"
                time_icon = "🚨"
            elif idx == 1:
                deployment_time = "Urgent (24-48 hours)"
                time_icon = "⚠️"
            elif idx == 2:
                deployment_time = "Scheduled (48-72 hours)"
                time_icon = "📅"
            else:
                hours = 72 + (idx - 2) * 12
                deployment_time = f"Scheduled ({hours}+ hours)"
                time_icon = "⏰"
            
            with st.expander(f"{idx + 1}. {row['Region']} - {priority_level} Priority", expanded=(idx==0)):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **Priority Score:** {row['Priority Score']:.3f}  
                    **Priority Level:** {priority_level}  
                    **Response Timeframe:** {response_hours} hours  
                    **Deployment Status:** {time_icon} {deployment_time}
                    """)
                    
                    st.markdown("**Impact Metrics:**")
                    st.write(f"- Casualties: {int(row['Casualties'])}")
                    st.write(f"- Affected Families: {int(row['Affected Families'])}")
                    st.write(f"- Damaged Houses: {int(row['Damaged Houses'])}")
                
                with col2:
                    st.markdown("**Normalized Impact Scores:**")
                    st.write(f"- Casualties Impact: {row['Norm_Casualties']:.3f}")
                    st.write(f"- Families Impact: {row['Norm_Affected']:.3f}")
                    st.write(f"- Housing Impact: {row['Norm_Damaged']:.3f}")
                    
                    # Resource allocation suggestion
                    if row['Priority Score'] >= 0.66:
                        st.warning("**Resource Allocation:** Priority 1 - Immediate deployment of full response team")
                    elif row['Priority Score'] >= 0.33:
                        st.info("**Resource Allocation:** Priority 2 - Deploy assessment team, prepare resources")
                    else:
                        st.success("**Resource Allocation:** Priority 3 - Monitor situation, schedule regular assessment")
                    
                    if row.get('Notes'):
                        st.markdown(f"**Notes:** {row['Notes']}")
        
        # Strategic recommendations
        st.markdown("---")
        st.subheader("💡 Strategic Recommendations")
        
        # Generate recommendations based on data
        high_priority_count = len(results_df_sorted[results_df_sorted['Priority Score'] >= 0.66])
        medium_priority_count = len(results_df_sorted[(results_df_sorted['Priority Score'] >= 0.33) & (results_df_sorted['Priority Score'] < 0.66)])
        low_priority_count = len(results_df_sorted[results_df_sorted['Priority Score'] < 0.33])
        
        # Calculate total impact
        total_casualties = results_df_sorted['Casualties'].sum()
        total_families = results_df_sorted['Affected Families'].sum()
        total_houses = results_df_sorted['Damaged Houses'].sum()
        
        st.markdown(f"""
        <div class="priority-card">
            <h3>📋 Response Strategy Based on Priority Distribution</h3>
            <p><strong>Immediate Response Required:</strong> {high_priority_count} area(s) need urgent attention within 24 hours.</p>
            <p><strong>Secondary Response:</strong> {medium_priority_count} area(s) should be addressed within 48-72 hours.</p>
            <p><strong>Monitored Response:</strong> {low_priority_count} area(s) can be scheduled for routine assessment.</p>
            <br>
            <h4>📊 Total Impact Assessment:</h4>
            <ul>
                <li>Total Casualties: {int(total_casualties)}</li>
                <li>Total Affected Families: {int(total_families)}</li>
                <li>Total Damaged Houses: {int(total_houses)}</li>
            </ul>
            <br>
            <h4>🎯 Resource Allocation Recommendation:</h4>
            <ul>
                <li>Allocate <strong>{min(70, 30 + high_priority_count * 20)}%</strong> of available resources to high-priority areas</li>
                <li>Distribute <strong>{min(50, 20 + medium_priority_count * 15)}%</strong> of resources to medium-priority areas</li>
                <li>Reserve <strong>{max(10, 20 - low_priority_count * 5)}%</strong> for low-priority and emerging needs</li>
            </ul>
            <br>
            <h4>📌 Key Action Items:</h4>
            <ol>
                <li>Immediately mobilize response teams to {high_priority_count} high-priority area(s)</li>
                <li>Conduct detailed damage assessment for medium-priority areas</li>
                <li>Establish communication channels with local government units</li>
                <li>Coordinate resource allocation based on priority scores</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Export functionality
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📥 Export Priority Report (CSV)", use_container_width=True):
                export_df = results_df_sorted[['Region', 'Priority Score', 'Casualties', 'Affected Families', 'Damaged Houses', 'Priority Level']].copy()
                export_df['Priority Score'] = export_df['Priority Score'].round(3)
                export_df['Priority Level'] = pd.cut(
                    export_df['Priority Score'],
                    bins=[-float('inf'), 0.33, 0.66, float('inf')],
                    labels=['Low', 'Medium', 'High']
                )
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="Click to Download CSV",
                    data=csv,
                    file_name=f"disaster_priority_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        # Add methodology explanation
        with st.expander("ℹ️ About the Prioritization Methodology"):
            st.markdown("""
            ### Weighted Priority Scheduler (WPS) Methodology
            
            This system uses the **Weighted Sum Model (WSM)** with equal weighting for disaster prioritization:
            
            **1. Data Normalization:**
            - Min-max normalization is applied to each criterion
            - Formula: `(value - min) / (max - min)`
            - Results in normalized scores between 0 and 1
            
            **2. Equal Weighting:**
            - Casualties: 33.3% weight
            - Affected Families: 33.3% weight
            - Damaged Houses: 33.3% weight
            
            **3. Priority Score Calculation:**
            - `Score = (Norm_Casualties × 0.333) + (Norm_Affected × 0.333) + (Norm_Damaged × 0.333)`
            
            **4. Priority Classification:**
            - High Priority: Score ≥ 0.66
            - Medium Priority: 0.33 ≤ Score < 0.66
            - Low Priority: Score < 0.33
            
            **5. Response Time Estimation:**
            - Based on queue position and priority score
            - Higher priority areas receive immediate response
            - Lower priority areas scheduled based on available resources
            """)
            
    else:
        st.warning("No data available. Please go to the 'LGU Data Entry & Queue' tab to add disaster-affected areas first.")
        st.info("💡 Tip: You can add multiple LGUs to compare their priority scores and get response time estimates.")
