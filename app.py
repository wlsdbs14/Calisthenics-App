import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import streamlit as st

# ==========================================================
# 칼리스데닉스 루틴 앱 (Streamlit 프로토타입)
# - 장비 선택(타일)
# - 동작 선택(타일/멀티)
# - 초기 능력 측정 + 4주마다 리테스트
# - 주간 루틴 생성(주 N회)
# - 운동 플레이어(세트/휴식 타이머, 휴식 건너뛰기)
# ==========================================================

APP_TITLE = "칼리스데닉스 루틴 앱(프로토타입)"

# --- 선택 가능한 장비(요청: 7개 타일) ---
EQUIPMENT: List[str] = [
    "풀업바",
    "딥스바(평행봉)",
    "링",
    "저항밴드",
    "벽(핸드스탠드용)",
    "덤벨",
    "바벨",
]

# --- 목표 동작(요청: 7개) ---
SKILLS: List[str] = [
    "머슬업",
    "프론트 레버",
    "핸드스탠드 푸쉬업",
    "플란체",
    "V-sit",
    "피스톨 스쿼트",
    "백 레버",
]

# --- 동작별 장비 조건(가능/불가 판정용) ---
# 바닥/매트는 기본 전제로 간주(선택 장비에 넣지 않음)

def can_do_skill(skill: str, eq: List[str]) -> Tuple[bool, str]:
    eqset = set(eq)
    if skill == "머슬업":
        ok = ("풀업바" in eqset) and ("딥스바(평행봉)" in eqset or "링" in eqset)
        note = "풀업바 + (딥스바 또는 링) 필요"
        return ok, note
    if skill in ("프론트 레버", "백 레버"):
        ok = ("풀업바" in eqset) or ("링" in eqset)
        note = "풀업바 또는 링 필요"
        return ok, note
    if skill == "핸드스탠드 푸쉬업":
        ok = "벽(핸드스탠드용)" in eqset
        note = "벽(초기 연습) 권장/필수"
        return ok, note
    # 플란체/V-sit/피스톨은 바닥만 있으면 가능(기본 전제)
    return True, "바닥에서 가능"


