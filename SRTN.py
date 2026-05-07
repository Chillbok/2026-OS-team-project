class Process:
    def __init__(self, processID, arrivalTime, burstTime):
        self.processID = processID
        self.arrivalTime = arrivalTime
        self.burstTime = burstTime
        # SRTN을 위해 추가된 남은 시간 추적용 변수
        self.remainingTime = burstTime
        self.isCompleted = False


def run_srtn_scheduler(task_list):
    """SRTN 알고리즘 """
    # 코어 세팅
    cores = [
        {"id": "P0", "perf": 2, "pwr": 3, "current": None, "idle": True},
        {"id": "P1", "perf": 2, "pwr": 3, "current": None, "idle": True},
        {"id": "E0", "perf": 1, "pwr": 1, "current": None, "idle": True},
        {"id": "E1", "perf": 1, "pwr": 1, "current": None, "idle": True}
    ]

    ABT = {c["id"]: [] for c in cores}
    task_list.sort(key=lambda x: x.arrivalTime)
    toDoTasks = []
    current_time = 0
    completed_processes = 0
    total_power = 0
    total_processes = len(task_list)

    while completed_processes < total_processes:
        # task가 도착했는지 확인
        for i in range(len(task_list)):
            if current_time == task_list[i].arrivalTime:
                toDoTasks.append(task_list[i])

        # 선점형: 코어들이 하던 일을 일단 대기열에 반납
        for core in cores:
            if core["current"]:
                toDoTasks.append(core["current"])
                core["current"] = None

        # 남은 시간 순 정렬
        if toDoTasks:
            toDoTasks.sort(key=lambda x: x.remainingTime)

        # 코어 할당
        for core in cores:
            if toDoTasks:
                core["current"] = toDoTasks.pop(0)

        # 1초 진행 및 전력/간트차트 기록
        for core in cores:
            if core["current"]:
                srTask = core["current"]

                # 시동 전력 계산
                if core["idle"]:
                    total_power += 0.5 if "P" in core["id"] else 0.1
                    core["idle"] = False

                total_power += core["pwr"]  # 유지 전력

                # 코어 성능만큼 남은 시간 차감
                work = core["perf"] if srTask.remainingTime >= core["perf"] else srTask.remainingTime
                srTask.remainingTime -= work
                ABT[core["id"]].append(srTask.processID)

                # 프로세스 완료 확인
                if srTask.remainingTime == 0:
                    srTask.isCompleted = True
                    completed_processes += 1
                    core["current"] = None
            else:
                ABT[core["id"]].append("idle")
                core["idle"] = True

        current_time += 1

    return ABT, total_power


def CompletionTimeChecker(Process_obj, ABT_dict):
    completionTime = 0
    for core_id in ABT_dict:
        for idx in range(len(ABT_dict[core_id]) - 1, -1, -1):
            if ABT_dict[core_id][idx] == Process_obj.processID:
                completionTime = max(completionTime, idx + 1)
                break
    return completionTime


def Output(Process_obj, ABT_dict):
    """TT, WT, NTT 결과 계산"""
    completionTime = CompletionTimeChecker(Process_obj, ABT_dict)
    turnaroundTime = completionTime - Process_obj.arrivalTime
    waitingTime = turnaroundTime - Process_obj.burstTime
    ntt = turnaroundTime / Process_obj.burstTime if Process_obj.burstTime > 0 else 0

    return waitingTime, turnaroundTime, ntt


def print_gantt_chart(ABT_dict):
    print("\n[Gantt Chart]")
    for core, timeline in ABT_dict.items():
        print(f"{core}: ", end="")
        for p in timeline:
            print(f"|{str(p).center(4)}", end="")
        print("|")


# 동작확인 (순수하게 시간과 길이만 테스트)
if __name__ == "__main__":
    tasks = []
    tasks.append(Process("P1", 0, 3))
    tasks.append(Process("P2", 1, 7))
    tasks.append(Process("P3", 3, 2))
    tasks.append(Process("P4", 5, 5))
    tasks.append(Process("P5", 6, 3))

    print("순수 SRTN 멀티코어 스케줄링 시뮬레이션...")
    ABT, total_power = run_srtn_scheduler(tasks)

    print("\n[프로세스별 결과]")
    for i in tasks:
        WT, TT, NTT = Output(i, ABT)
        print(f"{i.processID:3s}의 WT:{WT:2d}, TT:{TT:2d}, NTT:{NTT:.2f}")

    print_gantt_chart(ABT)
    print(f"\n▶ 시스템 총 소비 전력: {total_power}W")
