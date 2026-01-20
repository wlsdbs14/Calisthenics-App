import time
import datetime as _dt
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import streamlit as st

# -----------------------------
# 기본 설정
# -----------------------------
DEFAULTS = {
    "prep_seconds_hold": 5,
    "rest_seconds_skill": 120,
    "rest_seconds_power": 90,
    "rest_seconds_strength": 75,
    "rest_seconds_accessory": 45,
    "current_week": 1,          # 사용자가 수동으로 관리(프로토타입)
    "last_test_week": 0,        # 마지막 테스트 완료 주차
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
]

# 스킬별 “필수” 장비(없으면 선택 잠금)
SKILL_REQ_ANY_OF: Dict[str, List[str]] = {
    "머슬업": ["풀업바", "링/낮은바"],
    "프론트 레버": ["풀업바", "링/낮은바"],
    "백 레버": ["풀업바", "링/낮은바"],
}

SKILL_NOTE: Dict[str, str] = {
    "머슬업": "풀업바/링 필요",
    "프론트 레버": "풀업바/링 필요",
    "백 레버": "풀업바/링 필요",
    "핸드스탠드 푸쉬업": "벽 있으면 쉬움",
}

# -----------------------------
# 운동 설명(긴 버전)
# -----------------------------
EX_DESC: Dict[str, str] = {
    "머슬업 시도(무보조 시도)": (
        "목표: ‘실패를 반복’이 아니라 ‘좋은 시도’를 반복합니다.\n"
        "- 매 시도: 견갑 하강(어깨 내리기) + 몸통 긴장 → 당기기 → 가슴이 바에 가까워지는지 확인\n"
        "- 실패가 나오면: 즉시 시도 수를 줄이고, 다음 세트에서 품질을 회복합니다.\n"
        "- 흔한 실수: 반동으로 턱만 넘기기, 어깨가 올라가며 팔꿈치가 뒤로 빠지는 패턴"
    ),
    "상단 정지 풀업(턱 위 2초)": (
        "목표: 전환 구간을 위한 ‘상단 지배력’.\n"
        "- 턱이 바보다 위에서 2초 정지(흔들림 최소화)\n"
        "- 내릴 때도 통제(턱→가슴→어깨 순서로 내려간다고 생각)\n"
        "- 흔한 실수: 고개만 빼서 턱 위치만 맞추기, 견갑이 들린 상태로 정지"
    ),
    "풀업": (
        "목표: 견갑 고정 + 코어 고정 + 반동 없는 반복.\n"
        "- 시작: 매달린 상태에서 견갑을 ‘아래로’ 먼저 고정\n"
        "- 당김: 가슴이 바 쪽으로 간다고 생각(팔꿈치를 뒤로 ‘내린다’ 느낌)\n"
        "- 흔한 실수: 킵/반동, 허리 꺾임, 어깨가 귀 쪽으로 올라감"
    ),
    "딥스": (
        "목표: 어깨가 말리지 않게 깊이 조절하면서 잠금까지.\n"
        "- 내려갈 때: 팔꿈치가 너무 벌어지지 않게\n"
        "- 올라올 때: 몸통을 세우기보다 ‘어깨를 눌러 잠금’\n"
        "- 흔한 실수: 어깨 전방 통증 무시하고 깊이 과하게 내려가기"
    ),
    "푸쉬업": (
        "목표: 몸통 일직선 유지 + 가슴·삼두에 정확히 걸리게.\n"
        "- 코어: 갈비뼈를 말아 넣고(배 힘) 엉덩이 처짐 방지\n"
        "- 팔: 팔꿈치 45도 정도\n"
        "- 흔한 실수: 엉덩이 들림/처짐, 목 앞으로 빼기"
    ),
    "파이크 푸쉬업": (
        "HSPU 준비용.\n"
        "- 엉덩이를 최대한 높게, 시선은 손 사이 바닥\n"
        "- 팔꿈치 과도하게 벌리지 않기\n"
        "- 흔한 실수: ‘푸쉬업’처럼 앞으로 밀기(어깨 위로 수직 압박이 줄어듦)"
    ),
    "벽 킥업 연습(핸드스탠드 진입)": (
        "벽을 이용해 진입 정확도를 올립니다.\n"
        "- 한 번에 오래 버티기보다, ‘정확히 올라가기’를 반복\n"
        "- 복부·둔근 긴장으로 허리 꺾임 방지\n"
        "- 흔한 실수: 허리 과신전(바나나 자세), 손목 체중분배 불안정"
    ),
    "프론트 레버 기본 단계 홀드": (
        "레버는 ‘단계’가 핵심입니다.\n"
        "- 단계 선택 기준: 1~2초 버티는 단계가 아니라, ‘8초를 자세 유지’ 가능한 단계\n"
        "- 견갑: 아래로 누르고(하강) 등 넓게(후인/하강 느낌)\n"
        "- 흔한 실수: 허리 꺾임, 어깨가 말리며 팔꿈치가 굽어지는 패턴"
    ),
    "백 레버 기본 단계 홀드": (
        "어깨·팔꿈치 부담이 커서, 통증 관리가 최우선.\n"
        "- 단계 선택: 8초 자세 유지 가능한 단계\n"
        "- 통증 신호가 오면 즉시 중단하고 단계/볼륨을 낮춥니다.\n"
        "- 흔한 실수: 어깨 전면 통증을 참고 버티기(장기적으로 악화)"
    ),
    "플란체 기본 단계 홀드": (
        "플란체는 손목/어깨 준비가 필수.\n"
        "- 단계: tuck/advanced tuck/straddle 등 ‘8초 자세 유지’ 가능한 단계\n"
        "- 견갑 전인(앞으로 밀기) + 팔 잠금(가능 범위)\n"
        "- 흔한 실수: 팔꿈치 굽힘, 어깨가 내려앉으며 가슴이 떨어짐"
    ),
    "V-sit 기본 단계 홀드": (
        "코어 + 고관절 굴곡 + 햄스트링 유연성이 함께 필요.\n"
        "- 단계: L-sit → tuck V → V-sit\n"
        "- ‘골반 말기(후방경사)’를 유지해야 허리가 편합니다.\n"
        "- 흔한 실수: 허리 과신전, 어깨 으쓱, 다리만 올리고 골반이 풀림"
    ),
    "피스톨 스쿼트(보조 가능)": (
        "한쪽 다리 스쿼트.\n"
        "- 무릎이 안쪽으로 무너지지 않게(발-무릎 방향 일치)\n"
        "- 처음엔 문고리/기둥 잡고 보조 가능\n"
        "- 흔한 실수: 무릎 내반, 발뒤꿈치 뜸, 허리 말림"
    ),
    "스캐풀라 푸쉬업": (
        "팔은 펴고, 견갑만 움직입니다.\n"
        "- 내려가며 견갑 모으기(후인), 올라가며 견갑 밀기(전인)\n"
        "- 흔한 실수: 팔꿈치 굽혀서 일반 푸쉬업이 됨"
    ),
    "RKC 플랭크": (
        "짧게 강하게. ‘전신 긴장’이 핵심.\n"
        "- 갈비뼈 말기 + 둔근 조이기 + 팔꿈치로 바닥 끌어당기기\n"
        "- 흔한 실수: 허리 꺾임, 엉덩이 들림, 목 과신전"
    ),
}

