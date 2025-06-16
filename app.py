import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from gspread_pandas import Spread, Client

# --- การตั้งค่าเริ่มต้น (Initialization) ---
# กำหนดรายการตรวจสอบและเป้าหมาย
CHECKLIST_ITEMS = {
    "ความเร็วที่ใช้ในการเดินเครื่อง": "30 - 60 ถุง/นาที",
    "ตรวจสอบอุณหภูมิ Vertical Sealing": "120-210°C",
    "ตรวจสอบอุณหภูมิ Upper Inner": "90-155°C",
    "ตรวจสอบอุณหภูมิ Lower Inner": "75-155°C",
    "ตรวจสอบอุณหภูมิ Upper Outer": "90-155°C",
    "ตรวจสอบอุณหภูมิ Lower Outer": "75-155°C",
    "ตรวจสอบอุณหภูมิ KR Carousel": "60-200°C",
    "ตรวจสอบอุณหภูมิ KR hot top plate": "85-180°C",
    "ตรวจสอบอุณหภูมิ KR hot bottom plate": "60-140°C"
}

# กำหนดคอลัมน์เวลาสำหรับแต่ละกะ
ALL_HOURS_COLUMNS = [f'{h:02d}:00' for h in range(24)] # 00:00 - 23:00

# กะเช้า: 08:00 - 19:00 (รวม OT)
MORNING_SHIFT_HOURS = [f'{h:02d}:00' for h in range(8, 20)] # ถึง 19:00 -> range(8, 20)

# กะดึก: 19:00 - 08:00 (ของวันถัดไป)
NIGHT_SHIFT_HOURS_PART1 = [f'{h:02d}:00' for h in range(19, 24)] # 19:00 - 23:00
NIGHT_SHIFT_HOURS_PART2 = [f'{h:02d}:00' for h in range(8)] # 00:00 - 07:00 (ถึง 08:00 ของวันถัดไป)
NIGHT_SHIFT_HOURS = NIGHT_SHIFT_HOURS_PART1 + NIGHT_SHIFT_HOURS_PART2

SHIFT_OPTIONS = {
    "กะเช้า (08:00 - 19:00)": MORNING_SHIFT_HOURS,
    "กะดึก (19:00 - 08:00)": NIGHT_SHIFT_HOURS,
    "แสดงทั้งหมด (00:00 - 23:00)": ALL_HOURS_COLUMNS
}

# --- ฟังก์ชันสำหรับเชื่อมต่อ Google Sheets ---
@st.cache_resource(ttl=3600) # แคชการเชื่อมต่อไว้ 1 ชั่วโมง
def get_gspread_client():
    """สร้างและคืนค่า gspread Client โดยใช้ st.secrets"""
    creds = st.secrets["gcp_service_account"]
    client = Client(config=creds)
    return client

@st.cache_data(ttl=5) # แคชข้อมูล 5 วินาที เพื่อไม่ให้ดึงบ่อยเกินไป
def load_machine_params_data():
    """อ่านข้อมูล Machine Parameters จาก Google Sheet"""
    try:
        client = get_gspread_client()
        spreadsheet_name = st.secrets["machine_params_spreadsheet_name"]
        worksheet_name = st.secrets["machine_params_worksheet_name"]
        
        s = Spread(spreadsheet_name, sheet=worksheet_name, client=client)
        
        df = s.sheet_to_df(index=False, header_rows=1) 
        
        if not df.empty:
            # แปลง Date เป็น datetime.date
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            # ตรวจสอบและแปลง Time ให้เป็นรูปแบบ 'HH:MM:SS' ก่อนแปลงเป็น datetime.time
            # เพื่อจัดการค่าที่อาจมี Milliseconds หรือไม่ใช่รูปแบบที่ถูกต้อง
            df['Time'] = df['Time'].astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x) # ตัด microseconds ออก
            df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce').dt.time
            df = df.dropna(subset=['Time']) # ลบแถวที่เวลาแปลงไม่ได้ออก
        else:
            st.warning("Google Sheet สำหรับ Machine Parameters ว่างเปล่า จะเริ่มต้นด้วย DataFrame ว่างเปล่า")
            df = pd.DataFrame(columns=['Machine ID', 'Date', 'Time', 'Item', 'Value'])
            
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูล Machine Parameters จาก Google Sheet ได้: {e}")
        st.info("ตรวจสอบว่า Service Account มีสิทธิ์ Editor ใน Google Sheet และชื่อ Spreadsheet/Worksheet ใน secrets.toml ถูกต้อง")
        return pd.DataFrame(columns=['Machine ID', 'Date', 'Time', 'Item', 'Value'])

