import requests
from pathlib import Path
import ast

from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver import ActionChains
from multiprocessing import Process
import multiprocessing
import json
import pprint
from urllib import parse


def get_date(target_url):
    # https://blog.naver.com/ggtourkorea/222205886152
    # ttps://blog.naver.com/matsu2/222154600781
    idst = find_index(target_url, '/')[2] + 1
    idend = find_index(target_url, '/')[3]  # logNo start
    blog_id = target_url[idst:idend]
    log_no = target_url[idend + 1:]
    response = requests.get(
        'https://blog.naver.com/PostView.nhn?blogId={}&logNo={}&redirect=Dlog&widgetTypeCall=true&directAccess=false'.format(
            blog_id, log_no))
    soup = bs(str(response.text), 'html.parser')
    try:
        date = soup.find_all(attrs={'class': 'date fil5 pcol2 _postAddDate'})[0].get_text()
    except:
        try:
            date = soup.find_all(attrs={'class': 'se_publishDate pcol2'})[0].get_text()
        except:
            date = '오류발생, 해당 질의조건과 url을 알려주십시오'
    return date

def find_index(data, target):
    res = []
    lis = data
    while True:
        try:
            res.append(lis.index(target) + (res[-1] + 1 if len(res) != 0 else 0))  # +1의 이유 : 0부터 시작이니까
            lis = data[res[-1] + 1:]
        except:
            break
    return res
