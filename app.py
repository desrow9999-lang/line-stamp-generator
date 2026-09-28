import io
import zipfile
from PIL import Image
import openai
import requests
import streamlit as st

# ページの基本設定
st.set_page_config(
    page_title="StickerGen AI | 体験デモ",
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
    .info-box {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #FF3366;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ヘッダーセクション
st.markdown('<p class="main-title">✨ StickerGen AI Studio (Demo)</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">本番と同じUIで、まずは4個のスタンプ生成を無料でお試し体験！</p>', unsafe_allow_html=True)

# 1. APIキー入力エリア
st.markdown("### 🔑 Step 1: OpenAI APIキーの設定")
api_key = st.text_input(
    "OpenAI API Key",
    type="password",
    placeholder="sk-...",
    help="※画像生成を利用するためには、残高（クレジット）がチャージされたAPIキーが必要です。"
)

st.markdown("---")

# 2. テーマ入力エリア
st.markdown("### 🎨 Step 2: スタンプのテーマを入力")
theme = st.text_input(
    "作りたいキャラクターやメッセージのテーマ",
    placeholder="例: 敬語を使うシュールな白猫 など"
)

# デモ版では個数を「最大4個まで」に固定・制限
num_stickers = 4
st.info("💡 デモ版では動作確認のため、**4個**のスタンプを生成してZIPでお試しいただけます。（※製品版では最大40個一括生成に対応）")

st.markdown("<br>", unsafe_allow_html=True)

# 生成ボタン
if st.button("🚀 デモスタンプを4個生成＆ZIP化する", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ OpenAI APIキーを入力してください。")
    elif not theme:
        st.warning("⚠️ スタンプのテーマを入力してください。")
    else:
        with st.spinner("✨ AIがスタンプをデザインし、LINE規定サイズに整形中..."):
            try:
                client = openai.OpenAI(api_key=api_key)
                zip_buffer = io.BytesIO()

                progress_bar = st.progress(0)
                status_text = st.empty()

                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for i in range(num_stickers):
                        status_text.text(f"✨ スタンプ生成中... ({i+1}/{num_stickers}枚目)")
                        progress_bar.progress((i + 1) / num_stickers)

                        prompt = f"A cute sticker of {theme}, variation {i+1}, white background, flat vector art, clear clean outline, high contrast, friendly"
                        
                        response = client.images.generate(
                            model="dall-e-3",
                            prompt=prompt,
                            size="1024x1024",
                            quality="standard",
                            n=1
                        )

                        image_url = response.data[0].url
                        img_data = requests.get(image_url).content
                        img = Image.open(io.BytesIO(img_data))
                        
                        # LINE規定サイズ（370x320）へリサイズ
                        img_resized = img.resize((370, 320), Image.Resampling.LANCZOS)

                        img_byte_arr = io.BytesIO()
                        img_resized.save(img_byte_arr, format="PNG")
                        file_name = f"{str(i+1).zfill(2)}.png"
                        zip_file.writestr(file_name, img_byte_arr.getvalue())

                status_text.text("🎉 生成が完了しました！")
                progress_bar.progress(1.0)

                st.success("✨ デモ版のパッケージ（4個）が完成しました！")
                st.download_button(
                    label="📦 デモ用ZIPをダウンロード",
                    data=zip_buffer.getvalue(),
                    file_name="demo_stickers_4pcs.zip",
                    mime="application/zip",
                    use_container_width=True,
                )

                # マネタイズ導線（Stripe決済リンク）
                st.markdown("---")
                st.markdown("""
                <div class="info-box">
                    <strong>🔥 本格的に40個のスタンプを作りたい方へ</strong><br>
                    デモ版は4個までの制限がありますが、フルスペック版のソースコードを手に入れれば、LINE申請に必要な40個一括生成・メイン/タブ画像の自動作成が使い放題になります！
                </div>
                """, unsafe_allow_html=True)
                
                st.link_button(
                    "🔒 フルスペック版のソースコード（権利）を手に入れる（￥4,980）",
                    "https://buy.stripe.com/eVqaEWchM1MlENtbn8eZ20i",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"❌ エラーが発生しました: {e}\n※OpenAIアカウントに残高があるかご確認ください。")

# フッター
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888; font-size: 0.8rem;'>© 2026 StickerGen AI Platform. Built with Streamlit & OpenAI API.</p>",
    unsafe_allow_html=True
)