# --- 긴 설명(요청: 자세하고 정확하게) ---
SKILL_DESCS: Dict[str, str] = {
    "머슬업": (
        "풀업(당기기)에서 딥스(밀기)로 이어지는 전환 동작입니다. 핵심은\n"
        "1) 당기는 구간에서 가슴이 바 쪽으로 접근(팔로만 당기지 않기)\n"
        "2) 전환 구간에서 손목이 바 위로 빨리 넘어가고, 팔꿈치가 바 뒤로 가며\n"
        "3) 바로 밀기(딥스)로 연결되는 흐름입니다.\n\n"
        "초기에는 낮은 바가 없어도 ‘밴드 보조 전환’, ‘상단 서포트 홀드’, ‘딥스 강화’로 전환을 준비합니다."
    ),
    "프론트 레버": (
        "매달린 상태에서 몸을 일자로 ‘앞으로’ 수평에 가깝게 버티는 정적 동작입니다. 핵심은\n"
        "1) 견갑 하강(어깨를 귀에서 멀리) + 약한 후인\n"
        "2) 골반 후방경사(배/엉덩이로 몸통 고정)\n"
        "3) 몸이 ‘꺾이지 않는’ 일자 긴장입니다.\n\n"
        "초기에는 턱-투-바가 아니라 ‘턱걸이 그립 유지 + 턱걸이 상단에서 몸통 긴장’이 우선이며,\n"
        "프록시로 ‘턱 레버/턱-무릎 접은(tuck) 레버 홀드’부터 진행합니다."
    ),
    "백 레버": (
        "링/바에서 몸을 ‘뒤로’ 수평에 가깝게 버티는 정적 동작입니다. 어깨 전면에 부담이 커서\n"
        "견갑 안정(하강/후인)과 통증 관리가 최우선입니다.\n\n"
        "초기에는 ‘스킨더캣(가능 시) → tuck back lever’로 단계화하고,\n"
        "어깨가 말리거나 찌릿하면 범위를 줄이고 중단합니다."
    ),
    "핸드스탠드 푸쉬업": (
        "손으로 서서(핸드스탠드) 머리를 아래로 내려갔다가 어깨로 밀어 올리는 푸쉬업입니다.\n"
        "핵심은\n"
        "1) 팔꿈치 잠금(과신전 말고 ‘단단한 잠금’)\n"
        "2) 견갑 상방회전/거상은 하되, 목을 짧게 만들 정도로 으쓱하지 않기\n"
        "3) 갈비뼈 들림(허리 과신전) 억제입니다.\n\n"
        "초기에는 ‘벽 핸드스탠드 홀드’와 ‘파이크 푸쉬업’으로 어깨 수직 프레스를 만듭니다."
    ),
    "플란체": (
        "팔을 편 채로 몸을 앞으로 기울여 수평에 가깝게 버티는 정적 동작입니다.\n"
        "핵심은\n"
        "1) 견갑 전인(등을 둥글게 ‘미는’ 느낌)\n"
        "2) 팔 완전 신전\n"
        "3) 골반 후방경사로 일자 유지입니다.\n\n"
        "초기는 ‘플란체 린(lean) 홀드’가 표준 시작점이며,\n"
        "손목 부담이 크므로 손목 준비 운동이 필수입니다."
    ),
    "V-sit": (
        "L-sit에서 다리를 더 높게 들어 ‘V’ 모양에 가깝게 만드는 정적 동작입니다.\n"
        "핵심은\n"
        "1) 어깨 하강(딥스 서포트처럼)\n"
        "2) 햄스트링 유연성 + 고관절 굴곡\n"
        "3) 복부 압박(허리 과신전 금지)입니다.\n\n"
        "초기에는 ‘턱-업(tuck) L-sit’ 또는 ‘한쪽 무릎 굽힌 L-sit’부터 진행합니다."
    ),
    "피스톨 스쿼트": (
        "한 발로 앉았다 일어나는 스쿼트입니다.\n"
        "핵심은\n"
        "1) 발바닥 3점 지지(엄지/새끼/뒤꿈치)\n"
        "2) 무릎이 안쪽으로 무너지지 않기\n"
        "3) 내려갈 때 2~3초 컨트롤입니다.\n\n"
        "초기에는 ‘박스(의자)까지 내려가기’ 또는 ‘기둥/문틀 보조’로 가동범위를 만듭니다."
    ),
}

STRETCH_MENU: List[Tuple[str, str]] = [
    ("손목 준비", "손목 굴곡/신전 10회씩 → 손바닥/손등 바닥 짚고 가벼운 체중 싣기 2세트"),
    ("팔꿈치·전완", "팔 뻗고 손목 젖혀 전완 스트레치 20초×2 → 반대로 20초×2"),
    ("어깨", "어깨 원 10회씩(앞/뒤) → 견갑(날개뼈) 올림/내림 10회"),
    ("흉추·고관절", "고양이-소 6회 → 런지 자세에서 고관절 앞쪽 20초×2"),
]


# =========================
# 데이터 구조
# =========================

@dataclass
class Task:
    name: str
    mode: str  # 'reps' | 'hold' | 'timer' | 'rest'
    target: int  # reps or seconds
    sets: int
    rest_s: int
    cue: str


# =========================
# UI 스타일
# =========================