# -----------------------------
# 데이터 구조
# -----------------------------
@dataclass
class Exercise:
    name: str
    kind: str            # rep | hold
    reps: int
    sets: int
    work_seconds: int
    rest_seconds: int
    cues: str

# -----------------------------
# 상태 초기화
# -----------------------------
def init_state():
    st.session_state.setdefault("step", 1)  # 1 장비 -> 2 스킬 -> 3 초기테스트 -> 4 주당횟수 -> 5 목록 -> 6 플레이어 -> 99 설정 -> 98 테스트
    st.session_state.setdefault("settings", DEFAULTS.copy())
    st.session_state.setdefault("profile", {
        "equipment": [], "skills": [], "freq": 3, "session_minutes": 60,
        "height_cm": 0, "weight_kg": 0
    })
    st.session_state.setdefault("plan", [])
    st.session_state.setdefault("stretch_done", False)

    st.session_state.setdefault("equip_selected", {e: False for e in EQUIPMENT})
    st.session_state.setdefault("skill_selected", {s: False for s in SKILLS})

    # 테스트 결과 저장(최신)
    st.session_state.setdefault("tests", {
        "baseline": {},   # 최초 측정값
        "latest": {},     # 최근 측정값
        "history": [],    # (week, results)
    })

    # 플레이어(타이머)
    st.session_state.setdefault(
        "player",
        {"session_idx": 0, "ex_idx": 0, "set_idx": 1, "phase": "idle", "phase_end": None, "phase_total": None},
    )

def go_step(n: int):
    st.session_state.step = n

# -----------------------------
# 유틸
# -----------------------------
def rest_for(cat: str, settings: Dict) -> int:
    if cat == "skill":
        return int(settings["rest_seconds_skill"])
    if cat == "power":
        return int(settings["rest_seconds_power"])
    if cat == "strength":
        return int(settings["rest_seconds_strength"])
    return int(settings["rest_seconds_accessory"])

