# pages/1_Quality_Check.py
import streamlit as st
import pandas as pd # อาจจะต้องใช้ถ้าโค้ดเดิมใช้ dataframe

st.title("หน้าตรวจสอบคุณภาพ")
st.write("นี่คือส่วนที่คุณเคยพัฒนาไว้สำหรับตรวจสอบคุณภาพ")

# ตัวอย่างการดึงข้อมูลจาก session_state
if 'df_machine_params' in st.session_state:
    st.subheader("ข้อมูล Machine Parameters (จากหน้าหลัก):")
    st.dataframe(st.session_state['df_machine_params'])
else:
    st.info("ข้อมูล Machine Parameters ยังไม่ถูกโหลด หรือไม่พร้อมใช้งาน")

# ... (โค้ดเดิมของหน้าตรวจคุณภาพของคุณ) ...