CSS = """
<style>
/* 공통 */
.block-container { padding-top: 2.2rem; }

/* 체크박스 타일(장비/동작 공용)
   - Streamlit 위젯을 HTML로 감싸면 레이아웃이 깨져서,
     stCheckbox 자체를 '타일'처럼 보이게 CSS로 스킨 처리합니다.
   - :has(input:checked)로 즉시(지연 없이) 선택 상태 반영
*/

div[data-testid="stCheckbox"] {
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 18px;
  padding: 14px 14px 12px 14px;
  background: rgba(255,255,255,0.04);
  margin-bottom: 12px;
}

/* 타일 높이를 일정하게 */
div[data-testid="stCheckbox"] > label {
  display: block;
  min-height: 72px;
}

/* 체크박스/텍스트 정렬 */
div[data-testid="stCheckbox"] input { transform: scale(1.15); }
div[data-testid="stCheckbox"] span { font-weight: 700; font-size: 1.02rem; }

/* 선택 상태(지연 없이) */
div[data-testid="stCheckbox"]:has(input:checked) {
  border: 2px solid rgba(255,90,90,0.95);
  background: rgba(255,90,90,0.12);
}

/* 비활성(조건 미충족) */
div[data-testid="stCheckbox"]:has(input:disabled) {
  opacity: 0.55;
}

/* Next 버튼 강조 */
div.stButton > button[kind="primary"] {
  border-radius: 14px;
  padding: 0.65rem 1rem;
}

/* 설명 텍스트 */
.small-note { opacity: 0.85; font-size: 0.92rem; line-height: 1.35; margin-top: -6px; margin-bottom: 12px; }
</style>
"""


# =========================
# 상태 초기화
# =========================

def init_state():
    st.session_state.setdefault("step", 1)
    st.session_state.setdefault("equip", [])
    st.session_state.setdefault("skills", [])
    st.session_state.setdefault(
        "profile",
        {
            "height_cm": 170,
            "weight_kg": 65,
            "sessions_per_week": 3,
            "session_minutes": 60,
            "current_week": 1,
        },
    )
    st.session_state.setdefault(
        "tests",
        {
            "pullup_max": 0,
            "dip_max": 0,
            "pushup_max": 0,
            "pike_pushup_max": 0,
            "tuck_fl_hold_s": 0,
            "tuck_bl_hold_s": 0,
            "wall_hs_hold_s": 0,
            "planche_lean_hold_s": 0,
            "tuck_lsit_hold_s": 0,
            "pistol_assisted_each": 0,
            "latest_retest_week": 0,
        },
    )

    # 운동 플레이어 상태
    st.session_state.setdefault("workout", {"queue": [], "idx": 0, "set_i": 1})
    st.session_state.setdefault("timer", {"running": False, "end_ts": 0.0, "label": "", "allow_skip": False, "kind": "", "post": None})


def go_step(n: int):
    st.session_state.step = n


# =========================
# 타일 렌더
# =========================



def tile_multiselect(
    title: str,
    items: List[str],
    selected: List[str],
    notes: Dict[str, str] | None = None,
    cols: int = 2,
    key_prefix: str = "ms",
    disabled: set[str] | None = None,
) -> List[str]:
    """멀티 선택: '체크박스 자체를 타일처럼' 보이게 렌더링."""
    st.subheader(title)

    notes = notes or {}
    disabled = disabled or set()

    out = list(selected)
    grid = st.columns(cols)

    for i, item in enumerate(items):
        with grid[i % cols]:
            key = f"{key_prefix}_{i}"
            val = st.checkbox(item, value=(item in out), key=key, disabled=(item in disabled))

            # 선택 상태 반영
            if val and item not in out:
                out.append(item)
            if (not val) and item in out:
                out.remove(item)

            note = notes.get(item, "")
            if note:
                st.markdown(f"<div class='small-note'>{note}</div>", unsafe_allow_html=True)

    return out


