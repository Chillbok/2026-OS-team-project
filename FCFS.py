class Process:
	def __init__(self, processID, arrivalTime, burstTime):
		self.processID=processID
		self.arrivalTime=arrivalTime
		self.burstTime=burstTime

#간트차트 그리기
def FCFS(task_list):
	task_list.sort(key=lambda x: x.arrivalTime)

	ABT = []#간트차트 그리는 배열
	currentTime = 0
	for i in task_list:
		while(currentTime < i.arrivalTime):
			ABT.append("idle")
			currentTime +=1

		for j in range(i.burstTime):
			ABT.append(i.processID)
			currentTime +=1

	return ABT

#실행종료 시간 계산
def CompletionTimeChecker(process, ABT_list):
	for i in range(len(ABT_list) - 1, -1, -1):
		if ABT_list[i] == process.processID:
			return i + 1
	return 0

#반환값 계산
def Output(process, ABT_list):
	completionTime=CompletionTimeChecker(process, ABT_list)
	turnaroundTime=completionTime-process.arrivalTime
	waitingTime=turnaroundTime-process.burstTime
	NTT=turnaroundTime/process.burstTime if process.burstTime > 0 else 0

	return waitingTime, turnaroundTime, NTT

'''
동작확인
'''
tasks = []
ABT = []

tasks.append(Process("P1",0,3))
tasks.append(Process("P2",1,7))
tasks.append(Process("P3",3,2))
tasks.append(Process("P4",5,5))
tasks.append(Process("P5",6,3))

tasks.sort(key=lambda x: x.arrivalTime)

# FCFS 실행 결과로 ABT 생성
ABT = FCFS(tasks)

for i in tasks:
    WT, TT, NTT = Output(i, ABT)
    print(f"{i.processID}의 WT:{WT}, TT:{TT}, NTT:{NTT}")


def print_gantt_chart(ABT_list):
    print("\n[Gantt Chart]")
    
    # 프로세스
    for p in ABT_list:
        print(f"| {p} ", end="")
    print("|")
    
    # 시간
    for t in range(len(ABT_list) + 1):
        print(f"{t}".ljust(4), end="")
    print()

print_gantt_chart(ABT)
