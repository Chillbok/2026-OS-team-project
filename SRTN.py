class Process:
    def __init__(self, processID, arrivalTime, burstTime):
        self.processID = processID
        self.arrivalTime = arrivalTime
        self.burstTime = burstTime
        self.remainingTime = burstTime  
        self.completionTime = 0  # [피드백 반영] 완료 시간 기록용 변수 추가
        self.isCompleted = False

def run_srtn_scheduler(task_list):
    cores = [
        {"id": "P0", "perf": 2, "pwr": 3, "current": None, "idle": True},
        {"id": "P1", "perf": 2, "pwr": 3, "current": None, "idle": True},
        {"id": "E0", "perf": 1, "pwr": 1, "current": None, "idle": True},
        {"id": "E1", "perf": 1, "pwr": 1, "current": None, "idle": True}
    ]

    ABT = {c["id"]: [] for c in cores} 
    
    # [피드백 반영] 원본 리스트 보호를 위해 복사본 정렬 
    sorted_tasks = sorted(task_list, key=lambda x: x.arrivalTime)
    
    todo_tasks = []  # [피드백 5 반영] PEP 8 네이밍 규칙 적용
    
    current_time = 0
    completed_processes = 0
    total_power = 0
    total_processes = len(sorted_tasks)
    
    task_idx = 0  # [피드백 반영] 전체 순회를 막기 위한 인덱스 포인터

    while completed_processes < total_processes:
        new_arrival = False
        
        # [피드백  반영] 포인터를 사용하여 도착한 프로세스만 효율적으로 큐에 삽입
        while task_idx < total_processes and sorted_tasks[task_idx].arrivalTime <= current_time:
            todo_tasks.append(sorted_tasks[task_idx])
            task_idx += 1
            new_arrival = True  # 새로운 작업이 큐에 들어왔음을 표시
            
        # [피드백  반영] 매초 회수하지 않고, 새로운 프로세스가 도착했을 때만 코어 작업 선점
        if new_arrival:
            for core in cores:
                if core["current"]:
                    todo_tasks.append(core["current"])
                    core["current"] = None

        # 남은 시간 순 정렬
        if todo_tasks:
            todo_tasks.sort(key=lambda x: x.remainingTime)

        # 빈 코어에 작업 할당 (P코어부터 우선 배치됨)
        for core in cores:
            if core["current"] is None and todo_tasks:
                core["current"] = todo_tasks.pop(0)

        # 1초 진행 및 전력/간트차트 기록
        for core in cores:
            if core["current"]:
                srTask = core["current"]
                
                # 시동 전력 계산
                if core["idle"]:
                    total_power += 0.5 if "P" in core["id"] else 0.1
                    core["idle"] = False
                
                total_power += core["pwr"]

                # 코어 성능만큼 남은 시간 차감
                work = core["perf"] if srTask.remainingTime >= core["perf"] else srTask.remainingTime
                srTask.remainingTime -= work
                ABT[core["id"]].append(srTask.processID)

                # 프로세스 완료 확인
                if srTask.remainingTime == 0:
                    srTask.isCompleted = True
                    # [피드백 4 반영] 작업이 끝나는 즉시 객체에 완료 시간을 기록 (탐색 비용 제로)
                    srTask.completionTime = current_time + 1
                    completed_processes += 1
                    core["current"] = None
            else:
                ABT[core["id"]].append("idle")
                core["idle"] = True

        current_time += 1

    return ABT, total_power


# [피드백 반영] CompletionTimeChecker 함수 삭제

def Output(Process_obj):
    """TT, WT, NTT 결과 계산"""
    # ABT를 넘겨받아 탐색할 필요 없이, 객체에 저장된 완료 시간을 바로 꺼내 씀
    turnaroundTime = Process_obj.completionTime - Process_obj.arrivalTime
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

# =======================================================
# 동작확인 테스트
# =======================================================
if __name__ == "__main__":
    tasks = []
    tasks.append(Process("P1", 0, 3))
    tasks.append(Process("P2", 1, 7))
    tasks.append(Process("P3", 3, 2))
    tasks.append(Process("P4", 5, 5))
    tasks.append(Process("P5", 6, 3))

    print("SRTN 스케줄링 시뮬레이션...")
    ABT, total_power = run_srtn_scheduler(tasks)

    print("\n[프로세스별 결과]")
    for i in tasks:
        # 변경점: Output 함수에 더 이상 ABT를 넘겨주지 않아도 됨
        WT, TT, NTT = Output(i)
        print(f"{i.processID:3s}의 WT:{WT:2d}, TT:{TT:2d}, NTT:{NTT:.2f}")

    print_gantt_chart(ABT)
    print(f"\n▶ 시스템 총 소비 전력: {total_power}W")
