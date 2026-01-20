import time
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import streamlit as st

# -----------------------------
# 기본 설정
# -----------------------------
APP_TITLE = "칼리스데닉스 루틴 앱(프로토타입)"

EQUIPMENT: List[str] = [
    "풀업바",
    "딥스바(평행봉)",
    "링",
    "저항밴드",
    "벽(핸드스탠드용)",
    "덤벨",
    "바닥/매트",
]

SKILLS: List[str] = [
    "머슬업",
    "프론트 레버",
    "핸드스탠드 푸쉬업",
    "플란체",
    "V-sit",
    "피스톨 스쿼트",
    "백 레버",
]

SKILL_REQUIREMENTS: Dict[str, List[str]] = {
    "머슬업": ["풀업바", "딥스바(평행봉)", "링"],  # 딥스바 또는 링 중 하나면 OK
    "프론트 레버": ["풀업바", "링"],
    "백 레버": ["풀업바", "링"],
    "핸드스탠드 푸쉬업": ["벽(핸드스탠드용)", "바닥/매트"],
    "플란체": ["바닥/매트"],
    "V-sit": ["바닥/매트"],
    "피스톨 스쿼트": ["바닥/매트"],
}

# 운동 설명(길게)
DESC: Dict[str, str] = {
    "스트레칭(손목)": "손바닥을 바닥에 대고 손가락을 앞/뒤/옆으로 돌려가며 가볍게 체중을 싣습니다. 통증이 아니라 당김 수준에서 20~30초씩. 손목이 꺾인 상태에서 갑자기 밀지 않습니다.",
    "스트레칭(팔꿈치/전완)": "팔을 뻗고 손목을 젖힌 뒤 반대 손으로 손가락을 당겨 전완을 늘립니다. 팔꿈치에 찌릿한 통증이 오면 각도를 줄이고, 반동 없이 20~30초 유지합니다.",
    "스트레칭(어깨)": "어깨 원 그리기(큰 원) → 가슴 열기(팔 뒤로 깍지) → 견갑(날개뼈) 상하/전후 움직임. 어깨를 으쓱한 채로 버티지 말고 목 길게.",
    "풀업": "매달린 상태에서 견갑을 먼저 안정(가슴을 살짝 들어올리는 느낌)시키고, 몸을 바에 끌어올립니다. 턱을 억지로 빼서 올라가려 하지 말고, 가슴이 위로 간다는 느낌을 유지합니다. 내려올 때는 1~2초 정도로 통제.",
    "네거티브 풀업": "턱이 바 위에 있는 상단에서 시작해 3~5초에 걸쳐 천천히 내려옵니다. 어깨가 귀로 말려 올라가면 범위를 줄이거나 밴드 보조를 사용합니다.",
    "딥스": "팔꿈치를 뒤로 접으며 몸통을 약간 앞으로 기울이고 내려갑니다. 어깨가 앞으로 말리지 않게 가슴을 열고, 내려가며 반동을 쓰지 않습니다. 올라올 때 팔꿈치를 완전히 잠그기 전까지 힘을 유지.",
    "서포트 홀드": "딥스바/링에서 팔을 펴고 몸을 고정합니다. 어깨를 귀에서 멀리(견갑 하강)하고, 갈비뼈가 들리지 않게 코어를 단단히. 흔들리면 범위를 줄이고 5~10초부터.",
    "밴드 보조 머슬업 전환": "풀업바에서 밴드를 발/무릎에 걸어 상단에서 가슴을 바 위로 보내는 전환을 연습합니다. 핵심은 '당기기'와 '밀기'를 끊지 않고, 손목을 바 위로 빠르게 겹치는 것. 낮은 바가 없어도 상단 구간을 밴드로 반복하면 전환 감각을 만들 수 있습니다.",
    "머슬업 시도": "지금 능력에서 가능한 범위로 '깨끗하게' 시도합니다. 반동을 크게 쓰기보다, 당기는 구간에서 가슴을 바 쪽으로 끌어오고 전환에서 손목이 바 위로 넘어가게 집중합니다. 실패해도 1회는 기록으로 남겨 진행도를 관리합니다.",
    "프론트 레버(프록시)": "초기에는 턱걸이 자세에서 무릎을 접은(턱-투-바가 아니라) '턱걸이 그립 유지 + 몸통 긴장'이 핵심입니다. 골반이 처지지 않게 후방경사(배에 힘, 엉덩이 말기)로 몸을 일자로 만들고, 견갑은 눌러 고정합니다.",
    "백 레버(프록시)": "어깨가 말리기 쉬워서 견갑을 아래/뒤로 안정시키는 게 핵심입니다. 초기에는 무릎을 접은 상태로, 어깨 통증이 있으면 범위를 줄입니다.",
    "벽 핸드스탠드 홀드": "벽을 등지고 서서 손을 바닥에 두고 발을 벽에 올립니다. 손가락으로 바닥을 '긁는 느낌'으로 균형을 잡고, 팔꿈치는 잠그되 어깨를 으쓱하지 않습니다.",
    "파이크 푸쉬업": "엉덩이를 높이고 상체를 아래로 내려 어깨로 밀어올립니다. 팔꿈치는 너무 벌리지 말고 약간 대각선. 고개를 바닥에 박지 말고 팔 사이로 내려갑니다.",
    "플란체(프록시)": "초기에는 플란체 린(몸을 앞으로 기울인 버티기)로 시작합니다. 팔은 펴고, 어깨를 앞으로 내밀어 견갑 전인을 만들며, 골반 후방경사로 몸통을 단단히.",
    "V-sit(프록시)": "초기에는 L-sit 또는 턱-업(무릎 굽힌) 자세로 시작합니다. 팔을 펴고 어깨를 아래로 눌러, 다리를 들 때 허리가 과하게 꺾이지 않게 복부로 버팁니다.",
    "피스톨 스쿼트(프록시)": "처음에는 박스/의자에 앉았다 일어나기(한발)로 시작합니다. 무릎이 안쪽으로 무너지지 않게, 발바닥 삼점 지지(엄지/새끼/뒤꿈치)를 유지합니다. 내려갈 때 2~3초로 통제하고, 발뒤꿈치가 들리면 가동범위를 줄이거나 보조를 사용합니다.",
    "RKC 플랭크": "일반 플랭크보다 '전신 긴장'을 강하게 합니다. 팔꿈치로 바닥을 당기고, 발끝으로 바닥을 밀어 복부를 최대한 조입니다. 허리가 꺾이면 시간보다 자세를 우선.",
}

