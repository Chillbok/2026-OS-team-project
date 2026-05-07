from collections import deque

class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
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

        # 성능
        self.performance = performance # 1이면 E-Core, 2면 P-Core
        self.run_power = run_power
        self.wake_power = wake_power
        self.current = None

        # RR quantum
        self.time_slice = 0

        # 이전 tick 활성 상태
        self.was_idle = True



def create_cores(p_count, e_count):

    cores = []

    for i in range(p_count):
        cores.append(
            Core(
                name=f"P-Core {i}",
                performance=2,
                run_power=2,
                wake_power=2
            )
        )

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

def round_robin_multi_core(processes, quantum, p_count, e_count):

    time = 0
    queue = deque()
    completed = []
    cores = create_cores(p_count, e_count)
    total_power = 0

    gantt = {}
    for core in cores:  
        gantt[core.name] = []

    processes = sorted(processes, key=lambda x: x.arrival)
    i = 0
    n = len(processes)

    
    

    while len(completed) < n:

        # 도착 처리
        while i < n and processes[i].arrival <= time:
            queue.append(processes[i])
            i += 1

        # 각 코어 실행
        for core in cores:

            # 작업 없으면 할당
            if not core.current and queue:
                core.current = queue.popleft()
                core.time_slice = 0

            if core.current:
                if core.was_idle:
                    total_power += core.wake_power
                total_power += core.run_power
                core.was_idle = False
                
                # 성능만큼 실행
                for _ in range(core.performance):
                    if core.current.remaining <= 0:
                        break

                    core.current.remaining -= 1
                    core.time_slice += 1

                gantt[core.name].append(core.current.pid)

                # 완료 체크
                if core.current.remaining == 0:
                    core.current.finish_time = time + 1
                    completed.append(core.current)
                    core.current = None

                # quantum 종료 → 다시 큐
                elif core.time_slice >= quantum:
                    queue.append(core.current)
                    core.current = None

            else:
                gantt[core.name].append(0)
                core.was_idle = True

        time += 1

    return completed, gantt, total_power


def print_gantt(gantt):
    print("\n[Gantt Chart]")
    for core, timeline in gantt.items():
        print(f"{core}: ", end="")
        for t in timeline:
            print(f"|{t}", end="")
        print("|")


# 테스트
tasks = [
    Process(1, 0, 5),
    Process(2, 2, 8),
    Process(3, 4, 6),
    Process(4, 4, 2),
    Process(5, 5, 4),
]

result, gantt, power = round_robin_multi_core(
    tasks,
    quantum=3,
    p_count=2,
    e_count=2
)

print_gantt(gantt)

print(f"\n총 소비전력: {power}W")
