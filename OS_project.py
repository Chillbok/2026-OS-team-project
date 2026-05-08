def is_emergency(task):
    # 안전과 직결되는 작업
    return task.task_type in ["EmergencyBrake", "AirbagTrigger"]


def is_control(task):
    # 자율주행 제어 관련 작업
    return task.task_type in ["ABSControl", "EngineControl", "Steering", "LaneKeep", "CollisionAvoidance"]

# 우선순위를 두어 같은 작업 내의 선점 막기
PRIORITY = {
    # EMERGENCY
    "AirbagTrigger": 0,
    "EmergencyBrake": 1,

    # CONTROL
    "ABSControl": 2,
    "EngineControl" : 2,
    "Steering": 3,
    "LaneKeep": 3,
    "CollisionAvoidance": 4,

    # NORMAL
    "TirePressureMonitor": 5,
    "BatteryMonitor": 5,
    "CoolantTempMonitor": 5,
    "OBDDiagnostics": 6,
    "GPSNavigation": 6,
    "DashcamRecording": 6,
    "AirConditioning": 7,
    "Infotainment": 7
}

class Process:
    def __init__(self, pid, arrival, burst, task_type):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.task_type = task_type
        self.start_time = None
        self.finish_time = 0
        self.priority = PRIORITY[task_type]

class Core:
    def __init__(self, name, role, power, performance, wake_power):
        self.name = name
        self.role = role  # EMERGENCY / CONTROL / NORMAL
        self.current = None # 현재 실행 중인 프로세스
        self.power = power # 전력
        self.performance = performance # 일 하는 양
        self.wake_power = wake_power
        self.was_idle = True

def create_cores(p_count, e_count):

    cores = []
    # P-Core 생성
    for i in range(p_count):

        if i == 0:
            role = "EMERGENCY" #첫 번째의 P-Core는 긴급 작업 전용
        else:
            role = "CONTROL" #나머지 P-Core는 제어 작업 전용

        cores.append(
            Core(
                name=f"P{i}",
                role=role,
                power=2,
                performance=2,
                wake_power=0.5
            )
        )

    # E-Core 생성
    for i in range(e_count):

        cores.append(
            Core(
                name=f"E{i}",
                role="NORMAL",
                power=1,
                performance=1,
                wake_power=0.1
            )
        )

    return cores

def preempt(current, incoming):
    # 더 높은 우선순위(숫자 작음)일 때만 선점
    return incoming.priority < current.priority

def scheduler(processes,  p_count, e_count):

    time = 0
    completed = []

    #작업별 분리를 위한 3개의 큐
    emergency_q = [] # 긴급
    control_q = [] # 제어
    normal_q = [] # 일반

    cores = create_cores(p_count, e_count)
    gantt = {c.name: [] for c in cores}
    total_power = 0

    while len(completed) < len(processes):

        for p in processes:
            if p.arrival == time: #도착한 프로세스
                #타입별로 분리
                if is_emergency(p):
                    emergency_q.append(p)
                elif is_control(p):
                    control_q.append(p)
                else:
                    normal_q.append(p)

        for core in cores:
            if not core.current:
                continue

            candidates = []
            candidates.extend(emergency_q)
            candidates.extend(control_q)
            candidates.extend(normal_q)

            if not candidates:
                continue

            best = min(candidates, key=lambda x: (x.priority, x.arrival))

            # 더 높은 priority일 때만 선점
            if preempt(core.current, best):
                if is_emergency(core.current):
                    emergency_q.append(core.current)
                elif is_control(core.current):
                    control_q.append(core.current)
                else:
                    normal_q.append(core.current)

                core.current = None

        # 작업 할당
        for core in cores: 

            if core.current: # 작업 중인 일은 계속
                continue

            if core.role == "EMERGENCY":

                if emergency_q:
                    best = min(emergency_q,key=lambda x: (x.priority, x.arrival))
                    emergency_q.remove(best)
                    core.current = best

                elif control_q:
                    best = min(control_q, key=lambda x: (x.priority, x.arrival))
                    control_q.remove(best)
                    core.current = best

                if core.current and core.current.start_time is None:
                    core.current.start_time = time

            elif core.role == "CONTROL":
                
                if control_q:
                    best = min(control_q, key=lambda x: (x.priority, x.arrival))
                    control_q.remove(best)
                    core.current = best

                elif emergency_q:

                    best = min(emergency_q,key=lambda x: (x.priority, x.arrival))
                    emergency_q.remove(best)
                    core.current = best

                elif normal_q:
                    best = min(normal_q,key=lambda x: (x.priority, x.arrival))
                    normal_q.remove(best)
                    core.current = best

                if core.current and core.current.start_time is None:
                    core.current.start_time = time 

                

            elif core.role == "NORMAL": # 일반 코어는 제어, 일반 작업 순으로 작업처리
                
                if control_q:
                    best = min(control_q, key=lambda x: (x.priority, x.arrival))
                    control_q.remove(best)
                    core.current = best
                    if best.start_time is None:
                        best.start_time = time

                elif normal_q:
                    best = min(normal_q, key=lambda x: (x.priority, x.arrival))
                    normal_q.remove(best)
                    core.current = best
                    if best.start_time is None:
                        best.start_time = time  

        


        # 성능 기반 시간 처리 실행
        for core in cores:
            if core.current:
                
                #시동 전력 + 작업 전력
                if core.was_idle:
                    total_power += core.wake_power
                total_power += core.power
                core.was_idle = False

                core.current.remaining -= core.performance

                gantt[core.name].append(core.current.pid)

                if core.current.remaining <= 0:
                    core.current.finish_time = time + 1
                    completed.append(core.current)
                    core.current = None
            else:
                gantt[core.name].append("idle")
                core.was_idle = True
        time += 1

    return gantt, processes, total_power 

def print_gantt(gantt):
    print("\n[Gantt Chart]")

    for core, timeline in gantt.items():
        print(f"{core}: ", end="")
        for t in timeline:
            print(f"|{t}", end="")
        print("|")
