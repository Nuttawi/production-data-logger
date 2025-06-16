import streamlit as st
import gspread
import json
import pandas as pd

st.set_page_config(
    page_title="ระบบจัดการข้อมูลการผลิต",
    page_icon="📊",
    layout="wide"
)

st.title("ระบบจัดการข้อมูลการผลิต") # ตั้งชื่อหัวข้อแอป

# กำหนดตัวแปร gc เป็น None ไว้ก่อน
gc = None

# --- ส่วนเชื่อมต่อ Google Sheets Service Account ---
try:
    # ดึงข้อมูล Service Account ทั้งก้อนมาเป็น JSON String
    gcp_service_account_json_string = st.secrets["gcp_service_account"]

    # แปลง JSON String เป็น Python dictionary
    gcp_service_account_info = json.loads(gcp_service_account_json_string)

    # สร้าง object 'gc' ตรงนี้
    gc = gspread.service_account_from_dict(gcp_service_account_info)
    st.success("เชื่อมต่อ Google Sheets ด้วย Service Account สำเร็จ!")

    # เก็บ gc ไว้ใน session_state เพื่อให้หน้าอื่นๆ (เช่น หน้าตรวจคุณภาพ) สามารถนำไปใช้ได้
    st.session_state['gc'] = gc

except KeyError:
    st.error("ไม่พบ 'gcp_service_account' ใน Streamlit Secrets. กรุณาตรวจสอบ secrets.toml.")
    st.info("คุณสามารถดูวิธีการตั้งค่า Secrets ได้ที่: https://docs.streamlit.io/deploy/streamlit-cloud/connect-to-data-sources/gsheets")
    st.stop() # หยุดการทำงานของแอป ถ้าหา secrets ไม่เจอ
except json.JSONDecodeError as e:
    st.error(f"ข้อผิดพลาดในการถอดรหัส JSON ของ Service Account Key: {e}. ตรวจสอบรูปแบบ JSON ใน secrets.toml")
    st.stop() # หยุดการทำงานของแอป ถ้า JSON มีปัญหา
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดที่ไม่คาดคิดในการประมวลผล Secrets หรือสร้าง Service Account: {e}")
    st.stop() # หยุดการทำงานของแอป ถ้าเกิดข้อผิดพลาดอื่น

# --- ส่วนโหลดและแสดงผลข้อมูลจาก Google Sheets (ถ้า gc ถูกสร้างสำเร็จ) ---
if gc is not None:
    try:
        # --- สำหรับ Machine_Parameters ---
        machine_params_spreadsheet_name = st.secrets["machine_params_spreadsheet_name"]
        sh_machine_params = gc.open(machine_params_spreadsheet_name)
        machine_params_worksheet_name = st.secrets["machine_params_worksheet_name"]
        worksheet_mp = sh_machine_params.worksheet(machine_params_worksheet_name)
        data_mp = worksheet_mp.get_all_values()
        # ตรวจสอบว่ามีข้อมูลหรือไม่ก่อนสร้าง DataFrame เพื่อหลีกเลี่ยง error ถ้าชีทว่างเปล่า
        if data_mp:
            df_mp = pd.DataFrame(data_mp[1:], columns=data_mp[0]) # แถวแรกเป็น header
        else:
            df_mp = pd.DataFrame(columns=["Machine ID", "Date", "Time", "Item", "Value"]) # สร้าง DataFrame ว่างเปล่าพร้อมคอลัมน์ที่คาดหวัง

        st.success(f"โหลดข้อมูลจาก Spreadsheet '{machine_params_spreadsheet_name}', Worksheet '{machine_params_worksheet_name}' สำเร็จ.")
        st.subheader("ข้อมูล Machine Parameters:")
        st.dataframe(df_mp) # แสดง DataFrame

        # เก็บ df_mp ไว้ใน session_state
        st.session_state['df_machine_params'] = df_mp

        # --- สำหรับ Production_Orders_Database ---
        production_orders_spreadsheet_name = st.secrets["production_orders_spreadsheet_name"]
        sh_production_orders = gc.open(production_orders_spreadsheet_name)
        production_orders_worksheet_name = st.secrets["production_orders_worksheet_name"]
        worksheet_po = sh_production_orders.worksheet(production_orders_worksheet_name)
        data_po = worksheet_po.get_all_values()
        # ตรวจสอบว่ามีข้อมูลหรือไม่ก่อนสร้าง DataFrame
        if data_po:
            df_po = pd.DataFrame(data_po[1:], columns=data_po[0]) # แถวแรกเป็น header
        else:
            df_po = pd.DataFrame(columns=["Order ID", "Product", "Quantity", "Status", "Delivery Date"]) # ตัวอย่างคอลัมน์ที่คาดหวัง

        st.success(f"โหลดข้อมูลจาก Spreadsheet '{production_orders_spreadsheet_name}', Worksheet '{production_orders_worksheet_name}' สำเร็จ.")
        st.subheader("ข้อมูล Production Orders:")
        st.dataframe(df_po)

        # เก็บ df_po ไว้ใน session_state
        st.session_state['df_production_orders'] = df_po

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดหรือแสดงผลข้อมูล: {e}")
        st.warning("ตรวจสอบว่า Sheet ของคุณมีข้อมูลอยู่หรือไม่ และชื่อ Column ถูกต้อง")
else:
    st.error("ไม่สามารถเชื่อมต่อ Google Service Account ได้ โปรดตรวจสอบการตั้งค่า")

st.write("---") # เพิ่มเส้นแบ่ง
st.write("ยินดีต้อนรับสู่ระบบจัดการข้อมูลการผลิต!")
st.write("โปรดเลือกหน้าจากแถบด้านข้าง (Sidebar) เพื่อเข้าถึงส่วนต่างๆ ของแอปพลิเคชัน")
st.write("---")