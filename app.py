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
st.markdown('<p class="sub-title">テキストテーマから、瞬時にLINEスタンプの規定サイズへ最適化する体験デモ</p>', unsafe_allow_html=True)

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
    placeholder="例: 敬語を使うシュールな白猫、関西弁のハムスター など"
)

st.markdown("<br>", unsafe_allow_html=True)

# 生成ボタン
if st.button("🚀 デモスタンプを生成する（1枚）", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ OpenAI APIキーを入力してください。")
    elif not theme:
        st.warning("⚠️ スタンプのテーマを入力してください。")
    else:
        with st.spinner("✨ AIがスタンプをデザインし、LINE規定サイズに整形中..."):
            try:
                client = openai.OpenAI(api_key=api_key)

                # DALL-E 3で高品質なスタンプ画像を生成
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=f"A cute sticker of {theme}, white background, flat vector art, clear clean outline, high contrast, transparent style, friendly",
                    size="1024x1024",
                    quality="standard",
                    n=1
                )

                image_url = response.data[0].url

                # 画像ダウンロード＆LINE規定サイズ（370x320）へリサイズ
                img_data = requests.get(image_url).content
                img = Image.open(io.BytesIO(img_data))
                img_resized = img.resize((370, 320), Image.Resampling.LANCZOS)

                # プレビュー表示
                st.success("🎉 生成＆レギュレーション整形が完了しました！")

                col1, col2 = st.columns(2)
                with col1:
                    st.image(img_resized, caption="LINE規定サイズ (370x320px)", use_container_width=True)
                with col2:
                    st.markdown("#### 💡 デモの自動化ポイント")
                    st.write("✅ テキストからのAIデザイン生成")
                    st.write("✅ LINE専用サイズ（370x320）へ自動リサイズ")
                    st.markdown("---")
                    st.caption("※製品版では「40個一括生成」「ZIP一括DL」のフル機能が手に入ります。")

                # マネタイズ導線（Stripe決済リンク直結）
                st.markdown("---")
                st.markdown("""
                <div class="info-box">
                    <strong>🔥 自分専用のフルスペック生成機を手に入れませんか？</strong><br>
                    面倒な40個のスタンプ作成とZIP一括エクスポートを完全自動化できるソースコードを手元に導入できます。
                </div>
                """, unsafe_allow_html=True)
                
                st.link_button(
                    "🔒 フルスペック版のソースコード（権利）を手に入れる",
                    "https://buy.stripe.com/eVqaEWchM1MlENtbn8eZ20i",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"❌ エラーが発生しました: {e}\n※OpenAIアカウントに残高（クレジット）があるか、DALL-E 3が利用可能なプランかご確認ください。")

# フッター
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888; font-size: 0.8rem;'>© 2026 StickerGen AI Platform. Built with Streamlit & OpenAI API.</p>",
    unsafe_allow_html=True
)
