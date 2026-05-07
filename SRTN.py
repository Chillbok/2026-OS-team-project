class Process:
    # 프로세스가 무슨 일을 하는지 알 수 있게 추가
    def __init__(self, pid, arrival, burst, task_type="NORMAL"):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remainingTime = burst
        self.task_type = task_type
        self.isCompleted = False


# 작업 타입에 따라 어떤 코어에 들어가야 하는지 판별하는 함수
def get_role(task_type):
    if task_type in ["EMERGENCY_BRAKE", "AIRBAG", "ABS"]: return "EMERGENCY"
    if task_type in ["ENGINE", "STEERING", "LANE_KEEP", "COLLISION_AVOID"]: return "CONTROL"
    return "NORMAL"


def run_srtn_scheduler(task_list):
    # 코어 생성 시 담당 구역을 명확히 부여 (보고서 3.2.2 기준)
    cores = [
        {"id": "P0", "perf": 2, "pwr": 3, "current": None, "idle": True, "role": "EMERGENCY"},
        {"id": "P1", "perf": 2, "pwr": 3, "current": None, "idle": True, "role": "CONTROL"},
        {"id": "E0", "perf": 1, "pwr": 1, "current": None, "idle": True, "role": "NORMAL"},
        {"id": "E1", "perf": 1, "pwr": 1, "current": None, "idle": True, "role": "NORMAL"}
    ]

    ABT = {c['id']: [] for c in cores}
    task_list.sort(key=lambda x: x.arrivalTime)
    toDoTasks = []
    current_time = 0
    completed_processes = 0
    total_power = 0

    while completed_processes < len(task_list):
        for p in task_list:
            if current_time == p.arrivalTime:
                toDoTasks.append(p)

        # 현재 코어에서 실행 중인 작업들을 큐로 회수
        for core in cores:
            if core['current']:
                toDoTasks.append(core['current'])
                core['current'] = None

        # 남은 시간이 짧은 순으로 줄 세우기 
        toDoTasks.sort(key=lambda x: x.remainingTime)

        # 3. 코어 재할당 시 "담당 구역의 일"만 가져감
        for core in cores:
            for task in toDoTasks:
                if get_role(task.task_type) == core['role']:
                    core['current'] = task
                    toDoTasks.remove(task)
                    break  # 내 일을 찾았으니 다음 코어로 넘어감

        # 1초 동안 실행 및 전력 계산 
        for core in cores:
            if core['current']:
                task = core['current']

                if core['idle']:
                    total_power += (0.5 if "P" in core['id'] else 0.1)
                    core['idle'] = False

                total_power += core['pwr']

                work = core['perf'] if task.remainingTime >= core['perf'] else task.remainingTime
                task.remainingTime -= work
                ABT[core['id']].append(task.pid)  

                if task.remainingTime == 0:
                    task.isCompleted = True
                    completed_processes += 1
                    core['current'] = None
            else:
                ABT[core['id']].append("idle")
                core['idle'] = True

        current_time += 1

    return ABT, total_power


# 시간 계산 및 출력 함수 
def CompletionTimeChecker(Process_obj, ABT_list):
    completionTime = 0
    for core_id in ABT_list:
        for idx in range(len(ABT_list[core_id]) - 1, -1, -1):
            if ABT_list[core_id][idx] == Process_obj.pid:
                completionTime = max(completionTime, idx + 1)
                break
    return completionTime


def Output(Process_obj, ABT_list):
    completionTime = CompletionTimeChecker(Process_obj, ABT_list)
    turnaroundTime = completionTime - Process_obj.arrivalTime
    waitingTime = turnaroundTime - Process_obj.burstTime
    ntt = turnaroundTime / Process_obj.burstTime if Process_obj.burstTime > 0 else 0
    return waitingTime, turnaroundTime, ntt


def print_gantt(gantt):
    print("\n[SRTN Gantt Chart]")
    for core, timeline in gantt.items():
        print(f"{core}: ", end="")
        for t in timeline:
            print(f"|{str(t).center(4)}", end="")
        print("|")
