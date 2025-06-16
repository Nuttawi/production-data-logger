import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

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

# กำหนดคอลัมน์เริ่มต้นสำหรับ DataFrame ที่จะเก็บข้อมูล
# เราจะใช้ structure ที่แตกต่างออกไป เพื่อให้ง่ายต่อการแสดงผลแบบตารางชั่วโมง
# เพิ่มคอลัมน์เวลาให้ครอบคลุม 24 ชั่วโมง เพื่อความยืดหยุ่นในการบันทึก manual
# แต่จะแสดงแค่ 8:00 - 21:00 ในตารางผลลัพธ์
ALL_HOURS_COLUMNS = [f'{h:02d}:00' for h in range(24)] # 00:00 - 23:00

if 'machine_params_data_by_time' not in st.session_state:
    st.session_state.machine_params_data_by_time = pd.DataFrame(
        columns=['รายการตรวจสอบ', 'เป้าหมาย'] + ALL_HOURS_COLUMNS
    )
    # เพิ่มรายการตรวจสอบและเป้าหมายลงใน DataFrame เริ่มต้น
    for item, target in CHECKLIST_ITEMS.items():
        st.session_state.machine_params_data_by_time.loc[len(st.session_state.machine_params_data_by_time)] = \
            [item, target] + ['' for _ in range(len(ALL_HOURS_COLUMNS))] # ใช้ ALL_HOURS_COLUMNS ในการสร้างคอลัมน์เริ่มต้น

# เพิ่ม DataFrame สำหรับเก็บข้อมูลรายวัน (แยกตามวันที่)
if 'daily_machine_params_data' not in st.session_state:
    st.session_state.daily_machine_params_data = {} # Dictionary เพื่อเก็บ DataFrame แยกตามวันที่


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
        # ช่องให้เลือกวันที่
        selected_date = st.date_input("วันที่บันทึก", datetime.now())
    with col3:
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

        # ตรวจสอบว่ามีข้อมูลสำหรับวันที่เลือกอยู่แล้วหรือไม่
        if record_date_str not in st.session_state.daily_machine_params_data:
            # ถ้ายังไม่มี ให้สร้าง DataFrame ใหม่สำหรับวันนี้
            new_day_df = pd.DataFrame(
                columns=['รายการตรวจสอบ', 'เป้าหมาย'] + ALL_HOURS_COLUMNS
            )
            for item, target in CHECKLIST_ITEMS.items():
                new_day_df.loc[len(new_day_df)] = [item, target] + ['' for _ in range(len(ALL_HOURS_COLUMNS))]
            st.session_state.daily_machine_params_data[record_date_str] = new_day_df

        # ดึง DataFrame ของวันที่เลือกมาใช้งาน
        current_day_df = st.session_state.daily_machine_params_data[record_date_str]

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

### ส่วนที่ 2: ข้อมูลพารามิเตอร์ที่บันทึกไว้

st.header("บันทึกผลการตรวจสอบ / เวลาตรวจสอบ")

# เพิ่มช่องให้เลือกวันที่สำหรับแสดงข้อมูล
display_date = st.date_input("เลือกวันที่เพื่อแสดงข้อมูล", datetime.now())
display_date_str = display_date.strftime("%Y-%m-%d")

if display_date_str in st.session_state.daily_machine_params_data:
    st.dataframe(st.session_state.daily_machine_params_data[display_date_str])
else:
    st.info(f"ยังไม่มีข้อมูลพารามิเตอร์เครื่องจักรสำหรับวันที่ {display_date_str} ถูกบันทึก")