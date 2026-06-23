import time
import os
import pandas as pd
import streamlit as st

# --- 1. 페이지 기본 설정 ---
# 💡 사이드바와 사용법을 위해 화면을 넓게 쓰도록 layout="wide" 추가
st.set_page_config(page_title="랜덤 메뉴 추천기", page_icon="🍔", layout="wide")

# 💡 수정됨: 구글 크롬 + 엣지 브라우저 번역 방지 태그를 안전하게 주입
st.markdown("""
    <meta name="google" content="notranslate">
    <meta name="translate" content="no">
""", unsafe_allow_html=True)

# 💡 [3번 요청] 메뉴 추천받기 버튼 글자를 초록색으로 바꾸는 CSS 주입
st.markdown("""
<style>
div.stButton > button p {
    color: #28a745 !important; /* 초록색 */
    font-weight: 800 !important;
}
</style>
""", unsafe_allow_html=True)


# --- 2. 데이터 & 기능 함수 정의 ---
@st.cache_data
def load_data():
    return pd.read_csv("final_menu_db_v3.csv", encoding="utf-8-sig")


COMMENT_FILE = "comments.csv"


def load_comments():
    if not os.path.exists(COMMENT_FILE):
        return pd.DataFrame(columns=["닉네임", "내용", "시간"])
    return pd.read_csv(COMMENT_FILE, encoding="utf-8-sig")


def save_comment(nickname, content):
    new_comment = pd.DataFrame({
        "닉네임": [nickname],
        "내용": [content],
        "시간": [time.strftime("%Y-%m-%d %H:%M:%S")]
    })
    new_comment.to_csv(COMMENT_FILE, mode='a', header=not os.path.exists(COMMENT_FILE), index=False,
                       encoding="utf-8-sig")


# --- 3. 사이드바 ---
st.sidebar.title("🍔 목록")  # 💡 1번 요청: 내비게이션 -> 목록 변경
menu = st.sidebar.radio("이동할 화면을 선택하세요", ["🎲 메뉴 추천받기", "💬 커뮤니티 (방명록)"])

