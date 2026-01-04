import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

# 頁面設定
st.set_page_config(page_title="AI 股市分析大師", layout="centered")

st.title("📈 AI 股票趨勢分析")
st.caption("輸入股票代號，讓 Gemini 為您解讀市場趨勢")

# 側邊欄設定
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("輸入 Gemini API Key", type="password")
    target_stock = st.text_input("股票代碼 (例如: 2330.TW 或 AAPL)", value="2330.TW")
    period = st.selectbox("分析區間", ["1mo", "3mo", "6mo", "1y"])

# 主程式邏輯
if st.button("開始分析"):
    if not api_key:
        st.warning("請在左側選單輸入 API Key")
    else:
        try:
            # 1. 配置 Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')

            # 2. 抓取數據
            with st.spinner('正在獲取市場數據...'):
                stock = yf.Ticker(target_stock)
                hist = stock.history(period=period)
                current_price = hist['Close'].iloc[-1]
                
                # 計算簡單指標 (均線)
                hist['MA20'] = hist['Close'].rolling(window=20).mean()
                ma20_current = hist['MA20'].iloc[-1]
                
            # 3. 顯示圖表
            st.subheader(f"{target_stock} 歷史走勢")
            st.line_chart(hist[['Close', 'MA20']])

            # 4. AI 分析
            with st.spinner('Gemini 正在分析趨勢...'):
                prompt = f"""
                你是一位資深股市分析師。請針對 {target_stock} 的數據進行分析：
                - 當前股價: {current_price:.2f}
                - 20日均線(MA20): {ma20_current:.2f}
                - 趨勢觀察: {"股價在均線上空" if current_price > ma20_current else "股價在均線下方"}
                
                請用白話文給予投資人分析，包括：
                1. 目前的市場情緒。
                2. 技術面的具體建議。
                3. 風險提示。
                字數請控制在 200 字內。
                """
                response = model.generate_content(prompt)
                
                st.subheader("🤖 AI 專業點評")
                st.write(response.text)
                
        except Exception as e:

            st.error(f"發生錯誤: {e}")



