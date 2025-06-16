import streamlit as st
import gspread # ต้อง import gspread ด้วย
import json
import pandas as pd # ต้อง import pandas ด้วย ถ้าจะใช้ DataFrame

st.title("ระบบจัดการข้อมูลการผลิต") # เพิ่ม title ให้แอปดูดีขึ้น

# การเรียกใช้ Service Account จาก st.secrets
# ทำให้ตัวแปร gc เป็น None ไว้ก่อน
gc = None

try:
    # ดึงข้อมูล Service Account ทั้งก้อนมาเป็น JSON String
    gcp_service_account_json_string = st.secrets["gcp_service_account"]

    # แปลง JSON String เป็น Python dictionary
    gcp_service_account_info = json.loads(gcp_service_account_json_string)

    # สร้าง object 'gc' ตรงนี้ เพื่อให้แน่ใจว่าถูกสร้างขึ้นหลังจากการโหลด secrets สำเร็จ
    gc = gspread.service_account_from_dict(gcp_service_account_info)
    st.success("เชื่อมต่อ Google Sheets ด้วย Service Account สำเร็จ!")

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

# ตรวจสอบว่า gc ถูกสร้างขึ้นมาจริงๆ ก่อนที่จะนำไปใช้งาน
if gc is not None:
    try:
        # --- ส่วนสำหรับการโหลดและแสดงผล Machine_Parameters ---
        machine_params_spreadsheet_name = st.secrets["machine_params_spreadsheet_name"]
        sh_machine_params = gc.open(machine_params_spreadsheet_name)
        machine_params_worksheet_name = st.secrets["machine_params_worksheet_name"]
        worksheet_mp = sh_machine_params.worksheet(machine_params_worksheet_name)
        data_mp = worksheet_mp.get_all_values()
        df_mp = pd.DataFrame(data_mp[1:], columns=data_mp[0]) # แถวแรกเป็น header

        st.success(f"โหลดข้อมูลจาก Spreadsheet '{machine_params_spreadsheet_name}', Worksheet '{machine_params_worksheet_name}' สำเร็จ.")

        st.subheader("ข้อมูล Machine Parameters:")
        st.dataframe(df_mp)

        # --- ส่วนสำหรับการโหลดและแสดงผล Production_Orders_Database ---
        production_orders_spreadsheet_name = st.secrets["production_orders_spreadsheet_name"]
        sh_production_orders = gc.open(production_orders_spreadsheet_name)
        production_orders_worksheet_name = st.secrets["production_orders_worksheet_name"]
        worksheet_po = sh_production_orders.worksheet(production_orders_worksheet_name)
        data_po = worksheet_po.get_all_values()
        df_po = pd.DataFrame(data_po[1:], columns=data_po[0]) # แถวแรกเป็น header

        st.success(f"โหลดข้อมูลจาก Spreadsheet '{production_orders_spreadsheet_name}', Worksheet '{production_orders_worksheet_name}' สำเร็จ.")

        st.subheader("ข้อมูล Production Orders:")
        st.dataframe(df_po)

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดหรือแสดงผลข้อมูล: {e}")
        st.warning("ตรวจสอบว่า Sheet ของคุณมีข้อมูลอยู่หรือไม่ และชื่อ Column ถูกต้อง")
else:
    # กรณีที่ gc เป็น None (ซึ่งหมายถึงการเชื่อมต่อ Service Account ล้มเหลว)
    st.error("ไม่สามารถเชื่อมต่อ Google Service Account ได้ โปรดตรวจสอบการตั้งค่า")

st.write("นี่คือหน้าจอแอปพลิเคชันของคุณ!")