def tile_skill_select(skills: List[str], selected: List[str], equip_selected: List[str], cols: int = 2) -> List[str]:
    """동작 선택(멀티) + 장비 조건 반영."""
    notes: Dict[str, str] = {}
    disabled: set[str] = set()

    for s in skills:
        ok, why = can_do_skill(s, equip_selected)
        if not ok:
            disabled.add(s)
        if why:
            notes[s] = why

    return tile_multiselect(
        "2) 원하는 동작 선택(멀티)",
        skills,
        selected,
        notes=notes,
        cols=cols,
        key_prefix="skill",
        disabled=disabled,
    )

# =========================
# 루틴 생성 로직(간단하지만 점진)
# =========================

def clamp(x: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, x))


def week_phase(week: int) -> int:
    # 1~4 반복
    w = ((week - 1) % 4) + 1
    return w


def progression_multiplier(week: int) -> float:
    # 4주 사이클: 1(입문) -> 2(증가) -> 3(증가+) -> 4(테스트/약간 감소)
    p = week_phase(week)
    if p == 1:
        return 0.85
    if p == 2:
        return 1.00
    if p == 3:
        return 1.10
    return 0.90


def make_tasks_for_day(day_index: int, skills: List[str], eq: List[str], tests: Dict, prof: Dict) -> List[Task]:
    # day_index: 1..N (주 N회)
    week = int(prof.get("current_week", 1))
    mult = progression_multiplier(week)

    pullup_max = int(tests.get("pullup_max", 0))
    dip_max = int(tests.get("dip_max", 0))
    pushup_max = int(tests.get("pushup_max", 0))
    pike_max = int(tests.get("pike_pushup_max", 0))

    # 기본 휴식(초) - 플레이어에서 타이머로만 보여줌
    base_rest = 60

    tasks: List[Task] = []

    # 스트레칭(고정)
    for name, cue in STRETCH_MENU:
        tasks.append(Task(name=f"스트레칭: {name}", mode="timer", target=40, sets=1, rest_s=10, cue=cue))

    # 3~5회 기준으로 Day A/B/C 스플릿
    # A: 당기기+레버, B: 밀기+핸드스탠드/플란체, C: 혼합+하체/V-sit

    if day_index % 3 == 1:
        # Pull day
        if "풀업바" in eq or "링" in eq:
            reps = clamp(int(pullup_max * 0.55 * mult), 2, 8)
            sets = 4 if pullup_max >= 5 else 5
            tasks.append(Task("풀업(또는 밴드 보조 풀업)", "reps", reps, sets, base_rest, "가슴이 위로. 내려올 때 1~2초 컨트롤."))

        if "머슬업" in skills:
            # 전환 드릴(밴드 있을 때)
            if "저항밴드" in eq:
                tasks.append(Task("밴드 보조 머슬업 전환 드릴", "reps", 3, 4, base_rest, "당기기-전환-밀기 흐름을 끊지 않기."))
            else:
                tasks.append(Task("탑 포지션 서포트 홀드(딥스바/링)", "hold", 10, 4, base_rest, "어깨 내리고(견갑 하강), 팔 펴서 고정."))

        if "프론트 레버" in skills:
            hold = clamp(int(tests.get("tuck_fl_hold_s", 0) * 0.7 * mult), 6, 15)
            tasks.append(Task("턱 프론트 레버 홀드(무릎 접은 tuck)", "hold", hold, 5, base_rest, "골반 말고(후방경사), 견갑 하강 유지."))

        if "백 레버" in skills:
            hold = clamp(int(tests.get("tuck_bl_hold_s", 0) * 0.7 * mult), 6, 15)
            tasks.append(Task("턱 백 레버 홀드(무릎 접은 tuck)", "hold", hold, 4, base_rest, "어깨 통증 나오면 즉시 중단/범위 축소."))

        tasks.append(Task("RKC 플랭크", "hold", 20, 3, 45, "팔꿈치로 바닥 당기고, 발끝으로 밀어 전신 긴장."))

    elif day_index % 3 == 2:
        # Push day
        reps = clamp(int(pushup_max * 0.50 * mult), 6, 20)
        tasks.append(Task("푸쉬업", "reps", reps, 4, base_rest, "몸통 일자. 반동 없이. 바닥에서 밀어내기."))

        if "딥스바(평행봉)" in eq or "링" in eq:
            r = clamp(int(dip_max * 0.55 * mult), 3, 10)
            tasks.append(Task("딥스", "reps", r, 4, base_rest, "어깨 말리지 않게 가슴 열고, 팔꿈치 뒤로."))

        if "핸드스탠드 푸쉬업" in skills:
            # 파이크 푸쉬업 -> 벽 핸드스탠드 홀드
            r = clamp(int(pike_max * 0.60 * mult), 3, 12)
            tasks.append(Task("파이크 푸쉬업", "reps", r, 4, base_rest, "엉덩이 높이, 어깨로 밀어올리기."))
            hold = clamp(int(tests.get("wall_hs_hold_s", 0) * 0.7 * mult), 10, 40)
            tasks.append(Task("벽 핸드스탠드 홀드", "hold", hold, 4, base_rest, "손가락으로 바닥 잡고, 갈비뼈 들리지 않게."))

        if "플란체" in skills:
            hold = clamp(int(tests.get("planche_lean_hold_s", 0) * 0.7 * mult), 8, 20)
            tasks.append(Task("플란체 린 홀드", "hold", hold, 5, base_rest, "팔 편 채로 전인. 골반 말고 버티기."))

        tasks.append(Task("사이드 플랭크", "hold", 20, 2, 30, "골반 수평. 어깨-골반-발 일자."))

    else:
        # Mixed + Legs/Core
        if "피스톨 스쿼트" in skills:
            r = clamp(int(tests.get("pistol_assisted_each", 0) * 0.6 * mult), 3, 8)
            tasks.append(Task("보조 피스톨 스쿼트(각 다리)", "reps", r, 4, 60, "무릎 안쪽 붕괴 금지. 2~3초 내려가기."))
        else:
            tasks.append(Task("스쿼트", "reps", 12, 4, 45, "발 3점 지지. 무릎-발끝 같은 방향."))

        if "V-sit" in skills:
            hold = clamp(int(tests.get("tuck_lsit_hold_s", 0) * 0.7 * mult), 6, 18)
            tasks.append(Task("턱 L-sit 홀드(무릎 접은)", "hold", hold, 6, 45, "어깨 내리고, 허리 꺾이지 않게 복부 고정."))

        if "머슬업" in skills:
            # 기술 시도(저반동)
            tasks.append(Task("머슬업 기술 시도(가능 범위 1회)", "reps", 1, 4, 75, "시도는 ‘깨끗하게’. 실패해도 기록."))

        tasks.append(Task("행잉 니 레이즈(또는 레그레이즈)", "reps", 8, 3, 45, "반동 최소. 골반 말아올리기."))

    return tasks


