# pages/1_Quality_Check.py
import streamlit as st
import pandas as pd # import เมื่อจำเป็นเท่านั้น

st.title("หน้าตรวจสอบคุณภาพ")
st.write("นี่คือส่วนที่คุณเคยพัฒนาไว้สำหรับตรวจสอบคุณภาพ")

# ตัวอย่างการดึงข้อมูลจาก session_state
if 'df_machine_params' in st.session_state:
    st.subheader("ข้อมูล Machine Parameters (จากหน้าหลัก):")
    st.dataframe(st.session_state['df_machine_params'])
else:
    st.info("ข้อมูล Machine Parameters ยังไม่ถูกโหลด หรือไม่พร้อมใช้งาน")

if 'df_production_orders' in st.session_state:
    st.subheader("ข้อมูล Production Orders (จากหน้าหลัก):")
    st.dataframe(st.session_state['df_production_orders'])
else:
    st.info("ข้อมูล Production Orders ยังไม่ถูกโหลด หรือไม่พร้อมใช้งาน")

# ... (ส่วนโค้ดเดิมของหน้าตรวจคุณภาพที่คุณเคยเขียนไว้) ...

# pages/1_Quality_Check.py (ส่วนต่อจากโค้ดเดิม)

st.markdown("---") # เพิ่มเส้นแบ่ง
st.header("บันทึกผลการตรวจสอบคุณภาพ")

# กำหนดรายการตรวจสอบและเป้าหมาย (จากภาพที่คุณให้มา)
check_items = [
    {"item": "1. ความเร็วที่ใช้ในการเดินเครื่อง", "target": "30 - 60 รอบ/นาที"},
    {"item": "2. ตรวจสอบอุณหภูมิ Vertical Sealing", "target": "120-210 °C"},
    {"item": "3. ตรวจสอบอุณหภูมิ Upper Inner", "target": "90-155 °C"},
    {"item": "4. ตรวจสอบอุณหภูมิ Lower Inner", "target": "75-155 °C"},
    {"item": "5. ตรวจสอบอุณหภูมิ Upper Outer", "target": "90-155 °C"},
    {"item": "6. ตรวจสอบอุณหภูมิ Lower Outer", "target": "75-155 °C"},
    {"item": "7. ตรวจสอบอุณหภูมิ KR Carousel", "target": "60-200 °C"},
    {"item": "8. ตรวจสอบอุณหภูมิ KR hot top plate", "target": "85-180 °C"},
    {"item": "9. ตรวจสอบอุณหภูมิ KR hot bottom plate", "target": "60-140 °C"},
]

# กำหนดช่วงเวลาการตรวจสอบ (จากภาพที่คุณให้มา)
times = ["8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00",
         "16:00", "17:00", "18:00", "19:00", "20:00", "21:00"]
# หรือถ้าจะใช้เป็นช่วงเวลากลางคืนด้วย
# times = ["8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00",
#          "16:00", "17:00", "18:00", "19:00", "20:00", "21:00",
#          "19:00", "20:00", "21:00", "22:00", "23:00", "0:00", "1:00", "2:00",
#          "3:00", "4:00", "5:00", "6:00", "7:00", "8:00"] # ต้องแยกช่วงเวลาให้ชัดเจน

st.write("---") # เพิ่มเส้นแบ่ง

# สร้างส่วนหัวตาราง
cols = st.columns([0.2, 0.1] + [0.05] * len(times))
cols[0].write("**รายการตรวจสอบ**")
cols[1].write("**เป้าหมาย**")
for i, t in enumerate(times):
    cols[i+2].write(f"**{t}**")

# สร้างแถวข้อมูลสำหรับแต่ละรายการตรวจสอบ
# คุณอาจจะต้องมีวิธีบันทึกข้อมูลเหล่านี้จริงๆ ลงใน Google Sheets อีกที
# ตรงนี้แค่แสดงช่องให้กรอก
for i, item_info in enumerate(check_items):
    cols = st.columns([0.2, 0.1] + [0.05] * len(times))
    cols[0].write(item_info["item"])
    cols[1].write(item_info["target"])
    for j, t in enumerate(times):
        # สร้างช่องให้กรอกข้อมูล ตัวอย่างใช้ text_input
        # key ช่วยให้แต่ละช่องมี id ที่ไม่ซ้ำกัน
        cols[j+2].text_input(label="", key=f"qc_input_{i}_{j}", label_visibility="collapsed")

# ปุ่มสำหรับบันทึกข้อมูล (จะต้องมีโค้ดสำหรับบันทึกลง Google Sheets เพิ่มเติม)
st.markdown("---")
if st.button("บันทึกผลการตรวจสอบ"):
    st.success("บันทึกผลการตรวจสอบแล้ว! (ฟังก์ชันการบันทึกจริงยังไม่ได้เชื่อมต่อ)")
    # คุณจะต้องเขียนโค้ดที่นี่เพื่อนำข้อมูลจาก text_input ไปบันทึกลง Google Sheets