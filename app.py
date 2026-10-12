import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import date, datetime
import os

# ---------------- Негізгі баптаулар ----------------
st.set_page_config(
    page_title="Эко-мектеп AI | 7А",
    page_icon="🌿",
    layout="wide"
)

BASE = Path(__file__).resolve().parent
DB = BASE / "eco_mektep.db"
PHOTO_DIR = BASE / "eco_photos"
PHOTO_DIR.mkdir(exist_ok=True)

TEACHER = "Ибраева Алтынай Абылкасымовна"
TEACHER_PASSWORD = os.environ.get("ECO_TEACHER_PASSWORD", "eco2026")

STUDENTS = [
    "Абдыбай Айару Алдабергенқызы",
    "Айдынов Алижан Айдынұлы",
    "Аманхан Ерсұлтан Аянұлы",
    "Базарбек Камила Асқарбекқызы",
    "Гади Мади Қадырұлы",
    "Гусманова Сезім Берикболқызы",
    "Дюсенбек Алтынай Дарханқызы",
    "Ермекұлы Эльдар",
    "Ерзат Олжас Ерзатұлы",
    "Жаканбаева Амина Мұхтарқызы",
    "Жұмағалиева Аделя Ерланқызы",
    "Казикан Дәулет Дастанұлы",
    "Касен Даяна Айдосқызы",
    "Қуанышбаева Жанеля Біржанқызы",
    "Марғұланова Айсезім Айдосқызы",
    "Мұратбек Айару Асылбекқызы",
    "Нығметоллаева Рабия Бегім Медетқызы",
    "Онғар Мақсат Берікұлы",
    "Оразханова Айсара Серікжанқызы",
    "Өнербек Айзере Төлегенқызы",
    "Серікбай Айару Аятқызы",
    "Талғатова Жібек Талантқызы",
    "Тоқтасынов Сенім Асқарұлы"
]

TASKS = [
    ("Қоқысты сұрыптау",
     "Қағаз, пластик және басқа қалдықтарды бөлек жинаудың үлгісін көрсет. Фотоесеп жібер."),
    ("Суды үнемдеу",
     "Суды үнемдеудің бір тәсілін орында. Мысалы, тіс тазалағанда суды босқа ағызба."),
    ("Электр қуатын үнемдеу",
     "Қажетсіз жанып тұрған шамды сөндіріп, энергияны үнемдеу туралы фотоесеп жаса."),
    ("Таза аула",
     "Қауіпсіз әрі қолжетімді шағын аумақты таза ұстауға үлес қос. Қажет болса, ересек адамның көмегін ал."),
    ("Затты қайта пайдалану",
     "Бір затты лақтырмай, қайта пайдаланудың үлгісін көрсет."),
    ("Өсімдікке қамқорлық",
     "Өсімдікке су құй немесе оны күтіп-бапта. Фотоесепке қысқа түсініктеме қос."),
    ("Экологиялық кеңес",
     "Отбасыңа табиғатты қорғау туралы бір пайдалы кеңес айт. Кеңесті қағазға жазып, фотоға түсір."),
    ("Қағазды үнемдеу",
     "Қағаздың екі жағын пайдалан немесе макулатураны бөлек жина."),
    ("Пластикті азайту",
     "Бір рет қолданылатын пластикті азайтудың жолын көрсет. Мысалы, қайта қолданылатын су құтысын пайдалан."),
    ("Табиғатты бақылау",
     "Айналаңдағы өсімдік немесе табиғи көріністі бақылап, фотоға түсір және сипатта."),
    ("Эко-көлік",
     "Жаяу жүрудің немесе велосипедтің экологиялық пайдасы туралы қысқаша жаз."),
    ("Құстарға қамқорлық",
     "Құстарды бақылап, олар туралы бір қызықты мәлімет жаз. Құстарға зиян келтірме."),
    ("Эко-бұрыш",
     "Сыныпқа немесе үйге табиғатты қорғау туралы шағын ақпараттық жазба дайында."),
    ("Таза су",
     "Судың адам мен табиғат үшін маңызы туралы екі сөйлем жазып, фотоесепке тірке."),
    ("Табиғатты аялау",
     "Табиғатта қоқыс қалдырмау туралы шағын ескерту немесе жадынама жаса."),
    ("Жасыл әдет",
     "Бүгін орындаған бір экологиялық әдетіңді сипаттап, фотоесеп жібер.")
]