def make_week_plan(skills: List[str], eq: List[str], tests: Dict, prof: Dict) -> Dict[str, List[Task]]:
    n = int(prof.get("sessions_per_week", 3))
    n = clamp(n, 2, 6)
    plan = {}
    for d in range(1, n + 1):
        plan[f"Day {d}"] = make_tasks_for_day(d, skills, eq, tests, prof)
    return plan


# =========================
# 플레이어(타이머)
# =========================



def start_timer(seconds: int, label: str, allow_skip: bool, kind: str, post=None):
    st.session_state.timer.update(
        {
            "running": True,
            "end_ts": time.time() + float(seconds),
            "label": label,
            "allow_skip": allow_skip,
            "kind": kind,
            "post": post,
        }
    )


def timer_screen() -> bool:
    """타이머 화면.
    - 실행 중이면 화면에 남은 시간을 보여주고 자동으로 갱신합니다.
    - 종료되면 True를 반환(이 run에서 처리).
    """
    t = st.session_state.timer
    if not t.get("running"):
        return False

    remaining = int(max(0.0, t.get("end_ts", 0.0) - time.time()))

    st.markdown(f"### {t.get('label','타이머')}")
    st.metric("남은 시간(초)", remaining)

    # 휴식만 스킵 허용
    if t.get("allow_skip"):
        if st.button("휴식 건너뛰기", key=f"skip_{t.get('kind','')}"):
            t["running"] = False
            t["skipped"] = True
            return True

    if remaining <= 0:
        t["running"] = False
        t["skipped"] = False
        return True

    # 자동 갱신(한 번의 run이 짧게 끝나도록)
    time.sleep(0.25)
    st.rerun()


