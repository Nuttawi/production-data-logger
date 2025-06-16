import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time

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


# เพิ่ม DataFrame สำหรับเก็บข้อมูลรายวัน (แยกตามวันที่)
# โดยแต่ละวันจะเก็บข้อมูลในรูปแบบ DataFrame ที่มีคอลัมน์เวลาครบ 24 ชั่วโมง
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