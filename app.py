import time
from dataclasses import dataclass
from typing import List, Dict
import streamlit as st

DEFAULTS = {
    "prep_seconds_hold": 5,
    "rest_seconds_skill": 120,
    "rest_seconds_power": 90,
    "rest_seconds_strength": 75,
    "rest_seconds_accessory": 45,
    "rest_seconds_block": 60,
    "auto_next": False,
}

SKILLS = [
    "머슬업",
    "프론트 레버",
    "핸드스탠드 푸쉬업",
    "플란체",
    "V-sit",
    "피스톨 스쿼트",
    "백 레버",
]

EQUIPMENT = [
    "풀업바",
    "딥스 가능(평행봉/의자 포함)",
    "벽 사용 가능",
    "덤벨",
    "바벨",
    "밴드",
    "링/낮은바",
    "바닥만 가능",
]

@dataclass
class Exercise:
    name: str
    kind: str            # rep | hold
    reps: int
    sets: int
    work_seconds: int
    rest_seconds: int
    cues: str

def init_state():
    st.session_state.setdefault("step", 1)
    st.session_state.setdefault("settings", DEFAULTS.copy())
    st.session_state.setdefault("profile", {"equipment": [], "skills": [], "freq": 3, "session_minutes": 60})
    st.session_state.setdefault("plan", [])
    st.session_state.setdefault("player", {"session_idx": 0, "ex_idx": 0, "set_idx": 1, "phase": "idle", "phase_end": None, "phase_total": None})
    st.session_state.setdefault("stretch_done", False)

def go_step(n: int):
    st.session_state.step = n

def rest_for(cat: str, settings: Dict) -> int:
    if cat == "skill":
        return int(settings["rest_seconds_skill"])
    if cat == "power":
        return int(settings["rest_seconds_power"])
    if cat == "strength":
        return int(settings["rest_seconds_strength"])
    return int(settings["rest_seconds_accessory"])

def generate_plan(profile: Dict, settings: Dict) -> List[List[Exercise]]:
    eq = set(profile.get("equipment", []))
    skills = profile.get("skills", [])
    freq = int(profile.get("freq", 3))
    can_dips = "딥스 가능(평행봉/의자 포함)" in eq
    can_wall = "벽 사용 가능" in eq
    can_pull = "풀업바" in eq

    plan: List[List[Exercise]] = []
    for i in range(freq):
        day: List[Exercise] = []
        if skills:
            s = skills[i % len(skills)]
            if s in ["프론트 레버", "백 레버", "플란체", "V-sit"]:
                day.append(Exercise(
                    name=f"{s} 기본 단계 홀드",
                    kind="hold",
                    reps=0,
                    sets=6,
                    work_seconds=8,
                    rest_seconds=rest_for("power", settings),
                    cues="폼이 깨지기 전에 멈춥니다. 허리 꺾임/어깨 말림이 나오면 즉시 종료합니다."
                ))
            elif s == "머슬업":
                day.append(Exercise(
                    name="머슬업 시도(무보조 시도)",
                    kind="rep",
                    reps=4,
                    sets=4,
                    work_seconds=0,
                    rest_seconds=rest_for("skill", settings),
                    cues="실패 금지. 동작 품질이 무너지면 시도 수를 줄이고 휴식을 지킵니다."
                ))
                if can_pull:
                    day.append(Exercise(
                        name="상단 정지 풀업(턱 위 2초)",
                        kind="rep",
                        reps=3,
                        sets=8,
                        work_seconds=0,
                        rest_seconds=rest_for("strength", settings),
                        cues="턱이 바보다 위에 고정되도록 2초 정지. 반동 금지."
                    ))
                if can_dips:
                    day.append(Exercise(
                        name="딥스",
                        kind="rep",
                        reps=6,
                        sets=5,
                        work_seconds=0,
                        rest_seconds=rest_for("strength", settings),
                        cues="어깨가 앞으로 말리면 깊이를 줄입니다. 잠금까지 밀어 올립니다."
                    ))
                else:
                    day.append(Exercise(
                        name="푸쉬업",
                        kind="rep",
                        reps=15,
                        sets=5,
                        work_seconds=0,
                        rest_seconds=rest_for("strength", settings),
                        cues="몸통 일직선. 가슴이 먼저 내려가지 않게 코어 고정."
                    ))
            elif s == "핸드스탠드 푸쉬업":
                if can_wall:
                    day.append(Exercise(
                        name="벽 킥업 연습(핸드스탠드 진입)",
                        kind="rep",
                        reps=6,
                        sets=5,
                        work_seconds=0,
                        rest_seconds=rest_for("power", settings),
                        cues="한 번에 오래 버티려 하지 말고, 진입 품질을 우선합니다."
                    ))
                day.append(Exercise(
                    name="파이크 푸쉬업",
                    kind="rep",
                    reps=10,
                    sets=5,
                    work_seconds=0,
                    rest_seconds=rest_for("strength", settings),
                    cues="엉덩이를 높게. 팔꿈치가 너무 벌어지지 않게."
                ))
            elif s == "피스톨 스쿼트":
                day.append(Exercise(
                    name="피스톨 스쿼트(보조 가능)",
                    kind="rep",
                    reps=5,
                    sets=4,
                    work_seconds=0,
                    rest_seconds=rest_for("strength", settings),
                    cues="무릎이 안쪽으로 무너지지 않게. 가능하면 천천히 내려갑니다."
                ))

        if can_pull:
            day.append(Exercise(
                name="풀업",
                kind="rep",
                reps=5,
                sets=5,
                work_seconds=0,
                rest_seconds=rest_for("strength", settings),
                cues="견갑 먼저 고정 후 당깁니다. 반동 금지."
            ))

        day.append(Exercise(
            name="스캐풀라 푸쉬업",
            kind="rep",
            reps=12,
            sets=3,
            work_seconds=0,
            rest_seconds=rest_for("accessory", settings),
            cues="팔은 펴고 견갑만 움직입니다."
        ))
        day.append(Exercise(
            name="RKC 플랭크",
            kind="hold",
            reps=0,
            sets=4,
            work_seconds=20,
            rest_seconds=rest_for("accessory", settings),
            cues="엉덩이/갈비뼈를 말아 넣고 전신 긴장. 허리 꺾임 금지."
        ))

        plan.append(day)
    return plan

