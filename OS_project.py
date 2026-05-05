def is_emergency(task):
    # 안전과 직결되는 작업
    return task.task_type in ["EMERGENCY_BRAKE", "COLLISION_AVOID"]


def is_control(task):
    # 자율주행 제어 관련 작업
    return task.task_type in ["STEERING", "LANE_KEEP"]

# 우선순위를 두어 같은 작업 내의 선점 막기
PRIORITY = {
    # EMERGENCY
    "EMERGENCY_BRAKE": 0,
    "COLLISION_AVOID": 1,

    # CONTROL
    "STEERING": 2,
    "LANE_KEEP": 3,

    # NORMAL
    "CRUISE_CONTROL": 4,
    "INFOTAINMENT": 5,
}

class Process:
    def __init__(self, pid, arrival, burst, task_type):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.task_type = task_type
        self.finish_time = 0
        self.priority = PRIORITY[task_type]

class Core:
    def __init__(self, name, role, power, performance):
        self.name = name
        self.role = role  # EMERGENCY / CONTROL / NORMAL
        self.current = None # 현재 실행 중인 프로세스
        self.power = power # 전력
        self.performance = performance # 일 하는 양

def preempt(current, incoming):
    # 더 높은 우선순위(숫자 작음)일 때만 선점
    return incoming.priority < current.priority

def scheduler(processes):

    if len(processes) > 15:
        raise ValueError("최대 15개 제한") # 프로세스 15개 이상 에러

    time = 0
    completed = []

    #작업별 분리를 위한 3개의 큐
    emergency_q = [] # 긴급
    control_q = [] # 제어
    normal_q = [] # 일반

    # 코어 정의. P2: 긴급 전용, P1: 제어 전용, E1/E2: 일반
    cores = [
        Core("P2", "EMERGENCY", power=3, performance=2), #전력 3 작업량 2
        Core("P1", "CONTROL", power=3, performance=2),
        Core("E1", "NORMAL", power=1, performance=1), #전력 1 작업량 1
        Core("E2", "NORMAL", power=1, performance=1),
    ]

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

            best = min(candidates, key=lambda x: x.priority)

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

            if core.role == "EMERGENCY" and emergency_q:
                best = min(emergency_q, key=lambda x: x.priority)
                emergency_q.remove(best)
                core.current = best

            elif core.role == "CONTROL":
                if control_q:
                    best = min(control_q, key=lambda x: x.priority)
                    control_q.remove(best)
                    core.current = best

                elif emergency_q:
                    best = min(emergency_q, key=lambda x: x.priority)
                    emergency_q.remove(best)
                    core.current = best

            elif core.role == "NORMAL":
                if normal_q:
                    best = min(normal_q, key=lambda x: x.priority)
                    normal_q.remove(best)
                    core.current = best

        


        # 성능 기반 시간 처리 실행
        for core in cores:
            if core.current:

                core.current.remaining -= core.performance

                gantt[core.name].append(core.current.pid)
                total_power += core.power

                if core.current.remaining <= 0:
                    core.current.finish_time = time + 1
                    completed.append(core.current)
                    core.current = None
            else:
                gantt[core.name].append("idle")

        time += 1

    return gantt, processes, total_power

def print_gantt(gantt):
    print("\n[Gantt Chart]")

    for core, timeline in gantt.items():
        print(f"{core}: ", end="")
        for t in timeline:
            print(f"|{t}", end="")
        print("|")

if __name__ == "__main__":

    tasks = [
        Process("P1", 1, 5, "LANE_KEEP"),
        Process("P2", 0, 3, "STEERING"),
        Process("P3", 2, 2, "EMERGENCY_BRAKE"),
        Process("P4", 3, 4, "CRUISE_CONTROL"),
        Process("P5", 4, 3, "INFOTAINMENT"),
        Process("P6", 5, 2, "COLLISION_AVOID"),
    ]

    gantt, processes, power = scheduler(tasks)

    print_gantt(gantt)

    print("\n총 전력 소비:", power)