def has_any(eq_set: set, any_of: List[str]) -> bool:
    return any(x in eq_set for x in any_of)

def skill_allowed(skill: str, eq_set: set) -> Tuple[bool, Optional[str]]:
    req = SKILL_REQ_ANY_OF.get(skill)
    if not req:
        return True, None
    if has_any(eq_set, req):
        return True, None
    return False, SKILL_NOTE.get(skill, "장비 필요")

def mmss(sec: int) -> str:
    return f"{sec//60:02d}:{sec%60:02d}"

def seconds_left(end_epoch: float) -> int:
    return max(0, int(round(end_epoch - time.time())))

def autorefresh(interval_ms: int = 250):
    if hasattr(st, "autorefresh"):
        st.autorefresh(interval=interval_ms, key="__ar__")
    else:
        st.button("새로고침", key="manual_refresh")

# -----------------------------
# 체크박스 타일 UI (안정성 최우선)
# -----------------------------
def tile_checkbox_css():
    st.markdown("""
<style>
div[data-testid="stCheckbox"] {
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 16px;
    padding: 10px 10px 6px 10px;
    min-height: 74px;
}
div[data-testid="stCheckbox"]:has(input:checked) {
    border-color: rgba(64, 135, 255, 0.75);
    background: rgba(64, 135, 255, 0.10);
}
div[data-testid="stCheckbox"] label { font-weight: 800; }
.small-note {
    font-size: 12px;
    opacity: 0.75;
    margin-top: 6px;
    line-height: 1.15;
}
</style>
""", unsafe_allow_html=True)

def checkbox_tile_grid(options: List[str],
                       selected_map: Dict[str, bool],
                       key_prefix: str,
                       disabled_map: Optional[Dict[str, bool]] = None,
                       note_map: Optional[Dict[str, str]] = None):
    tile_checkbox_css()
    rows = [options[:4], options[4:]]
    for r, opts in enumerate(rows):
        cols = st.columns(len(opts))
        for c, name in enumerate(opts):
            disabled = bool(disabled_map.get(name, False)) if disabled_map else False
            k = f"{key_prefix}__{name}"
            if k not in st.session_state:
                st.session_state[k] = bool(selected_map.get(name, False))

            with cols[c]:
                label = f"✓ {name}" if st.session_state[k] else name
                val = st.checkbox(label, value=bool(st.session_state[k]), key=k, disabled=disabled)
                selected_map[name] = bool(val)

                if note_map and name in note_map:
                    st.markdown(f"<div class='small-note'>{note_map[name]}</div>", unsafe_allow_html=True)

# -----------------------------
# 초기/주기 테스트 설계
# -----------------------------
def test_items(profile: Dict) -> List[Tuple[str, str]]:
    """
    (key, 표시명)
    key는 결과 저장용.
    """
    eq = set(profile.get("equipment", []))
    skills = profile.get("skills", [])

    items: List[Tuple[str, str]] = []
    # 공통 테스트
    if ("풀업바" in eq) or ("링/낮은바" in eq):
        items.append(("max_pullups", "풀업 최대 반복(반동 없이)"))
    items.append(("max_pushups", "푸쉬업 최대 반복(가슴-바닥 가까이)"))

    if ("딥스 가능(평행봉/의자 포함)" in eq) or ("링/낮은바" in eq):
        items.append(("max_dips", "딥스 최대 반복(가능 시)"))

    # 코어/지지력(타이머로 재기)
    items.append(("rkc_plank_sec", "RKC 플랭크 유지(초)"))

    # 스킬별 테스트(가능한 범위의 프록시)
    if "머슬업" in skills and (("풀업바" in eq) or ("링/낮은바" in eq)):
        items.append(("top_hold_pullups", "상단 정지 풀업 2초 유지 가능한 반복수"))

    if "프론트 레버" in skills and (("풀업바" in eq) or ("링/낮은바" in eq)):
        items.append(("tuck_fl_sec", "턱 프론트레버 유지(초)"))

    if "백 레버" in skills and (("풀업바" in eq) or ("링/낮은바" in eq)):
        items.append(("tuck_bl_sec", "턱 백레버 유지(초)"))

    if "핸드스탠드 푸쉬업" in skills:
        items.append(("max_pike_pushups", "파이크 푸쉬업 최대 반복"))

    if "플란체" in skills:
        items.append(("planche_lean_sec", "플란체 린(전경사) 유지(초)"))

    if "V-sit" in skills:
        items.append(("l_sit_sec", "L-sit 또는 tuck V 유지(초)"))

    if "피스톨 스쿼트" in skills:
        items.append(("pistol_each_leg", "피스톨 스쿼트(각 다리) 최대 반복"))

    return items

