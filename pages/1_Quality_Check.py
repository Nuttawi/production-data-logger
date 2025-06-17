import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

# ... (โค้ดส่วน CHECKLIST_ITEMS, ALL_HOURS_COLUMNS, MORNING_SHIFT_HOURS, NIGHT_SHIFT_HOURS_PART1, NIGHT_SHIFT_HOURS_PART2, NIGHT_SHIFT_HOURS, SHIFT_OPTIONS เหมือนเดิม) ...

# Ensure NIGHT_SHIFT_HOURS_PART2 is corrected from previous step
NIGHT_SHIFT_HOURS_PART2 = [f'{h:02d}:00' for h in range(9)] # 00:00 - 08:00 (ถึง 08:00 ของวันถัดไป)
NIGHT_SHIFT_HOURS = NIGHT_SHIFT_HOURS_PART1 + NIGHT_SHIFT_HOURS_PART2

SHIFT_OPTIONS = {
    "กะเช้า (08:00 - 19:00)": MORNING_SHIFT_HOURS,
    "กะดึก (19:00 - 08:00)": NIGHT_SHIFT_HOURS,
    "แสดงทั้งหมด (00:00 - 23:00)": ALL_HOURS_COLUMNS
}

# เพิ่ม DataFrame สำหรับเก็บข้อมูลรายวัน (เหมือนเดิม)
if 'daily_machine_params_data' not in st.session_state:
    st.session_state.daily_machine_params_data = {}

# เพิ่มค่าเริ่มต้นสำหรับเวลาที่บันทึก
# ใช้ key สำหรับ session_state เพื่อเก็บค่าเริ่มต้นของเวลา
if 'initial_record_time' not in st.session_state:
    st.session_state.initial_record_time = datetime.now().time()


def get_daily_df(date_str):
    if date_str not in st.session_state.daily_machine_params_data:
        new_day_df = pd.DataFrame(
            columns=['รายการตรวจสอบ', 'เป้าหมาย'] + ALL_HOURS_COLUMNS
        )
        for item, target in CHECKLIST_ITEMS.items():
            new_day_df.loc[len(new_day_df)] = [item, target] + ['' for _ in range(len(ALL_HOURS_COLUMNS))]
        st.session_state.daily_machine_params_data[date_str] = new_day_df
    return st.session_state.daily_machine_params_data[date_str]


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
        selected_date = st.date_input("วันที่บันทึก", datetime.now())
    with col3:
        # ****** การแก้ไขที่สำคัญตรงนี้ ******
        # ใช้ค่าจาก st.session_state.initial_record_time เป็นค่าเริ่มต้นของ time_input
        selected_time = st.time_input("เวลาบันทึก", value=st.session_state.initial_record_time)
        
    st.write("---")

    input_values = {}
    for i, (item, target) in enumerate(CHECKLIST_ITEMS.items()):
        input_label = f"{i+1}. {item} (เป้าหมาย: {target})"
        input_values[item] = st.text_input(input_label, key=f"param_input_{i}")

    submitted = st.form_submit_button("บันทึกข้อมูลพารามิเตอร์")

    if submitted:
        combined_datetime = datetime.combine(selected_date, selected_time)
        record_date_str = combined_datetime.strftime("%Y-%m-%d")
        record_hour_str = combined_datetime.strftime("%H:00")

        current_day_df = get_daily_df(record_date_str)

        if record_hour_str in current_day_df.columns:
            for item, value in input_values.items():
                row_index = current_day_df[current_day_df['รายการตรวจสอบ'] == item].index[0]
                current_day_df.at[row_index, record_hour_str] = value
            
            st.session_state.daily_machine_params_data[record_date_str] = current_day_df
            st.success(f"บันทึกข้อมูลพารามิเตอร์เครื่องจักรสำหรับวันที่ {record_date_str} เวลา {record_hour_str} เรียบร้อยแล้ว!")
            
            # ****** การแก้ไขที่สำคัญตรงนี้ ******
            # อัปเดตค่า initial_record_time ใน session_state เป็นเวลาที่ผู้ใช้เลือกและกดบันทึกสำเร็จ
            st.session_state.initial_record_time = selected_time

        else:
            st.error(f"ไม่สามารถบันทึกข้อมูลในคอลัมน์เวลา {record_hour_str} ได้. กรุณาตรวจสอบการตั้งค่า.")




### ส่วนที่ 2: บันทึกผลการตรวจสอบ / เวลาตรวจสอบ (แสดงผลตารางตามต้องการ)

st.header("บันทึกผลการตรวจสอบ / เวลาตรวจสอบ")

display_date = st.date_input("เลือกวันที่เพื่อแสดงข้อมูล", datetime.now(), key="display_date_qc")
display_date_str = display_date.strftime("%Y-%m-%d")

selected_shift_for_display_key = st.selectbox(
    "เลือกกะเพื่อแสดงผล", 
    list(SHIFT_OPTIONS.keys()), 
    index=0, # กะเช้าเป็นค่าเริ่มต้น
    key="select_shift_qc"
)
selected_shift_hours_to_display = SHIFT_OPTIONS[selected_shift_for_display_key]

if display_date_str in st.session_state.daily_machine_params_data:
    df_to_display = st.session_state.daily_machine_params_data[display_date_str].copy()
    
    cols_to_select = ['รายการตรวจสอบ', 'เป้าหมาย'] + selected_shift_hours_to_display
    cols_present = [col for col in cols_to_select if col in df_to_display.columns]
    
    st.dataframe(df_to_display[cols_present], use_container_width=True)
else:
    st.info(f"ยังไม่มีข้อมูลพารามิเตอร์เครื่องจักรสำหรับวันที่ {display_date_str} ถูกบันทึก")

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
