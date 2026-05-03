# 프로세스 객체 클래스
class Process:
    def __init__(self, processID, arrivalTime, burstTime):
        self.processID = processID
        self.arrivalTime = arrivalTime
        self.burstTime = burstTime
        self.isCompleted = False # 작업 완료 상태 체크용

# SPN 스케줄링 알고리즘 모듈
def run_spn_scheduler(task_list):
    """
    SPN 스케줄링 알고리즘을 실행하고 타임라인(ABT)을 반환합니다.
    """
    ABT = []
    current_time = 0
    completed_processes = 0
    total_processes = len(task_list)

    while completed_processes < total_processes:
        # 1. 현재 시간 기준으로 도착했고, 아직 완료되지 않은 프로세스들 찾기
        ready_queue = [p for p in task_list if p.arrivalTime <= current_time and not p.isCompleted]
        
        if not ready_queue:
            # 2. 실행할 프로세스가 없는경우
            ABT.append("IDLE")
            current_time += 1
        else:
            # 3. 대기열 중에서 실행 시간(Burst Time)이 가장 짧은 프로세스 선택 (SPN 로직)
            shortest_process = min(ready_queue, key=lambda x: x.burstTime)
            
            # 4 선택된 프로세스를 실행 시간만큼 ABT 리스트에 채워 넣기 간트차트 그리기용
            for _ in range(shortest_process.burstTime):
                ABT.append(shortest_process.processID)
                
            # 시간 점프 및 완료 처리
            current_time += shortest_process.burstTime
            shortest_process.isCompleted = True
            completed_processes += 1

    return ABT

# 결과 계산용 함수
def CompletionTimeChecker(Process_obj, ABT_list):
    completionTime = 0
    temp = Process_obj.burstTime

    for idx, val in enumerate(ABT_list):
        if Process_obj.processID == val:
            temp = temp - 1
            if temp == 0:
                completionTime = idx + 1
                break

    return completionTime

def Output(Process_obj, ABT_list):
    completionTime = CompletionTimeChecker(Process_obj, ABT_list)
    turnaroundTime = completionTime - Process_obj.arrivalTime
    waitingTime = turnaroundTime - Process_obj.burstTime

    return turnaroundTime, waitingTime, NTT