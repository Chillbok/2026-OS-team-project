from collections import deque

class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
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

        # 성능
        self.performance = performance # 1이면 E-Core, 2면 P-Core
        self.run_power = run_power
        self.wake_power = wake_power
        self.current = None

        # RR quantum
        self.time_slice = 0

        # 이전 tick 활성 상태
        self.was_idle = True



def create_cores(coreTypes):

    cores = []
    
    for i in coreTypes:
        if i.get() == "P":
            cores.append(
                Core(
                    name=f"P-Core {len(cores)}",
                    performance=2,
                    run_power=3,
                    wake_power=0.5
                )
            )
        else:
            cores.append(
                Core(
                    name=f"E-Core {len(cores)}",
                    performance=1,
                    run_power=1,
                    wake_power=0.1
                )
            )
    return cores

def RR(processes, quantum, coreTypes):

    time = 0
    queue = deque()
    completed = []
    cores = create_cores(coreTypes)
    total_power = 0

    gantt = {}
    for core in cores:  
        gantt[core.name] = []

    processes = sorted(processes, key=lambda x: x.arrival)
    i = 0
    n = len(processes)

    
    in_use = []  # RR에서 quantum 끝나서 다음 시간 텀까지 대기하는 프로세스들
    while len(completed) < n:

        # 도착 처리
        while i < n and processes[i].arrival <= time:
            queue.append(processes[i])
            i += 1
            
        queue.extend(in_use)
        in_use = []

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
                
                if core.current.start_time is None:
                    core.current.start_time = time

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
                    in_use.append(core.current)
                    core.current = None

            else:
                gantt[core.name].append("idle")
                core.was_idle = True

        time += 1


    return completed, gantt, total_power