# -----------------------------
# 데이터 모델
# -----------------------------
@dataclass
class Exercise:
    name: str
    kind: str  # reps / hold / stretch
    reps: int = 0
    sets: int = 0
    hold_seconds: int = 0
    rest_seconds: int = 60
    notes: str = ""


def init_state() -> None:
    if "page" not in st.session_state:
        st.session_state.page = "onboarding"
    if "step" not in st.session_state:
        st.session_state.step = 1

    if "equip_selected" not in st.session_state:
        st.session_state.equip_selected = {k: False for k in EQUIPMENT}
    if "skill_selected" not in st.session_state:
        st.session_state.skill_selected = {k: False for k in SKILLS}

    if "profile" not in st.session_state:
        st.session_state.profile = {
            "height_cm": 0,
            "weight_kg": 0,
            "equipment": [],
            "skills": [],
            "freq_per_week": 3,
        }

    if "settings" not in st.session_state:
        st.session_state.settings = {
            "current_week": 1,
            "last_test_week": 0,
            "prep_seconds_hold": 5,
            "rest_default": 60,
        }

    if "tests" not in st.session_state:
        st.session_state.tests = {
            "baseline": {},
            "latest": {},
            "history": [],  # list of (week, dict)
        }

    if "plan" not in st.session_state:
        st.session_state.plan = []  # list of sessions; each session is list[Exercise]

    if "player" not in st.session_state:
        st.session_state.player = {
            "active": False,
            "session_idx": 0,
            "ex_idx": 0,
            "set_idx": 1,
            "phase": "idle",  # idle/prep/work/rest
            "phase_end": 0.0,
            "phase_total": 0,
        }

    if "return_page" not in st.session_state:
        st.session_state.return_page = "onboarding"


