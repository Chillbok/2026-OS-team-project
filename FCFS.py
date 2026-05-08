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

class Process:
	def __init__(self, pid, arrival, burst):
		self.pid=pid
		self.arrival=arrival
		self.burst=burst
		self.remaining=burst
		self.start_time=None
		self.finish_time = 0


#간트차트 그리기
def FCFS(processes, coreTypes):
	time = 0
	arrived = []
	completed = []
	cores = create_cores(coreTypes)
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
				
				if core.current.start_time is None:
					core.current.start_time = time

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
				gantt[core.name].append("idle")
				core.was_idle = True
				
		time +=1

	return completed, gantt, total_power
