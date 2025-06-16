import streamlit as st
import gspread
import json # *** เพิ่มบรรทัดนี้เข้ามา ***

# --- Google Sheets Connection ---
# โหลด gcp_service_account จาก st.secrets
# st.secrets["gcp_service_account"] ตอนนี้เป็น string ที่เก็บ JSON service account key
# เราต้องใช้ json.loads() เพื่อแปลง string นั้นให้เป็น Python dictionary (JSON object)
try:
    service_account_info = json.loads(st.secrets["gcp_service_account"])
    gc = gspread.service_account_from_dict(service_account_info)
    st.success("เชื่อมต่อ Google Sheets ด้วย Service Account สำเร็จ!") # ข้อความยืนยันการเชื่อมต่อ

except KeyError:
    st.error("ไม่พบ 'gcp_service_account' ใน Streamlit Secrets. กรุณาตรวจสอบ secrets.toml.")
    st.info("คุณสามารถดูวิธีการตั้งค่า Secrets ได้ที่: https://docs.streamlit.io/deploy/streamlit-cloud/connect-to-data-sources/gsheets")
    st.stop() # หยุดการทำงานของแอปถ้าไม่มี Secret
except json.JSONDecodeError:
    st.error("รูปแบบของ 'gcp_service_account' ใน Streamlit Secrets ไม่ถูกต้อง. ไม่ใช่ JSON ที่สมบูรณ์.")
    st.stop()
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Google Sheets: {e}")
    st.warning("ตรวจสอบว่า Service Account มีสิทธิ์ Editor ใน Google Sheet และชื่อ Spreadsheet/Worksheet ใน secrets.toml ถูกต้อง")
    st.stop()


# --- Spreadsheet Names from Secrets ---
try:
    machine_params_spreadsheet_name = st.secrets["machine_params_spreadsheet_name"]
    machine_params_worksheet_name = st.secrets["machine_params_worksheet_name"]
    production_orders_spreadsheet_name = st.secrets["production_orders_spreadsheet_name"]
    production_orders_worksheet_name = st.secrets["production_orders_worksheet_name"]
except KeyError as e:
    st.error(f"ไม่พบ Secret Key ที่จำเป็น: {e}. กรุณาตรวจสอบ secrets.toml.")
    st.stop()

# --- Open Google Sheets ---
try:
    sh_machine_params = gc.open(machine_params_spreadsheet_name)
    worksheet_machine_params = sh_machine_params.worksheet(machine_params_worksheet_name)
    st.write(f"โหลดข้อมูลจาก Spreadsheet '{machine_params_spreadsheet_name}', Worksheet '{machine_params_worksheet_name}' สำเร็จ.")

    sh_production_orders = gc.open(production_orders_spreadsheet_name)
    worksheet_production_orders = sh_production_orders.worksheet(production_orders_worksheet_name)
    st.write(f"โหลดข้อมูลจาก Spreadsheet '{production_orders_spreadsheet_name}', Worksheet '{production_orders_worksheet_name}' สำเร็จ.")

except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"ไม่พบ Spreadsheet ที่ระบุ. โปรดตรวจสอบชื่อใน secrets.toml: '{machine_params_spreadsheet_name}' หรือ '{production_orders_spreadsheet_name}'")
    st.stop()
except gspread.exceptions.WorksheetNotFound:
    st.error(f"ไม่พบ Worksheet ที่ระบุ. โปรดตรวจสอบชื่อใน secrets.toml: '{machine_params_worksheet_name}' หรือ '{production_orders_worksheet_name}'")
    st.stop()
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการเปิด Spreadsheet/Worksheet: {e}")
    st.stop()

# --- ส่วนนี้คือโค้ด Streamlit UI และ Logic หลักของคุณ
# ... (วางโค้ดที่เหลือจาก app.py ของคุณต่อจากตรงนี้)
# ตัวอย่างเช่น ถ้าคุณมีส่วนของโค้ดที่แสดง UI หรือเก็บข้อมูล
# คุณจะต้องตรวจสอบว่าโค้ดเดิมของคุณเรียกใช้ 'worksheet_machine_params'
# และ 'worksheet_production_orders' ในการอ่านหรือเขียนข้อมูล
# โดยไม่จำเป็นต้องแก้ไขการเรียกใช้เมธอด .get_all_values() หรือ .append_row() อีก