# -----------------------------
# 유틸
# -----------------------------
def mmss(seconds: int) -> str:
    seconds = max(0, int(seconds))
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"


def seconds_left(end_ts: float) -> int:
    return max(0, int(round(end_ts - time.time())))


def safe_rerun() -> None:
    try:
        st.rerun()
    except Exception:
        try:
            st.experimental_rerun()
        except Exception:
            return


def autorefresh(interval_ms: int = 250) -> None:
    """타이머 화면 자동 갱신."""
    try:
        from streamlit_autorefresh import st_autorefresh

        st_autorefresh(interval=interval_ms, key="__ar__")
    except Exception:
        # 패키지가 없으면 타이머가 자동으로 안 흐릅니다.
        st.info("타이머 자동 갱신을 위해 requirements.txt에 streamlit-autorefresh가 필요합니다.")
        st.button("새로고침")


# -----------------------------
# 타일(체크박스) UI
# -----------------------------
def tile_css() -> None:
    st.markdown(
        """
<style>
.tile {
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 14px;
  padding: 12px 12px 10px 12px;
  background: rgba(255,255,255,0.04);
}
.tile_on {
  border: 2px solid rgba(80,180,255,0.9);
  background: rgba(80,180,255,0.10);
}
.small_note { font-size: 0.85rem; opacity: 0.9; }
</style>
        """,
        unsafe_allow_html=True,
    )


def checkbox_tile_grid(
    items: List[str],
    state_map: Dict[str, bool],
    key_prefix: str,
    cols: int = 2,
    disabled_map: Optional[Dict[str, bool]] = None,
    note_map: Optional[Dict[str, str]] = None,
) -> None:
    tile_css()
    disabled_map = disabled_map or {}
    note_map = note_map or {}

    rows = (len(items) + cols - 1) // cols
    idx = 0
    for _ in range(rows):
        cs = st.columns(cols)
        for c in cs:
            if idx >= len(items):
                break
            name = items[idx]
            idx += 1
            checked = bool(state_map.get(name, False))
            disabled = bool(disabled_map.get(name, False))
            note = note_map.get(name, "")

            klass = "tile tile_on" if checked else "tile"
            with c:
                st.markdown(f"<div class='{klass}'>", unsafe_allow_html=True)
                new_val = st.checkbox(
                    name,
                    value=checked,
                    key=f"{key_prefix}_{name}",
                    disabled=disabled,
                )
                if note:
                    st.markdown(f"<div class='small_note'>{note}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            state_map[name] = bool(new_val)


# -----------------------------
# 조건(장비/스킬)
# -----------------------------
def skill_allowed(skill: str, eq_set: set) -> Tuple[bool, str]:
    req = SKILL_REQUIREMENTS.get(skill, [])

    if skill == "머슬업":
        # 풀업바는 필수, 딥스바 또는 링 중 하나
        if "풀업바" not in eq_set:
            return False, "풀업바 필요"
        if ("딥스바(평행봉)" not in eq_set) and ("링" not in eq_set):
            return False, "딥스바 또는 링 필요"
        return True, "권장: 풀업바 + 딥스(바/링)"

    if skill in ("프론트 레버", "백 레버"):
        if ("풀업바" in eq_set) or ("링" in eq_set):
            return True, "권장: 풀업바 또는 링"
        return False, "풀업바/링 필요"

    if skill == "핸드스탠드 푸쉬업":
        if "바닥/매트" not in eq_set:
            return False, "바닥/매트 필요"
        if "벽(핸드스탠드용)" not in eq_set:
            return True, "권장: 벽(초기)"
        return True, "권장: 벽(초기)"

    # 나머지는 매트만 있으면 OK로
    if "바닥/매트" not in eq_set:
        return False, "바닥/매트 권장"
    return True, ""


# -----------------------------
# 테스트/루틴 생성
# -----------------------------
def baseline_items(selected_skills: List[str]) -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []
    # 공통
    items += [("pullup_max", "풀업 최대 반복(정자세)"), ("pushup_max", "푸쉬업 최대 반복"), ("plank_sec", "RKC 플랭크 최대 유지(초)")]

    if "머슬업" in selected_skills:
        items.append(("dip_max", "딥스 최대 반복"))

    if "핸드스탠드 푸쉬업" in selected_skills:
        items.append(("wall_hs_sec", "벽 핸드스탠드 홀드(초)"))

    if ("프론트 레버" in selected_skills) or ("백 레버" in selected_skills):
        items.append(("hang_sec", "매달리기(데드행) 최대(초)"))

    if "피스톨 스쿼트" in selected_skills:
        items.append(("pistol_box_reps", "한발 박스 스쿼트(한쪽) 최대 반복"))

    return items


def save_test_results(results: Dict[str, float], is_baseline: bool) -> None:
    week = int(st.session_state.settings.get("current_week", 1))
    if is_baseline:
        st.session_state.tests["baseline"] = dict(results)
        st.session_state.tests["latest"] = dict(results)
        st.session_state.settings["last_test_week"] = week
    else:
        st.session_state.tests["latest"] = dict(results)
        st.session_state.settings["last_test_week"] = week

    st.session_state.tests["history"].append((week, dict(results)))


def clamp_int(x: float, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(round(x))))


