import streamlit as st
import pandas as pd
from datetime import datetime

# --- การตั้งค่าเริ่มต้น (Initialization) ---
# ตรวจสอบว่ามี session state สำหรับเก็บข้อมูลหรือไม่ ถ้าไม่มีให้สร้างขึ้นมา
# st.session_state เป็นวิธีที่ Streamlit ใช้ในการเก็บข้อมูลข้ามการรีเฟรชของแอป
if 'machine_params_df' not in st.session_state:
    st.session_state.machine_params_df = pd.DataFrame(columns=[
        'Timestamp', 'Machine ID', 'Parameter 1 (Temp)', 'Parameter 2 (Pressure)', 'Parameter 3 (Speed)'
    ])

st.title("🏭 ระบบบันทึกข้อมูลการผลิต (Machine Parameters)")
st.write("---")

### ส่วนที่ 1: บันทึกพารามิเตอร์เครื่องจักร

st.header("บันทึกพารามิเตอร์เครื่องจักร")

# st.form ใช้สำหรับสร้างฟอร์ม เพื่อให้การบันทึกข้อมูลเกิดขึ้นเมื่อกดปุ่ม Submit เท่านั้น
with st.form("machine_param_form"):
    st.markdown("**กรุณากรอกข้อมูลพารามิเตอร์เครื่องจักร:**")
    # text_input สำหรับรับข้อความ (เช่น รหัสเครื่องจักร)
    machine_id = st.text_input("รหัสเครื่องจักร (Machine ID)", value="M001")
    # number_input สำหรับรับตัวเลข พร้อมกำหนดช่วงค่า (min_value, max_value) และค่าเริ่มต้น (value)
    param1 = st.number_input("พารามิเตอร์ 1 (อุณหภูมิ - °C)", min_value=0.0, max_value=500.0, value=150.0, step=0.1)
    param2 = st.number_input("พารามิเตอร์ 2 (ความดัน - Bar)", min_value=0.0, max_value=100.0, value=25.0, step=0.1)
    param3 = st.number_input("พารามิเตอร์ 3 (ความเร็ว - RPM)", min_value=0.0, max_value=5000.0, value=1200.0, step=1.0)
    
    # ปุ่มสำหรับส่งข้อมูลในฟอร์ม
    submitted = st.form_submit_button("บันทึกข้อมูลพารามิเตอร์")

    if submitted:
        # ดึงเวลาปัจจุบันเพื่อบันทึก Timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # สร้างแถวข้อมูลใหม่ในรูปแบบ Dictionary
        new_data = {
            'Timestamp': current_time,
            'Machine ID': machine_id,
            'Parameter 1 (Temp)': param1,
            'Parameter 2 (Pressure)': param2,
            'Parameter 3 (Speed)': param3
        }
        
        # แปลง Dictionary เป็น DataFrame ชั่วคราว
        new_df = pd.DataFrame([new_data])
        # เพิ่มข้อมูลใหม่เข้าไปใน DataFrame หลักที่เก็บอยู่ใน session_state
        st.session_state.machine_params_df = pd.concat([st.session_state.machine_params_df, new_df], ignore_index=True)
        st.success("บันทึกข้อมูลพารามิเตอร์เครื่องจักรเรียบร้อยแล้ว!")

st.write("---")

### ส่วนที่ 2: ข้อมูลพารามิเตอร์ที่บันทึกไว้

st.header("ข้อมูลพารามิเตอร์ที่บันทึกไว้")

# ตรวจสอบว่า DataFrame มีข้อมูลหรือไม่ ก่อนที่จะแสดงผล
if not st.session_state.machine_params_df.empty:
    st.dataframe(st.session_state.machine_params_df) # st.dataframe ใช้สำหรับแสดง DataFrame ในรูปแบบตาราง
else:
    st.info("ยังไม่มีข้อมูลพารามิเตอร์เครื่องจักรถูกบันทึก")