import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class Process:

    def __init__(self, pid, arrival, burst):

        self.pid = pid
        self.arrival = arrival
        self.burst = burst

root = tk.Tk()

root.title("Process Scheduling Simulator")
root.geometry("1400x800")
process_data = []

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

left_frame = tk.Frame(main_frame)
left_frame.pack(side="left", fill="y", padx=10)

# 프로세스 테이블
process_table = ttk.Treeview(
    left_frame,
    columns=("PID", "AT", "BT"),
    show="headings",
    height=15
)

process_table.heading("PID", text="Process")
process_table.heading("AT", text="Arrival")
process_table.heading("BT", text="Burst")

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

def add_process():

    pid = pid_entry.get()
    arrival = arrival_entry.get()
    burst = burst_entry.get()

    # 빈칸 체크
    if not pid or not arrival or not burst:
        return

    # 숫자 변환 예외 처리
    try:
        arrival = int(arrival)
        burst = int(burst)

    except ValueError:
        return
    
    for process in process_data:

        if process["pid"] == pid:
            messagebox.showerror(
                "Error",
                "PID already exists."
            )   
            return

        if len(process_data) >= 15:

            messagebox.showerror(
                "Error",
                "Maximum 15 processes allowed."
            )
            return
        
    # 데이터 저장
    process_data.append({
        "pid": pid,
        "arrival": arrival,
        "burst": burst
    })

    # Treeview 추가
    process_table.insert(
        "",
        "end",
        values=(pid, arrival, burst)
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

def run_scheduler():

    algorithm = algorithm_var.get()

    tasks = []

    # Process 객체 변환
    for p in process_data:

        tasks.append(
            Process(
                p["pid"],
                p["arrival"],
                p["burst"]
            )
        )

    print("Selected Algorithm:", algorithm)

    print("Tasks:")

    for task in tasks:

        print(
            task.pid,
            task.arrival,
            task.burst
        )

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

for i in range(4):

    core_box = tk.LabelFrame(
        core_frame,
        text=f"Core {i}",
        width=150,
        height=150
    )

    core_box.pack(side="left", padx=5, pady=5)

    core_type = tk.StringVar(value="P")

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

gantt_frame = tk.LabelFrame(
    right_frame,
    text="Gantt Chart"
)

gantt_frame.pack(fill="both", expand=True, pady=10)

canvas = tk.Canvas(
    gantt_frame,
    bg="white",
    height=300
)

canvas.pack(fill="both", expand=True)

root.mainloop()