def derive_reps(max_reps: float, intensity: float, week: int) -> int:
    # intensity: 0.55~0.75 정도
    base = max_reps * intensity
    # 주차가 늘수록 아주 조금 증가(주당 +0.5회 정도)
    prog = base + 0.5 * max(0, week - 1)
    return clamp_int(prog, 1, max(1, int(max_reps)))


def derive_hold(sec: float, intensity: float, week: int) -> int:
    base = sec * intensity
    prog = base + 1.0 * max(0, week - 1)  # 주당 +1초
    return clamp_int(prog, 5, max(5, int(sec)))


def make_session(selected_skills: List[str], week: int, tests: Dict[str, float], settings: Dict) -> List[Exercise]:
    rest_default = int(settings.get("rest_default", 60))

    # 스트레칭(고정)
    session: List[Exercise] = [
        Exercise("스트레칭(손목)", "stretch", hold_seconds=30, rest_seconds=10, notes=DESC.get("스트레칭(손목)", "")),
        Exercise("스트레칭(팔꿈치/전완)", "stretch", hold_seconds=30, rest_seconds=10, notes=DESC.get("스트레칭(팔꿈치/전완)", "")),
        Exercise("스트레칭(어깨)", "stretch", hold_seconds=30, rest_seconds=10, notes=DESC.get("스트레칭(어깨)", "")),
    ]

    pull_max = float(tests.get("pullup_max", 0) or 0)
    push_max = float(tests.get("pushup_max", 0) or 0)
    dip_max = float(tests.get("dip_max", 0) or 0)
    plank_sec = float(tests.get("plank_sec", 30) or 30)
    wall_hs_sec = float(tests.get("wall_hs_sec", 10) or 10)
    hang_sec = float(tests.get("hang_sec", 20) or 20)
    pistol_box = float(tests.get("pistol_box_reps", 5) or 5)

    # 핵심: 스킬별 프록시 + 기본 근력(풀/푸시/코어/하체)
    # Pull
    if pull_max > 0:
        session.append(Exercise("풀업", "reps", reps=derive_reps(pull_max, 0.65, week), sets=5, rest_seconds=rest_default, notes=DESC.get("풀업", "")))
    else:
        session.append(Exercise("네거티브 풀업", "reps", reps=3, sets=5, rest_seconds=rest_default, notes=DESC.get("네거티브 풀업", "")))

    # Skill-specific
    if "머슬업" in selected_skills:
        # 전환 감각 + 시도
        session.append(Exercise("밴드 보조 머슬업 전환", "reps", reps=3, sets=4, rest_seconds=rest_default, notes=DESC.get("밴드 보조 머슬업 전환", "")))
        session.append(Exercise("머슬업 시도", "reps", reps=1, sets=4, rest_seconds=rest_default, notes=DESC.get("머슬업 시도", "")))

    if "프론트 레버" in selected_skills:
        session.append(Exercise("프론트 레버(프록시)", "hold", hold_seconds=derive_hold(hang_sec, 0.5, week), sets=4, rest_seconds=rest_default, notes=DESC.get("프론트 레버(프록시)", "")))

    if "백 레버" in selected_skills:
        session.append(Exercise("백 레버(프록시)", "hold", hold_seconds=derive_hold(hang_sec, 0.45, week), sets=4, rest_seconds=rest_default, notes=DESC.get("백 레버(프록시)", "")))

    # Push
    if "핸드스탠드 푸쉬업" in selected_skills:
        session.append(Exercise("벽 핸드스탠드 홀드", "hold", hold_seconds=derive_hold(wall_hs_sec, 0.7, week), sets=4, rest_seconds=rest_default, notes=DESC.get("벽 핸드스탠드 홀드", "")))
        session.append(Exercise("파이크 푸쉬업", "reps", reps=derive_reps(push_max if push_max > 0 else 10, 0.55, week), sets=5, rest_seconds=rest_default, notes=DESC.get("파이크 푸쉬업", "")))
    else:
        session.append(Exercise("푸쉬업", "reps", reps=derive_reps(push_max if push_max > 0 else 15, 0.65, week), sets=5, rest_seconds=rest_default, notes="정자세로 1~2초 통제. 어깨 통증 있으면 범위 줄이기."))

    if "플란체" in selected_skills:
        session.append(Exercise("플란체(프록시)", "hold", hold_seconds=derive_hold(plank_sec, 0.35, week), sets=4, rest_seconds=rest_default, notes=DESC.get("플란체(프록시)", "")))

    if "V-sit" in selected_skills:
        session.append(Exercise("V-sit(프록시)", "hold", hold_seconds=derive_hold(plank_sec, 0.25, week), sets=4, rest_seconds=rest_default, notes=DESC.get("V-sit(프록시)", "")))

    if "피스톨 스쿼트" in selected_skills:
        session.append(Exercise("피스톨 스쿼트(프록시)", "reps", reps=derive_reps(pistol_box, 0.6, week), sets=4, rest_seconds=rest_default, notes=DESC.get("피스톨 스쿼트(프록시)", "")))

    # Core finisher
    session.append(Exercise("RKC 플랭크", "hold", hold_seconds=derive_hold(plank_sec, 0.6, week), sets=3, rest_seconds=rest_default, notes=DESC.get("RKC 플랭크", "")))

    return session


