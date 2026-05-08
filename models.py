# ==========================================
# models.py (자율주행 프로세스-코어 알고리즘 전용)
# ==========================================

class Process:
    def __init__(self, pid, arrival, burst, task_type="NORMAL"):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.task_type = task_type
        self.finish_time = 0

class Core:
    def __init__(self, name, performance, run_power, wake_power, role):
        self.name = name
        self.performance = performance
        self.run_power = run_power
        self.wake_power = wake_power
        self.role = role
        self.current = None
        self.time_slice = 0
        self.was_idle = True

def get_role(task_type):
    if task_type in ["EMERGENCY_BRAKE", "AIRBAG", "ABS"]: return "EMERGENCY"
    if task_type in ["ENGINE", "STEERING", "LANE_KEEP", "COLLISION_AVOID"]: return "CONTROL"
    return "NORMAL"

def create_cores():
    return [
        Core("P0", 2, 3, 0.5, "EMERGENCY"),
        Core("P1", 2, 3, 0.5, "CONTROL"),
        Core("E0", 1, 1, 0.1, "NORMAL"),
        Core("E1", 1, 1, 0.1, "NORMAL")
    ]

#  자율주행 규칙(role)에 맞춰 필터링!
def get_eligible_tasks(core, ready_queue):
    return [p for p in ready_queue if get_role(p.task_type) == core.role]

def CompletionTimeChecker(process, gantt):
    temp = 0
    for key in gantt:
        for item in range(len(gantt[key]) - 1, -1, -1):
            if gantt[key][item] == process.pid:
                temp = max(temp, item + 1)
                break
    return temp

def Output(process, gantt):
    completionTime = CompletionTimeChecker(process, gantt)
    turnaroundTime = completionTime - process.arrival
    waitingTime = turnaroundTime - process.burst
    NTT = turnaroundTime / process.burst if process.burst > 0 else 0
    return waitingTime, turnaroundTime, NTT

def print_gantt(gantt, title="Gantt Chart"):
    print(f"\n[{title}]")
    for core, timeline in gantt.items():
        print(f"{core.ljust(4)}: ", end="")
        for t in timeline:
            print(f"|{str(t).center(4)}", end="")
        print("|")
