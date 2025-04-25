import re
import pandas as pd
import streamlit as st

st.title("📝 テロップ誤字チェッカー（日本語 & 英語対応）")

# 言語選択
lang = st.radio("チェックする言語を選んでください", ("日本語", "English"))

# ファイルアップロード
uploaded_file = st.file_uploader("テロップファイル（.txt）をアップロードしてください", type="txt")

if uploaded_file is not None:
    lines = uploaded_file.read().decode("utf-8").splitlines()
    
    # タイムコードとテキスト抽出
    time_pattern = re.compile(r"\d{2}:\d{2}:\d{2}:\d{2}")
    entries = []
    current_time = ""
    for line in lines:
        line = line.strip()
        if time_pattern.match(line):
            current_time = line
        elif line and not line.startswith("V"):
            entries.append((current_time, line))
    
    df = pd.DataFrame(entries, columns=["Time", "Text"])

    # チェックパターン定義
    if lang == "日本語":
        error_patterns = {
            "が着ていない": "助詞誤用（服**を**着ていない）",
            "なかったでした": "二重否定的表現",
            "下ない": "誤字（出ない・掘れない？）",
            "意外連打": "助詞抜け（意外**に/と**連打）",
            "玄海を迎えて": "誤変換（限界）",
            "子ども達": "表記揺れ（たち推奨）"
        }
    else:  # English
        error_patterns = {
            r"\byour\b.*\byou're\b|\byou're\b.*\byour\b": "your / you're 混同",
            r"\btheir\b.*\bthere\b|\bthere\b.*\btheir\b": "their / there 混同",
            r"\bits\b.*\bit's\b|\bit's\b.*\bits\b": "its / it's 混同",
            r"\bteh\b": "誤字（teh → the）",
            r"\brecieve\b": "誤字（recieve → receive）",
            r"\bseperate\b": "誤字（seperate → separate）",
            r"\boccured\b": "誤字（occured → occurred）",
            r"\bsuprising\b": "誤字（suprising → surprising）"
        }

    # 検出関数
    def find_error(text):
        for pattern, comment in error_patterns.items():
            if re.search(pattern, text, flags=re.IGNORECASE):
                return pattern, comment
        return None, None

    df[["Matched Pattern", "Comment"]] = df["Text"].apply(lambda t: pd.Series(find_error(t)))
    error_df = df[df["Matched Pattern"].notnull()].reset_index(drop=True)

    st.subheader("🔍 検出された誤字・文法ミス")
    st.dataframe(error_df)

    csv = error_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 誤字一覧をCSVでダウンロード", csv, "errors.csv", "text/csv")

else:
    st.info("まずは .txt ファイルをアップロードしてください。")
