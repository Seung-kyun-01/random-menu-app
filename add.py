import time
import os
import pandas as pd
import streamlit as st

# --- 1. 페이지 기본 설정 ---
st.set_page_config(page_title="랜덤 메뉴 추천기", page_icon="🍔")
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)


# --- 2. 데이터 & 기능 함수 정의 (항상 맨 위에 있어야 에러가 안 나!) ---
@st.cache_data
def load_data():
    # 메뉴 데이터 불러오기
    return pd.read_csv("final_menu_db_v3.csv", encoding="utf-8-sig")


COMMENT_FILE = "comments.csv"


def load_comments():
    # 댓글 데이터 불러오기 (파일이 없으면 빈 표 만들기)
    if not os.path.exists(COMMENT_FILE):
        return pd.DataFrame(columns=["닉네임", "내용", "시간"])
    return pd.read_csv(COMMENT_FILE, encoding="utf-8-sig")


def save_comment(nickname, content):
    # 새 댓글 저장하기
    new_comment = pd.DataFrame({
        "닉네임": [nickname],
        "내용": [content],
        "시간": [time.strftime("%Y-%m-%d %H:%M:%S")]
    })
    new_comment.to_csv(COMMENT_FILE, mode='a', header=not os.path.exists(COMMENT_FILE), index=False,
                       encoding="utf-8-sig")


# --- 3. 사이드바 (왼쪽 메뉴) ---
st.sidebar.title("🍔 내비게이션")
menu = st.sidebar.radio("이동할 화면을 선택하세요", ["🎲 메뉴 추천받기", "💬 커뮤니티 (방명록)"])

# --- 4. 화면 분기 (선택한 메뉴에 따라 다른 화면 보여주기) ---

if menu == "🎲 메뉴 추천받기":
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

    if st.button("🎲 메뉴 추천받기!", use_container_width=True):
        filtered_df = df[df['time_slot'].isin(selected_times) & df['category'].isin(selected_categories)]

        if filtered_df.empty:
            st.warning("조건에 맞는 메뉴가 없습니다. 필터를 조정해주세요.")
        else:
            message_box = st.empty()
            for _ in range(20):
                temp_name = filtered_df.sample(1).iloc[0]['name']
                message_box.info(f"🎲 운명의 메뉴 탐색 중... [ {temp_name} ]")
                time.sleep(0.1)
            message_box.empty()

            result = filtered_df.sample(1).iloc[0]

            # 압도적인 크기의 결과 텍스트
            st.markdown(f"""
                <div style='text-align: center; margin: 20px 0;'>
                    <p style='font-size: 20px; color: gray;'>오늘의 추천 메뉴는 바로!</p>
                    <h1 style='font-size: 60px; color: #FF4B4B; font-weight: 900; margin: 0;'>{result['name']}</h1>
                </div>
            """, unsafe_allow_html=True)

            # 지도 버튼
            search_keyword = result['name']
            naver_map_url = f"https://map.naver.com/v5/search/{search_keyword}"
            st.link_button(f"🗺️ 내 주변 '{search_keyword}' 맛집 지도에서 찾기 (클릭)", naver_map_url, use_container_width=True)

            # 사진 및 정보
            st.image(result['image_url'], use_container_width=True)
            st.info(f"💡 카테고리: {result['category']} | ⏰ 추천 시간대: {result['time_slot']}")
            st.write(f"🏷️ 태그: {result['tags']}")
            st.caption(f"📝 설명: {result['desc']}")
            st.balloons()

elif menu == "💬 커뮤니티 (방명록)":
    st.title("💬 사용자 소통 공간")
    st.success("📢 [공지] 랜덤 메뉴 추천하고 인증샷 이벤트 참여하세요! (운영자)")

    # 댓글 입력 폼
    with st.form("comment_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 4])
        nickname = col1.text_input("닉네임", max_chars=10)
        content = col2.text_input("댓글 내용")
        submit_button = st.form_submit_button("댓글 남기기")

        if submit_button:
            if nickname and content:
                save_comment(nickname, content)
                st.rerun()  # 저장 후 새로고침
            else:
                st.warning("닉네임과 내용을 모두 입력해주세요.")

    # 댓글 리스트 출력
    comments_df = load_comments()
    if not comments_df.empty:
        st.write("---")
        for _, row in comments_df.iloc[::-1].iterrows():  # 최신순 정렬
            # 운영자 강조 로직
            if row['닉네임'] == "운영자":
                st.info(f"✨ **{row['닉네임']}**: {row['내용']} ({row['시간']})")
            else:
                st.write(f"**{row['닉네임']}**: {row['내용']} ({row['시간']})")