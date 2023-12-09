# 스케줄메니저
from itertools import product
from Schedule import Schedule

class ScheduleManager:
    @staticmethod
    def time_table_maker(must_group, prefer_group, credit_limit):
        must_group = [i for i in must_group.get_groups() if i != []]
        prefer_group = [i for i in prefer_group.get_groups() if i != []]
        prefer_rank = [i+1 for i in range(len(prefer_group))]
        possible_tables = []  # 꼭에 관한 가능한 시간표를 담아서 나중에 반환
        prefer_combinations = []  # 들으면 좋음에 관한 모든 경우의 수를 찾아서 반환
        #must_group에 [[1,2],[3,4],[5,6]]가 입력되면 prefer_combinations = [(1, 3, 5), (1, 3, 6), (1, 4, 5), (1, 4, 6), (2, 3, 5), (2, 3, 6), (2, 4, 5), (2, 4, 6)]로 모든 경우를 계산
        #prefer_group에 [[1,2],[3,4]]가 입력되면 prefer_combinations = [(1, 3), (2, 4), (2), (4), (1, 4), (2, 3), (1), (), (3)]로 모든 경우 + 각 그룹이 등장하지 않는 경우까지 계산

        must_combinations = list(product(*must_group))  # 가능한 모든 경우의 수를 뽑음
        for combination in product(*prefer_group):
            for binary_flag in product(range(2), repeat=len(prefer_group)): # [2,3]가 있다면 이 리스트의 길이만큼 0,1로 만들 수 있는 경우의 수 생성 예) [0,0], [0,1], [1,0], [1,1]
                result = [item if flag else None for item, flag in zip(combination, binary_flag)] #zip을 해서 binary_flag가 1이면 해당 강의는 살리고 0이면 None으로 보냄
                prefer_combinations.append(result)
        prefer_combinations = list(
            set(tuple(filter(lambda x: x is not None, combination)) for combination in prefer_combinations))#아까 각 그룹이 등장하지 않는 경우를 None으로 계산했었음, 이걸 없앰
        for i in must_combinations:  # 모든 꼭의 경우에 수에 대해서
            for j in prefer_combinations: #모든 들으면 좋음의 경우의 수에 대해서
                if ScheduleManager.magician(list(i) + list(j), credit_limit):  # 가능한 시간표인지 판단
                    if len(list(i) + list(j)) != 0: #빈 시간표인지 확인
                        rank_list = []
                        for lecture in list(j):
                            for group in prefer_group: #들으면 좋음에 있는 강의가 얼마나 반영됐는지 찾음
                                if lecture in group:
                                    rank_list.append(prefer_rank[prefer_group.index(group)]) #찾았다면 우선순위가 얼마였는지 찾아서 저장
                                    break
                        possible_tables.append(Schedule([list(i) + list(j), rank_list]))  # 가능한 시간표라면 추가
        return possible_tables  # 반환

    @staticmethod
    # 후보 하나가 주어지면 이 후보로 시간표가 작성이 가능한지 판단
    def magician(time_group, credit_limit):
        day = {'일': 0, '월': 1, '화': 2, '수': 3, '목': 4, '금': 5, '토': 6}
        compare_time = [[], [], [], [], [], [], []]  # 각 강의가 열리는 시간을 추가해서 겹치는지 계산하는 리스트
        credit_sum = 0
        for i in range(len(time_group)):
            credit_sum += float(time_group[i].credit.split("-")[0])
        if credit_sum > credit_limit: #사용자가 지정한 학점 제한을 넘기면 불가능한 시간표로 간주
            return False
        for i in range(len(time_group)):  # 주어진 수업의 갯수만큼
            for j in range(len(time_group[i].time)):  # 한 수업이 가진 분할 수업의 갯수만큼
                compare_time[day[time_group[i].time[j].day]].extend(
                    list(range(time_group[i].time[j].startmin, time_group[i].time[j].endmin)))
                # 이 코드가 startmin과 endmin사이의 모든 분을 만들어서 각 요일 리스트에 추가
        for i in range(len(compare_time)):  # 일-토까지
            if len(compare_time[i]) != len(set(compare_time[i])):  # 겹치는 시간이 있는 지 비교
                return False #겹치는 시간이 있다면 불가능한 시간표로 간주
        return True #문제가 없다면 가능한 시간표로 간주

#pyinstaller 성능 이슈로 삭제
'''if __name__ == "__main__":
    import Course, CourseDB
    import Candidate
    lecture_list = []
    DB = CourseDB.CourseDB()
    with open('Data/lecture.txt', 'r', encoding='utf-8') as f:
        lecture_data = f.readlines()
        for i in range(len(lecture_data)):
            # for i in range(300):
            course = Course.Course(lecture_data[i].strip().split("$"))
            DB.add(course)
    musts = [
        [DB.search_by_id("49361-01")],
        [DB.search_by_id("52320-01")],
        [DB.search_by_id("47710-07")],
        [DB.search_by_id("17182-01")]
    ]
    M = Candidate.Candidate()
    M.set_groups(musts)

    prefers = [
        [DB.search_by_id("56424-08")]
    ]
    P = Candidate.Candidate()
    P.set_groups(prefers)

    schedules = ScheduleManager.time_table_maker(M, P, 21)
    for s in schedules:
        print(s)
        print()
    print()'''