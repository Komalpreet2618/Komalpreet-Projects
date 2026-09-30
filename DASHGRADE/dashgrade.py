import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os

# Page configuration
st.set_page_config(page_title="DASHGRADE", layout="wide")

# Custom CSS for sidebar menu button and background
st.markdown("""
    <style>
    .menu-button {
        font-size: 25px;
        cursor: pointer;
        color: white;
        background: transparent;
        border: none;
        padding: 5px 10px;
        margin-bottom: 10px;
    }
    .stApp {
        background-image: url("https://investor.inseego.com/sites/g/files/knoqqb98021/themes/site/nir_pid873/client/assets/images/content/19931-1920w.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        height: 100vh;
        width: 100vw;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if 'show_sidebar' not in st.session_state:
    st.session_state.show_sidebar = False
if 'df' not in st.session_state:
    if os.path.exists("medical_data.csv"):
        st.session_state.df = pd.read_csv("medical_data.csv")
    else:
        st.session_state.df = None

# Toggle sidebar button
menu_clicked = st.button("\u2630", key="menu_button", help="Toggle Sidebar")
if menu_clicked:
    st.session_state.show_sidebar = not st.session_state.show_sidebar

# Sidebar
if st.session_state.show_sidebar:
    
    with st.sidebar:
        opt = st.radio('Menu', options=['Upload'])
        if opt=='Upload':
                st.header("📂 Navigation")
                selected_section = st.radio("Go to:", [
                    "View Data",
                    "MST Comparison",
                    "Final Marks Comparison",
                    "Attendance Comparison",
                    "Leaderboard",
                    "Detain List",
                    "Apply Medical"
                ])

                uploaded_file = st.file_uploader("Upload Student CSV", type=["csv"])
                if uploaded_file:
                    df = pd.read_csv(uploaded_file)
                    required_cols = {"ID", "Name", "Class", "MST1", "MST2", "Final", "Attendance"}
                    if not required_cols.issubset(df.columns):
                        st.error("❌ CSV must include: ID, Name, Class, MST1, MST2, Final, Attendance")
                    else:
                        if "Medical" not in df.columns:
                            df["Medical"] = "No"
                        st.session_state.df = df
                        df.to_csv("medical_data.csv", index=False)
        
else:
    selected_section = None

# Header
st.markdown("""
    <div style='display: flex; align-items: center;'>
        <img src='https://t4.ftcdn.net/jpg/05/91/40/47/360_F_591404733_XI6dw0OZMfxCsZLqzmY8BcWbzf2QwZdK.jpg' width='60' style='margin-right: 15px;'>
        <h1 style='margin: 0;'>DASHGRADE</h1>
    </div>
""", unsafe_allow_html=True)

# Main logic
if st.session_state.df is not None:
    df = st.session_state.df

    if selected_section == "View Data":
        st.subheader("📄 Student Data")
        st.markdown(f"**👥 Total Students:** {len(df)}")
        st.dataframe(df)

    elif selected_section == "MST Comparison":
        st.subheader("📊 MST1 and MST2 Comparison")

        # MST1
        st.markdown("### 📝 MST1 Marks")
        fig_mst1 = px.bar(df, x="Name", y="MST1", title="MST1 Marks",
                          color_discrete_sequence=["#00BFFF"], template="plotly_white")
        fig_mst1.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white", size=14)
        )
        st.plotly_chart(fig_mst1, use_container_width=True)

        # MST2
        st.markdown("### 📝 MST2 Marks")
        fig_mst2 = px.bar(df, x="Name", y="MST2", title="MST2 Marks",
                          color_discrete_sequence=["#FF69B4"], template="plotly_white")
        fig_mst2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white", size=14)
        )
        st.plotly_chart(fig_mst2, use_container_width=True)

    elif selected_section == "Final Marks Comparison":
        st.subheader("🎓 Final Semester Marks")
        fig_final = px.bar(df, x="Name", y="Final", title="Final Semester Marks",
                           color_discrete_sequence=["#6EC6FF"], template="plotly_white")
        fig_final.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white", size=14)
        )
        st.plotly_chart(fig_final, use_container_width=True)

    elif selected_section == "Attendance Comparison":
        st.subheader("📈 Attendance Comparison")
        fig_att = px.bar(df, x="Name", y="Attendance", title="Attendance of Students",
                         color_discrete_sequence=["#FFA07A"], template="plotly_white")
        fig_att.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white", size=14)
        )
        st.plotly_chart(fig_att, use_container_width=True)

    elif selected_section == "Leaderboard":
        st.subheader("🏆 Top 5 Students by Final Marks")
        leaderboard = df.sort_values(by="Final", ascending=False).head(5)
        st.dataframe(leaderboard[["Name", "Class", "MST1", "MST2", "Final"]])

    elif selected_section == "Detain List":
        st.subheader("🚫 Detain List (Attendance < 75%)")
        detain_list = df[df["Attendance"] < 75].sort_values(by="Attendance")
        if not detain_list.empty:
            st.dataframe(detain_list[["Name", "Class", "Attendance"]])
        else:
            st.success("🎉 No students to detain!")

    elif selected_section == "Apply Medical":
        st.subheader("🩺 Apply Medical Adjustment")
        student_list = df["Name"].tolist()
        selected_student = st.selectbox("Select Student", student_list)

        student_data = df[df["Name"] == selected_student].iloc[0]
        current_attendance = student_data["Attendance"]
        medical_status = student_data["Medical"]

        st.write(f"**Current Attendance:** {current_attendance}%")
        st.write(f"**Medical Status:** {medical_status}")

        if medical_status == "Yes":
            st.info("✅ Medical already applied.")
        else:
            if st.button("Apply Medical (Add 10%)"):
                idx = df[df["Name"] == selected_student].index[0]
                updated_attendance = min(current_attendance + 10, 100)
                df.at[idx, "Attendance"] = updated_attendance
                df.at[idx, "Medical"] = "Yes"
                df.to_csv("medical_data.csv", index=False)
                st.session_state.df = df
                st.success("✅ 10% Medical adjustment applied successfully.")
                st.rerun()

        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        st.download_button(
            label="📥 Download Updated CSV",
            data=buffer.getvalue(),
            file_name="updated_students.csv",
            mime="text/csv"
        )

else:
    st.info("📂 Please upload a student CSV file from the sidebar to continue.")