def need_4week_test(settings: Dict) -> bool:
    cw = int(settings.get("current_week", 1))
    lw = int(settings.get("last_test_week", 0))
    return (cw - lw) >= 4

def save_test_results(results: Dict[str, float], is_baseline: bool):
    settings = st.session_state.settings
    cw = int(settings.get("current_week", 1))

    if is_baseline and not st.session_state.tests["baseline"]:
        st.session_state.tests["baseline"] = dict(results)

    st.session_state.tests["latest"] = dict(results)
    st.session_state.tests["history"].append((cw, dict(results)))

    st.session_state.settings["last_test_week"] = cw

# -----------------------------
# 테스트 기반 “대략적인” 강도 산출(프로토타입)
# -----------------------------
def prescribe_from_tests(profile: Dict, tests_latest: Dict[str, float]) -> Dict[str, Dict[str, int]]:
    """
    테스트 결과 -> 주요 운동 처방(세트/반복/홀드초)
    반환: 운동명 -> {"reps":, "sets":, "hold":}
    """
    out: Dict[str, Dict[str, int]] = {}
    eq = set(profile.get("equipment", []))

    def clamp_int(x, lo, hi):
        return int(max(lo, min(hi, round(x))))

    # 풀업: 최대의 55~70% 근처(프로토타입: 60%)
    if (("풀업바" in eq) or ("링/낮은바" in eq)) and tests_latest.get("max_pullups", 0) > 0:
        m = tests_latest["max_pullups"]
        reps = clamp_int(m * 0.60, 2, max(3, int(m)))
        out["풀업"] = {"reps": reps, "sets": 5}

    # 푸쉬업: 최대의 55~70% 근처(프로토타입: 60%)
    if tests_latest.get("max_pushups", 0) > 0:
        m = tests_latest["max_pushups"]
        reps = clamp_int(m * 0.60, 6, int(m))
        out["푸쉬업"] = {"reps": reps, "sets": 5}

    # 딥스
    if tests_latest.get("max_dips", 0) > 0:
        m = tests_latest["max_dips"]
        reps = clamp_int(m * 0.60, 3, int(m))
        out["딥스"] = {"reps": reps, "sets": 5}

    # RKC 플랭크: 최대 유지의 50~60% 근처(프로토타입: 55%)
    if tests_latest.get("rkc_plank_sec", 0) > 0:
        m = tests_latest["rkc_plank_sec"]
        hold = clamp_int(m * 0.55, 10, int(m))
        out["RKC 플랭크"] = {"hold": hold, "sets": 4}

    # 레버/플란체/V-sit: 50~60% 근처 홀드
    for k, name in [
        ("tuck_fl_sec", "프론트 레버 기본 단계 홀드"),
        ("tuck_bl_sec", "백 레버 기본 단계 홀드"),
        ("planche_lean_sec", "플란체 기본 단계 홀드"),
        ("l_sit_sec", "V-sit 기본 단계 홀드"),
    ]:
        if tests_latest.get(k, 0) > 0:
            m = tests_latest[k]
            hold = clamp_int(m * 0.60, 6, int(m))
            out[name] = {"hold": hold, "sets": 6}

    # 파이크 푸쉬업
    if tests_latest.get("max_pike_pushups", 0) > 0:
        m = tests_latest["max_pike_pushups"]
        reps = clamp_int(m * 0.60, 4, int(m))
        out["파이크 푸쉬업"] = {"reps": reps, "sets": 5}

    # 피스톨
    if tests_latest.get("pistol_each_leg", 0) > 0:
        m = tests_latest["pistol_each_leg"]
        reps = clamp_int(m * 0.60, 2, int(m))
        out["피스톨 스쿼트(보조 가능)"] = {"reps": reps, "sets": 4}

    # 상단 정지 풀업(2초 유지): 최대의 70%로 볼륨 결정
    if tests_latest.get("top_hold_pullups", 0) > 0:
        m = tests_latest["top_hold_pullups"]
        reps = clamp_int(m * 0.70, 2, int(m))
        out["상단 정지 풀업(턱 위 2초)"] = {"reps": reps, "sets": 8}

    return out

