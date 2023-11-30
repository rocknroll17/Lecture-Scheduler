
import re
import Timeblock
class Course:
    fails = []
    def __init__(self):
        pass
    def __init__(self, line):
        self.parse_line(line)
        
    
    def parse_line(self, line):
        self.college = line[0]  # 대학
        self.department = line[1]  # 개설학과
        self.campus = line[2]  # 캠퍼스
        self.grade = line[3]  # 학년
        self.course = line[4]  # 과정
        self.category = line[5]  # 이수구분
        self.courseId = line[6]  # 과목번호
        self.title = line[7]  # 과목명
        self.credit = line[8]  # 학점
        self.instructor = line[9]  # 강의자
        self.closed = line[10]  # 폐강 여부
        self.time = self.__parse_time_info(line[11]) # 강의시간 -> Timeblock list로
        self.time_info_raw_string = line[11] # 강의시간/강의실정보 - 파싱 전
        self.annotations = line[12]  # 비고
        
    def __parse_time_info(self, time_string):
        # '수1,2 / 310관(310관) B603호 <대형강의실>' 꼴의 문자열을 Timeblock 객체로 만들어서 반환

        # 강의를 두번에 걸쳐서 하는 강의는, Timeblock을 두 개 갖는다
        # ex) 월3,4/ 수4 -> [Timeblock('월', 3, "12:00"), Timeblock('수', 4, '13:00')]
        """
        time 형식
        '월(16:30~17:45) / 수(16:30~17:45) / 310관(310관) 803호 <강의실>'
        '월(10:30~11:45) / 수(10:30~11:45) / 00 000000'  -> 비대면 강의인듯?
        '월(10:30~11:45) / 310관(310관) 803호 <강의실>'
        '수4,5 / 310관(310관) 503호 <강의실>'
        '수4,5,6 / 310관(310관) 503호 <강의실>'
        '월4,5,6, 금4,5,6 / 103관 406호 <강의실>
        '목4,5,6 / 00 000000'
        """
        # TODO:
        # 문제상황 1 : 10교시의 경우 시작교시가 1교시로 바뀜
        # 문제상황 2 : 가끔 두시간짜리 수업 lecture_time을 01:00으로 계산할 때가 있음

        # 시간 형식 (1) : 월(16:30~17:45) 형식
        time_type1 = re.compile(r'([월|화|수|목|금|토|일])\(([0-9]{2}:[0-9]{2})~([0-9]{2}:[0-9]{2})\)') 
        # 시간 형식 (2) : 월4 / 월4,5 / 월4,5,6 형식
        time_type2 = re.compile(r'([월|화|수|목|금|토|일])([0-9]+)(,[0-9]+)*') 
        # 강의실 정보는 파싱하지 않는다

        try:
            type1_matches = time_type1.finditer(time_string)
            type2_matches = time_type2.finditer(time_string)
            timeblocks = []
            # type1으로 적힌 경우
            for m in type1_matches:
                # 각 '월(16:30~17:45)' 형식의 문자열에 대해서
                day = m.group(1) # 요일 ex) '월'
                start_time = m.group(2) # 시작시간 ex) '16:30'
                end_time = m.group(3) # 종료시간 ex) '17:45'
                # 시작 교시를 계산한다
                start_hour, start_minute = map(int, start_time.split(':'))
                end_hour, end_minute = map(int, end_time.split(':'))
                if start_hour < 8:
                    raise ValueError
                # 9시 시작이면 1교시인거 맞지??
                period = start_hour - 8 
                # 15분 = .25교시 / 30분 = .5교시 / 45분 = .75교시  (소수점이라 정확히 저장 안될수도)
                period += (start_minute/60) 
                # 강의시간을 계산한다
                # 종료시간의 분이 더 적을 경우
                if end_minute < start_minute:
                    end_hour -= 1
                    end_minute += 60
                # 종료시간의 시간이 더 적을 경우 (에러)
                if end_hour < start_hour:
                    raise ValueError
                lecture_hour = end_hour - start_hour
                lecture_minute = end_minute - start_minute
                lecture_time = str(lecture_hour) + ":" + str(lecture_minute)
                if lecture_hour < 10:
                    lecture_time = '0' + lecture_time
                # Timeblock 객체 생성
                timeblock = Timeblock.Timeblock(day, period, lecture_time, start_time, end_time)
                timeblocks.append(timeblock)

            # type2로 적힌 경우
            for m in type2_matches:
                # 각 '월4,5,6' 형식의 문자열에 대해서
                day = m.group(1) # 요일 ex) '월'
                periods_list = list( map( int, m.group(0)[1:].split(','))) # 교시만 따로 리스트로 나타냄. ex) [4,5,6]
                # 교시들이 서로 이어지는지 확인한다 ex) 4,5,6교시
                consecutive = True
                last = periods_list[0]
                for i in range(1, len(periods_list)):
                    if last + 1 != periods_list[i]:
                        index = i
                        consecutive = False
                        break
                    last = periods_list[i]
                # 교시가 서로 이어지는 경우 한 개의 Timeblock으로 저장한다 ex) [4,5,6]
                if consecutive:
                    period = periods_list[0]
                    lecture_time = str(len(periods_list)) + ":" + "00"
                    if len(periods_list) < 10:
                        lecture_time = '0' + lecture_time # "HH:MM"으로 형식 맞추기
                    # start_time, end_time 계산
                    start_time = str(int(period) + 8) + ":00"
                    if int(period)+8 < 10:
                        start_time = '0' + start_time
                    end_time = str(int(periods_list[-1]) + 9) + ":00"
                    if int(periods_list[-1])+9 < 10:
                        end_time = '0' + end_time
                    timeblock = Timeblock.Timeblock(day, period, lecture_time, start_time, end_time)
                    timeblocks.append(timeblock)
                # 만약 교시가 이어지지 않는 경우 두 개의 Timeblock으로 나눠 저장한다 ex) [1,2,6,7]
                else:
                    period1 = periods_list[0]
                    period2 = periods_list[index]
                    lecture_time1 = str(index) + ":" + "00"
                    lecture_time2 = str(len(periods_list) - index) + ":" + "00"
                    if index < 10:
                        lecture_time1 = '0' + lecture_time1
                    if len(periods_list) - index < 10:
                        lecture_time2 = '0' + lecture_time2
                    # start_time, end_time 계산 (맞는지 확인필요)
                    start_time1 = str(int(period1) + 8) + ":00"
                    if int(period1)+8 < 10:
                        start_time1 = '0' + start_time1
                    start_time2 = str(int(period2) + 8) + ":00"
                    if int(period2)+8 < 10:
                        start_time2 = '0' + start_time2
                    end_time1 = str(int(periods_list[index-1]) + 9) + ":00"
                    end_time2 = str(int(periods_list[-1]) + 9) + ":00"
                    if int(periods_list[index-1])+9 < 10:
                        end_time1 = '0' + end_time1
                    if int(periods_list[-1])+9 < 10:
                        end_time2 = '0' + end_time2
                    timeblock1 = Timeblock.Timeblock(day, period1, lecture_time1, start_time1, end_time1)
                    timeblock2 = Timeblock.Timeblock(day, period2, lecture_time2, start_time2, end_time2)
                    timeblocks.extend([timeblock1, timeblock2])
                    Course.fails.append(f"'{self.title[:6]}' -> '{time_string}'") 
                    # 오류는 아닌데 보고싶음
        except:
            # 예외상황 -> 문자열 처리 오류 / 강의 정보 오류 -> 아무튼 예외처리
            Course.fails.append(f"'{self.title[:6]}' -> '{time_string}'")
            return []
        if not timeblocks:
            Course.fails.append(f"'{self.title[:6]}' -> '{time_string}' (no timeblocks)")
        return timeblocks


    def __repr__(self):
        return self.__str__()

    def __str__(self, option=None):
        if option is None:
            return f"{self.courseId} {self.title}"
        elif option == 'college':
            return self.college
        elif option == 'department':
            return self.department
        elif option == 'campus':
            return self.campus
        elif option == 'grade':
            return self.grade
        elif option == 'course':
            return self.course
        elif option == 'category':
            return self.category
        elif option == 'courseId':
            return self.courseId
        elif option == 'title':
            return self.title
        elif option == 'credit':
            return self.credit
        elif option == 'instructor':
            return self.instructor
        elif option == 'closed':
            return self.closed
        elif option == 'time':
            return self.time
        elif option == 'annotations':
            return self.annotations