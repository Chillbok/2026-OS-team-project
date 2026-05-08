class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid  # process ID
        self.arrival = arrival # arrival time
        self.burst = burst # burst time
        self.remaining = burst # 남은 실행 시간
        self.start_time = None 
        self.finish_time = 0 
        
class Core:
    def __init__(
        self,
        name,
        performance,
        run_power,
        wake_power
    ):
        self.name = name
        self.performance = performance
        self.run_power = run_power
        self.wake_power = wake_power

        # 현재 실행중 프로세스
        self.current = None
        self.was_idle = True

def create_cores(p_count, e_count):

    cores = []

    # P-Core
    for i in range(p_count):
        cores.append(
            Core(
                name=f"P-Core {i}",
                performance=2,
                run_power=2,
                wake_power=2
            )
        )

    # E-Core
    for i in range(e_count):
        cores.append(
            Core(
                name=f"E-Core {i}",
                performance=1,
                run_power=1,
                wake_power=1
            )
        )

    return cores

def HRRN(processes, p_count, e_count):
    time = 0 
    completed = []
    processes.sort(key=lambda x: x.arrival)
    ready_queue = []

    i = 0
    n = len(processes)
    total_power = 0
    cores = create_cores(p_count, e_count)

    gantt = {}  # 간트차트
    for core in cores:
        gantt[core.name] = []

    while len(completed) < n: #모든 프로세스가 완료될 때까지 반복 

        # 도착한 프로세스 큐에 추가
        while i < n and processes[i].arrival <= time:
            ready_queue.append(processes[i])
            i += 1

        for core in cores:

            # 현재 작업이 없는 경우
            if core.current is None:

                # HRRN 계산
                if ready_queue:

                    best = None
                    max_rr = -1

                    for p in ready_queue:

                        wt = time - p.arrival
                        rr = (wt + p.burst) / p.burst

                        if rr > max_rr:
                            max_rr = rr
                            best = p

                    ready_queue.remove(best)

                    core.current = best
                    if best.start_time is None:
                        best.start_time = time

            # 실행
            if core.current:

                # 시동전력
                if core.was_idle:
                    total_power += core.wake_power

                # 사용전력
                total_power += core.run_power

                core.was_idle = False

                # 성능만큼 처리
                core.current.remaining -= core.performance

                gantt[core.name].append(core.current.pid)

                # 종료
                if core.current.remaining <= 0:

                    core.current.finish_time = time + 1

                    completed.append(core.current)

                    core.current = None

            else:

                gantt[core.name].append("idle")

                core.was_idle = True

        time += 1

    return completed, gantt, total_power


def print_result(processes, gantt, total_power):
    print("\n[Gantt Chart]")
    for core, timeline in gantt.items():
        print(f"{core}: ", end="")

        for t in timeline:
            print(f"|{t}", end="")
        print("|")

    print("\n[Process Info]")
    for p in processes:
        tt = p.finish_time - p.arrival
        wt = p.start_time - p.arrival
        ntt = tt / p.burst
        print(f"{p.pid}: WT={wt}, TT={tt}, NTT={ntt:.2f}")
    print(f"\n총 소비전력: {total_power}W")