# ---------------- Дерекқор ----------------
def connect():
    con = sqlite3.connect(DB, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_date TEXT NOT NULL,
            student TEXT NOT NULL,
            title TEXT NOT NULL,
            task TEXT NOT NULL,
            UNIQUE(task_date, student)
        )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER NOT NULL UNIQUE,
            student TEXT NOT NULL,
            task_date TEXT NOT NULL,
            note TEXT DEFAULT '',
            photo_path TEXT DEFAULT '',
            submitted_at TEXT NOT NULL,
            status TEXT DEFAULT 'Күтуде',
            teacher_comment TEXT DEFAULT '',
            reviewed_at TEXT DEFAULT ''
        )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL UNIQUE,
            student TEXT NOT NULL,
            score INTEGER NOT NULL DEFAULT 10,
            awarded_at TEXT NOT NULL
        )
        """)
        con.commit()

def create_daily_tasks(day):
    day_text = day.isoformat()
    with connect() as con:
        existing = con.execute(
            "SELECT COUNT(*) n FROM assignments WHERE task_date=?",
            (day_text,)
        ).fetchone()["n"]

        if existing >= 5:
            return

        # 2026 жылғы 12 қазаннан бастап оқушыларды әділ кезекпен таңдау.
        start_day = date(2026, 10, 12)
        day_number = max(0, (day - start_day).days)
        first = (day_number * 5) % len(STUDENTS)
        chosen = [STUDENTS[(first + i) % len(STUDENTS)] for i in range(5)]

        for i, student in enumerate(chosen):
            task_index = (day_number * 5 + i) % len(TASKS)
            title, task = TASKS[task_index]
            con.execute("""
                INSERT OR IGNORE INTO assignments
                (task_date, student, title, task)
                VALUES (?, ?, ?, ?)
            """, (day_text, student, title, task))
        con.commit()

def get_assignments(day_text=None):
    with connect() as con:
        query = """
        SELECT a.id, a.task_date, a.student, a.title, a.task,
               r.id AS report_id, r.note, r.photo_path, r.submitted_at,
               r.status, r.teacher_comment
        FROM assignments a
        LEFT JOIN reports r ON r.assignment_id=a.id
        """
        params = ()
        if day_text:
            query += " WHERE a.task_date=?"
            params = (day_text,)
        query += " ORDER BY a.task_date DESC, a.id ASC"
        return [dict(r) for r in con.execute(query, params).fetchall()]

def submit_report(assignment_id, student, day_text, note, uploaded):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = ""
    if uploaded is not None:
        safe_original = "".join(
            c if c.isalnum() or c in "._-" else "_"
            for c in Path(uploaded.name).name
        )
        filename = f"{day_text}_{assignment_id}_{datetime.now().strftime('%H%M%S')}_{safe_original}"
        photo_file = PHOTO_DIR / filename
        photo_file.write_bytes(uploaded.getvalue())

    photo_path = str(PHOTO_DIR / filename) if filename else ""

    with connect() as con:
        previous = con.execute(
            "SELECT id, status FROM reports WHERE assignment_id=?",
            (assignment_id,)
        ).fetchone()

        if previous and previous["status"] == "Қабылданды":
            return False

        if previous:
            con.execute("""
                UPDATE reports
                SET student=?, task_date=?, note=?, photo_path=?,
                    submitted_at=?, status='Күтуде',
                    teacher_comment='', reviewed_at=''
                WHERE assignment_id=?
            """, (student, day_text, note, photo_path, timestamp, assignment_id))
        else:
            con.execute("""
                INSERT INTO reports
                (assignment_id, student, task_date, note, photo_path, submitted_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (assignment_id, student, day_text, note, photo_path, timestamp))
        con.commit()
    return True

def review_report(report_id, status, comment):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with connect() as con:
        row = con.execute(
            "SELECT student FROM reports WHERE id=?", (report_id,)
        ).fetchone()
        if not row:
            return

        con.execute("""
            UPDATE reports
            SET status=?, teacher_comment=?, reviewed_at=?
            WHERE id=?
        """, (status, comment, now, report_id))

        if status == "Қабылданды":
            con.execute("""
                INSERT OR IGNORE INTO points
                (report_id, student, score, awarded_at)
                VALUES (?, ?, 10, ?)
            """, (report_id, row["student"], now))
        else:
            con.execute("DELETE FROM points WHERE report_id=?", (report_id,))
        con.commit()

def get_ranking():
    with connect() as con:
        rows = con.execute("""
            SELECT s.student,
                   COALESCE(SUM(p.score),0) AS points,
                   COUNT(p.id) AS accepted
            FROM (SELECT DISTINCT student FROM assignments) s
            LEFT JOIN points p ON p.student=s.student
            GROUP BY s.student
            ORDER BY points DESC, accepted DESC, s.student
        """).fetchall()
    scores = {r["student"]: dict(r) for r in rows}
    return [
        scores.get(s, {"student": s, "points": 0, "accepted": 0})
        for s in STUDENTS
    ]

