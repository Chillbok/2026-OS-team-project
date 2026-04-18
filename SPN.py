# 1. 로컬 상태를 한 칸 전(잘못 올리기 전)으로 되돌림 (파일 내용은 그대로 남음)
git reset HEAD^

# 2. 깃허브 원격 저장소(develop)에 되돌린 상태를 강제로 덮어써서 기록 삭제
git push origin develop -f