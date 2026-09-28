import base64
import io
from PIL import Image
import openai
import requests
import streamlit as st

# ページの基本設定
st.set_page_config(
    page_title="StickerGen AI | LINEスタンプ自動生成プラットフォーム",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# スタイリッシュなカスタムCSS
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #FF3366, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1rem;
        color: #666666;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ヘッダーセクション
st.markdown('<p class="main-title">✨ StickerGen AI Studio</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">アイデアやラフ画像を瞬時にLINEスタンプの規定サイズへ最適化する次世代クリエイターツール</p>', unsafe_allow_html=True)

# 1. APIキー入力エリア
st.markdown("### 🔑 Step 1: OpenAI APIキーの設定")
api_key = st.text_input(
    "OpenAI API Key",
    type="password",
    placeholder="sk-...",
    help="ご自身のOpenAI APIキーを入力してください（サーバーには保存されません）"
)

st.markdown("---")

# 2. テーマ入力 ＆ 画像アップロードエリア
st.markdown("### 🎨 Step 2: スタンプのテーマ入力 または ラフ画のアップロード")
theme = st.text_input(
    "テキストテーマで指定する場合",
    placeholder="例: 敬語を使うシュールな白猫、関西弁のハムスター など"
)

uploaded_file = st.file_uploader(
    "または、手描きのラフ画や参考画像をアップロード (PNG / JPG)",
    type=["png", "jpg", "jpeg"]
)

st.markdown("<br>", unsafe_allow_html=True)

# 生成ボタン
if st.button("🚀 デモスタンプを生成する（1枚）", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ OpenAI APIキーを入力してください。")
    elif not theme and not uploaded_file:
        st.warning("⚠️ テキストテーマを入力するか、画像をアップロードしてください。")
    else:
        with st.spinner("✨ AIが画像やテーマを解析し、スタンプを生成中..."):
            try:
                client = openai.OpenAI(api_key=api_key)
                
                final_prompt = ""
                
                # 画像がアップロードされている場合はGPT-4oでビジョン解析してプロンプト化
                if uploaded_file:
                    image_bytes = uploaded_file.getvalue()
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                    
                    vision_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Analyze this image and describe it concisely as a character for a cute vector sticker, maintaining its core features."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ]
                            }
                        ],
                        max_tokens=300
                    )
                    desc = vision_response.choices[0].message.content
                    final_prompt = f"A cute sticker of {desc}, white background, flat vector art, clear clean outline, high contrast"
                else:
                    final_prompt = f"A cute sticker of {theme}, white background, flat vector art, clear clean outline, high contrast, friendly"

                # DALL-E 2で画像生成（※dall-e-3が使えない環境への互換性対応）
                response = client.images.generate(
                    model="dall-e-2",
                    prompt=final_prompt,
                    size="512x512",
                    n=1
                )

                image_url = response.data[0].url

                # 画像ダウンロード＆リサイズ
                img_data = requests.get(image_url).content
                img = Image.open(io.BytesIO(img_data))
                img_resized = img.resize((370, 320), Image.Resampling.LANCZOS)

                # プレビュー表示
                st.success("🎉 生成＆レギュレーション整形が完了しました！")

                col1, col2 = st.columns(2)
                with col1:
                    st.image(img_resized, caption="LINE規定サイズ (370x320px)", use_container_width=True)
                with col2:
                    st.markdown("#### 💡 自動化されたポイント")
                    st.write("✅ テキスト/画像からのマルチモーダル解析")
                    st.write("✅ AIによる高品質スタンプ化")
                    st.write("✅ LINE専用サイズ（370x320）へ自動リサイズ")
                    st.markdown("*※製品版では40個一括・背景透過・ZIP出力に対応*")

                # マネタイズ導線（CTA）
                st.markdown("---")
                st.info("💡 **「40個一括生成」「背景自動透過」「一括ZIPダウンロード」** ができる自分専用のジェネレーター環境を手に入れませんか？")
                
                st.link_button(
                    "🔒 自分専用のスタンプ生成機（ソースコード）を手に入れる",
                    "https://example.com/your-checkout-page",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"❌ エラーが発生しました: {e}\nAPIキーやアカウント残高をご確認ください。")

# フッター
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888; font-size: 0.8rem;'>© 2026 StickerGen AI Platform. Built with Streamlit & OpenAI API.</p>",
    unsafe_allow_html=True
)