def get_report_table():
    with connect() as con:
        rows = con.execute("""
            SELECT a.task_date AS 'Күні',
                   a.student AS 'Оқушы',
                   a.title AS 'Тапсырма',
                   COALESCE(r.status,'Жіберілмеген') AS 'Мәртебесі',
                   COALESCE(r.note,'') AS 'Түсініктеме',
                   COALESCE(r.submitted_at,'') AS 'Жіберілген уақыты',
                   COALESCE(r.teacher_comment,'') AS 'Мұғалім пікірі',
                   COALESCE(p.score,0) AS 'Ұпай'
            FROM assignments a
            LEFT JOIN reports r ON r.assignment_id=a.id
            LEFT JOIN points p ON p.report_id=r.id
            ORDER BY a.task_date DESC, a.student
        """).fetchall()
    return pd.DataFrame([dict(r) for r in rows])

init_db()
today = date.today()
create_daily_tasks(today)

# ---------------- Дизайн ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #effaf1 0%, #ffffff 48%);
}
[data-testid="stSidebar"] { background: #e4f4e7; }
.hero {
    background: linear-gradient(110deg, #14532d, #2e7d32);
    padding: 24px;
    border-radius: 18px;
    color: white;
    margin-bottom: 18px;
}
.hero h1 { color: white; margin: 0; }
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #d9eadc;
    padding: 12px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
    <h1>🌿 Эко-мектеп AI</h1>
    <p>«Табиғатты бірге қорғайық!»</p>
    <p>7А сыныбы · 2026–2027 оқу жылы</p>
    <p>Сынып жетекшісі: {TEACHER}</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "📍 Бөлімді таңдаңыз",
    [
        "🏡 Басты бет",
        "📸 Фотоесеп жіберу",
        "🏆 Оқушылар рейтингі",
        "👩‍🏫 Мұғалім бөлімі",
        "📊 Есептер"
    ]
)
st.sidebar.markdown("---")
st.sidebar.caption("Әр дұрыс қабылданған фотоесепке 10 ұпай беріледі.")

# ---------------- Басты бет ----------------
if page == "🏡 Басты бет":
    st.subheader("🌱 Бүгінгі экологиялық тапсырмалар")
    st.write(f"Күні: **{today.strftime('%d.%m.%Y')}**")
    tasks_today = get_assignments(today.isoformat())

    for item in tasks_today:
        with st.container(border=True):
            st.markdown(f"### 👤 {item['student']}")
            st.markdown(f"**{item['title']}**")
            st.write(item["task"])
            status = item.get("status")
            if status == "Қабылданды":
                st.success("Фотоесеп қабылданды · 10 ұпай")
            elif status == "Күтуде":
                st.info("Фотоесеп мұғалімнің тексеруін күтуде")
            elif status == "Қайта тапсыру":
                st.warning("Қайта тапсыру қажет")
            else:
                st.caption("Фотоесеп әлі жіберілмеген.")

    with connect() as con:
        total_tasks = con.execute("SELECT COUNT(*) n FROM assignments").fetchone()["n"]
        total_reports = con.execute("SELECT COUNT(*) n FROM reports").fetchone()["n"]
        accepted = con.execute("SELECT COUNT(*) n FROM reports WHERE status='Қабылданды'").fetchone()["n"]
        pending = con.execute("SELECT COUNT(*) n FROM reports WHERE status='Күтуде'").fetchone()["n"]
        points_total = con.execute("SELECT COALESCE(SUM(score),0) n FROM points").fetchone()["n"]

    st.subheader("📈 Жоба көрсеткіштері")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Тапсырма", total_tasks)
    c2.metric("Фотоесеп", total_reports)
    c3.metric("Қабылданған", accepted)
    c4.metric("Күтуде", pending)
    c5.metric("Жалпы ұпай", points_total)

# ---------------- Фотоесеп жіберу ----------------
elif page == "📸 Фотоесеп жіберу":
    st.subheader("📸 Орындалған тапсырмаға фотоесеп жіберу")
    today_tasks = get_assignments(today.isoformat())

    if not today_tasks:
        st.info("Бүгін тапсырма тағайындалмаған.")
    else:
        student = st.selectbox(
            "Оқушының аты-жөні",
            [r["student"] for r in today_tasks]
        )
        item = next(r for r in today_tasks if r["student"] == student)

        st.markdown(f"### {item['title']}")
        st.write(item["task"])

        if item.get("status") == "Қабылданды":
            st.success("Бұл тапсырманың фотоесебі қабылданған. Ұпай есептелген.")
        else:
            with st.form("photo_form", clear_on_submit=True):
                note = st.text_area(
                    "Тапсырманы қалай орындадың?",
                    placeholder="Қысқаша түсініктеме жаз..."
                )
                photo = st.file_uploader(
                    "Фотоесепті таңда",
                    type=["jpg", "jpeg", "png", "webp"]
                )
                send = st.form_submit_button(
                    "📤 Фотоесепті жіберу",
                    use_container_width=True
                )

            if send:
                if photo is None:
                    st.error("Алдымен фотоесеп жүктеңіз.")
                else:
                    saved = submit_report(
                        item["id"], student, today.isoformat(), note, photo
                    )
                    if saved:
                        st.success("Фотоесеп сәтті жіберілді! Мұғалім тексергеннен кейін ұпай беріледі.")
                        st.rerun()
                    else:
                        st.warning("Бұл тапсырма бұрын қабылданған.")

# ---------------- Рейтинг ----------------
elif page == "🏆 Оқушылар рейтингі":
    st.subheader("🏆 7А сыныбының экологиялық рейтингі")
    ranking = get_ranking()
    df = pd.DataFrame(ranking).rename(columns={
        "student": "Оқушы",
        "points": "Ұпай",
        "accepted": "Қабылданған фотоесеп"
    })
    df.insert(0, "Орын", range(1, len(df) + 1))
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption("Ұпай тек мұғалім қабылдаған фотоесепке беріледі.")

# ---------------- Мұғалім бөлімі ----------------
elif page == "👩‍🏫 Мұғалім бөлімі":
    st.subheader("👩‍🏫 Мұғалімнің басқару бөлімі")
    st.caption("Бастапқы құпиясөз: eco2026. Оны өзгерту ұсынылады.")
    password = st.text_input("Мұғалім құпиясөзі", type="password")

    if password != TEACHER_PASSWORD:
        st.info("Мұғалім бөлімін ашу үшін құпиясөзді енгізіңіз.")
    else:
        st.success(f"Қош келдіңіз, {TEACHER}!")
        all_items = [x for x in get_assignments() if x.get("report_id")]
        filter_status = st.selectbox(
            "Есептерді сүзу",
            ["Барлығы", "Күтуде", "Қабылданды", "Қайта тапсыру"]
        )
        if filter_status != "Барлығы":
            all_items = [x for x in all_items if x.get("status") == filter_status]

        if not all_items:
            st.info("Тексерілетін фотоесеп жоқ.")
        for item in all_items:
            with st.container(border=True):
                st.markdown(f"### {item['student']}")
                st.write(f"Күні: {item['task_date']}")
                st.write(f"Тапсырма: {item['title']}")
                st.write(f"Оқушы түсініктемесі: {item.get('note') or '—'}")
                st.write(f"Мәртебесі: {item.get('status') or '—'}")

                photo_path = item.get("photo_path")
                if photo_path and Path(photo_path).exists():
                    st.image(photo_path, caption="Оқушының фотоесебі", use_container_width=True)

                report_id = item["report_id"]
                comment = st.text_input(
                    "Мұғалім пікірі",
                    value=item.get("teacher_comment") or "",
                    key=f"comment_{report_id}"
                )
                left, right = st.columns(2)
                with left:
                    if st.button(
                        "✅ Қабылдау және 10 ұпай беру",
                        key=f"accept_{report_id}",
                        use_container_width=True
                    ):
                        review_report(report_id, "Қабылданды", comment)
                        st.success("Фотоесеп қабылданды. Ұпай бір рет қана қосылады.")
                        st.rerun()
                with right:
                    if st.button(
                        "🔄 Қайта тапсыру",
                        key=f"redo_{report_id}",
                        use_container_width=True
                    ):
                        review_report(report_id, "Қайта тапсыру", comment)
                        st.warning("Қайта тапсыру белгіленді.")
                        st.rerun()

# ---------------- Есептер ----------------
elif page == "📊 Есептер":
    st.subheader("📊 Жоба бойынша есеп")
    df = get_report_table()

    if df.empty:
        st.info("Есеп әзірге бос. Күнделікті тапсырмалар тағайындалған сайын деректер жиналады.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Барлық есепті CSV түрінде жүктеу",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"eko_mektep_{today.isoformat()}.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("### 📅 Айлық статистика")
        month_df = df.copy()
        month_df["Күні"] = pd.to_datetime(month_df["Күні"], errors="coerce")
        month_df["Ай"] = month_df["Күні"].dt.strftime("%Y-%m")
        monthly = month_df.groupby("Ай", dropna=True).agg(
            Тапсырма=("Оқушы", "count"),
            Қабылданған=("Мәртебесі", lambda x: (x == "Қабылданды").sum()),
            Ұпай=("Ұпай", "sum")
        ).reset_index()
        st.dataframe(monthly, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("🌍 **Табиғатты қорғау — әрқайсымыздың міндетіміз!**")