def regenerate_plan() -> None:
    prof = st.session_state.profile
    week = int(st.session_state.settings.get("current_week", 1))
    tests = st.session_state.tests.get("latest", {})
    skills = prof.get("skills", [])
    freq = int(prof.get("freq_per_week", 3))

    # 주당 횟수만큼 동일 구조로(주 3이면 A/B/C 동일, 대신 사용자가 선택해서 3회 수행)
    plan: List[List[Exercise]] = []
    for _ in range(max(1, freq)):
        plan.append(make_session(skills, week, tests, st.session_state.settings))

    st.session_state.plan = plan


def need_4week_test(settings: Dict) -> bool:
    week = int(settings.get("current_week", 1))
    last = int(settings.get("last_test_week", 0))
    return (week - last) >= 4


# -----------------------------
# 페이지: 테스트
# -----------------------------
def page_test() -> None:
    st.title("테스트(초기/4주)")

    prof = st.session_state.profile
    skills = prof.get("skills", [])

    st.subheader("프로필")
    prof["height_cm"] = st.number_input("키(cm)", 0, 250, int(prof.get("height_cm", 0)))
    prof["weight_kg"] = st.number_input("몸무게(kg)", 0, 250, int(prof.get("weight_kg", 0)))

    st.subheader("측정 입력")
    results: Dict[str, float] = {}
    items = baseline_items(skills)

    for key, label in items:
        if key.endswith("_sec"):
            results[key] = float(st.number_input(label, 0, 600, int(st.session_state.tests["latest"].get(key, 0)), key=f"t_{key}"))
        else:
            results[key] = float(st.number_input(label, 0, 200, int(st.session_state.tests["latest"].get(key, 0)), key=f"t_{key}"))

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("저장(초기 측정)", type="primary", use_container_width=True):
            save_test_results(results, is_baseline=True)
            regenerate_plan()
            st.success("초기 측정 저장 완료")
            safe_rerun()
    with c2:
        if st.button("저장(4주 테스트)", type="primary", use_container_width=True):
            save_test_results(results, is_baseline=False)
            regenerate_plan()
            st.success("4주 테스트 저장 완료")
            safe_rerun()
    with c3:
        if st.button("뒤로", use_container_width=True):
            go_page(st.session_state.get("return_page", "onboarding"))

    if st.session_state.tests["history"]:
        st.subheader("테스트 기록(최근)")
        for wk, res in st.session_state.tests["history"][-5:]:
            st.write(f"- {wk}주차: " + ", ".join([f"{k}={int(v)}" for k, v in res.items()]))