# --- 4. 화면 분기 ---
if menu == "🎲 메뉴 추천받기":

    # 💡 4번 요청: 화면을 7:3 비율로 나누어 오른쪽에 사용법 배치
    main_col, guide_col = st.columns([7, 3])

    with guide_col:
        # 애드센스 승인에 큰 도움이 되는 텍스트 콘텐츠 (사용법)
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #28a745; margin-top: 20px;">
            <h3 style="margin-bottom: 15px;">📖 사이트 사용법</h3>
            <p><b>1. 필터 선택하기</b><br>오늘의 기분과 상황에 맞춰 시간대와 음식 종류를 골라주세요. 중복 선택도 가능합니다.</p>
            <p><b>2. 메뉴 추천받기</b><br>조건을 모두 골랐다면 <b>메뉴 추천받기!</b> 버튼을 눌러주세요. 시스템이 최적의 메뉴를 탐색합니다.</p>
            <p><b>3. 주변 맛집 찾기</b><br>결과 화면 아래의 <b>초록색 지도 버튼</b>을 누르면, 현재 내 위치 주변의 해당 맛집을 네이버 지도에서 바로 확인할 수 있습니다.</p>
            <p><b>4. 커뮤니티 소통</b><br>왼쪽 목록 메뉴에서 '커뮤니티'로 이동해 다른 사용자들과 맛집 정보를 공유해 보세요!</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("💡 팁: 다양한 필터를 조합해서 매일 새로운 메뉴를 발견해 보세요!")

    with main_col:
        st.title("🍔 랜덤 메뉴 추천기")
        df = load_data()

        col1, col2 = st.columns(2)
        with col1:
            time_slots = df['time_slot'].unique().tolist()
            selected_times = st.multiselect("⏰ 시간대", options=time_slots, default=time_slots)
        with col2:
            categories = df['category'].unique().tolist()
            selected_categories = st.multiselect("✅ 종류", options=categories, default=categories)

        st.divider()

        # 버튼 텍스트는 상단의 CSS를 통해 초록색으로 자동 변경됨
        if st.button("🎲 메뉴 추천받기!", use_container_width=True):
            filtered_df = df[df['time_slot'].isin(selected_times) & df['category'].isin(selected_categories)]

            if filtered_df.empty:
                st.warning("조건에 맞는 메뉴가 없습니다. 필터를 조정해주세요.")
            else:
                message_box = st.empty()

                for _ in range(20):
                    temp_name = filtered_df.sample(1).iloc[0]['name']
                    slot_html = f"""
                    <div style="background-color: #262730; border: 5px solid #FF4B4B; border-radius: 20px; padding: 40px; text-align: center; box-shadow: 0 8px 16px rgba(0,0,0,0.3);">
                        <h3 style="color: #FAFAFA; margin-bottom: 15px;">🎰 운명의 룰렛을 돌리는 중...</h3>
                        <h1 style="font-size: 60px; color: #FF4B4B; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">{temp_name}</h1>
                    </div>
                    """
                    message_box.markdown(slot_html, unsafe_allow_html=True)
                    time.sleep(0.1)

                message_box.empty()

                result = filtered_df.sample(1).iloc[0]

                st.markdown(f"""
                    <div style='text-align: center; margin: 20px 0;'>
                        <p style='font-size: 20px; color: gray;'>오늘의 추천 메뉴는 바로!</p>
                        <h1 style='font-size: 60px; color: #FF4B4B; font-weight: 900; margin: 0;'>{result['name']}</h1>
                    </div>
                """, unsafe_allow_html=True)

                # 💡 2번 요청: 지도 버튼 안을 초록색으로 꽉 채우기 (HTML a 태그 활용)
                search_keyword = result['name']
                naver_map_url = f"https://map.naver.com/v5/search/{search_keyword}"
                st.markdown(f"""
                <a href="{naver_map_url}" target="_blank" style="display: block; width: 100%; text-align: center; background-color: #28a745; color: white; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.3s;">
                    🗺️ 내 주변 '{search_keyword}' 맛집 지도에서 찾기 (클릭)
                </a>
                """, unsafe_allow_html=True)

                st.image(result['image_url'], use_container_width=True)
                st.info(f"💡 카테고리: {result['category']} | ⏰ 추천 시간대: {result['time_slot']}")
                st.write(f"🏷️ 태그: {result['tags']}")
                st.caption(f"📝 설명: {result['desc']}")

                food_rain_css = """
                <style>
                @keyframes fall {
                    0% { top: -10%; transform: translateX(0) rotate(0deg); opacity: 1; }
                    100% { top: 110%; transform: translateX(30px) rotate(360deg); opacity: 0; }
                }
                .food-emoji {
                    position: fixed;
                    font-size: 50px;
                    z-index: 9999;
                    animation: fall 3s linear forwards;
                }
                </style>
                <div class="food-emoji" style="left: 10%; animation-duration: 2.5s;">🍔</div>
                <div class="food-emoji" style="left: 30%; animation-duration: 3.2s; animation-delay: 0.2s;">🍕</div>
                <div class="food-emoji" style="left: 50%; animation-duration: 2.8s; animation-delay: 0.5s;">🍗</div>
                <div class="food-emoji" style="left: 70%; animation-duration: 3.5s; animation-delay: 0.1s;">🍣</div>
                <div class="food-emoji" style="left: 90%; animation-duration: 3.0s; animation-delay: 0.4s;">🍜</div>
                """
                st.markdown(food_rain_css, unsafe_allow_html=True)

elif menu == "💬 커뮤니티 (방명록)":
    st.title("💬 사용자 소통 공간")
    st.success("📢 [공지] 랜덤 메뉴 추천하고 인증샷 이벤트 참여하세요! (운영자)")

    with st.form("comment_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 4])
        nickname = col1.text_input("닉네임", max_chars=10)
        content = col2.text_input("댓글 내용")
        submit_button = st.form_submit_button("댓글 남기기")

        if submit_button:
            if nickname and content:
                save_comment(nickname, content)
                st.rerun()
            else:
                st.warning("닉네임과 내용을 모두 입력해주세요.")

    comments_df = load_comments()
    if not comments_df.empty:
        st.write("---")
        for _, row in comments_df.iloc[::-1].iterrows():
            if row['닉네임'] == "운영자":
                st.info(f"✨ **{row['닉네임']}**: {row['내용']} ({row['시간']})")
            else:
                st.write(f"**{row['닉네임']}**: {row['내용']} ({row['시간']})")