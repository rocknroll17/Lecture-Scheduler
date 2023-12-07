# 스케줄메니저
from itertools import product

class ScheduleManager:
    @staticmethod
    def time_table_maker(must_group, prefer_group, credit_limit):
        must_group = [i for i in must_group.get_groups() if i != []]
        prefer_group = [i for i in prefer_group.get_groups() if i != []]
        prefer_rank = [i+1 for i in range(len(prefer_group))]
        possible_table = []  # 꼭에 관한 가능한 시간표를 담아서 나중에 반환
        prefer_combinations = []  # 들으면 좋음에 관한 모든 경우의 수를 찾아서 반환
        must_combinations = list(product(*must_group))  # 가능한 모든 경우의 수를 뽑음

        for combination in product(*prefer_group):
            for mask in product(range(2), repeat=len(prefer_group)):
                result = [item if flag else None for item, flag in zip(combination, mask)]
                prefer_combinations.append(result)
        prefer_combinations = list(
            set(tuple(filter(lambda x: x is not None, combination)) for combination in prefer_combinations))
        for i in must_combinations:  # 모든 경우에 수에 대해서
            for j in prefer_combinations:
                if ScheduleManager.magician(list(i) + list(j), credit_limit):  # 가능한 시간표인지 판단
                    if len(list(i) + list(j)) != 0:
                        rank_list = []
                        for lecture in list(j):
                            for group in prefer_group:
                                if lecture in group:
                                    rank_list.append(prefer_rank[prefer_group.index(group)])
                                    break;
                        possible_table.append([list(i) + list(j), rank_list])  # 가능한 시간표라면 추가
        return possible_table  # 반환

    @staticmethod
    # 후보 하나가 주어지면 이 후보로 시간표가 작성이 가능한지 판단
    def magician(time_group, credit_limit):
        day = {'일': 0, '월': 1, '화': 2, '수': 3, '목': 4, '금': 5, '토': 6}
        compare_time = [[], [], [], [], [], [], []]  # 리스트에 넣고 돌리려면 필요했음.
        credit_sum = 0
        for i in range(len(time_group)):
            credit_sum += float(time_group[i].credit.split("-")[0])
        if credit_sum > credit_limit:
            return False
        for i in range(len(time_group)):  # 주어진 수업의 갯수만큼
            for j in range(len(time_group[i].time)):  # 한 수업이 가진 분할 수업의 갯수만큼
                compare_time[day[time_group[i].time[j].day]].extend(
                    list(range(time_group[i].time[j].startmin, time_group[i].time[j].endmin)))
                # 이 코드가 startmin과 endmin사이의 모든 분을 만들어서 각 요일 리스트에 추가
        for i in range(len(compare_time)):  # 일-토까지
            if len(compare_time[i]) != len(set(compare_time[i])):  # 겹치는 시간이 있는 지 비교
                return False
        return True