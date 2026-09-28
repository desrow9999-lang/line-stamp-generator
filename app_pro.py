import io
import zipfile
from PIL import Image
import openai
import requests
import streamlit as st

# ページの基本設定
st.set_page_config(
    page_title="StickerGen AI Pro | フルスペック版", layout="centered"
)

st.title("🔥 StickerGen AI Pro (フルスペック版)")
st.write(
    "LINEスタンプ40個の一括生成、リサイズ、ZIPファイル一括ダウンロードを行う自分専用のジェネレーターです。"
)

# 1. APIキー設定
api_key = st.text_input("OpenAI APIキー (sk-...)", type="password")

st.markdown("---")

# 2. プロンプト（テーマ）入力
theme = st.text_input(
    "スタンプのキャラクター・テーマ",
    placeholder="例: 敬語を使うシュールな白猫の日常",
)

# 生成個数の選択（LINEスタンプは通常8, 16, 24, 32, 40個）
num_stickers = st.selectbox("生成するスタンプの個数", [8, 16, 24, 32, 40], index=4)

if st.button("🚀 40個のスタンプを一括生成＆ZIP化する", type="primary"):
  if not api_key:
    st.error("⚠️ APIキーを入力してください。")
  elif not theme:
    st.warning("⚠️ テーマを入力してください。")
  else:
    client = openai.OpenAI(api_key=api_key)
    zip_buffer = io.BytesIO()

    progress_bar = st.progress(0)
    status_text = st.empty()

    # ZIPファイルに画像を格納していく処理
    with zipfile.ZipFile(
        zip_buffer, "w", zipfile.ZIP_DEFLATED
    ) as zip_file:
      for i in range(num_stickers):
        status_text.text(
            f"✨ スタンプ生成中... ({i+1}/{num_stickers}枚目)"
        )
        progress_bar.progress((i + 1) / num_stickers)

        try:
          # バリエーション豊かに生成するためのプロンプト調整
          prompt = (
              f"A cute sticker of {theme}, variation {i+1}, white background,"
              " flat vector art, clear clean outline, high contrast, friendly"
          )

          response = client.images.generate(
              model="dall-e-3",
              prompt=prompt,
              size="1024x1024",
              quality="standard",
              n=1,
          )

          image_url = response.data[0].url
          img_data = requests.get(image_url).content
          img = Image.open(io.BytesIO(img_data))

          # LINE規定サイズ（370x320）にリサイズ
          img_resized = img.resize((370, 320), Image.Resampling.LANCZOS)

          # バイト形式に変換してZIPに追加 (01.png, 02.png ...)
          img_byte_arr = io.BytesIO()
          img_resized.save(img_byte_arr, format="PNG")
          file_name = f"{str(i+1).zfill(2)}.png"
          zip_file.writestr(file_name, img_byte_arr.getvalue())

        except Exception as e:
          st.error(f"エラーが発生しました ({i+1}枚目): {e}")
          break

      # LINE申請用に必要な「メイン画像 (main.png)」と「タブ画像 (tab.png)」も自動生成してZIPに含める
      try:
        status_text.text("📁 メイン画像とタブ画像を生成中...")
        main_res = client.images.generate(
            model="dall-e-3",
            prompt=f"Main banner image for sticker of {theme}, cute vector art",
            size="1024x1024",
            n=1,
        )
        main_img = Image.open(
            io.BytesIO(requests.get(main_res.data[0].url).content)
        )
        # メイン画像サイズ: 240×240
        main_img = main_img.resize((240, 240), Image.Resampling.LANCZOS)
        m_arr = io.BytesIO()
        main_img.save(m_arr, format="PNG")
        zip_file.writestr("main.png", m_arr.getvalue())

        # タブ画像サイズ: 96×74
        tab_img = main_img.resize((96, 74), Image.Resampling.LANCZOS)
        t_arr = io.BytesIO()
        tab_img.save(t_arr, format="PNG")
        zip_file.writestr("tab.png", t_arr.getvalue())

      except Exception as e:
        print(f"Main/Tab error: {e}")

    status_text.text("🎉 すべての処理が完了しました！")
    progress_bar.progress(1.0)

    # ダウンロードボタンの表示
    st.success("✨ LINE申請用パッケージ（ZIP）の作成が完了しました！")
    st.download_button(
        label="📦 スタンプ画像一括ZIPをダウンロード",
        data=zip_buffer.getvalue(),
        file_name="line_stickers_package.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True,
    )
