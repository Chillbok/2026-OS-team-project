from collections import deque #라운드 로빈을 구현하기 위한 큐 자료구조 사용

class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid #프로세스 ID
        self.arrival = arrival #도착 시간
        self.burst = burst #burst time
        self.remaining = burst #남은 실행 시간 계산용
        self.finish_time = 0

def round_robin(processes, quantum): #프로세스 리스트를 받고, 타임 퀀텀 설정.
    if quantum <= 0:
        raise ValueError("Quantum must be a positive integer.")
    time = 0
    queue = deque()
    completed = []
    gantt = []   # 간트차트 배열  

    processes = sorted(processes, key=lambda x: x.arrival)
    i = 0
    n = len(processes)

    while len(completed) < n: #모든 프로세스가 완료될 때까지 반복 

        #도착한 프로세스 큐에 추가
        while i < n and processes[i].arrival <= time:
            queue.append(processes[i])
            i += 1

        if not queue:
            gantt.append("idle")
            time += 1
            continue

        current = queue.popleft() #큐에서 가장 앞 프로세스 꺼냄, 현재 CPU에서 실행할 프로세스

        #실행
        exec_time = min(quantum, current.remaining) #타임 퀀텀과 남은 실행시간 중 작은 값만큼 실행

        for _ in range(exec_time): #1초씩 실행
            gantt.append(current.pid) #간트차트에 id 기록
            time += 1
            current.remaining -= 1

            ##현재 시간에 도착한 프로세스가 있다면 즉시 큐에 추가
            while i < n and processes[i].arrival <= time: 
                queue.append(processes[i])
                i += 1

            if current.remaining == 0:
                break

        #종료 or 재삽입
        if current.remaining == 0:
            current.finish_time = time #완료 시간 기록
            completed.append(current) #완료된 프로세스 리스트에 추가
        else:
            queue.append(current) #실행시간 남았으면 다시 큐로

    return completed, gantt

def print_completion_order(processes):
    print("\n[완료 순서]")
    for i, p in enumerate(processes):
        print(f"{i+1}번째 완료: P{p.pid} (finish_time={p.finish_time})")


def print_result(processes):
    for p in processes:
        tt = p.finish_time - p.arrival #Turnaround Time(TT) = Finish Time - Arrival Time
        wt = tt - p.burst #Waiting Time(WT) = Turnaround Time - Burst Time
        print(f"P{p.pid} | TT={tt}, WT={wt}")

def print_gantt_chart(gantt):
    print("\n[Gantt Chart]")
    
    # 프로세스
    for p in gantt:
        print(f"| {p} ", end="")
    print("|")
    
    # 시간
    for t in range(len(gantt) + 1):
        print(f"{t}".ljust(4), end="")
    print()

#프로세스 ID, 도착 시간, burst time 설정
tasks = []
tasks.append(Process(1, 0, 5))
tasks.append(Process(2, 2, 8))
tasks.append(Process(3, 4, 6))
tasks.append(Process(4, 4, 2))
tasks.append(Process(5, 5, 4))


result, gantt = round_robin(tasks, quantum=3)
print_result(result)
print_completion_order(result)
print_gantt_chart(gantt)