# -----------------------------
# 루틴 생성(테스트 기반 반영)
# -----------------------------
def generate_plan(profile: Dict, settings: Dict) -> List[List[Exercise]]:
    eq = set(profile.get("equipment", []))
    skills = profile.get("skills", [])
    freq = int(profile.get("freq", 3))

    can_pull = ("풀업바" in eq) or ("링/낮은바" in eq)
    can_dips = ("딥스 가능(평행봉/의자 포함)" in eq) or ("링/낮은바" in eq)
    can_wall = ("벽 사용 가능" in eq)

    tests_latest = st.session_state.tests.get("latest", {}) or {}
    prescription = prescribe_from_tests(profile, tests_latest)

    def get_reps(name: str, default: int) -> int:
        return int(prescription.get(name, {}).get("reps", default))

    def get_sets(name: str, default: int) -> int:
        return int(prescription.get(name, {}).get("sets", default))

    def get_hold(name: str, default: int) -> int:
        return int(prescription.get(name, {}).get("hold", default))

    plan: List[List[Exercise]] = []
    for i in range(freq):
        day: List[Exercise] = []

        # 스킬 1개/회차 로테이션(프로토타입)
        if skills:
            s = skills[i % len(skills)]

            if s in ["프론트 레버", "백 레버"] and can_pull:
                nm = f"{s} 기본 단계 홀드"
                day.append(Exercise(
                    name=nm,
                    kind="hold",
                    reps=0,
                    sets=get_sets(nm, 6),
                    work_seconds=get_hold(nm, 8),
                    rest_seconds=rest_for("power", settings),
                    cues="타이머로만 시간 표시. 폼이 깨지기 전에 중단합니다."
                ))

            elif s in ["플란체", "V-sit"]:
                nm = f"{s} 기본 단계 홀드"
                day.append(Exercise(
                    name=nm,
                    kind="hold",
                    reps=0,
                    sets=get_sets(nm, 6),
                    work_seconds=get_hold(nm, 8),
                    rest_seconds=rest_for("power", settings),
                    cues="타이머로만 시간 표시. 통증이 오면 즉시 중단합니다."
                ))

            elif s == "머슬업" and can_pull:
                day.append(Exercise(
                    name="머슬업 시도(무보조 시도)",
                    kind="rep",
                    reps=4,
                    sets=4,
                    work_seconds=0,
                    rest_seconds=rest_for("skill", settings),
                    cues="시도는 ‘품질 우선’. 실패 반복 금지."
                ))
                day.append(Exercise(
                    name="상단 정지 풀업(턱 위 2초)",
                    kind="rep",
                    reps=get_reps("상단 정지 풀업(턱 위 2초)", 3),
                    sets=get_sets("상단 정지 풀업(턱 위 2초)", 8),
                    work_seconds=0,
                    rest_seconds=rest_for("strength", settings),
                    cues="정지의 흔들림을 줄이고, 반동을 없앱니다."
                ))
                if can_dips:
                    day.append(Exercise(
                        name="딥스",
                        kind="rep",
                        reps=get_reps("딥스", 6),
                        sets=get_sets("딥스", 5),
                        work_seconds=0,
                        rest_seconds=rest_for("strength", settings),
                        cues="어깨가 말리면 깊이를 줄입니다."
                    ))
                else:
                    day.append(Exercise(
                        name="푸쉬업",
                        kind="rep",
                        reps=get_reps("푸쉬업", 15),
                        sets=get_sets("푸쉬업", 5),
                        work_seconds=0,
                        rest_seconds=rest_for("strength", settings),
                        cues="몸통 일직선 유지."
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
                        cues="진입 품질 우선."
                    ))
                day.append(Exercise(
                    name="파이크 푸쉬업",
                    kind="rep",
                    reps=get_reps("파이크 푸쉬업", 10),
                    sets=get_sets("파이크 푸쉬업", 5),
                    work_seconds=0,
                    rest_seconds=rest_for("strength", settings),
                    cues="어깨 수직 압박을 유지."
                ))

            elif s == "피스톨 스쿼트":
                day.append(Exercise(
                    name="피스톨 스쿼트(보조 가능)",
                    kind="rep",
                    reps=get_reps("피스톨 스쿼트(보조 가능)", 5),
                    sets=get_sets("피스톨 스쿼트(보조 가능)", 4),
                    work_seconds=0,
                    rest_seconds=rest_for("strength", settings),
                    cues="무릎 방향 고정."
                ))

        # 공통 베이스
        if can_pull:
            day.append(Exercise(
                name="풀업",
                kind="rep",
                reps=get_reps("풀업", 5),
                sets=get_sets("풀업", 5),
                work_seconds=0,
                rest_seconds=rest_for("strength", settings),
                cues="반동 없이 견갑 고정."
            ))

        # 푸쉬 베이스(딥스가 없으면 푸쉬업 유지)
        if can_dips:
            # 이미 머슬업 날에 딥스가 있을 수 있으니, 중복은 최소화
            pass
        else:
            day.append(Exercise(
                name="푸쉬업",
                kind="rep",
                reps=get_reps("푸쉬업", 12),
                sets=get_sets("푸쉬업", 4),
                work_seconds=0,
                rest_seconds=rest_for("strength", settings),
                cues="코어 고정."
            ))

        day.append(Exercise(
            name="스캐풀라 푸쉬업",
            kind="rep",
            reps=12,
            sets=3,
            work_seconds=0,
            rest_seconds=rest_for("accessory", settings),
            cues="팔은 펴고 견갑만."
        ))

        day.append(Exercise(
            name="RKC 플랭크",
            kind="hold",
            reps=0,
            sets=get_sets("RKC 플랭크", 4),
            work_seconds=get_hold("RKC 플랭크", 20),
            rest_seconds=rest_for("accessory", settings),
            cues="전신 긴장."
        ))

        plan.append(day)
    return plan

