import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from OS_project import Process
from OS_project import scheduler
from HRRN import HRRN
from HRRN import Process as HRRNProcess
from FCFS import FCFS
from FCFS import Process as FCFSProcess
from RR import RR
from RR import Process as RRProcess
from SPN import SPN, Process as SPNProcess
from SRTN import run_srtn_scheduler as SRTN, Process as SRTNProcess


root = tk.Tk()

root.title("Process Scheduling Simulator")
root.geometry("1400x800")
process_data = []

PID_COLORS = {

    "1": "#FF8A80",
    "2": "#FFD180",
    "3": "#FFFF8D",
    "4": "#CCFF90",
    "5": "#A7FFEB",

    "6": "#80D8FF",
    "7": "#82B1FF",
    "8": "#B388FF",
    "9": "#F8BBD0",
    "10": "#D7CCC8",

    "11": "#DCEDC8",
    "12": "#CFD8DC",
    "13": "#FFAB91",
    "14": "#B2DFDB",
    "15": "#D1C4E9",

    "idle": "#E0E0E0"
}

TASK_TYPES = [
    "EMERGENCY_BRAKE",
    "COLLISION_AVOID",
    "STEERING",
    "LANE_KEEP",
    "CRUISE_CONTROL",
    "INFOTAINMENT"
]

TASK_COLORS = {

    "EMERGENCY_BRAKE": "#FF5252",

    "COLLISION_AVOID": "#FF9800",

    "STEERING": "#42A5F5",

    "LANE_KEEP": "#81D4FA",

    "CRUISE_CONTROL": "#66BB6A",

    "INFOTAINMENT": "#BA68C8",

    "idle": "#E0E0E0"
}

def update_task_type_state(event=None):

    algorithm = algorithm_var.get()

    # Auto Driving만 활성화
    if algorithm == "Auto Driving":

        task_type_combo.config(
            state="readonly"
        )

        task_type_combo.set(
            "INFOTAINMENT"
        )

    # 나머지는 비활성
    else:

        task_type_combo.set("")

        task_type_combo.config(
            state="disabled"
        )

def add_process():

    pid = pid_entry.get()
    arrival = arrival_entry.get()
    burst = burst_entry.get()
    task_type = task_type_var.get()

    # 빈칸 체크
    if not pid or not arrival or not burst:
        return

    # 숫자 변환 예외 처리
    try:
        arrival = int(arrival)
        burst = int(burst)

    except ValueError:
        return
    
    if len(process_data) >= 15:

        messagebox.showerror(
            "Error",
            "Maximum 15 processes allowed."
        )
        return

    for process in process_data:

        if process["pid"] == pid:
            messagebox.showerror(
                "Error",
                "PID already exists."
            )
            return
        
    # 데이터 저장
    process_data.append({
        "pid": pid,
        "arrival": arrival,
        "burst": burst,
        "task_type": task_type
    })

    # Treeview 추가
    process_table.insert(
        "",
        "end",
        values=(pid, arrival, burst, task_type)
    )

    # 입력창 초기화
    pid_entry.delete(0, tk.END)
    arrival_entry.delete(0, tk.END)
    burst_entry.delete(0, tk.END)
    

def delete_process():

    selected = process_table.selection()

    if not selected:
        return

    for item in selected:

        values = process_table.item(item, "values")

        pid = values[0]

        # process_data 제거
        for process in process_data:

            if process["pid"] == pid:
                process_data.remove(process)
                break

        # Treeview 제거
        process_table.delete(item)

def clear_processes():

    process_data.clear()

    for item in process_table.get_children():
        process_table.delete(item)