@st.cache_data(ttl=5) 
def load_production_orders_data():
    """อ่านข้อมูล Production Orders จาก Google Sheet"""
    try:
        client = get_gspread_client()
        spreadsheet_name = st.secrets["production_orders_spreadsheet_name"]
        worksheet_name = st.secrets["production_orders_worksheet_name"]
        
        s = Spread(spreadsheet_name, sheet=worksheet_name, client=client)
        df = s.sheet_to_df(index=False, header_rows=1)
        
        if not df.empty:
            df['Start Date'] = pd.to_datetime(df['Start Date']).dt.date
            df['End Date'] = pd.to_datetime(df['End Date']).dt.date
        else:
            st.warning("Google Sheet สำหรับ Production Orders ว่างเปล่า จะเริ่มต้นด้วย DataFrame ว่างเปล่า")
            df = pd.DataFrame(columns=['Production Order', 'Product Name', 'Start Date', 'End Date', 'Machine ID', 'Status'])
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูล Production Orders จาก Google Sheet ได้: {e}")
        st.info("ตรวจสอบว่า Service Account มีสิทธิ์ Editor ใน Google Sheet และชื่อ Spreadsheet/Worksheet ใน secrets.toml ถูกต้อง")
        return pd.DataFrame(columns=['Production Order', 'Product Name', 'Start Date', 'End Date', 'Machine ID', 'Status'])

# โหลดข้อมูลเมื่อแอปเริ่มทำงาน หรือเมื่อแคชหมดอายุ
if 'machine_params_df' not in st.session_state:
    st.session_state.machine_params_df = load_machine_params_data()

if 'production_orders_df' not in st.session_state:
    st.session_state.production_orders_df = load_production_orders_data()

st.title("🏭 ระบบบันทึกข้อมูลการผลิต (Machine Parameters)")
st.write("---")

### ส่วนที่ 1: บันทึกพารามิเตอร์เครื่องจักร

st.header("บันทึกพารามิเตอร์เครื่องจักร")

with st.form("machine_param_form"):
    st.markdown("**กรุณากรอกข้อมูลพารามิเตอร์เครื่องจักร:**")
    
    col1, col2, col3 = st.columns(3) 
    with col1:
        machine_id = st.text_input("รหัสเครื่องจักร (Machine ID)", value="M001")
    with col2:
        selected_date = st.date_input("วันที่บันทึก", datetime.now().date()) # ใช้ .date() เพื่อให้เป็นแค่ Date Object
    with col3:
        # กำหนดค่าเริ่มต้นของ time_input ให้เป็นเวลาปัจจุบัน หรือ 08:00:00 ถ้าเป็นไปได้
        # เพื่อป้องกันค่าล็อค และให้ผู้ใช้เลือกได้ง่ายขึ้น
        default_time_value = datetime.now().time()
        # ถ้าต้องการให้ค่าเริ่มต้นเป็น 08:00 เฉพาะช่วงกะเช้า หรือปรับตามตรรกะอื่น
        # สามารถเพิ่มเงื่อนไขได้ที่นี่
        
        # ตรวจสอบว่ามีค่าใน session_state สำหรับเวลาที่บันทึกก่อนหน้าหรือไม่
        # หรือจะใช้ datetime.now().time() เป็นค่าเริ่มต้นเสมอ
        selected_time = st.time_input("เวลาบันทึก", value=default_time_value)
        
    st.write("---")

    input_values = {}
    for i, (item, target) in enumerate(CHECKLIST_ITEMS.items()):
        input_label = f"{i+1}. {item} (เป้าหมาย: {target})"
        input_values[item] = st.text_input(input_label, key=f"param_input_{i}")

    submitted = st.form_submit_button("บันทึกข้อมูลพารามิเตอร์")

    if submitted:
        new_records = []
        for item, value in input_values.items():
            if value: 
                new_records.append({
                    'Machine ID': machine_id,
                    'Date': selected_date.strftime("%Y-%m-%d"), # บันทึกวันที่เป็น string YYYY-MM-DD
                    'Time': selected_time.strftime("%H:%M:%S"), # บันทึกเวลาเป็น string HH:MM:SS
                    'Item': item,
                    'Value': value
                })
        
        if new_records:
            try:
                client = get_gspread_client()
                spreadsheet_name = st.secrets["machine_params_spreadsheet_name"]
                worksheet_name = st.secrets["machine_params_worksheet_name"]
                s = Spread(spreadsheet_name, sheet=worksheet_name, client=client)
                
                s.df_append(pd.DataFrame(new_records), sheet=worksheet_name, start='A1', headers=False)