def format_line(ex: Exercise) -> str:
    if ex.kind == "rep":
        return f"{ex.name}  {ex.reps}회×{ex.sets}세트"
    return f"{ex.name}  {ex.sets}세트"

# -----------------------------
# 페이지: 스트레칭 / 설정 / 플레이어 / 테스트
# -----------------------------
def page_stretch():
    st.title("운동 전 스트레칭")
    st.markdown("""
- 손목: 돌리기 30초, 손바닥 짚고 앞뒤 체중이동 30초, 손등 체중 20초  
- 팔꿈치: 팔꿈치 굴곡/신전 가볍게 15회, 전완 회전 15회  
- 어깨·견갑: 스캐풀라 푸쉬업 10회, 팔 원 20회  
- 흉추·고관절: 캣카우 8회, 런지 스트레치 양쪽 20초  
""")
    if st.button("준비 완료", type="primary"):
        st.session_state.stretch_done = True
        go_step(6)

def page_settings():
    st.title("설정")
    s = st.session_state.settings

    st.subheader("주차(프로토타입: 수동)")
    s["current_week"] = st.number_input("현재 주차", 1, 200, int(s["current_week"]))
    s["last_test_week"] = st.number_input("마지막 테스트 주차(자동 업데이트됨)", 0, 200, int(s["last_test_week"]))

    st.subheader("휴식/준비(초)")
    s["rest_seconds_skill"] = st.number_input("스킬 시도 휴식", 30, 300, int(s["rest_seconds_skill"]))
    s["rest_seconds_power"] = st.number_input("파워/기술 휴식", 30, 300, int(s["rest_seconds_power"]))
    s["rest_seconds_strength"] = st.number_input("힘운동 휴식", 30, 300, int(s["rest_seconds_strength"]))
    s["rest_seconds_accessory"] = st.number_input("코어/보조 휴식", 15, 180, int(s["rest_seconds_accessory"]))
    s["prep_seconds_hold"] = st.number_input("홀드 준비시간", 0, 30, int(s["prep_seconds_hold"]))

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("저장", type="primary"):
            go_step(5 if st.session_state.plan else 1)
    with c2:
        if st.button("테스트 화면"):
            go_step(98)
    with c3:
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
    day = plan[p["session_idx"]]
    ex = day[p["ex_idx"]]

    st.subheader(f"회차 {p['session_idx']+1} | 운동 {p['ex_idx']+1}/{len(day)} | 세트 {p['set_idx']}/{ex.sets}")

    t1, t2, t3 = st.columns(3)
    with t1:
        if st.button("회차/목록"):
            go_step(5)
    with t2:
        if st.button("테스트"):
            go_step(98)
    with t3:
        if st.button("설정"):
            go_step(99)

    # 운동 이름 + 긴 설명
    st.markdown(f"### {ex.name}")
    if ex.name in EX_DESC:
        st.write(EX_DESC[ex.name])

    if p["phase"] == "idle":
        st.write(ex.cues)

        if ex.kind == "rep":
            st.write(f"오늘 목표: {ex.reps}회×{ex.sets}세트")
            if st.button("세트 완료 → 휴식", type="primary", use_container_width=True):
                p["phase"] = "rest"
                p["phase_total"] = int(ex.rest_seconds)
                p["phase_end"] = time.time() + int(ex.rest_seconds)
                st.experimental_rerun()
        else:
            if st.button("홀드 시작", type="primary", use_container_width=True):
                p["phase"] = "prep"
                p["phase_total"] = int(st.session_state.settings["prep_seconds_hold"])
                p["phase_end"] = time.time() + int(st.session_state.settings["prep_seconds_hold"])
                st.experimental_rerun()

    else:
        autorefresh(250)
        left = seconds_left(float(p["phase_end"]))
        total = int(p["phase_total"])

        if p["phase"] == "prep":
            st.markdown("### 준비")
            st.metric("남은 시간", mmss(left))
            st.progress(0 if total == 0 else (total-left)/total)
            if left == 0:
                p["phase"] = "work"
                p["phase_total"] = int(ex.work_seconds)
                p["phase_end"] = time.time() + int(ex.work_seconds)
                st.experimental_rerun()

        elif p["phase"] == "work":
            st.markdown("### 홀드")
            st.metric("남은 시간", mmss(left))
            st.progress(0 if total == 0 else (total-left)/total)
            if left == 0:
                p["phase"] = "rest"
                p["phase_total"] = int(ex.rest_seconds)
                p["phase_end"] = time.time() + int(ex.rest_seconds)
                st.experimental_rerun()

        elif p["phase"] == "rest":
            st.markdown("### 휴식")
            st.metric("남은 시간", mmss(left))
            st.progress(0 if total == 0 else (total-left)/total)

            if left == 0:
                last_set = (p["set_idx"] >= ex.sets)
                st.success("휴식 종료")

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