def get_blog_posting2(id, cnt):
    """
    설명 : [파라미터 중 id]를 네이버 ID로 가진 사용자의 블로그의 포스팅 타이틀과 포스팅 url을 지정된 개수([피라미터 중 cnt])만큼 가져옴.
    사용법 : get_blog_posting(사용자 id, 수집 개수)
    return값
    * return_string, title_url *
    1. return_string = '입력한 수량이 블로그 전체 게시물보다 많습니다.\n블로그의 전체 게시물을 가져옵니다.fin' 혹은, 'fin'
        전자 : 입력수량 > 전체 게시물 수량
        후자 : 입력수량 <= 전체 게시물 수량
    2. title_url : [[제목1, 주소1][제목2, 주소2] ... ]의 형식
    """
    print("id, cnt",id, cnt)
    try:
        header = {'content-type':'application/x-www-form-urlencoded; charset=utf-8',
                'referer': 'https://blog.naver.com/PostList.nhn?blogId=zawe1&categoryNo=0&from=postList/',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}

        url = 'https://blog.naver.com/PostTitleListAsync.nhn?blogId={}&viewdate=&currentPage=1&categoryNo=0&parentCategoryNo=&countPerPage=30'.format(id)
        status = requests.get(url,headers = header)
        if  status.status_code== 404:
            return "-1", ''

        data = (status.text).replace("\\", "")
        data = json.loads(data)
        pprint.pprint(data)
        total_count = data['totalCount']
        print("total_count :",total_count)
        # pprint.pprint(data)
        return_string = ''
        if (int(data['totalCount']) < cnt):
            return_string += '입력한 수량이 블로그 전체 게시물보다 많습니다.\n블로그의 전체 게시물을 가져옵니다.'
            cnt = int(data['totalCount'])  # 전체 게시물 개수로 설정(강제 수량 다운그레이드)

        if (cnt == 0):
            print("in here")
            try:
                return_string += '블로그의 전체 게시물을 가져옵니다'
                cnt = int(total_count)
            except Exception as e:
                print("if :", e)

        print(cnt)
        k = 1
        title_url = []
        for i in range(1, cnt // 30 + 2):  # 페이지(api)
            url = 'https://blog.naver.com/PostTitleListAsync.nhn?blogId=' + str(id) + '&viewdate=&currentPage=' + str(i) + '&categoryNo=0&parentCategoryNo=&countPerPage=30'
            data = (requests.get(url).text).replace("\\", "")
            data = json.loads(data)

            for j in range(len(data['postList'])):  # api 페이지 안에 있는 포스팅
                log_no = data['postList'][j]['logNo']  # 블로그 포스팅 번호?
                blog_url = "https://blog.naver.com/" + id + "/" + log_no
                title = parse.unquote(data['postList'][j]['title']).replace('+', ' ')
                date = data['postList'][j]['addDate']
                title_url.append([title, blog_url, date, cnt])
                if k >= cnt:  # 총량을 검사하는 조건문
                    break
                k += 1

        return return_string, title_url

    except Exception as e:
        print("여기에요 여기",e)
def get_title(target_url):
    idst = find_index(target_url, '/')[2] + 1
    idend = find_index(target_url, '/')[3]  # logNo start
    response = requests.get(
        'https://blog.naver.com/PostView.nhn?blogId={}&logNo={}&redirect=Dlog&widgetTypeCall=true&directAccess=false'.format(
            target_url[idst:idend], target_url[idend + 1:]))
    soup = bs(str(response.text), 'html.parser')
    title = soup.find_all(attrs={'property': 'og:title'})[0]['content']
    return title, target_url[idst:idend]



def get_result(keywords, urlS, target, driver_path, processN, show_chrome):
    # print(multiprocessing.current_process().name)
    # print(processN)
    def view(target_url, keyword, driver, rank=False):
        """
        설명 : [파라미터 중 keyword]를 필수포함 검색어(검색연산자 "")로 네이버 검색시
                view 탭에서 [파라미터 중 target_url]을 URL로 가지는 포스팅이 있는지 확인함.
                추가적으로 그 포스팅이 검색결과에서 몇 번째 순위에 위치하는지도 추출할 수 있음.
        사용법 : view(대상 url, 필수포함 검색어, 크롬드라이버(chromium)위치, 순위 추출여부(기본 : Falsel))
        return 값
            경우
            1. rank=False(순위추출 x)의 경우, '노출' 혹은 '미노출'
            2. rank=True(순위추출 o)의 경우, 순위(숫자) 혹은 '미노출'
        """
        # st_t = time.time()
        try:
            if rank == False:
                keyword = '"{}"'.format(keyword)
                driver.get("https://search.naver.com/search.naver?where=view&sm=tab_jum&query={}&qvt=0".format(keyword))  # 키워드 검색
                # print("https://search.naver.com/search.naver?where=view&sm=tab_jum&query={}&qvt=0".format(keyword))

                driver.implicitly_wait(time_to_wait=0.3)
            elif rank == True:
                keyword = '{}'.format(keyword)
                driver.get("https://search.naver.com/search.naver?where=view&sm=tab_jum&query={}&qvt=0".format(keyword))  # 키워드 검색
                # print("https://search.naver.com/search.naver?where=view&sm=tab_jum&query={}&qvt=0".format(keyword))
                driver.implicitly_wait(time_to_wait=0.3)

            before_len_of_url = None
            n_for_break = 0
            while True:
                li = driver.find_element_by_xpath('//li[@class="bx _svp_item"]')
                li = driver.execute_script("return arguments[0].parentNode;", li)
                # print('//*[@id="main_pack"]/section[{}]/div/div[2]/panel-list/div/more-contents/div/ul'.format(1 if rank == True else 2))
                html = li.get_attribute('innerHTML')
                soup = bs(html, 'html.parser')

                urlS = [k.attrs['href'] for k in soup.find_all(attrs={'class': 'api_txt_lines total_tit'})]  # JUST 노출 확인
                if rank == False and target_url in urlS:
                    returns = '노출'
                    break
                elif rank == True and target_url in urlS:
                    child = driver.find_element_by_xpath('//a[@href="' + target_url + '"]')
                    parent = driver.execute_script("return arguments[0].parentNode;", child)
                    parent = driver.execute_script("return arguments[0].parentNode;", parent)
                    html = parent.get_attribute('outerHTML')
                    soup = bs(html, 'html.parser')
                    rank_n = soup.find('li').attrs['data-cr-rank']
                    returns = rank_n
                    break

                if before_len_of_url != None and before_len_of_url == len(urlS):
                    n_for_break += 1
                else:
                    n_for_break = 0
                # print(n_for_break)
                if n_for_break >= 10:
                    returns = '미노출'
                    # print(len(urlS))
                    break
                A = driver.find_elements_by_xpath('//li[@class="bx _svp_item"]')
                html = A[-1].get_attribute('outerHTML')
                soup = bs(html, 'html.parser')
                rank_n = soup.find('li').attrs['data-cr-rank']
                # print(rank_n)
                if int(rank_n) > 40:
                    returns = '미노출'
                    break

                before_len_of_url = len(urlS)

                last = driver.find_element_by_xpath('//*[@id="footer"]')
                action = ActionChains(driver)
                action.move_to_element(last).perform()
                driver.implicitly_wait(time_to_wait=0.3)
        # print(time.time()-st_t)
        except Exception as e:
            # print(e)
            returns = '미노출'

        return returns   #   #

    def site(keyword, target_url):  # 인자값으로 크롤링해온 블로그 URL과 포스트 Title을 집어넣음
        """
        설명 : [파라미터 중 keyword]를 필수포함 검색어로 검색시에, 통합검색 2page부터 시작되는 웹사이트 검색결과에서 해당 URL이 발견되는지 확인함.
                (1페이지의 웹사이트 결과도 2페이지에 포함되서 나옴, 웹사이트 탭 존재x -> 2페이지부터를 웹사이트 탭으로 생각하기)
        사용법 : site(필수포함 검색어(키워드), 찾을 url(대상이 되는 url))
        return 값 : 'exist' 혹은 'notExist'
        """
        flag = False    #만약 비교 중 들어온 siteUrl이 있으면 True로 바뀜
        # kl = 0 #rank 필요시 사용
        for i in range(0, 10): #네이버 정책상 검색은 10페이지가 limit임 즉 100개까지만 들고옴
            page_cnt = 0
            url = 'https://search.naver.com/search.naver?display=10&f=&filetype=0&query="{}"&sm=tab_pge&start={}&where=web&qvt=0'.format(keyword, i * 10)
            req = requests.get(url)
            html = req.text
            soup = bs(html, 'html.parser')   #setting
            # print(soup.prettify())

            for div in soup.find_all('div', {'class': 'total_source'}):
                # kl += 1
                if flag == True:
                    break
                for a in div('a', {'target': '_blank'}, href=True):
                    page_cnt += 1
                    # print(a['href'])
                    if a['href'] == target_url:
                        flag = True
                    break
            if flag == True:
                break

            if page_cnt < 10:   #마지막 페이지에 10개가 나오지 않는 경우는 break 해버림
                break
        if flag == True:
            # print(kl)
            return "노출"

        else:
            # print(kl)
            return "미노출"

    def video(target_url, keyword, driver, rank=False):
        """
        설명 : [파라미터 중 keyword]를 필수포함 검색어(검색연산자 "")로 네이버 검색시
                video 탭에서 [파라미터 중 target_url]을 URL로 가지는 포스팅이 있는지 확인함.
                추가적으로 그 포스팅이 검색결과에서 몇 번째 순위에 위치하는지도 추출할 수 있음.
        사용법 : video(대상 url, 필수포함 검색어, 크롬드라이버(chromium)위치, 순위 추출여부(기본 : Falsel))
        return 값
            경우
            1. rank=False(순위추출 x)의 경우, '노출' 혹은 '미노출'
            2. rank=True(순위추출 o)의 경우, 순위(숫자) 혹은 '미노출'
        """
        # st_t = time.time()
        try:
            keyword = '"{}"'.format(keyword)
            driver.get("https://search.naver.com/search.naver?where=video&sm=tab_jum&query={}&qvt=0".format(keyword))  # 키워드 검색
            # print("https://search.naver.com/search.naver?where=video&sm=tab_jum&query={}&qvt=0".format(keyword))
            driver.implicitly_wait(time_to_wait=0.3)

            before_len_of_url = None
            n_for_break = 0
            while True:
                li = driver.find_element_by_xpath('//li[@class="video_item _svp_item"]')
                li = driver.execute_script("return arguments[0].parentNode;", li)
                html = li.get_attribute('innerHTML')
                soup = bs(html, 'html.parser')

                urlS = [k.attrs['href'] for k in soup.find_all(attrs={'class': 'info_title'})]  # JUST 노출 확인
                if rank == False and exposure(urlS, target_url):
                    returns = '노출'
                    break
                elif rank == True and exposure(urlS, target_url):
                    child = driver.find_element_by_xpath('//a[@href="' + target_url + '"]')
                    parent = driver.execute_script("return arguments[0].parentNode;", child)
                    parent = driver.execute_script("return arguments[0].parentNode;", parent)
                    parent = driver.execute_script("return arguments[0].parentNode;", parent)
                    html = parent.get_attribute('outerHTML')
                    soup = bs(html, 'html.parser')
                    rank_n = soup.find('li').attrs['data-cr-rank']
                    returns = rank_n
                    break

                if before_len_of_url != None and before_len_of_url == len(urlS):
                    n_for_break += 1
                else:
                    n_for_break = 0
                # print(n_for_break)
                if n_for_break >= 10:
                    returns = '미노출'
                    # print(len(urlS))
                    break
                A = driver.find_elements_by_xpath('//li[@class="video_item _svp_item"]')
                html = A[-1].get_attribute('outerHTML')
                soup = bs(html, 'html.parser')
                rank_n = soup.find('li').attrs['data-cr-rank']
                # print(rank_n)
                if int(rank_n) > 40:
                    returns = '미노출'
                    break

                before_len_of_url = len(urlS)

                last = driver.find_element_by_xpath('//*[@id="footer"]')
                action = ActionChains(driver)
                action.move_to_element(last).perform()
                driver.implicitly_wait(time_to_wait=0.3)
        # print(time.time()-st_t)
        except Exception as e:
            # print(e)
            returns = '미노출'

        return returns

    def image(target_url, keyword, driver):
        """
        설명 : [파라미터 중 keyword]를 필수포함 검색어(검색연산자 "")로 네이버 검색시
                video 탭에서 [파라미터 중 target_url]을 URL로 가지는 포스팅이 있는지 확인함.
        사용법 : image(대상 url, 필수포함 검색어, 크롬드라이버(chromium)위치)
        return 값
         : '노출' 혹은 '미노출'
        """
        # st_t = time.time()
        try:
            keyword = '"{}"'.format(keyword)
            driver.get("https://search.naver.com/search.naver?where=image&sm=tab_jum&query={}&qvt=0".format(keyword))  # 키워드 검색
            driver.implicitly_wait(time_to_wait=0.3)

            before_len_of_url = None
            n_for_break = 0
            while True:
                div_root = driver.find_element_by_xpath('//div[@class="photo_tile _grid"]')
                html = div_root.get_attribute('innerHTML')
                soup = bs(html, 'html.parser')

                urlS = [k.attrs['href'] for k in soup.find_all(attrs={'class': 'text'})]  # JUST 노출 확인
                # print(urlS)
                if exposure(urlS, target_url):
                    returns = '노출'
                    break

                if before_len_of_url != None and before_len_of_url == len(urlS):
                    n_for_break += 1
                else:
                    n_for_break = 0
                # print('a', n_for_break)
                if n_for_break >= 10:
                    returns = '미노출T'
                    # print(len(urlS))
                    break
                # print(len(urlS))
                if len(urlS) > 40:
                    returns = '미노출C'
                    break

                before_len_of_url = len(urlS)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                driver.implicitly_wait(time_to_wait=0.3)
        # print(time.time()-st_t)
        except Exception as e:
            # print(e)
            returns = '미노출E'
        return returns

    def find_index(data, target):
        res = []
        lis = data
        while True:
            try:
                res.append(lis.index(target) + (res[-1] + 1 if len(res) != 0 else 0)) #+1의 이유 : 0부터 시작이니까
                lis = data[res[-1]+1:]
            except:
                break
        return res

    def exposure(urlS, target_url):
        FlagExposure = False
        for i in urlS:
            if target_url[target_url.index('//')+2:] in i:
                FlagExposure = True
                break
        return FlagExposure

    def get_title(target_url):
        idst = find_index(target_url, '/')[2] + 1
        idend = find_index(target_url, '/')[3] # logNo start
        response = requests.get('https://blog.naver.com/PostView.nhn?blogId={}&logNo={}&redirect=Dlog&widgetTypeCall=true&directAccess=false'.format(target_url[idst:idend], target_url[idend+1:]))
        soup = bs(str(response.text), 'html.parser')
        title = soup.find_all(attrs={'property': 'og:title'})[0]['content']
        return title, target_url[idst:idend]

    def get_date(target_url):
        # https://blog.naver.com/ggtourkorea/222205886152
        # ttps://blog.naver.com/matsu2/222154600781
        idst = find_index(target_url, '/')[2] + 1
        idend = find_index(target_url, '/')[3] # logNo start
        blog_id = target_url[idst:idend]
        log_no = target_url[idend + 1:]
        response = requests.get('https://blog.naver.com/PostView.nhn?blogId={}&logNo={}&redirect=Dlog&widgetTypeCall=true&directAccess=false'.format(blog_id, log_no))
        soup = bs(str(response.text),'html.parser')
        try:
            date = soup.find_all(attrs={'class': 'date fil5 pcol2 _postAddDate'})[0].get_text()
        except:
            try:
                date = soup.find_all(attrs={'class': 'se_publishDate pcol2'})[0].get_text()
            except:
                date = '오류발생, 해당 질의조건과 url을 알려주십시오'
        return date

    def replaceURLCODE(keyword):
        keyword = keyword.replace('&', r'%26')
        keyword = keyword.replace('/', r'%2F')
        keyword = keyword.replace(':', r'%3A')
        keyword = keyword.replace('?', r'%3F')
        keyword = keyword.replace('=', r'%3D')
        return keyword
    if show_chrome == False:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('lang=ko_KR')
        driver = webdriver.Chrome(str(driver_path), chrome_options=chrome_options)  # 드라이버 설정
    else:
        driver = webdriver.Chrome(driver_path) # 드라이버 설정
    if target != 'viewlist':
        result = {'blog': [],
            'date': [],
            'img': [],
            'site': [],
            'url': urlS,
            'video': []
        }
    else:
        result = {'date': [],
                'keyword': keywords,
                'rank': [],
                'title': [],
                'url': urlS
        }
    for keyword, url in zip(keywords, urlS):
        if target != 'viewlist':
            result['blog'].append(view(url, replaceURLCODE(keyword), driver))
            result['date'].append(get_date(url))
            result['img'].append(image(url, replaceURLCODE(keyword), driver))
            result['site'].append(site(replaceURLCODE(keyword), url))
            result['video'].append(video(url, replaceURLCODE(keyword), driver))
        else:
            result['date'].append(get_date(url))
            result['rank'].append(view(url, replaceURLCODE(keyword), driver, rank=True))
            result['title'].append(get_title(url))
    driver.quit()
    print(multiprocessing.current_process().name, "'s chromium driver finished! :", processN)

    f = open('tmp/Process-{}.txt'.format(processN), 'w', encoding='UTF8')
    print(result, file=f)
    f.close()

    print('******************', multiprocessing.current_process().name, 'FINISHED******************')


def main(keywords, urlS, target, driver_path):
    """
    사용법
    main(keywords, urlS, target, driver_path)
    keywords : 키워드
    urlS : URLS
    target : 'urllist', 'newlist', 'viewlist' 중 하나
    driver_path : 드라이버 경로
    """
    # print(__name__)
    Path('tmp').mkdir(parents=True, exist_ok=True)
    def get_maxProcessNAndshowChrome():
        f = open('NumberOfProcess.txt', 'r',encoding='UTF-8')
        max_processN = f.readlines()[-2]
        show_chrome = f.readlines()[-1]
        f.close()
        try:
            max_processN = int(max_processN[max_processN.index('Number of process :') + len('Number of process :'):])
            show_chrome = show_chrome[show_chrome.index('Show Chrome Tab :') + len('Show Chrome Tab :'):]
            show_chrome = True if 'True' in show_chrome or 'true' in show_chrome else False
            return max_processN, show_chrome
        except:
            print(max_processN[max_processN.index('Number of process :') + len('Number of process :'):])
            return 'NumberOfProcess.txt에서의 잘못된 입력, 에러발생'

    def reading(i):
        with open('tmp/Process-{}.txt'.format(i), 'r', encoding='UTF8') as f:
            s = f.read()
            whip = ast.literal_eval(s)
        return whip

    def get_NPer_process(p, n):
        tmp_ = (n // p + 1) if n % p != 0 else n // p 
        res = [tmp_ for i in range(n // tmp_)] + ([n % tmp_] if n % tmp_ != 0 else [])
        return res, len(res)

    if __name__ == 'crawlingFunction':
        # multiprocessing.freeze_support()
        """
        Structure of both keywords and urlS
        [[],[]] -> newlist -> 한 원소당 하나의 질의
        [[]] -> urlist -> 한 원소에 모든 질의가 담김
        target : 'urllist' or 'newlist' or 'viewlist'
        """
        if target not in ['urllist', 'newlist', 'viewlist']: return 'Exception : Not valid target'
        if target != 'viewlist':
            result = {'blog': [],
                    'date': [],
                    'img': [],
                    'site': [],
                    'url': [],
                    'video': []
            }
        else:
            result = {'date': [],
                    'keyword': [],
                    'rank': [],
                    'title': [],
                    'url': []
            }
        # print(keywords, urlS)
        for keywords_, urlS_ in zip(keywords, urlS): # urllist : for문 1회 반복, newlist : for문 원소 개수만큼 반복
            procs = []
            len_of_data = len(keywords_) if len(keywords_) == len(urlS_) else 'Diff, Error'
            print("len_of_data :",len_of_data)

            if len_of_data == 'Diff, Error': return len_of_data

            max_processN, show_chrome = get_maxProcessNAndshowChrome()
            if type(max_processN) == str:
                return max_processN

            if len_of_data < 20: max_processN = 1
            from_, to_ = 0, 0
            intervalList, loop = get_NPer_process(max_processN, len_of_data)
            for interval, i in zip(intervalList, range(loop)):
                from_ = to_         # 0, 3, 6
                to_ = from_ + interval  # 3, 6, 9
                print(from_, to_, i+1)
                proc = Process(target=get_result, args=(keywords_[from_:to_], urlS_[from_:to_], target, driver_path, i + 1, show_chrome))6
                proc.start()
                procs.append(proc)

            print("Processes Started")

            for proc in procs:
                proc.join()
            print("Processes Joined")
            # print(loop)
            if target != 'viewlist':
                result['blog'].append([])
                result['date'].append([])
                result['img'].append([])
                result['site'].append([])
                result['url'].append([])
                result['video'].append([])
            else:
                result['date'].append([])
                result['keyword'].append([])
                result['rank'].append([])
                result['title'].append([])
                result['url'].append([])
            for i in range(loop):
                # print('in loop', i)
                dic = reading(i + 1)

                if target != 'viewlist':
                    result['blog'][-1] += (dic['blog'])
                    result['date'][-1] += (dic['date'])
                    result['img'][-1] += (dic['img'])
                    result['site'][-1] += (dic['site'])
                    result['url'][-1] += (dic['url'])
                    result['video'][-1] += (dic['video'])
                else:
                    result['date'][-1] += dic['date']
                    result['keyword'][-1] += dic['keyword']
                    result['rank'][-1] += dic['rank']
                    result['title'][-1] += dic['title']
                    result['url'][-1] += dic['url']
        # f = open('test1.txt','w')
        # print(result,file = f)
        # f.close()
        return result


# driver_dir = "..\\ROOT\\Programming\\AssociatedFiles\\chromedriver.exe"
# print(main(keywords, urlS, 'viewlist', driver_dir), file=f)


# cd "OneDrive - 인천광역시교육청\바탕 화면\외주 _ 블로그 크롤링"