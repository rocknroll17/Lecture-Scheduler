import re
strings = [        
        '월(16:30~17:45) / 수(16:30~17:45) / 310관(310관) 803호 <강의실>'
        , '월(10:30~11:45) / 수(10:30~11:45) / 00 000000'
        , '월(10:30~11:45) / 310관(310관) 803호 <강의실>'
        , '수4,5 / 310관(310관) 503호 <강의실>'
        , '수4,5,6 / 310관(310관) 503호 <강의실>'
        , '월4,5,6, 금4,5,6 / 103관 406호 <강의실>'
        , '목4,5,6 / 00 000000'
        ]
# r'.(\([0-9]{2}:[0-9]{2})~([0-9]{2}:[0-9]{2}\))'
# r'.([0-9])(,[0-9])*'
time_type1 = re.compile(r'%([월|화|수|목|금|토|일])\(([0-9]{2}:[0-9]{2})~([0-9]{2}:[0-9]{2})\)') # 그루핑으로 시간 꺼낼 수 있음 .group(2)이랑 .group(3)
time_type2 = re.compile(r'([월|화|수|목|금|토|일])([0-9])(,[0-9])*') # 그루핑으로 시간 꺼낼 수 있음. .group(1)

'''
idx = 0
for s in strings:
    print(f"#{idx}")
    idx += 1
    match1 = time_type1.match(s)
    match2 = time_type2.match(s)
    if match1:
        print(match1)
    if match2: 
        print(match2.group(2), end=" ")
        print(match2)
print()
idx=0
for s in strings:
    print(f"#{idx}")
    idx += 1
    match2_all = time_type2.findall(s)
    print(match2_all)
print()
'''
match1_all = time_type1.finditer(' '.join(strings))
match2_all = time_type2.finditer(' '.join(strings))
for m in match1_all:
    day = m.group(1) # 요일 ex) '월'
    start_time = m.group(2) # 시작시간 ex) '16:30'
    end_time = m.group(3) # 종료시간 ex) '17:45'  
    h, min = map(int, start_time.split(':'))
    print(m.group(1), h, min, end=" | ")
    h, min = map(int, end_time.split(':'))
    print(m.group(1), h, min, end=" | ")
    print(m.group(0))



for m in match2_all:
    print(m.group(1), m.group(2), m.group(3), end=" | ")
    print(list( map( int, m.group(0)[1:].split(','))))