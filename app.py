import io
from PIL import Image
import openai
import requests
import streamlit as st

# ページの基本設定
st.set_page_config(
    page_title="LINEスタンプAIジェネレーター [デモ]", layout="centered"
)

st.title("🎨 LINEスタンプ AIジェネレーター (Demo)")
st.write(
    "あなたのアイデアを投げ入れるだけで、LINEスタンプの規定サイズに自動変換するデモ機です。"
)

# 1. APIキー入力エリア
st.sidebar.header("⚙️ 設定")
api_key = st.sidebar.text_input(
    "OpenAI APIキー (sk-...)", type="password", help="ご自身のAPIキーを入力してください"
)

st.markdown("---")

# 2. メイン入力エリア
theme = st.text_input(
    "💡 作りたいスタンプのテーマ・キャラクター",
    placeholder="例: 敬語を使うシュールな猫の日常、関西弁のウサギ など",
)

# デモ用の制限（1枚生成）
if st.button("🚀 デモスタンプを1枚生成してみる", type="primary"):
  if not api_key:
    st.error(
        "⚠️ サイドバーにOpenAI APIキーを入力してください。"
        "（キーはサーバーに保存されません）"
    )
  elif not theme:
    st.warning("⚠️ テーマを入力してください。")
  else:
    with st.spinner("✨ AIがスタンプを生成し、LINE規定サイズに整形中..."):
      try:
        # OpenAIクライアントの初期化
        client = openai.OpenAI(api_key=api_key)

        # DALL-E 3で画像生成（正方形で生成）
        response = client.images.generate(
            model="dall-e-3",
            prompt=(
                f"A cute sticker of {theme}, white background, flat vector art,"
                " clear clean outline, high contrast, transparent style"
                " friendly"
            ),
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        # 画像のダウンロード
        img_data = requests.get(image_url).content
        img = Image.open(io.BytesIO(img_data))

        # LINEスタンプの規定サイズ（横370px × 縦320px）にリサイズ
        img_resized = img.resize((370, 320), Image.Resampling.LANCZOS)

        # 3. プレビュー表示
        st.success("🎉 生成＆レギュレーション整形が完了しました！")

        col1, col2 = st.columns(2)
        with col1:
          st.image(
              img_resized,
              caption="LINE規定サイズ (370x320px)",
              use_container_width=True,
          )
        with col2:
          st.markdown("### 📌 このデモで自動化されたこと")
          st.write("✅ DALL-E 3による高品質なキャラクター生成")
          st.write("✅ LINEスタンプ専用サイズ（370x320）への自動リサイズ")
          st.write("*(※製品版では背景透過・40個一括生成・ZIP一括DLに対応)*")

        # 4. マネタイズ・購入への導線（CTA）
        st.markdown("---")
        st.info(
            "💡 **「40個一括生成」「背景自動透過」「一括ZIPダウンロード」**"
            "ができる自分専用のジェネレーターが欲しいですか？"
        )

        st.link_button(
            "🔒 自分専用のスタンプ生成機（ソースコード）を手に入れる",
            "https://example.com/your-checkout-page",
            use_container_width=True,
        )

      except Exception as e:
        st.error(
            f"❌ エラーが発生しました: {e}\nAPIキーや残高をご確認ください。"
        )

# フッター
st.markdown("---")
st.caption(
    "© 2026 Stamp Generator Platform. Built with Streamlit & OpenAI API."
)