def draw_gantt(gantt, algorithm):
    

    canvas.delete("all")  # 기존 내용 지우기

    cell_width = 30
    cell_height = 28

    x_offset = 80
    y_offset = 10

    min_start = 0

    all_timelines = list(gantt.values())

    while True:

        removable = True

        for timeline in all_timelines:

            if min_start >= len(timeline):
                removable = False
                break

            if timeline[min_start] != "idle":
                removable = False
                break

        if removable:
            min_start += 1
        else:
            break

    for row, (core_name, timeline) in enumerate(gantt.items()):

        y = y_offset + row * (cell_height + 5)

        # 코어 이름
        canvas.create_text(
            x_offset - 10,
            y + cell_height // 2,
            text=core_name,
            anchor="e"
        )

        for col, pid in enumerate(timeline[min_start:]):

            x = x_offset + col * cell_width

            if str(pid) == "idle" or str(pid) == "0":

                color = TASK_COLORS["idle"]

            else:

                if algorithm == "Auto Driving":

                    task_type = "INFOTAINMENT"

                    for p in process_data:

                        if str(p["pid"]) == str(pid):

                            task_type = p["task_type"]
                            break

                    color = TASK_COLORS[task_type]

                else:

                    color = PID_COLORS.get(
                        str(pid),
                        "#FFFFFF"
                    )

            # 박스
            canvas.create_rectangle(
                x,
                y,
                x + cell_width,
                y + cell_height,
                fill=color
            )

            # pid
            canvas.create_text(
                x + cell_width // 2,
                y + cell_height // 2,
                text=str(pid)
            )

            # 시간
            canvas.create_text(
                x,
                y + cell_height + 5,
                text=str(col + min_start),
                anchor="n"
            )
            canvas.config(
                scrollregion=canvas.bbox("all")
            )

def get_core_counts():

    p_count = 0
    e_count = 0

    for core in core_vars:

        if core.get() == "P":

            p_count += 1

        else:

            e_count += 1

    return p_count, e_count

def run_scheduler():

    algorithm = algorithm_var.get()
    print("Selected Algorithm:", algorithm)
    tasks = []
    gantt = None
    processes = None
    power = 0

    if algorithm == "HRRN":

        hrrn_tasks = []

        for p in process_data:

            hrrn_tasks.append(
                HRRNProcess(
                    p["pid"],
                    p["arrival"],
                    p["burst"]
                )
            )

        p_count, e_count = get_core_counts()
        processes, gantt, power = HRRN(
            hrrn_tasks,
            p_count=p_count,
            e_count=e_count
        )

    elif algorithm == "Auto Driving":
        for p in process_data:

            tasks.append(
                Process(
                    p["pid"],
                    p["arrival"],
                    p["burst"],
                    p["task_type"]
                )
            )
        p_count, e_count = get_core_counts()
        if algorithm == "Auto Driving" and p_count == 0:

            messagebox.showerror(
                "Core Error",
                "자율 주행은 적어도 하나의 P-Core가 필요합니다."
            )

            return
        gantt, processes, power = scheduler(tasks, p_count, e_count)

    elif algorithm == "FCFS":

        fcfs_tasks = []

        for p in process_data:

            fcfs_tasks.append(
                FCFSProcess(
                    p["pid"],
                    p["arrival"],
                    p["burst"]
                )
            )

        p_count, e_count = get_core_counts()
        processes, gantt, power = FCFS(
            fcfs_tasks,
            coreTypes=core_vars
        )

    elif algorithm == "RR":

        rr_tasks = []

        for p in process_data:

            rr_tasks.append(
                RRProcess(
                    p["pid"],
                    p["arrival"],
                    p["burst"]
                )
            )

        quantum=int(quantum_entry.get())
        p_count, e_count = get_core_counts()
        processes, gantt, power = RR(
            rr_tasks,
            quantum=quantum,
            coreTypes=core_vars
        )
    
    elif algorithm == "SPN":
        tasks = [SPNProcess(p["pid"], p["arrival"], p["burst"]) for p in process_data]
        p_count, e_count = get_core_counts()
        processes, gantt, power = SPN(tasks, p_count, e_count)

    elif algorithm == "SRTN":
        tasks = [SRTNProcess(p["pid"], p["arrival"], p["burst"]) for p in process_data]
        p_count, e_count = get_core_counts()
        gantt, power = SRTN(tasks, p_count, e_count)
        processes = tasks

    if gantt is not None:

        print("\n========== RESULT ==========")

        print("\n[Gantt Chart]")

        for core, timeline in gantt.items():

            print(f"{core}: ", end="")

            for t in timeline:

                print(f"|{t}", end="")

            print("|")

        print("\n[Process Result]")

        for p in processes:
            actual_burst = 0 # 실제 실행 시간(Tick)을 저장할 변수 초기화
        
        # 1. Gantt 차트의 모든 코어(P, E) 타임라인을 전부 뒤집니다.
            for timeline in gantt.values():
                for t in timeline:
                # 2. 현재 프로세스의 PID와 일치하는 기록(칸)이 있으면 카운트 증가
                    if str(t) == str(p.pid):
                        actual_burst += 1
                    
        # (예외 처리: 간트 차트에 기록이 없는 치명적 오류 등 대비용 초기화)
            if actual_burst == 0:
                actual_burst = p.burst

        # 결과 출력 (터미널 및 UI 테이블)
            tt = p.finish_time - p.arrival
            wt = tt - actual_burst
            ntt = tt / actual_burst if actual_burst > 0 else 0

            print(
                f"{p.pid} | WT={wt} "
                f"| TT={tt} "
                f"| NTT={ntt:.2f}"
            )

        print(f"\nTotal Power: {power}")

        power_var.set(
            f"전체 사용 전력: {power}W"
        )

        draw_gantt(gantt, algorithm)

        for item in result_table.get_children():

            result_table.delete(item)

        for p in processes:

            actual_burst = 0 # 실제 실행 시간(Tick)을 저장할 변수 초기화
        
        # 1. Gantt 차트의 모든 코어(P, E) 타임라인을 전부 뒤집니다.
            for timeline in gantt.values():
                for t in timeline:
                # 2. 현재 프로세스의 PID와 일치하는 기록(칸)이 있으면 카운트 증가
                    if str(t) == str(p.pid):
                        actual_burst += 1
                    
        # (예외 처리: 간트 차트에 기록이 없는 치명적 오류 등 대비용 초기화)
            if actual_burst == 0:
                actual_burst = p.burst

        # 결과 출력 (터미널 및 UI 테이블)
            tt = p.finish_time - p.arrival
            wt = tt - actual_burst
            ntt = tt / actual_burst if actual_burst > 0 else 0

            result_table.insert(
                "",
                "end",
                values=(
                    p.pid,
                    wt,
                    tt,
                    f"{ntt:.2f}"
                )
            )


