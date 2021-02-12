# Outsourcing-Last-Full-Crawling-of-Naver-View
## UI 구조
1. input창 : line input(Query_LineEdit) + notepad file(openFile_btn) + 직접수정(new window : QueryBrowseAndEdit_PTextEdit)
2. Crawling 시작 : start(start_btn)
3. 결과를 table로 나타내기 : 나타낼 data의 키워드 선택(SelectKeyword_cbox), data를 표현할 table(ViewResult_table)
4. 결과물 저장하기 : SaveAsFile(SaveAsFIle_btn)

## 진행 과정(수정될 수 있음)
1. query할 keywords 받기(직접 입력, 파일입력, 직접 수정)
2. Crawling하기
3. Crawling한 Result결과 받기
4. UI에 선택한 keyword에 해당하는 data를 table에 나타내기
5. data(result)를 excel로 저장하기