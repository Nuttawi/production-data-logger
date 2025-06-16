import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from gspread_pandas import Spread, Client

# --- การตั้งค่าเริ่มต้น (Initialization) ---
# กำหนดรายการตรวจสอบและเป้าหมาย
CHECKLIST_ITEMS = {
    "ความเร็วที่ใช้ในการเดินเครื่อง": "30 - 60 องคุลี/นาที",
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
    # ดึงข้อมูล Service Account จาก secrets.toml
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
        
        # เปิด Spreadsheet และ Worksheet
        s = Spread(spreadsheet_name, sheet=worksheet_name, client=client)
        
        # อ่านข้อมูลเป็น DataFrame
        df = s.sheet_to_df(index=False, header_rows=1) # header_rows=1 บอกว่าแถวแรกคือ header
        
        # ตรวจสอบและแปลงชนิดข้อมูล
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date']).dt.date # เก็บเฉพาะวันที่
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

@st.cache_data(ttl=5) # แคชข้อมูล 5 วินาที เพื่อไม่ให้ดึงบ่อยเกินไป
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
        selected_date = st.date_input("วันที่บันทึก", datetime.now().date()) 
    with col3:
        default_time_value = datetime.now().time()
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
                    'Date': selected_date.strftime("%Y-%m-%d"), 
                    'Time': selected_time.strftime("%H:%M:%S"), 
                    'Item': item,
                    'Value': value
                })
        
        if new_records:
            try:
                client = get_gspread_client()
                spreadsheet_name = st.secrets["machine_params_spreadsheet_name"]
                worksheet_name = st.secrets["machine_params_worksheet_name"]
                s = Spread(spreadsheet_name, sheet=worksheet_name, client=client)
                
                # เพิ่มข้อมูลลงใน Google Sheet
                s.df_append(pd.DataFrame(new_records), sheet=worksheet_name, start='A1', headers=False) 
                
                # รีโหลดข้อมูลจาก Google Sheet เพื่ออัปเดต DataFrame ใน Session State
                st.session_state.machine_params_df = load_machine_params_data()
                st.success(f"บันทึกข้อมูลพารามิเตอร์เครื่องจักรเรียบร้อยแล้ว!")
            except Exception as e: # ย้าย except block มาอยู่ตรงนี้
                st.error(f"เกิดข้อผิดพลาดในการบันทึกข้อมูลลง Google Sheet: {e}")
                st.info("ตรวจสอบสิทธิ์ Service Account และชื่อ Spreadsheet/Worksheet ใน secrets.toml")
        else:
            st.warning("กรุณากรอกข้อมูลอย่างน้อยหนึ่งรายการเพื่อบันทึก.")

st.write("---")

### ส่วนที่ 2: ข้อมูลพารามิเตอร์ที่บันทึกไว้ (แสดงจาก Google Sheet)

st.header("บันทึกผลการตรวจสอบ / เวลาตรวจสอบ")

display_date = st.date_input("เลือกวันที่เพื่อแสดงข้อมูล", datetime.now().date())

selected_shift_for_display_key = st.selectbox(
    "เลือกกะเพื่อแสดงผล", 
    list(SHIFT_OPTIONS.keys()), 
    index=0 
)
selected_shift_hours_to_display = SHIFT_OPTIONS[selected_shift_for_display_key]

df_filtered_by_date = st.session_state.machine_params_df[
    st.session_state.machine_params_df['Date'] == display_date
].copy()

if not df_filtered_by_date.empty:
    df_pivot = df_filtered_by_date.pivot_table(
        index=['Machine ID', 'Item'],
        columns='Time',
        values='Value',
        aggfunc='first' 
    ).reset_index()

    # ตรวจสอบชนิดข้อมูลของคอลัมน์ก่อนแปลงเป็น string
    # และแปลงเฉพาะ col ที่เป็น datetime.time object
    df_pivot.columns = [
        col.strftime("%H:00") if isinstance(col, time) else col 
        for col in df_pivot.columns
    ]

    df_display = pd.DataFrame(CHECKLIST_ITEMS.items(), columns=['รายการตรวจสอบ', 'เป้าหมาย'])

    # วนลูปผ่านแต่ละรายการตรวจสอบเพื่อเติมข้อมูล
    for index, row in df_display.iterrows():
        item = row['รายการตรวจสอบ']
        # ค้นหาแถวใน df_pivot ที่มี Item ตรงกัน
        matching_rows = df_pivot[df_pivot['Item'] == item]
        if not matching_rows.empty:
            for hour_col_str in selected_shift_hours_to_display:
                # ตรวจสอบว่าคอลัมน์ชั่วโมงนี้มีอยู่ใน df_pivot หรือไม่
                if hour_col_str in matching_rows.columns:
                    value = matching_rows[hour_col_str].iloc[0] 
                    df_display.at[index, hour_col_str] = value
                else:
                    df_display.at[index, hour_col_str] = ''
        
    # เลือกเฉพาะคอลัมน์ที่ต้องการแสดงตามกะที่เลือก
    # ต้องกรองเฉพาะคอลัมน์ที่มีอยู่จริงใน df_display
    cols_to_display = ['รายการตรวจสอบ', 'เป้าหมาย'] + [h for h in selected_shift_hours_to_display if h in df_display.columns]
    
    st.dataframe(df_display[cols_to_display].fillna(''))
else:
    st.info(f"ยังไม่มีข้อมูลพารามิเตอร์เครื่องจักรสำหรับวันที่ {display_date.strftime('%Y-%m-%d')} ถูกบันทึก")

st.write("---")

### ส่วนที่ 3: การจัดการใบสั่งผลิต (Production Order Management) - (ยังคงเป็นคอมเมนต์ไว้)
# st.header("การจัดการใบสั่งผลิต (Production Order Management)")
# st.write("ส่วนนี้จะใช้สำหรับอัปโหลดไฟล์ Production Order และแสดงรายการ")

# df_production_orders = st.session_state.production_orders_df
# if not df_production_orders.empty:
#    st.subheader("รายการใบสั่งผลิตปัจจุบัน:")
#    st.dataframe(df_production_orders)
# else:
#    st.info("ยังไม่มีข้อมูลใบสั่งผลิต")
#
# uploaded_file = st.file_uploader("อัปโหลดไฟล์ Production Order (Excel/CSV)", type=["xlsx", "xls", "csv"])
# if uploaded_file is not None:
#    try:
#        if uploaded_file.name.endswith('.csv'):
#            new_orders_df = pd.read_csv(uploaded_file)
#        else:
#            new_orders_df = pd.read_excel(uploaded_file)
#
#        st.success("ไฟล์ Production Order ถูกอัปโหลดและประมวลผลแล้ว (ยังไม่ได้บันทึกลง Google Sheet)")
#        st.dataframe(new_orders_df)
#