def workout_player():
    w = st.session_state.workout
    q: List[Task] = w.get("queue", [])

    if not q:
        st.warning("오늘 운동이 비어 있습니다. 루틴 화면으로 돌아가세요.")
        if st.button("루틴으로"):
            go_step(4)
        return

    # 타이머가 켜져 있으면, 먼저 타이머 화면만 보여줌
    finished = timer_screen()
    if finished:
        t = st.session_state.timer
        kind = t.get("kind", "")
        post = t.get("post")

        # 타이머 완료 후 다음 상태 반영
        if kind == "prep":
            # 준비 끝 -> 홀드 본 타이머
            idx = w.get("idx", 0)
            set_i = w.get("set_i", 1)
            task = q[idx]
            start_timer(int(task.target), "홀드", allow_skip=False, kind="hold", post={"idx": idx, "set_i": set_i})
            st.rerun()

        if kind in ("hold", "rest") and post:
            # post: {"next_idx":..., "next_set_i":...}
            w["idx"] = int(post.get("next_idx", w.get("idx", 0)))
            w["set_i"] = int(post.get("next_set_i", 1))

        # 타이머 상태 정리
        st.session_state.timer.update({"kind": "", "post": None})
        st.rerun()

    idx = int(w.get("idx", 0))
    set_i = int(w.get("set_i", 1))

    if idx >= len(q):
        st.success("오늘 루틴 끝.")
        if st.button("루틴 화면으로"):
            go_step(4)
        return

    task = q[idx]

    st.subheader(f"운동 진행: {w.get('day','')}")
    st.progress(min(1.0, (idx + 1) / max(1, len(q))))

    st.markdown(f"## {task.name}")
    st.write(task.cue)

    def start_rest_and_then(next_idx: int, next_set_i: int):
        if int(task.rest_s) > 0:
            start_timer(int(task.rest_s), "휴식", allow_skip=True, kind="rest", post={"next_idx": next_idx, "next_set_i": next_set_i})
            st.rerun()
        else:
            w["idx"] = next_idx
            w["set_i"] = next_set_i
            st.rerun()

    # 홀드/타이머 동작: 준비 5초 -> 홀드 -> 휴식
    if task.mode in ("hold", "timer"):
        st.info("홀드는 시작 전에 준비 5초를 줍니다.")

        if st.button("시작", key=f"start_hold_{idx}_{set_i}"):
            # 홀드가 끝난 뒤 어디로 갈지(post) 미리 계산
            if set_i < task.sets:
                post = {"next_idx": idx, "next_set_i": set_i + 1}
            else:
                post = {"next_idx": idx + 1, "next_set_i": 1}

            # 준비 끝 -> 홀드 끝 -> 휴식(혹은 바로 post) 순서가 필요해서
            # hold 타이머가 끝나면 rest 타이머를 켜고 post 적용하도록 구성
            # 1) prep
            st.session_state.timer.update({"kind": "prep", "post": post})
            start_timer(5, "준비", allow_skip=False, kind="prep", post=post)
            st.rerun()

        # 홀드/휴식은 타이머 화면에서 처리됨
        return

    # reps 동작
    st.markdown(f"**목표:** {task.target}회 × {task.sets}세트")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("세트 완료", key=f"done_{idx}_{set_i}"):
            if set_i < task.sets:
                start_rest_and_then(idx, set_i + 1)
            else:
                start_rest_and_then(idx + 1, 1)

    with col2:
        if st.button("이 운동 건너뛰기", key=f"skip_task_{idx}_{set_i}"):
            w["idx"] = idx + 1
            w["set_i"] = 1
            st.rerun()

    with col3:
        if st.button("설정으로", key=f"to_settings_{idx}_{set_i}"):
            st.session_state.setdefault("resume_step", 5)
            go_step(1)
            st.rerun()

