class Process:
    def __init__(self, processID, arrivalTime, burstTime):
        self.processID = processID
        self.arrivalTime = arrivalTime
        self.burstTime = burstTime
        # SRTN을 위해 추가된 남은 시간 추적용 변수
        self.remainingTime = burstTime  
        self.isCompleted = False

def run_srtn_scheduler(task_list):
    """
    SRTN (Shortest Remaining Time Next) 알고리즘 구현부
    """
    ABT = [] # 간트 차트 기록용 리스트
    task_list.sort(key=lambda x: x.arrivalTime)
    toDoTasks=[]
    current_time = 0
    completed_processes = 0
    total_processes = len(task_list)

    # 모든 프로세스가 완료될 때까지 1초씩 진행
    while completed_processes < total_processes:
        #매번 task가 도착했는지 확인
        for i in range(len(task_list)):
            if current_time == task_list[i].arrivalTime:
                toDoTasks.append(task_list[i])
        if not toDoTasks:
            ABT.append("idle")
        else:
            srTask=min(toDoTasks, key=lambda x: x.remainingTime)
            ABT.append(srTask.processID)
            srTask.remainingTime -= 1
            if(srTask.remainingTime == 0):
                toDoTasks.remove(srTask)
                completed_processes += 1
        current_time += 1

    return ABT


def CompletionTimeChecker(Process_obj, ABT_list):
    completionTime = 0
    for idx in range(len(ABT_list) - 1, -1, -1):
        if ABT_list[idx] == Process_obj.processID:
            completionTime = idx + 1
            break
    return completionTime

def Output(Process_obj, ABT_list):
    """TT, WT, NTT 결과 계산"""
    completionTime = CompletionTimeChecker(Process_obj, ABT_list)
    turnaroundTime = completionTime - Process_obj.arrivalTime
    waitingTime = turnaroundTime - Process_obj.burstTime
    ntt=turnaroundTime/Process_obj.burstTime

    return waitingTime, turnaroundTime, ntt

#process 입력
tasks = []
tasks.append(Process("P1",0,3))
tasks.append(Process("P2",1,7))
tasks.append(Process("P3",3,2))
tasks.append(Process("P4",5,5))
tasks.append(Process("P5",6,3))


#동작확인

ABT=run_srtn_scheduler(tasks)

for i in tasks:
   WT, TT, NTT = Output(i,ABT)
   print(f"{i.processID}의 WT:{WT}, TT:{TT}, NTT:{NTT}")

def print_gantt_chart(ABT):
    print("\n[Gantt Chart]")
    
    # 프로세스
    for p in ABT:
        print(f"| {p} ", end="")
    print("|")
    
    # 시간
    for t in range(len(ABT) + 1):
        print(f"{t}".ljust(4), end="")
    print()

print_gantt_chart(ABT)