def format_line(ex: Exercise) -> str:
    if ex.kind == "rep":
        return f"{ex.name}  {ex.reps}회×{ex.sets}세트"
    return f"{ex.name}  {ex.sets}세트"

def seconds_left(end_epoch: float) -> int:
    return max(0, int(round(end_epoch - time.time())))

def mmss(sec: int) -> str:
    return f"{sec//60:02d}:{sec%60:02d}"

def autorefresh(interval_ms: int = 250):
    if hasattr(st, "autorefresh"):
        st.autorefresh(interval=interval_ms, key="__ar__")
    else:
        st.button("새로고침", key="manual_refresh")

def page_stretch():
    st.title("운동 전 스트레칭")
    st.markdown("""
- 손목: 돌리기 30초, 손바닥 짚고 앞뒤 체중이동 30초, 손등 체중 20초  
- 어깨·견갑: 스캐풀라 푸쉬업 10회, 팔 원 20회  
- 흉추·고관절: 캣카우 8회, 런지 스트레치 양쪽 20초  
""")
    if st.button("준비 완료", type="primary"):
        st.session_state.player["phase"] = "idle"
        st.session_state.stretch_done = True
        go_step(5)

def page_settings():
    st.title("설정")
    s = st.session_state.settings

    st.subheader("타이머/휴식")
    s["prep_seconds_hold"] = st.number_input("홀드 준비시간(초)", 0, 30, int(s["prep_seconds_hold"]))
    s["rest_seconds_skill"] = st.number_input("스킬 시도 휴식(초)", 30, 300, int(s["rest_seconds_skill"]))
    s["rest_seconds_power"] = st.number_input("파워/기술 휴식(초)", 30, 300, int(s["rest_seconds_power"]))
    s["rest_seconds_strength"] = st.number_input("힘운동 휴식(초)", 30, 300, int(s["rest_seconds_strength"]))
    s["rest_seconds_accessory"] = st.number_input("코어/보조 휴식(초)", 15, 180, int(s["rest_seconds_accessory"]))
    s["rest_seconds_block"] = st.number_input("블록 전환 휴식(초)", 30, 180, int(s["rest_seconds_block"]))
    s["auto_next"] = st.checkbox("휴식 종료 후 자동 진행", value=bool(s["auto_next"]))

    c1, c2 = st.columns(2)
    with c1:
        if st.button("저장", type="primary"):
            go_step(4 if st.session_state.plan else 1)
    with c2:
        if st.button("초기화"):
            st.session_state.settings = DEFAULTS.copy()
            st.experimental_rerun()