# 상단 프레임
top_frame = tk.Frame(root)
top_frame.pack(fill="x", padx=10, pady=10)

# 알고리즘 선택
tk.Label(
    top_frame,
    text="Algorithm"
).pack(side="left")

algorithm_var = tk.StringVar()

algorithm_combo = ttk.Combobox(
    top_frame,
    textvariable=algorithm_var,
    values=[
        "FCFS",
        "RR",
        "SPN",
        "SRTN",
        "HRRN",
        "Auto Driving"
    ],
    width=15,
    state="readonly"
)

algorithm_combo.current(0)
algorithm_combo.pack(side="left", padx=5)
algorithm_combo.bind(
    "<<ComboboxSelected>>",
    update_task_type_state
)

# RR Quantum
tk.Label(
    top_frame,
    text="Quantum"
).pack(side="left", padx=(20, 0))

quantum_entry = tk.Entry(
    top_frame,
    width=5
)

quantum_entry.insert(0, "3")
quantum_entry.pack(side="left")

# 메인 영역
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# 좌측 패널
left_frame = tk.Frame(
    main_frame,
    width=500
)

left_frame.pack_propagate(False)
left_frame.pack(side="left", fill="y", padx=10)

# 프로세스 테이블
process_table = ttk.Treeview(
    left_frame,
    columns=("PID", "AT", "BT", "TYPE"),
    show="headings",
    height=15
)

process_table.heading("PID", text="Process")
process_table.heading("AT", text="Arrival")
process_table.heading("BT", text="Burst")
process_table.heading("TYPE", text="Task Type")
process_table.column("PID", width=80, anchor="center")
process_table.column("AT", width=80, anchor="center")
process_table.column("BT", width=80, anchor="center")
process_table.column("TYPE", width=200, anchor="center")

process_table.pack()

# 프로세스 입력
input_frame = tk.LabelFrame(
    left_frame,
    text="Add Process"
)

input_frame.pack(fill="x", pady=10)

tk.Label(input_frame, text="PID").pack()

pid_entry = tk.Entry(input_frame)
pid_entry.pack(fill="x")

tk.Label(input_frame, text="Arrival Time").pack()