# =========================
# 페이지
# =========================

def page_equipment():
    st.title(APP_TITLE)

    # 운동 중 설정으로 잠깐 왔을 때(진행상태 유지)
    if st.session_state.get("resume_step") == 5 and st.session_state.get("workout", {}).get("in_progress"):
        if st.button("운동 화면으로 돌아가기", key="resume_workout_btn"):
            go_step(5)
            st.rerun()
    st.header("1) 장비 선택")

    st.session_state.equip = tile_multiselect(
        "장비(복수 선택)",
        EQUIPMENT,
        st.session_state.equip,
        notes={
            "풀업바": "바/문틀철봉 포함",
            "딥스바(평행봉)": "딥스/서포트 가능",
            "링": "레버/서포트/딥스 가능",
            "저항밴드": "보조/점진 난이도 조절",
            "벽(핸드스탠드용)": "초기 균형 필수",
            "덤벨": "보조근/어깨 강화",
            "바벨": "최대근력 보완",
        },
        cols=2,
        key_prefix="eq",
    )

    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col2:
        if st.button("다음", type="primary"):
            go_step(2)


def page_skills():
    st.title(APP_TITLE)
    st.header("2) 원하는 동작 선택")

    st.session_state.skills = tile_skill_select(SKILLS, st.session_state.skills, st.session_state.equip)

    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("이전"):
            go_step(1)
    with col2:
        if st.button("다음", type="primary"):
            if not st.session_state.skills:
                st.warning("동작을 1개 이상 선택하세요.")
            else:
                go_step(3)


