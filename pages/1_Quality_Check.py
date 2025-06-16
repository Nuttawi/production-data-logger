import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

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

# เพิ่ม DataFrame สำหรับเก็บข้อมูลรายวัน (แยกตามวันที่)
# โดยแต่ละวันจะเก็บข้อมูลในรูปแบบ DataFrame ที่มีคอลัมน์เวลาครบ 24 ชั่วโมง
# หากข้อมูลหายไปทุกครั้งที่ Deploy หรือรีเฟรช นั่นเพราะข้อมูลถูกเก็บใน session_state เท่านั้น
# ต้องมีการบันทึกลงไฟล์หรือ database จริงๆ เพื่อให้ข้อมูลอยู่ถาวร
if 'daily_machine_params_data' not in st.session_state:
    st.session_state.daily_machine_params_data = {} # Dictionary เพื่อเก็บ DataFrame แยกตามวันที่

# --- ฟังก์ชันช่วยสร้าง DataFrame สำหรับแต่ละวัน ---
def get_daily_df(date_str):
    if date_str not in st.session_state.daily_machine_params_data:
        # ถ้ายังไม่มีข้อมูลสำหรับวันที่นี้ ให้สร้าง DataFrame ใหม่
        new_day_df = pd.DataFrame(
            columns=['รายการตรวจสอบ', 'เป้าหมาย'] + ALL_HOURS_COLUMNS
        )
        for item, target in CHECKLIST_ITEMS.items():
            new_day_df.loc[len(new_day_df)] = [item, target] + ['' for _ in range(len(ALL_HOURS_COLUMNS))]
        st.session_state.daily_machine_params_data[date_str] = new_day_df
    return st.session_state.daily_machine_params_data[date_str]


# เปลี่ยน title ให้เป็นชื่อของหน้านี้
st.title("✅ หน้าตรวจสอบคุณภาพเครื่องจักร")
st.write("---")

### ส่วนที่ 1: บันทึกพารามิเตอร์เครื่องจักร

st.header("บันทึกพารามิเตอร์เครื่องจักร")

with st.form("machine_param_form"):
    st.markdown("**กรุณากรอกข้อมูลพารามิเตอร์เครื่องจักร:**")
    
    col1, col2, col3 = st.columns(3) 
    with col1:
        machine_id = st.text_input("รหัสเครื่องจักร (Machine ID)", value="M001")
    with col2:
        # ช่องให้เลือกวันที่
        selected_date = st.date_input("วันที่บันทึก", datetime.now())
    with col3: # แก้ไข: ต้องมี ":" หลัง col3
        # ช่องให้เลือกเวลา
        selected_time = st.time_input("เวลาบันทึก", datetime.now().time())
        
    st.write("---")

    # สร้างช่องกรอกข้อมูลสำหรับแต่ละรายการตรวจสอบ
    input_values = {}
    for i, (item, target) in enumerate(CHECKLIST_ITEMS.items()):
        input_label = f"{i+1}. {item} (เป้าหมาย: {target})"
        input_values[item] = st.text_input(input_label, key=f"param_input_{i}")

    submitted = st.form_submit_button("บันทึกข้อมูลพารามิเตอร์")

    if submitted:
        # รวมวันที่และเวลาที่เลือก
        combined_datetime = datetime.combine(selected_date, selected_time)
        record_date_str = combined_datetime.strftime("%Y-%m-%d")
        record_hour_str = combined_datetime.strftime("%H:00") # ปัดเป็นชั่วโมงเต็ม

        # ดึง DataFrame ของวันที่เลือกมาใช้งาน
        current_day_df = get_daily_df(record_date_str)

        # ตรวจสอบว่าคอลัมน์ชั่วโมงที่จะบันทึกมีอยู่ใน DataFrame หรือไม่
        if record_hour_str in current_day_df.columns:
            # อัปเดตข้อมูลใน DataFrame
            for item, value in input_values.items():
                row_index = current_day_df[current_day_df['รายการตรวจสอบ'] == item].index[0]
                current_day_df.at[row_index, record_hour_str] = value
            
            # บันทึก DataFrame ที่อัปเดตแล้วกลับไป
            st.session_state.daily_machine_params_data[record_date_str] = current_day_df
            st.success(f"บันทึกข้อมูลพารามิเตอร์เครื่องจักรสำหรับวันที่ {record_date_str} เวลา {record_hour_str} เรียบร้อยแล้ว!")
        else:
            st.error(f"ไม่สามารถบันทึกข้อมูลในคอลัมน์เวลา {record_hour_str} ได้. กรุณาตรวจสอบการตั้งค่า.")


st.write("---")

### ส่วนที่ 2: บันทึกผลการตรวจสอบ / เวลาตรวจสอบ (แสดงผลตารางตามต้องการ)

st.header("บันทึกผลการตรวจสอบ / เวลาตรวจสอบ")

# เพิ่มช่องให้เลือกวันที่สำหรับแสดงข้อมูล
display_date = st.date_input("เลือกวันที่เพื่อแสดงข้อมูล", datetime.now(), key="display_date_qc")
display_date_str = display_date.strftime("%Y-%m-%d")

# เพิ่มช่องให้เลือกกะสำหรับการแสดงผล
selected_shift_for_display_key = st.selectbox(
    "เลือกกะเพื่อแสดงผล", 
    list(SHIFT_OPTIONS.keys()), 
    index=0, # กะเช้าเป็นค่าเริ่มต้น
    key="select_shift_qc"
)
selected_shift_hours_to_display = SHIFT_OPTIONS[selected_shift_for_display_key]

if display_date_str in st.session_state.daily_machine_params_data:
    df_to_display = st.session_state.daily_machine_params_data[display_date_str].copy()
    
    # กรองเฉพาะคอลัมน์ที่ต้องการแสดงตามกะที่เลือก
    cols_to_select = ['รายการตรวจสอบ', 'เป้าหมาย'] + selected_shift_hours_to_display
    cols_present = [col for col in cols_to_select if col in df_to_display.columns]
    
    # แสดง DataFrame ด้วย st.dataframe ที่สามารถแก้ไขได้ (ถ้าต้องการ)
    st.dataframe(df_to_display[cols_present], use_container_width=True)
else:
    st.info(f"ยังไม่มีข้อมูลพารามิเตอร์เครื่องจักรสำหรับวันที่ {display_date_str} ถูกบันทึก")

# เพิ่มส่วนสำหรับแสดงข้อมูลจาก Machine Parameters และ Production Orders
# ที่ดึงมาจาก app.py ผ่าน session_state (เหมือนที่คุณเคยมี)
st.markdown("---")
st.subheader("ข้อมูล Machine Parameters (จากหน้าหลัก):")
if 'df_machine_params' in st.session_state:
    st.dataframe(st.session_state['df_machine_params'])
else:
    st.info("ข้อมูล Machine Parameters ยังไม่ถูกโหลด หรือไม่พร้อมใช้งาน")

st.subheader("ข้อมูล Production Orders (จากหน้าหลัก):")
if 'df_production_orders' in st.session_state:
    st.dataframe(st.session_state['df_production_orders'])
else:
    st.info("ข้อมูล Production Orders ยังไม่ถูกโหลด หรือไม่พร้อมใช้งาน")