def page_test():
    st.title("능력 측정 / 4주 테스트")
    prof = st.session_state.profile
    settings = st.session_state.settings
    items = test_items(prof)

    st.caption("최초 실행 시 ‘초기 측정’을 먼저 하고 루틴을 생성합니다. 이후 4주마다 같은 항목으로 재측정합니다.")

    # 타이머형 테스트(홀드용) 안내
    st.markdown("""
- 반복 테스트(풀업/푸쉬업/딥스 등)는 **직접 수행 후 숫자 입력**  
- 홀드 테스트(RKC, 레버, 린 등)는 **원하면 아래 타이머로 재고 숫자 입력**  
""")

    # 간단 홀드 타이머(준비 5초 -> 스톱워치)
    with st.expander("홀드 타이머(준비 5초 후 스톱워치)"):
        if "hold_timer" not in st.session_state:
            st.session_state.hold_timer = {"phase": "idle", "start": None, "prep_end": None, "elapsed": 0.0}

        ht = st.session_state.hold_timer
        if ht["phase"] == "idle":
            if st.button("타이머 시작"):
                ht["phase"] = "prep"
                ht["prep_end"] = time.time() + int(settings["prep_seconds_hold"])
                ht["elapsed"] = 0.0
                st.experimental_rerun()
        else:
            autorefresh(250)
            if ht["phase"] == "prep":
                left = seconds_left(float(ht["prep_end"]))
                st.metric("준비", mmss(left))
                if left == 0:
                    ht["phase"] = "run"
                    ht["start"] = time.time()
                    st.experimental_rerun()
            elif ht["phase"] == "run":
                ht["elapsed"] = time.time() - float(ht["start"])
                st.metric("경과", mmss(int(ht["elapsed"])))
                if st.button("정지"):
                    ht["phase"] = "idle"
                    st.success(f"기록: {int(ht['elapsed'])}초")

    st.subheader("신체 정보(선택)")
    prof["height_cm"] = st.number_input("키(cm)", 0, 250, int(prof.get("height_cm", 0)))
    prof["weight_kg"] = st.number_input("몸무게(kg)", 0, 250, int(prof.get("weight_kg", 0)))

    st.subheader("측정 입력")
    results: Dict[str, float] = {}
    for key, label in items:
        if key.endswith("_sec"):
            results[key] = float(st.number_input(label, 0, 600, int(st.session_state.tests["latest"].get(key, 0)), key=f"in_{key}"))
        else:
            results[key] = float(st.number_input(label, 0, 200, int(st.session_state.tests["latest"].get(key, 0)), key=f"in_{key}"))

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("저장(초기 측정)", type="primary"):
            save_test_results(results, is_baseline=True)
            st.success("초기 측정 저장 완료")
    with c2:
        if st.button("저장(4주 테스트)", type="primary"):
            save_test_results(results, is_baseline=False)
            st.success("4주 테스트 저장 완료")
    with c3:
        if st.button("뒤로"):
            # 초기테스트가 없으면 온보딩으로
            if st.session_state.tests["latest"]:
                go_step(5 if st.session_state.plan else 4)
            else:
                go_step(3)

    if st.session_state.tests["history"]:
        st.subheader("테스트 기록(최근)")
        for wk, res in st.session_state.tests["history"][-5:]:
            st.write(f"- {wk}주차: " + ", ".join([f"{k}={int(v)}" for k, v in res.items()]))