arrival_entry = tk.Entry(input_frame)
arrival_entry.pack(fill="x")

tk.Label(input_frame, text="Burst Time").pack()

burst_entry = tk.Entry(input_frame)
burst_entry.pack(fill="x")

tk.Label(input_frame, text="Task Type").pack()

task_type_var = tk.StringVar()

task_type_combo = ttk.Combobox(
    input_frame,
    textvariable=task_type_var,
    values=TASK_TYPES,
    state="readonly"
)

task_type_combo.current(5)  # INFOTAINMENT 기본값

task_type_combo.pack(fill="x")

# 우측 패널
add_button = tk.Button(
    input_frame,
    text="Add",
    command=add_process
)

add_button.pack(fill="x", pady=5)

delete_button = tk.Button(
    input_frame,
    text="Delete Selected",
    bg="#B71C1C",
    fg="white",
    command=delete_process
)

clear_button = tk.Button(
    input_frame,
    text="Clear All",
    bg="#616161",
    fg="white",
    command=clear_processes
)

# 실행 버튼
run_button = tk.Button(
    top_frame,
    text="RUN",
    bg="#607D8B",
    fg="white",
    width=10,
    height=2,
    command=run_scheduler
)

clear_button.pack(fill="x", pady=5)
delete_button.pack(fill="x", pady=5)
run_button.pack(side="right")

right_frame = tk.Frame(main_frame)
right_frame.pack(side="left", fill="both", expand=True)

# 코어 설정
core_frame = tk.LabelFrame(
    right_frame,
    text="Processor"
)

core_frame.pack(fill="x")
core_vars = []

for i in range(4):

    core_box = tk.LabelFrame(
        core_frame,
        text=f"Core {i}",
        width=150,
        height=150
    )

    core_box.pack(side="left", padx=5, pady=5)

    core_type = tk.StringVar(value="P")
    core_vars.append(core_type)

    tk.Radiobutton(
        core_box,
        text="P-Core",
        variable=core_type,
        value="P"
    ).pack(anchor="w")

    tk.Radiobutton(
        core_box,
        text="E-Core",
        variable=core_type,
        value="E"
    ).pack(anchor="w")

# Gantt Chart 영역
power_var = tk.StringVar()

power_var.set("전체 사용 전력: 0W")

power_label = tk.Label(
    right_frame,
    textvariable=power_var,
    font=("Arial", 11, "bold"),
    anchor="w"
)

power_label.pack(
    fill="x",
    padx=10,
    pady=(5, 0)
)

gantt_frame = tk.LabelFrame(
    right_frame,
    text="Gantt Chart"
)

gantt_frame.pack(fill="both", expand=True, pady=10)
result_frame = tk.LabelFrame(
    right_frame,
    text="Scheduling Result"
)

result_frame.pack(
    fill="x",
    padx=5,
    pady=5
)


result_table = ttk.Treeview(
    result_frame,
    columns=("PID", "WT", "TT", "NTT"),
    show="headings",
    height=6
)

result_table.heading("PID", text="Process")
result_table.heading("WT", text="WT")
result_table.heading("TT", text="TT")
result_table.heading("NTT", text="NTT")

result_table.column("PID", width=100, anchor="center")
result_table.column("WT", width=80, anchor="center")
result_table.column("TT", width=80, anchor="center")
result_table.column("NTT", width=100, anchor="center")

result_table.pack(fill="x")


canvas = tk.Canvas(
    gantt_frame,
    bg="white",
    height=300
)

# 가로 스크롤바
x_scrollbar = tk.Scrollbar(
    gantt_frame,
    orient="horizontal",
    command=canvas.xview
)

# 세로 스크롤바 (추천)
y_scrollbar = tk.Scrollbar(
    gantt_frame,
    orient="vertical",
    command=canvas.yview
)

# canvas와 scrollbar 연결
canvas.configure(
    xscrollcommand=x_scrollbar.set,
    yscrollcommand=y_scrollbar.set
)

# 배치
x_scrollbar.pack(side="bottom", fill="x")

y_scrollbar.pack(side="right", fill="y")

canvas.pack(
    side="left",
    fill="both",
    expand=True
)

canvas.pack(fill="both", expand=True)
update_task_type_state()
root.mainloop()