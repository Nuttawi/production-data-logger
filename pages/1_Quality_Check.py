#1_Quality_Check.py
import streamlit as st
import pandas as pd # import เมื่อจำเป็นเท่านั้น

st.title("หน้าตรวจสอบคุณภาพ")
st.write("นี่คือส่วนที่คุณเคยพัฒนาไว้สำหรับตรวจสอบคุณภาพ")

# ตัวอย่างการดึงข้อมูลจาก session_state
if 'df_machine_params' in st.session_state:
    st.subheader("ข้อมูล Machine Parameters (จากหน้าหลัก):")
    st.dataframe(st.session_state['df_machine_params'])
else:
    st.info("ข้อมูล Machine Parameters ยังไม่ถูกโหลด หรือไม่พร้อมใช้งาน")

if 'df_production_orders' in st.session_state:
    st.subheader("ข้อมูล Production Orders (จากหน้าหลัก):")
    st.dataframe(st.session_state['df_production_orders'])
else:
    st.info("ข้อมูล Production Orders ยังไม่ถูกโหลด หรือไม่พร้อมใช้งาน")

# ... (ส่วนโค้ดเดิมของหน้าตรวจคุณภาพที่คุณเคยเขียนไว้) ...