# -----------------------------
# 온보딩(장비/동작/초기테스트/주당횟수/목록)
# -----------------------------
def page_onboarding():
    st.title("칼리스데닉스 루틴 앱(프로토타입)")

    settings = st.session_state.settings
    prof = st.session_state.profile
    step = st.session_state.step

    # 4주 테스트 알림
    if st.session_state.plan and need_4week_test(settings):
        st.warning(f"{settings['current_week']}주차입니다. 마지막 테스트는 {settings['last_test_week']}주차입니다. 4주 테스트를 진행하세요.")
        if st.button("지금 테스트하기"):
            go_step(98)

    if step == 1:
        st.subheader("1) 장비 선택")
        checkbox_tile_grid(EQUIPMENT, st.session_state.equip_selected, "equip_tiles")
        prof["equipment"] = [e for e in EQUIPMENT if st.session_state.equip_selected.get(e, False)]

        if st.button("다음", type="primary", use_container_width=True):
            go_step(2)

    elif step == 2:
        st.subheader("2) 원하는 동작 선택(멀티)")
        eq_set = set(prof.get("equipment", []))

        disabled_map: Dict[str, bool] = {}
        note_map: Dict[str, str] = {}
        for s in SKILLS:
            ok, note = skill_allowed(s, eq_set)
            disabled_map[s] = not ok
            if not ok:
                st.session_state.skill_selected[s] = False
            if note:
                note_map[s] = note

        checkbox_tile_grid(SKILLS, st.session_state.skill_selected, "skill_tiles", disabled_map=disabled_map, note_map=note_map)
        prof["skills"] = [s for s in SKILLS if st.session_state.skill_selected.get(s, False)]

        st.write("현재 선택:", ", ".join(prof["skills"]) if prof["skills"] else "없음")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("이전", use_container_width=True):
                go_step(1)
        with c2:
            if st.button("다음", type="primary", use_container_width=True, disabled=(len(prof["skills"]) == 0)):
                go_step(3)

    elif step == 3:
        # 최초 측정 강제(테스트가 없으면 다음으로 못감)
        st.subheader("3) 초기 능력 측정(필수)")
        st.info("루틴을 만들기 전에 최초 1회 측정이 필요합니다. ‘테스트 화면’에서 입력 후 돌아오세요.")
        if st.button("테스트 화면으로", type="primary"):
            go_step(98)

        if st.session_state.tests["latest"]:
            st.success("초기 측정이 존재합니다. 다음 단계로 이동할 수 있습니다.")
            if st.button("다음", type="primary"):
                go_step(4)

        if st.button("이전"):
            go_step(2)

    elif step == 4:
        st.subheader("4) 주당 운동 횟수 / 1회 시간")
        prof["freq"] = st.slider("주당 운동 횟수", 2, 6, int(prof["freq"]))
        prof["session_minutes"] = st.slider("1회 운동 가능 시간(분)", 30, 120, int(prof["session_minutes"]), step=5)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("이전", use_container_width=True):
                go_step(3)
        with c2:
            if st.button("루틴 생성", type="primary", use_container_width=True):
                st.session_state.plan = generate_plan(prof, settings)
                st.session_state.player = {"session_idx": 0, "ex_idx": 0, "set_idx": 1, "phase": "idle", "phase_end": None, "phase_total": None}
                st.session_state.stretch_done = False
                go_step(5)

    elif step == 5:
        st.subheader("루틴 목록(시간 미표기)")
        plan = st.session_state.plan

        if not plan:
            st.warning("루틴이 없습니다. 이전 단계로 돌아가세요.")
            if st.button("처음으로"):
                go_step(1)
            return

        for i, day in enumerate(plan):
            with st.expander(f"회차 {i+1}"):
                for ex in day:
                    st.write("• " + format_line(ex))

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("설정"):
                go_step(99)
        with c2:
            if st.button("테스트"):
                go_step(98)
        with c3:
            if st.button("처음으로"):
                go_step(1)
        with c4:
            if st.button("운동 시작", type="primary"):
                go_step(6)

    elif step == 6:
        page_player()

    elif step == 98:
        page_test()

    elif step == 99:
        page_settings()

def main():
    st.set_page_config(page_title="칼리스데닉스 루틴 앱(프로토타입)", layout="centered")
    init_state()
    page_onboarding()

if __name__ == "__main__":
    main()