def page_player():
    plan = st.session_state.plan
    if not plan:
        st.warning("루틴이 없습니다.")
        if st.button("처음으로"):
            go_step(1)
        return

    if not st.session_state.stretch_done:
        page_stretch()
        return

    p = st.session_state.player
    settings = st.session_state.settings
    day = plan[p["session_idx"]]
    ex = day[p["ex_idx"]]

    st.subheader(f"회차 {p['session_idx']+1} | 운동 {p['ex_idx']+1}/{len(day)} | 세트 {p['set_idx']}/{ex.sets}")

    t1, t2 = st.columns(2)
    with t1:
        if st.button("회차/목록"):
            go_step(4)
    with t2:
        if st.button("설정"):
            go_step(99)

    phase = p["phase"]

    if phase == "idle":
        st.markdown(f"### {ex.name}")
        st.write(ex.cues)
        if ex.kind == "rep":
            st.write(f"오늘 목표: {ex.reps}회×{ex.sets}세트")
            if st.button("세트 완료 → 휴식", type="primary", use_container_width=True):
                p["phase"] = "rest"
                p["phase_total"] = int(ex.rest_seconds)
                p["phase_end"] = time.time() + int(ex.rest_seconds)
                st.experimental_rerun()
        else:
            st.write(f"오늘 목표: {ex.sets}세트 (시간은 타이머에서만 표시)")
            if st.button("홀드 시작", type="primary", use_container_width=True):
                p["phase"] = "prep"
                p["phase_total"] = int(settings["prep_seconds_hold"])
                p["phase_end"] = time.time() + int(settings["prep_seconds_hold"])
                st.experimental_rerun()

    else:
        autorefresh(250)
        left = seconds_left(float(p["phase_end"]))
        total = int(p["phase_total"])

        if phase == "prep":
            st.markdown("### 준비")
            st.metric("남은 시간", mmss(left))
            st.progress(0 if total == 0 else (total-left)/total)
            if left == 0:
                p["phase"] = "work"
                p["phase_total"] = int(ex.work_seconds)
                p["phase_end"] = time.time() + int(ex.work_seconds)
                st.experimental_rerun()

        elif phase == "work":
            st.markdown("### 홀드")
            st.metric("남은 시간", mmss(left))
            st.progress(0 if total == 0 else (total-left)/total)
            if left == 0:
                p["phase"] = "rest"
                p["phase_total"] = int(ex.rest_seconds)
                p["phase_end"] = time.time() + int(ex.rest_seconds)
                st.experimental_rerun()

        elif phase == "rest":
            st.markdown("### 휴식")
            st.metric("남은 시간", mmss(left))
            st.progress(0 if total == 0 else (total-left)/total)

            if left == 0:
                st.success("휴식 종료")
                last_set = (p["set_idx"] >= ex.sets)
                c1, c2 = st.columns(2)
                with c1:
                    if not last_set:
                        if st.button("다음 세트", type="primary", use_container_width=True):
                            p["set_idx"] += 1
                            p["phase"] = "idle"
                            st.experimental_rerun()
                    else:
                        st.button("다음 세트", disabled=True, use_container_width=True)

                with c2:
                    if last_set:
                        if st.button("다음 운동", type="primary", use_container_width=True):
                            if p["ex_idx"] + 1 < len(day):
                                p["ex_idx"] += 1
                                p["set_idx"] = 1
                                p["phase"] = "idle"
                                st.experimental_rerun()
                            else:
                                st.success("회차 완료")
                                st.session_state.stretch_done = False
                                if p["session_idx"] + 1 < len(plan):
                                    p["session_idx"] += 1
                                    p["ex_idx"] = 0
                                    p["set_idx"] = 1
                                    p["phase"] = "idle"
                                    st.experimental_rerun()
                    else:
                        if st.button("운동 건너뛰기", use_container_width=True):
                            if p["ex_idx"] + 1 < len(day):
                                p["ex_idx"] += 1
                                p["set_idx"] = 1
                                p["phase"] = "idle"
                                st.experimental_rerun()

def page_onboarding():
    st.title("칼리스데닉스 루틴 앱(프로토타입)")
    st.caption("루틴 목록에는 시간을 쓰지 않고, 타이머 화면에서만 시간을 표시합니다.")

    step = st.session_state.step
    profile = st.session_state.profile

    if step == 1:
        st.subheader("1) 장비 선택")
        profile["equipment"] = st.multiselect("장비를 선택하세요.", EQUIPMENT, default=profile["equipment"])
        if st.button("다음", type="primary"):
            go_step(2)

    elif step == 2:
        st.subheader("2) 목표 스킬 선택")
        profile["skills"] = st.multiselect("운동을 선택하세요.", SKILLS, default=profile["skills"])
        c1, c2 = st.columns(2)
        with c1:
            if st.button("이전"):
                go_step(1)
        with c2:
            if st.button("다음", type="primary"):
                go_step(3)

    elif step == 3:
        st.subheader("3) 주당 운동 횟수 / 1회 시간")
        profile["freq"] = st.slider("주당 운동 횟수", 2, 6, int(profile["freq"]))
        profile["session_minutes"] = st.slider("1회 운동 가능 시간(분)", 30, 120, int(profile["session_minutes"]), step=5)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("이전"):
                go_step(2)
        with c2:
            if st.button("루틴 생성", type="primary"):
                st.session_state.plan = generate_plan(profile, st.session_state.settings)
                st.session_state.player = {"session_idx": 0, "ex_idx": 0, "set_idx": 1, "phase": "idle", "phase_end": None, "phase_total": None}
                st.session_state.stretch_done = False
                go_step(4)

    elif step == 4:
        st.subheader("루틴 목록(시간 미표기)")
        plan = st.session_state.plan
        for i, day in enumerate(plan):
            with st.expander(f"회차 {i+1}"):
                for ex in day:
                    st.write("• " + format_line(ex))
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("설정"):
                go_step(99)
        with c2:
            if st.button("처음으로"):
                go_step(1)
        with c3:
            if st.button("운동 시작", type="primary"):
                go_step(5)

    elif step == 5:
        page_player()

    elif step == 99:
        page_settings()

def main():
    st.set_page_config(page_title="칼리스데닉스 루틴 앱(프로토타입)", layout="centered")
    init_state()
    page_onboarding()

if __name__ == "__main__":
    main()
