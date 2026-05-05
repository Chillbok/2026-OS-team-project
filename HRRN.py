class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid  # process ID
        self.arrival = arrival # arrival time
        self.burst = burst # burst time
        self.start_time = 0 
        self.finish_time = 0 


def HRRN(processes):
    time = 0 
    completed = []
    gantt = []   # 간트차트
    n = len(processes)

    processes.sort(key=lambda x: x.arrival)
    ready_queue = []

    i = 0

    while len(completed) < n: #모든 프로세스가 완료될 때까지 반복 

        # 도착한 프로세스 큐에 추가
        while i < n and processes[i].arrival <= time:
            ready_queue.append(processes[i])
            i += 1

        if not ready_queue:
            gantt.append("Idle")  
            time += 1
            continue

        # HRRN 계산
        best = None
        max_rr = -1 # 최대 응답률(response ratio)

        for p in ready_queue:
            wt = time - p.arrival # 대기 시간(waiting time)
            rr = (wt + p.burst) / p.burst # response ratio 계산

            if rr > max_rr:
                max_rr = rr 
                best = p # 가장 높은 응답률을 가진 프로세스 선택

        current = best
        ready_queue.remove(current) 

        current.start_time = time

        # 비선점 실행
        for _ in range(current.burst):
            gantt.append(current.pid) # 간트차트에 현재 프로세스 ID 추가
            time += 1

            # 실행 중 도착 처리
            while i < n and processes[i].arrival <= time:
                ready_queue.append(processes[i])
                i += 1

        current.finish_time = time
        completed.append(current)

    return completed, gantt


def print_result(processes, gantt):
    print("\n[Gantt Chart]")
    print(gantt)

    print("\n[Process Info]")
    for p in processes:
        tt = p.finish_time - p.arrival # turnaround time 계산
        wt = tt - p.burst # waiting time 계산
        ntt = tt / p.burst #NTT
        print(f"{p.pid}: WT={wt}, TT={tt}, NTT={ntt:.2f}")


# 테스트
processes = []
processes.append(Process(1, 0, 3))
processes.append(Process(2, 2, 6))
processes.append(Process(3, 4, 4))
processes.append(Process(4, 6, 5))


completed, gantt = HRRN(processes)
print_result(completed, gantt)