def page_profile_and_tests():
    st.title(APP_TITLE)
    st.header("3) 초기 설정 + 능력 측정")

    prof = st.session_state.profile
    tests = st.session_state.tests

    colA, colB, colC = st.columns(3)
    with colA:
        prof["height_cm"] = st.number_input("키(cm)", 120, 220, int(prof["height_cm"]))
        prof["weight_kg"] = st.number_input("몸무게(kg)", 30, 200, int(prof["weight_kg"]))
    with colB:
        prof["sessions_per_week"] = st.radio("주 몇 회?", [2, 3, 4, 5, 6], index=[2,3,4,5,6].index(int(prof["sessions_per_week"])) if int(prof["sessions_per_week"]) in [2,3,4,5,6] else 1)
        prof["session_minutes"] = st.slider("1회 운동 가능 시간(분)", 30, 120, int(prof["session_minutes"]), step=5)
    with colC:
        prof["current_week"] = st.number_input("현재 진행 주차(숫자)", 1, 260, int(prof.get("current_week", 1)))
        st.caption("4주마다 리테스트를 권장합니다.")

    st.subheader("기본 테스트(권장)")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        tests["pullup_max"] = st.number_input("최대 풀업(정자세)", 0, 50, int(tests["pullup_max"]))
    with c2:
        tests["dip_max"] = st.number_input("최대 딥스(정자세)", 0, 50, int(tests["dip_max"]))
    with c3:
        tests["pushup_max"] = st.number_input("최대 푸쉬업(정자세)", 0, 200, int(tests["pushup_max"]))
    with c4:
        tests["pike_pushup_max"] = st.number_input("최대 파이크 푸쉬업", 0, 100, int(tests["pike_pushup_max"]))

    st.subheader("동작별 테스트(선택한 것만 입력)")

    if "프론트 레버" in st.session_state.skills:
        tests["tuck_fl_hold_s"] = st.number_input("tuck 프론트 레버 홀드(초)", 0, 120, int(tests["tuck_fl_hold_s"]))

    if "백 레버" in st.session_state.skills:
        tests["tuck_bl_hold_s"] = st.number_input("tuck 백 레버 홀드(초)", 0, 120, int(tests["tuck_bl_hold_s"]))

    if "핸드스탠드 푸쉬업" in st.session_state.skills:
        tests["wall_hs_hold_s"] = st.number_input("벽 핸드스탠드 홀드(초)", 0, 180, int(tests["wall_hs_hold_s"]))

    if "플란체" in st.session_state.skills:
        tests["planche_lean_hold_s"] = st.number_input("플란체 린 홀드(초)", 0, 120, int(tests["planche_lean_hold_s"]))

    if "V-sit" in st.session_state.skills:
        tests["tuck_lsit_hold_s"] = st.number_input("tuck L-sit 홀드(초)", 0, 120, int(tests["tuck_lsit_hold_s"]))

    if "피스톨 스쿼트" in st.session_state.skills:
        tests["pistol_assisted_each"] = st.number_input("보조 피스톨 최대(각 다리, 회)", 0, 30, int(tests["pistol_assisted_each"]))

    # 4주마다 리테스트 안내
    phase = week_phase(int(prof["current_week"]))
    if int(prof["current_week"]) > 1 and phase == 1:
        st.warning("이번 주는 4주 사이클이 새로 시작되는 주입니다. 가능하면 리테스트(최대치)를 다시 입력하면 루틴 정확도가 올라갑니다.")
        if st.button("이번 주 리테스트로 저장"):
            tests["latest_retest_week"] = int(prof["current_week"])  # 기록
            st.success("리테스트 주차로 저장했습니다.")

    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("이전"):
            go_step(2)
    with col2:
        if st.button("루틴 생성", type="primary"):
            go_step(4)


def page_plan():
    st.title(APP_TITLE)
    st.header("4) 이번 주 루틴")

    eq = st.session_state.equip
    skills = st.session_state.skills
    prof = st.session_state.profile
    tests = st.session_state.tests

    plan = make_week_plan(skills, eq, tests, prof)
    st.session_state["plan"] = plan

    st.caption("표의 홀드/스트레칭은 실제 운동 화면에서 타이머로 진행됩니다.")

    for day, tasks in plan.items():
        with st.expander(day, expanded=(day == "Day 1")):
            for t in tasks:
                if t.mode == "reps":
                    st.write(f"- {t.name}: {t.target}회 × {t.sets}세트")
                elif t.mode == "hold":
                    st.write(f"- {t.name}: (타이머) × {t.sets}세트")
                else:
                    st.write(f"- {t.name}: (타이머)")

            if st.button(f"{day} 시작", type="primary", key=f"start_{day}"):
                start_workout(plan, day)

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("이전"):
            go_step(3)
    with col2:
        if st.button("설정(장비/동작) 바꾸기"):
            go_step(1)
    with col3:
        if st.button("초기화"):
            # 모든 상태를 지우되, 의도적 클릭에서만
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


def page_workout():
    st.title(APP_TITLE)
    st.header("5) 운동 진행")

    # 설정 들어갔다가 돌아와도 진행 유지하려면 초기화 금지
    workout_player()

    st.markdown("---")
    if st.button("루틴 화면으로"):
        go_step(4)


# =========================
# 메인
# =========================

def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)

    init_state()

    step = int(st.session_state.step)

    if step == 1:
        page_equipment()
    elif step == 2:
        page_skills()
    elif step == 3:
        page_profile_and_tests()
    elif step == 4:
        page_plan()
    elif step == 5:
        page_workout()
    else:
        go_step(1)
        page_equipment()


if __name__ == "__main__":
    main()
