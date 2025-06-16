import streamlit as st
import gspread
import json
import pandas as pd # ถ้าจะใช้ DataFrame

# ... (โค้ดส่วนเชื่อมต่อ Service Account ที่คุณทำสำเร็จแล้ว) ...

# ส่วนนี้คือโค้ดที่คุณควรจะเพิ่ม/ตรวจสอบเพื่อแสดงผล
try:
    # เชื่อมต่อกับ Spreadsheet Machine_Parameters
    machine_params_spreadsheet_name = st.secrets["machine_params_spreadsheet_name"]
    sh_machine_params = gc.open(machine_params_spreadsheet_name)
    # เลือก Worksheet
    machine_params_worksheet_name = st.secrets["machine_params_worksheet_name"]
    worksheet_mp = sh_machine_params.worksheet(machine_params_worksheet_name)
    # ดึงข้อมูลทั้งหมดจาก Worksheet
    data_mp = worksheet_mp.get_all_values()
    # แปลงเป็น DataFrame (ถ้าจำเป็น)
    df_mp = pd.DataFrame(data_mp[1:], columns=data_mp[0]) # แถวแรกเป็น header

    st.success(f"โหลดข้อมูลจาก Spreadsheet '{machine_params_spreadsheet_name}', Worksheet '{machine_params_worksheet_name}' สำเร็จ.")

    # แสดงผลข้อมูล Machine_Parameters
    st.subheader("ข้อมูล Machine Parameters:")
    st.dataframe(df_mp) # หรือ st.table(df_mp) ถ้าข้อมูลไม่เยอะมาก

    # เชื่อมต่อกับ Spreadsheet Production_Orders_Database
    production_orders_spreadsheet_name = st.secrets["production_orders_spreadsheet_name"]
    sh_production_orders = gc.open(production_orders_spreadsheet_name)
    # เลือก Worksheet
    production_orders_worksheet_name = st.secrets["production_orders_worksheet_name"]
    worksheet_po = sh_production_orders.worksheet(production_orders_worksheet_name)
    # ดึงข้อมูลทั้งหมดจาก Worksheet
    data_po = worksheet_po.get_all_values()
    # แปลงเป็น DataFrame (ถ้าจำเป็น)
    df_po = pd.DataFrame(data_po[1:], columns=data_po[0]) # แถวแรกเป็น header

    st.success(f"โหลดข้อมูลจาก Spreadsheet '{production_orders_spreadsheet_name}', Worksheet '{production_orders_worksheet_name}' สำเร็จ.")

    # แสดงผลข้อมูล Production Orders
    st.subheader("ข้อมูล Production Orders:")
    st.dataframe(df_po)


except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลดหรือแสดงผลข้อมูล: {e}")
    st.warning("ตรวจสอบว่า Sheet ของคุณมีข้อมูลอยู่หรือไม่ และชื่อ Column ถูกต้อง")

# เพิ่มเนื้อหาอื่นๆ ที่คุณต้องการให้แสดงบนหน้าจอ
st.write("นี่คือหน้าจอแอปพลิเคชันของคุณ!")