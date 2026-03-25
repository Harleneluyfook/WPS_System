import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

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
</style>
""", unsafe_allow_html=True)

# -------------------------
# Initialize session state for storing multiple entries
# -------------------------
if 'lgu_entries' not in st.session_state:
    st.session_state.lgu_entries = []
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

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
                # Calculate normalized scores for this single entry
                # For normalization, we need context from existing entries
                if st.session_state.lgu_entries:
                    # Combine with existing entries for normalization context
                    temp_df = pd.DataFrame(st.session_state.lgu_entries)
                    temp_df = pd.concat([temp_df, pd.DataFrame([{
                        'Region': region_name,
                        'Casualties': casualties,
                        'Affected Families': affected_families,
                        'Damaged Houses': damaged_houses
                    }])], ignore_index=True)
                    
                    # Normalize using all data
                    temp_df['Norm_Casualties'] = normalize_single(temp_df['Casualties'])
                    temp_df['Norm_Affected'] = normalize_single(temp_df['Affected Families'])
                    temp_df['Norm_Damaged'] = normalize_single(temp_df['Damaged Houses'])
                    
                    weight = 1/3
                    temp_df['Priority Score'] = (
                        temp_df['Norm_Casualties'] * weight +
                        temp_df['Norm_Affected'] * weight +
                        temp_df['Norm_Damaged'] * weight
                    )
                    
                    # Get the score for the new entry
                    new_score = temp_df.iloc[-1]['Priority Score']
                else:
                    # First entry - assign default score
                    new_score = 0.5  # Middle priority for first entry
                
                # Add to session state
                st.session_state.lgu_entries.append({
                    'Region': region_name,
                    'Casualties': casualties,
                    'Affected Families': affected_families,
                    'Damaged Houses': damaged_houses,
                    'Priority Score': new_score,
                    'Timestamp': datetime.now(),
                    'Notes': additional_notes
                })
                
                st.success(f"✅ Added {region_name} to the queue with Priority Score: {new_score:.3f}")
            else:
                st.error("Please enter a Region/Municipality name")
    
    # Display current queue
    st.markdown("---")
    st.subheader("📍 Current Response Queue")
    
    if st.session_state.lgu_entries:
        # Convert to DataFrame for display
        queue_df = pd.DataFrame(st.session_state.lgu_entries)
        
        # Recalculate priorities with full context
        temp_df = queue_df[['Region', 'Casualties', 'Affected Families', 'Damaged Houses']].copy()
        temp_df['Norm_Casualties'] = normalize_single(temp_df['Casualties'])
        temp_df['Norm_Affected'] = normalize_single(temp_df['Affected Families'])
        temp_df['Norm_Damaged'] = normalize_single(temp_df['Damaged Houses'])
        
        weight = 1/3
        temp_df['Priority Score'] = (
            temp_df['Norm_Casualties'] * weight +
            temp_df['Norm_Affected'] * weight +
            temp_df['Norm_Damaged'] * weight
        )
        
        # Sort by priority score
        queue_df['Priority Score'] = temp_df['Priority Score']
        queue_df_sorted = queue_df.sort_values('Priority Score', ascending=False).reset_index(drop=True)
        
        # Display queue with priority indicators
        for idx, row in queue_df_sorted.iterrows():
            priority_level = "🔴 HIGH" if row['Priority Score'] >= 0.66 else "🟡 MEDIUM" if row['Priority Score'] >= 0.33 else "🟢 LOW"
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div class="info-box">
                        <h3>{idx + 1}. {row['Region']}</h3>
                        <p><strong>Priority Score:</strong> {row['Priority Score']:.3f} - {priority_level}</p>
                        <p><strong>Impact Data:</strong> {row['Casualties']} casualties, {row['Affected Families']} families affected, {row['Damaged Houses']} houses damaged</p>
                        <p><small>Submitted: {row['Timestamp'].strftime('%Y-%m-%d %H:%M')}</small></p>
                        {f"<p><small>Notes: {row['Notes']}</small></p>" if row['Notes'] else ""}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"Remove {row['Region']}", key=f"remove_{idx}"):
                        st.session_state.lgu_entries = [e for e in st.session_state.lgu_entries if e['Region'] != row['Region']]
                        st.rerun()
        
        # Add clear all button
        if st.button("🗑️ Clear All Entries", type="secondary"):
            st.session_state.lgu_entries = []
            st.rerun()
            
    else:
        st.info("No entries in the queue yet. Use the form above to add disaster-affected areas.")

# ==================== TAB 2: RESULTS & ANALYSIS ====================
with tab2:
    st.header("📊 Priority Analysis & Recommendations")
    st.markdown("---")
    
    if st.session_state.lgu_entries:
        # Prepare data for analysis
        results_df = pd.DataFrame(st.session_state.lgu_entries)
        
        # Recalculate normalized scores
        results_df['Norm_Casualties'] = normalize_single(results_df['Casualties'])
        results_df['Norm_Affected'] = normalize_single(results_df['Affected Families'])
        results_df['Norm_Damaged'] = normalize_single(results_df['Damaged Houses'])
        
        weight = 1/3
        results_df['Priority Score'] = (
            results_df['Norm_Casualties'] * weight +
            results_df['Norm_Affected'] * weight +
            results_df['Norm_Damaged'] * weight
        )
        
        results_df_sorted = results_df.sort_values('Priority Score', ascending=False).reset_index(drop=True)
        
        # Display prioritized regions with enhanced visualization
        st.subheader("🎯 Prioritized Regions")
        
        # Create a better visualization using plotly
        fig = px.bar(results_df_sorted, 
                     x='Region', 
                     y='Priority Score',
                     color='Priority Score',
                     color_continuous_scale=['green', 'yellow', 'red'],
                     title='Priority Scores by Region',
                     text='Priority Score')
        
        fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig.update_layout(
            xaxis_title="Region/Municipality",
            yaxis_title="Priority Score",
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display detailed results with interpretation
        st.subheader("📋 Detailed Priority Analysis")
        
        # Create metrics columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Areas Assessed", len(results_df_sorted))
        with col2:
            st.metric("Highest Priority Score", f"{results_df_sorted['Priority Score'].max():.3f}")
        with col3:
            st.metric("Average Priority Score", f"{results_df_sorted['Priority Score'].mean():.3f}")
        
        st.markdown("---")
        
        # Display priority queue with interpretation
        for idx, row in results_df_sorted.iterrows():
            priority_level = "🔴 HIGH" if row['Priority Score'] >= 0.66 else "🟡 MEDIUM" if row['Priority Score'] >= 0.33 else "🟢 LOW"
            
            # Calculate estimated response time
            if idx == 0:
                response_time = "Immediate (Within 24 hours)"
                time_color = "red"
            elif idx == 1:
                response_time = "Short-term (24-48 hours)"
                time_color = "orange"
            elif idx == 2:
                response_time = "Medium-term (2-3 days)"
                time_color = "orange"
            else:
                hours = 48 + (idx - 2) * 12
                response_time = f"Extended ({hours} hours)"
                time_color = "green"
            
            with st.expander(f"{idx + 1}. {row['Region']} - {priority_level}", expanded=(idx==0)):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **Priority Score:** {row['Priority Score']:.3f}  
                    **Priority Level:** {priority_level}  
                    **Estimated Response Time:** <span style='color:{time_color}; font-weight:bold'>{response_time}</span>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**Impact Metrics:**")
                    st.write(f"- Casualties: {row['Casualties']}")
                    st.write(f"- Affected Families: {row['Affected Families']}")
                    st.write(f"- Damaged Houses: {row['Damaged Houses']}")
                
                with col2:
                    st.markdown("**Normalized Scores:**")
                    st.write(f"- Casualties Impact: {row['Norm_Casualties']:.3f}")
                    st.write(f"- Families Impact: {row['Norm_Affected']:.3f}")
                    st.write(f"- Housing Impact: {row['Norm_Damaged']:.3f}")
                    
                    if row.get('Notes'):
                        st.markdown(f"**Notes:** {row['Notes']}")
        
        # Interpretation and recommendations
        st.markdown("---")
        st.subheader("💡 Strategic Recommendations")
        
        # Generate recommendations based on data
        high_priority_count = len(results_df_sorted[results_df_sorted['Priority Score'] >= 0.66])
        medium_priority_count = len(results_df_sorted[(results_df_sorted['Priority Score'] >= 0.33) & (results_df_sorted['Priority Score'] < 0.66)])
        low_priority_count = len(results_df_sorted[results_df_sorted['Priority Score'] < 0.33])
        
        st.markdown(f"""
        <div class="priority-card">
            <h3>Response Strategy Based on Priority Distribution</h3>
            <p><strong>Immediate Response Required:</strong> {high_priority_count} area(s) need urgent attention.</p>
            <p><strong>Secondary Response:</strong> {medium_priority_count} area(s) should be addressed within 48-72 hours.</p>
            <p><strong>Monitored Response:</strong> {low_priority_count} area(s) can be scheduled for routine assessment.</p>
            <br>
            <h4>Resource Allocation Recommendation:</h4>
            <ul>
                <li>Allocate <strong>{max(40, high_priority_count * 30)}%</strong> of available resources to high-priority areas</li>
                <li>Distribute <strong>{max(30, medium_priority_count * 20)}%</strong> of resources to medium-priority areas</li>
                <li>Reserve <strong>{max(20, low_priority_count * 10)}%</strong> for low-priority and emerging needs</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Export functionality
        st.markdown("---")
        if st.button("📥 Export Priority Report (CSV)"):
            export_df = results_df_sorted[['Region', 'Priority Score', 'Casualties', 'Affected Families', 'Damaged Houses']]
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"disaster_priority_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
    else:
        st.warning("No data available. Please go to the 'LGU Data Entry & Queue' tab to add disaster-affected areas first.")
        st.info("💡 Tip: You can add multiple LGUs to compare their priority scores and get response time estimates.")

# Helper function for normalization
def normalize_single(column):
    """Normalize a single column of data"""
    if column.max() == column.min():
        return column * 0
    return (column - column.min()) / (column.max() - column.min())