# -----------------------------
# 페이지: 설정
# -----------------------------
def page_settings() -> None:
    st.title("설정")
    settings = st.session_state.settings
    prof = st.session_state.profile

    st.subheader("주차")
    settings["current_week"] = st.number_input("현재 주차", 1, 999, int(settings.get("current_week", 1)))
    settings["last_test_week"] = st.number_input("마지막 테스트 주차", 0, 999, int(settings.get("last_test_week", 0)))

    st.subheader("타이머")
    settings["prep_seconds_hold"] = st.number_input("홀드 준비시간(초)", 0, 20, int(settings.get("prep_seconds_hold", 5)))
    settings["rest_default"] = st.number_input("기본 휴식(초)", 15, 300, int(settings.get("rest_default", 60)))

    st.subheader("프로필")
    prof["height_cm"] = st.number_input("키(cm)", 0, 250, int(prof.get("height_cm", 0)), key="s_h")
    prof["weight_kg"] = st.number_input("몸무게(kg)", 0, 250, int(prof.get("weight_kg", 0)), key="s_w")

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("저장", type="primary", use_container_width=True):
            # 저장만 하고 돌아가기
            regenerate_plan()
            go_page(st.session_state.get("return_page", "onboarding"))
    with c2:
        if st.button("테스트", use_container_width=True):
            st.session_state.return_page = st.session_state.get("return_page", "onboarding")
            go_page("test")
    with c3:
        if st.button("초기화(진짜)", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            safe_rerun()


# -----------------------------
# 페이지: 온보딩
# -----------------------------
def go_page(name: str) -> None:
    st.session_state.page = name
    safe_rerun()


def page_onboarding() -> None:
    st.title(APP_TITLE)
    prof = st.session_state.profile
    settings = st.session_state.settings

    # 4주 테스트 알림
    if st.session_state.plan and need_4week_test(settings):
        st.warning(f"{settings['current_week']}주차입니다. 마지막 테스트는 {settings['last_test_week']}주차입니다. 4주 테스트를 진행하세요.")
        if st.button("지금 테스트하기"):
            st.session_state.return_page = "onboarding"
            go_page("test")

    step = int(st.session_state.step)

    if step == 1:
        st.subheader("1) 장비 선택")
        checkbox_tile_grid(EQUIPMENT, st.session_state.equip_selected, "equip")
        prof["equipment"] = [e for e in EQUIPMENT if st.session_state.equip_selected.get(e, False)]

        if st.button("다음", type="primary", use_container_width=True):
            st.session_state.step = 2
            safe_rerun()

    elif step == 2:
        st.subheader("2) 원하는 동작 선택(멀티)")
        eq_set = set(prof.get("equipment", []))

        disabled_map: Dict[str, bool] = {}
        note_map: Dict[str, str] = {}
        for s in SKILLS:
            ok, note = skill_allowed(s, eq_set)
            disabled_map[s] = not ok
            note_map[s] = ("선택 불가: " + note) if (not ok and note) else note
            if not ok:
                st.session_state.skill_selected[s] = False

        checkbox_tile_grid(SKILLS, st.session_state.skill_selected, "skill", disabled_map=disabled_map, note_map=note_map)
        prof["skills"] = [s for s in SKILLS if st.session_state.skill_selected.get(s, False)]

        c1, c2 = st.columns(2)
        with c1:
            if st.button("이전", use_container_width=True):
                st.session_state.step = 1
                safe_rerun()
        with c2:
            if st.button("다음", type="primary", use_container_width=True):
                st.session_state.step = 3
                safe_rerun()

    elif step == 3:
        st.subheader("3) 주당 운동 횟수")
        prof["freq_per_week"] = st.radio("주당", [2, 3, 4], index=1)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("이전", use_container_width=True):
                st.session_state.step = 2
                safe_rerun()
        with c2:
            if st.button("다음", type="primary", use_container_width=True):
                st.session_state.step = 4
                safe_rerun()

    elif step == 4:
        st.subheader("4) 초기 능력 측정")
        st.caption("초기 측정 결과로 루틴이 자동으로 맞춰집니다.")

        items = baseline_items(prof.get("skills", []))
        results: Dict[str, float] = {}
        for key, label in items:
            if key.endswith("_sec"):
                results[key] = float(st.number_input(label, 0, 600, int(st.session_state.tests["baseline"].get(key, 0)), key=f"b_{key}"))
            else:
                results[key] = float(st.number_input(label, 0, 200, int(st.session_state.tests["baseline"].get(key, 0)), key=f"b_{key}"))

        c1, c2 = st.columns(2)
        with c1:
            if st.button("이전", use_container_width=True):
                st.session_state.step = 3
                safe_rerun()
        with c2:
            if st.button("저장하고 루틴 생성", type="primary", use_container_width=True):
                save_test_results(results, is_baseline=True)
                regenerate_plan()
                st.session_state.step = 5
                safe_rerun()

    elif step == 5:
        st.subheader("5) 루틴(이번 주)")
        if not st.session_state.plan:
            st.info("아직 루틴이 없습니다. 초기 측정을 먼저 저장하세요.")
        else:
            for i, sess in enumerate(st.session_state.plan, start=1):
                with st.expander(f"세션 {i} (오늘 할 날 {i})", expanded=(i == 1)):
                    for ex in sess:
                        if ex.kind == "reps":
                            st.write(f"- {ex.name}: {ex.reps}회 × {ex.sets}세트")
                        else:
                            st.write(f"- {ex.name}: {ex.hold_seconds}초 × {ex.sets}세트")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"세션 {i} 시작", type="primary", use_container_width=True, key=f"start_{i}"):
                            start_workout(i - 1)
                    with col2:
                        if st.button("설정", use_container_width=True, key=f"set_{i}"):
                            st.session_state.return_page = "onboarding"
                            go_page("settings")

            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                if st.button("테스트", use_container_width=True):
                    st.session_state.return_page = "onboarding"
                    go_page("test")
            with c2:
                if st.button("주차 +1", type="primary", use_container_width=True):
                    st.session_state.settings["current_week"] = int(st.session_state.settings.get("current_week", 1)) + 1
                    regenerate_plan()
                    safe_rerun()


