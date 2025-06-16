import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

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

# กำหนดคอลัมน์เริ่มต้นสำหรับ DataFrame ที่จะเก็บข้อมูล
# เราจะใช้ structure ที่แตกต่างออกไป เพื่อให้ง่ายต่อการแสดงผลแบบตารางชั่วโมง
if 'machine_params_data_by_time' not in st.session_state:
    st.session_state.machine_params_data_by_time = pd.DataFrame(
        columns=['รายการตรวจสอบ', 'เป้าหมาย'] + [f'{h:02d}:00' for h in range(8, 22)] # คอลัมน์เวลา 8:00 - 21:00
    )
    # เพิ่มรายการตรวจสอบและเป้าหมายลงใน DataFrame เริ่มต้น
    for item, target in CHECKLIST_ITEMS.items():
        st.session_state.machine_params_data_by_time.loc[len(st.session_state.machine_params_data_by_time)] = \
            [item, target] + ['' for _ in range(len(st.session_state.machine_params_data_by_time.columns) - 2)]


st.title("🏭 ระบบบันทึกข้อมูลการผลิต (Machine Parameters)")
st.write("---")

### ส่วนที่ 1: บันทึกพารามิเตอร์เครื่องจักร

st.header("บันทึกพารามิเตอร์เครื่องจักร")

with st.form("machine_param_form"):
    st.markdown("**กรุณากรอกข้อมูลพารามิเตอร์เครื่องจักร:**")
    
    col1, col2 = st.columns(2)
    with col1:
        machine_id = st.text_input("รหัสเครื่องจักร (Machine ID)", value="M001")
    with col2:
        # ใช้ datetime.now().strftime เพื่อแสดงเวลาปัจจุบันและเลือกเวลาที่ใกล้ที่สุด
        current_display_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.markdown(f"**เวลาบันทึกปัจจุบัน:** `{current_display_time}`")

    st.write("---")

    # สร้างช่องกรอกข้อมูลสำหรับแต่ละรายการตรวจสอบ
    input_values = {}
    for i, (item, target) in enumerate(CHECKLIST_ITEMS.items()):
        # เพิ่มข้อความแนะนำเป้าหมาย
        input_label = f"{i+1}. {item} (เป้าหมาย: {target})"
        input_values[item] = st.text_input(input_label, key=f"param_input_{i}")
        # คุณอาจจะเปลี่ยนเป็น st.number_input ถ้าพารามิเตอร์นั้นเป็นตัวเลขล้วนๆ
        # แต่ text_input ยืดหยุ่นกว่าสำหรับการกรอกค่าที่มีหน่วย หรืออยู่ในช่วง

    submitted = st.form_submit_button("บันทึกข้อมูลพารามิเตอร์")

    if submitted:
        # กำหนดเวลาที่จะบันทึกข้อมูลลงในคอลัมน์ชั่วโมงที่ใกล้ที่สุด (ปัดลง)
        now = datetime.now()
        # หาชั่วโมงปัจจุบัน และใช้เป็นคอลัมน์ที่จะบันทึก
        record_hour = now.hour 
        # ถ้าเลยนาทีที่ 30 ไปแล้ว จะปัดขึ้นไปชั่วโมงถัดไปเพื่อให้ตรงกับแนวคิด "ทุก 1 ชม."
        # แต่ถ้าต้องการแบบ 8:00, 9:00 เป๊ะๆ ไม่สนใจนาที ให้ใช้ record_hour = now.hour ได้เลย
        # ตัวอย่างนี้จะปัดลงตามชั่วโมงปัจจุบัน เพื่อให้คุณกรอกข้อมูลและระบุชั่วโมงที่กรอกได้
        
        # ปัดชั่วโมงให้ตรงกับคอลัมน์ที่เรามี (8:00 - 21:00)
        if record_hour < 8: # ถ้าก่อน 8 โมงเช้า
            target_hour_col = '08:00'
        elif record_hour > 21: # ถ้าหลัง 3 ทุ่ม
            target_hour_col = '' # หรืออาจจะแจ้งว่าไม่สามารถบันทึกได้ หรือไปลงคอลัมน์ 'OT' ในอนาคต
            st.warning("ขณะนี้อยู่นอกช่วงเวลาบันทึกปกติ (8:00-21:00) ข้อมูลอาจไม่แสดงในตาราง.")
        else:
            target_hour_col = f'{record_hour:02d}:00' # รูปแบบ 08:00, 09:00


        # ตรวจสอบว่าคอลัมน์ชั่วโมงที่จะบันทึกมีอยู่ใน DataFrame หรือไม่
        if target_hour_col in st.session_state.machine_params_data_by_time.columns:
            # อัปเดตข้อมูลใน DataFrame
            for item, value in input_values.items():
                row_index = st.session_state.machine_params_data_by_time[
                    st.session_state.machine_params_data_by_time['รายการตรวจสอบ'] == item
                ].index[0]
                st.session_state.machine_params_data_by_time.at[row_index, target_hour_col] = value
            
            st.success(f"บันทึกข้อมูลพารามิเตอร์เครื่องจักรสำหรับเวลา {target_hour_col} เรียบร้อยแล้ว!")
        else:
            st.error(f"ไม่สามารถบันทึกข้อมูลในคอลัมน์เวลา {target_hour_col} ได้. กรุณาติดต่อผู้ดูแล.")


st.write("---")

### ส่วนที่ 2: ข้อมูลพารามิเตอร์ที่บันทึกไว้

st.header("บันทึกผลการตรวจสอบ / เวลาตรวจสอบ")

# กรองเฉพาะคอลัมน์ที่ต้องการแสดงในตาราง (รายการตรวจสอบ, เป้าหมาย, และคอลัมน์เวลา)
columns_to_display = ['รายการตรวจสอบ', 'เป้าหมาย'] + [col for col in st.session_state.machine_params_data_by_time.columns if ':' in col]
st.dataframe(st.session_state.machine_params_data_by_time[columns_to_display])