class Process:
	def __init__(self, processID, arrivalTime, burstTime):
		self.processID=processID
		self.arrivalTime=arrivalTime
		self.burstTime=burstTime

tasks = []
ABT = []

tasks.append(Process("P1",0,3))
tasks.append(Process("P2",1,7))
tasks.append(Process("P3",3,2))
tasks.append(Process("P4",5,5))
tasks.append(Process("P5",6,3))

tasks.sort(key=lambda x: x.arrivalTime)

for i in tasks:
	for j in range(i.burstTime):
		ABT.append(i.processID)

def CompletionTimeChecker(Process):
	completionTime=0
	temp=Process.burstTime

	for idx, val in enumerate(ABT):
		if(Process.processID==val):
			temp=temp-1
			if(temp==0):
				completionTime=idx+1
				break

	return completionTime

def Output(Process):
	completionTime=CompletionTimeChecker(Process)
	turnaroundTime=completionTime-Process.arrivalTime
	waitingTime=turnaroundTime-Process.burstTime
	NTT=turnaroundTime/Process.burstTime

	return turnaroundTime, waitingTime, NTT

#동작확인
for i in tasks:
	WT, TT, NTT = Output(i)
	print(f"{i.processID}의 WT:{WT}, TT:{TT}, NTT:{NTT}")