# -----------------------------
# 운동 플레이어
# -----------------------------
def start_workout(session_idx: int) -> None:
    st.session_state.page = "player"
    st.session_state.return_page = "player"  # 설정/테스트에서 돌아올 곳

    p = st.session_state.player
    p["active"] = True
    p["session_idx"] = int(session_idx)
    p["ex_idx"] = 0
    p["set_idx"] = 1
    p["phase"] = "idle"
    p["phase_end"] = 0.0
    p["phase_total"] = 0

    safe_rerun()


def page_player() -> None:
    p = st.session_state.player
    plan = st.session_state.plan

    if not p.get("active") or not plan:
        st.info("진행 중인 운동이 없습니다.")
        if st.button("루틴으로 돌아가기"):
            st.session_state.page = "onboarding"
            safe_rerun()
        return

    sess = plan[int(p["session_idx"]) % len(plan)]
    ex = sess[int(p["ex_idx"]) % len(sess)]

    # 상단
    st.title("운동")
    top1, top2, top3 = st.columns([1, 1, 1])
    with top1:
        st.write(f"세션: {p['session_idx']+1}")
        st.write(f"운동: {p['ex_idx']+1}/{len(sess)}")
    with top2:
        st.write(f"세트: {p['set_idx']}/{max(1, ex.sets)}")
    with top3:
        if st.button("설정"):
            st.session_state.return_page = "player"
            go_page("settings")
        if st.button("테스트"):
            st.session_state.return_page = "player"
            go_page("test")

    st.subheader(ex.name)

    # 설명(이름 밑 빈칸 채우기)
    if ex.notes:
        st.write(ex.notes)
    else:
        st.write(DESC.get(ex.name, ""))

    # 타이머/진행
    if p["phase"] in ("prep", "work", "rest"):
        autorefresh(250)

    # phase 진행 로직
    if p["phase"] == "prep":
        total = int(p["phase_total"])
        left = seconds_left(float(p["phase_end"]))
        st.markdown("### 준비")
        st.metric("남은 시간", mmss(left))
        st.progress(0 if total == 0 else (total - left) / total)

        if left == 0:
            # 준비 끝 -> work
            p["phase"] = "work"
            if ex.kind == "hold" or ex.kind == "stretch":
                p["phase_total"] = int(ex.hold_seconds)
                p["phase_end"] = time.time() + int(ex.hold_seconds)
            else:
                # reps는 work 타이머 없음(버튼으로 완료)
                p["phase_total"] = 0
                p["phase_end"] = 0
            safe_rerun()

    elif p["phase"] == "work":
        if ex.kind == "reps":
            st.markdown("### 수행")
            st.write(f"목표: {ex.reps}회")
            if st.button("세트 완료", type="primary", use_container_width=True):
                p["phase"] = "rest"
                p["phase_total"] = int(ex.rest_seconds)
                p["phase_end"] = time.time() + int(ex.rest_seconds)
                safe_rerun()

        else:
            total = int(p["phase_total"])
            left = seconds_left(float(p["phase_end"]))
            st.markdown("### 타이머")
            st.metric("남은 시간", mmss(left))
            st.progress(0 if total == 0 else (total - left) / total)

            if left == 0:
                p["phase"] = "rest"
                p["phase_total"] = int(ex.rest_seconds)
                p["phase_end"] = time.time() + int(ex.rest_seconds)
                safe_rerun()

    elif p["phase"] == "rest":
        total = int(p["phase_total"])
        left = seconds_left(float(p["phase_end"]))

        st.markdown("### 휴식")
        st.metric("남은 시간", mmss(left))
        st.progress(0 if total == 0 else (total - left) / total)

        # 휴식 건너뛰기
        if st.button("휴식 건너뛰기", use_container_width=True):
            p["phase_end"] = time.time()
            safe_rerun()

        if left == 0:
            st.markdown("### 다음")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("다음 세트", type="primary", use_container_width=True):
                    if p["set_idx"] < max(1, ex.sets):
                        p["set_idx"] += 1
                        p["phase"] = "idle"
                        safe_rerun()
                    else:
                        st.info("이미 마지막 세트입니다. 다음 운동을 선택하세요.")
            with c2:
                if st.button("다음 운동", type="primary", use_container_width=True):
                    if p["ex_idx"] + 1 < len(sess):
                        p["ex_idx"] += 1
                        p["set_idx"] = 1
                        p["phase"] = "idle"
                        safe_rerun()
                    else:
                        st.success("세션 완료")
                        p["active"] = False
                        st.session_state.page = "onboarding"
                        safe_rerun()

    else:
        # idle
        if ex.kind == "reps":
            st.write(f"목표: {ex.reps}회 × {ex.sets}세트")
            if st.button("세트 시작", type="primary", use_container_width=True):
                # reps는 준비시간 없이 바로 수행
                p["phase"] = "work"
                p["phase_total"] = 0
                p["phase_end"] = 0
                safe_rerun()
        else:
            st.write(f"목표: {ex.hold_seconds}초 × {ex.sets}세트")
            if st.button("홀드 시작", type="primary", use_container_width=True):
                p["phase"] = "prep"
                p["phase_total"] = int(st.session_state.settings.get("prep_seconds_hold", 5))
                p["phase_end"] = time.time() + int(st.session_state.settings.get("prep_seconds_hold", 5))
                safe_rerun()


# -----------------------------
# 라우팅
# -----------------------------
def main() -> None:
    init_state()

    page = st.session_state.page

    if page == "onboarding":
        page_onboarding()
    elif page == "player":
        page_player()
    elif page == "settings":
        page_settings()
    elif page == "test":
        page_test()
    else:
        st.session_state.page = "onboarding"
        safe_rerun()


if __name__ == "__main__":
    main()
