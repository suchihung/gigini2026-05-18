import streamlit as st
import json
from google import genai
from google.genai import types
 
# 頁面設定
st.set_page_config(page_title="附中 AI 導覽員")
st.title("陽明交大附中 - 67導覽")
 
# 讀取背景知識
try:
	with open('tour.json', 'r', encoding='utf-8') as f:
		context_data = json.load(f)
		context_text = json.dumps(context_data, ensure_ascii=False)
except FileNotFoundError:
	st.error("找不到 tour.json 檔案")
	st.stop()
except Exception as e:
	st.error(f"讀取 JSON 發生錯誤：{e}")
	st.stop()

# 初始化 API 與對話
if "gemini_client" not in st.session_state:
	try:
    	api_key = st.secrets["GEMINI_API_KEY"]
	except KeyError:
    	st.error("未找到 GEMINI_API_KEY")
    	st.stop()
 
	client = genai.Client(api_key=api_key)
	st.session_state.gemini_client = client
 
	system_instruction = (
    	f"你是陽明交大附中導覽員「67」。\n"
    	f"請優先參考以下內容回答，若找不到請自動搜尋。\n\n"
    	f"內容：\n{context_text}"
	)


	config = types.GenerateContentConfig(
    	system_instruction=system_instruction,
    	tools=[types.Tool(google_search=types.GoogleSearch())],
    	temperature=0.7,
	)
	st.session_state.config = config
 
	# 設定使用 Gemini 2.5
	st.session_state.chat_session = client.chats.create(
    	model="gemini-2.5-flash",
    	config=config
	)
	
	st.session_state.messages = [
    	{"role": "assistant", "content": "你好，我是導覽員67，請隨時發問。"}
	]
# 顯示歷史紀錄
for msg in st.session_state.messages:
	with st.chat_message(msg["role"]):
    	st.write(msg["content"])
 
# 處理輸入
if prompt := st.chat_input("想問什麼事"):
	st.chat_message("user").write(prompt)
	st.session_state.messages.append({"role": "user", "content": prompt})

	with st.spinner("處理中"):
    	try:
        	response = st.session_state.chat_session.send_message(prompt)
        	response_text = response.text
        	
        	st.chat_message("assistant").write(response_text)
        	st.session_state.messages.append({"role": "assistant", "content": response_text})
        	
    	except Exception as e:
        	st.error(f"對話發生異常：{e}")
        	st.info("可能是 API 或模型限制")

