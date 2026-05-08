class Core:
    def __init__(self, name, performance, run_power, wake_power):
        self.name = name
        self.performance = performance 
        self.run_power = run_power
        self.wake_power = wake_power
        self.current = None
        self.time_slice = 0
        self.was_idle = True

def create_cores(p_count, e_count):
    cores = []
    for i in range(p_count):
        cores.append(Core(name=f"P-Core {i}", performance=2, run_power=3, wake_power=0.5))
    for i in range(e_count):
        cores.append(Core(name=f"E-Core {i}", performance=1, run_power=1, wake_power=0.1))
    return cores

class Process:
    def __init__(self, pid, arrival, burst):
        self.pid=pid
        self.arrival=arrival
        self.burst=burst
        self.remaining=burst
        self.start_time = None
        self.finish_time = 0

# ==========================================
# SPN 알고리즘
# ==========================================
def SPN(processes, p_count, e_count):
    time = 0
    arrived = []
    completed = []
    cores = create_cores(p_count, e_count)
    total_power = 0

    processes.sort(key=lambda x: x.arrival)
    i = 0

    gantt = {}
    for core in cores:  
        gantt[core.name] = []
    
    while len(completed) < len(processes):

        while i < len(processes) and processes[i].arrival <= time:
            arrived.append(processes[i])
            i += 1

        for core in cores:
            if not core.current and arrived:
                # SPN 핵심: 큐에서 가장 burst가 짧은 프로세스를 찾아서 꺼냄
                arrived.sort(key=lambda x: x.burst)
                core.current = arrived.pop(0)
            
            if core.current:
                if core.was_idle:
                    total_power += core.wake_power
                total_power += core.run_power
                core.was_idle = False

                if core.current.start_time is None:
                    core.current.start_time = time

                for _ in range(core.performance): 
                    if core.current.remaining <= 0:
                        break
                    core.current.remaining -= 1

                gantt[core.name].append(core.current.pid)
                
                if core.current.remaining == 0:
                    core.current.finish_time = time + 1
                    completed.append(core.current)
                    core.current = None

            else:
                gantt[core.name].append("idle")
                core.was_idle = True
                
        time += 1

    return completed, gantt, total_power