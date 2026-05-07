class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid  
        self.arrival = arrival  
        self.burst = burst  
        self.remaining = burst  # P/E 코어 성능 차감을 위한 변수
        self.start_time = 0 
        self.finish_time = 0 

class Core:
    def __init__(self, name, performance, run_power, wake_power):
        self.name = name
        self.performance = performance  # P코어=2, E코어=1
        self.run_power = run_power      
        self.wake_power = wake_power    
        self.current = None  
        self.was_idle = True 

def create_cores(p_count, e_count):
    cores = []
    for i in range(p_count):
        cores.append(Core(name=f"P-Core {i}", performance=2, run_power=2, wake_power=2))
    for i in range(e_count):
        cores.append(Core(name=f"E-Core {i}", performance=1, run_power=1, wake_power=1))
    return cores

def SPN_multi_core(processes, p_count, e_count):
    time = 0 
    completed = []
    processes.sort(key=lambda x: x.arrival)
    ready_queue = []

    i = 0
    n = len(processes)
    total_power = 0
    cores = create_cores(p_count, e_count)

    gantt = {core.name: [] for core in cores}

    while len(completed) < n:
        # 1. 도착한 프로세스를 대기열에 추가
        while i < n and processes[i].arrival <= time:
            ready_queue.append(processes[i])
            i += 1

        for core in cores:
            # 2. 작업 할당 (비선점형: 코어가 비어있을 때만)
            if core.current is None and ready_queue:
                # SPN 로직: Burst Time이 가장 짧은 프로세스 선택
                best = min(ready_queue, key=lambda x: x.burst)
                ready_queue.remove(best)
                core.current = best
                if best.start_time == 0:
                    best.start_time = time

            # 3. 코어 실행 및 전력/성능 계산
            if core.current:
                if core.was_idle:
                    total_power += core.wake_power # 시동 전력
                total_power += core.run_power      # 유지 전력
                core.was_idle = False

                # P/E 코어의 성능만큼 작업량 감소
                core.current.remaining -= core.performance
                gantt[core.name].append(core.current.pid)

                # 작업 종료 체크
                if core.current.remaining <= 0:
                    core.current.finish_time = time + 1
                    completed.append(core.current)
                    core.current = None
            else:
                gantt[core.name].append("idle")
                core.was_idle = True
                
        time += 1

    return completed, gantt, total_power

def print_result(processes, gantt, total_power, algo_name="SPN"):
    print(f"\n[{algo_name} 간트 차트]")
    for core, timeline in gantt.items():
        print(f"{core.ljust(10)}: ", end="")
        for t in timeline:
            print(f"|{str(t).center(4)}", end="")
        print("|")

    print(f"\n[{algo_name} 결과 요약]")
    for p in processes:
        tt = p.finish_time - p.arrival
        wt = tt - p.burst
        ntt = tt / p.burst if p.burst > 0 else 0
        print(f"[{p.pid}] WT: {wt}, TT: {tt}, NTT: {ntt:.2f}")
    print(f"▶ 총 소비전력: {total_power}W")

# ==========================================
# 실행 테스트
# ==========================================
if __name__ == "__main__":
    tasks = [
        Process("P1", 0, 7), Process("P2", 1, 6), Process("P3", 2, 4),
        Process("P4", 3, 3), Process("P5", 5, 6), Process("P6", 7, 2)
    ]
    completed, gantt, power = SPN_multi_core(tasks, p_count=2, e_count=2)
    print_result(completed, gantt, power, "SPN")
