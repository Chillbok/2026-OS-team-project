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
                run_power=3,
                wake_power=0.5
            )
        )

    for i in range(e_count):
        cores.append(
            Core(
                name=f"E-Core {i}",
                performance=1,
                run_power=1,
                wake_power=0.1
            )
        )

    return cores

class Process:
	def __init__(self, pid, arrival, burst):
		self.pid=pid
		self.arrival=arrival
		self.burst=burst
		self.remaining=burst
		self.finish_time = 0


#간트차트 그리기
def FCFS_multi_core(processes, p_count, e_count):
	time = 0
	arrived = []
	completed = []
	cores = create_cores(p_count, e_count)
	total_power = 0

	processes.sort(key=lambda x: x.arrival)
	i = 0

	gantt = {}#간트차트 그리는 딕셔너리
	for core in cores:  
		gantt[core.name] = []

	
	while len(completed) < len(processes):

		while i < len(processes) and processes[i].arrival <= time:
			arrived.append(processes[i])
			i += 1

		for core in cores:
			if not core.current and arrived:
				core.current = arrived.pop(0)
			
			if core.current:
				if core.was_idle:
					total_power += core.wake_power
				total_power += core.run_power
				core.was_idle = False

				for _ in range(core.performance):#성능만큼 실행
					if core.current.remaining <= 0:
						break
					
					core.current.remaining -= 1

				gantt[core.name].append(core.current.pid)
				
				# 완료 체크
				if core.current.remaining == 0:
					core.current.finish_time = time + 1
					completed.append(core.current)
					core.current = None

			else:
				gantt[core.name].append(0)
				core.was_idle = True
				
		time +=1

	return completed, gantt, total_power

#반환값 계산
def Output(process, gantt):
	completionTime=process.finish_time
	turnaroundTime=completionTime-process.arrival

	for key in gantt:
		if "P-Core" in key:
			if process.pid in gantt[key]:
				burst = (process.burst + 1) // 2
				break
	else:
		burst = process.burst

	waitingTime=turnaroundTime-burst
	NTT=turnaroundTime/burst

	return waitingTime, turnaroundTime, NTT

'''
동작확인
'''
tasks = []

tasks.append(Process(1,0,3))
tasks.append(Process(2,1,7))
tasks.append(Process(3,3,2))
tasks.append(Process(4,5,5))
tasks.append(Process(5,6,3))

# FCFS 실행 결과로 ABT 생성
completed, gantt, total_power = FCFS_multi_core(tasks, p_count=2, e_count=2)

for i in tasks:
    WT, TT, NTT = Output(i, gantt)
    print(f"{i.pid}의 WT:{WT}, TT:{TT}, NTT:{NTT}")


def print_gantt(gantt):
    print("\n[Gantt Chart]")
    for core, timeline in gantt.items():
        print(f"{core}: ", end="")
        for t in timeline:
            print(f"|{t}", end="")
        print("|")

print_gantt(gantt)
print(f"\n총 소비전력: {total_power}W")
