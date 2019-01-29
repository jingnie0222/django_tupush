from django.shortcuts import render, HttpResponse, redirect
from django.forms.models import model_to_dict
from webqo import models
from utils import pagination
from utils import urlhandle
import time, json
import requests
import sys
from bs4 import BeautifulSoup
import difflib
import re


# Create your views here.
def auth(func):
    def inner(request, *args, **kwargs):
        login_url = "https://login.sogou-inc.com/?appid=1220&sso_redirect=http://webqa.web.sjs.ted/login&targetUrl="
        try:
            user_id = request.COOKIES.get('uid')
            if not user_id:
                return redirect(login_url)
        except:
            return redirect(login_url)
        return func(request, *args, **kwargs)

    return inner


# @auth

def debug(request):
    user_id = "zhangjingjun"
    #user_id = request.COOKIES.get('uid')
    if request.method == 'GET':
        page = request.GET.get('page')
        current_page = 1
        if page:
            current_page = int(page)
        try:
            # req_list = models.DebugQo.objects.filter(user_fk_id=user_id)
            req_list = models.DebugQo.objects.order_by('id')[::-1]
            page_obj = pagination.Page(current_page, len(req_list), 8, 5)
            data = req_list[page_obj.start:page_obj.end]
            page_str = page_obj.page_str("/webqo/debug?page=")
        except Exception as e:
            print(e)
            pass
        return render(request, 'webqo/debug.html', {'user_id': user_id, 'req_lst': data, 'page_str': page_str})

    elif request.method == 'POST':
        ret = {
            'status': True,
            'error': None,
            'data': None
        }
        inputHost = request.POST.get('inputHost')
        query_from = request.POST.get('query_from')
        forceQuery = request.POST.get('forceQuery')
        query = request.POST.get('query')

        if forceQuery == '':
            forceQuery = '0'
        else:
            forceQuery = forceQuery

        if query_from == '':
            query_from = 'web'
        else:
            query_from = query_from

        params = {
            'queryString': query,
            'queryFrom': query_from,
            'forceQuery': forceQuery,
        }

        params_gbk = urlhandle.urlencode(params, 'gbk', 'ignore')

        headers = {"Content-type": "application/x-www-form-urlencoded;charset=UTF-16LE"}

        try:
            resp = requests.post(inputHost, data=params_gbk, headers=headers)
            status = resp.reason
            if status != 'OK':
                print(sys.stderr, query, status)
                ret['error'] = 'Error:未知的请求类型'
                ret['status'] = False
                return ret

            data = BeautifulSoup(resp.text)
            ret['data'] = data.prettify()

        except Exception as e:
            print(e)
            print(sys.stderr, sys.exc_info()[0], sys.exc_info()[1])
            ret['error'] = "Error:" + str(e)
            ret['status'] = False
        return HttpResponse(json.dumps(ret))




def debug_diff(request):
    data = {
        'total_data': None,
        'jzwd_data': None,
        'rec_data': None,
        'int_data': None,
    }
    ret = {
        'status': True,
        'error': None,
        'data': None
    }
    inputHost = request.POST.get('inputHost')
    forceQuery = request.POST.get('forceQuery')
    query_from = request.POST.get('query_from')

    inputHost_diff = request.POST.get('inputHost_diff')
    forceQuery_diff = request.POST.get('forceQuery_diff')
    query_from_diff = request.POST.get('query_from_diff')

    query = request.POST.get('query')

    if forceQuery == '':
        forceQuery = '0'
    else:
        forceQuery = forceQuery

    if forceQuery_diff == '':
        forceQuery_diff = '0'
    else:
        forceQuery_diff = forceQuery_diff

    if query_from == '':
        query_from = 'web'
    else:
        query_from = query_from

    if query_from_diff == '':
        query_from_diff = 'web'
    else:
        query_from_diff = query_from_diff


    params = {
        'queryString': query,
        'queryFrom': query_from,
        'forceQuery': forceQuery,
    }

    params_diff = {
        'queryString': query,
        'queryFrom': query_from_diff,
        'forceQuery': forceQuery_diff,
    }

    params_gbk = urlhandle.urlencode(params, 'gbk', 'ignore')

    params_diff_gbk = urlhandle.urlencode(params_diff, 'gbk', 'ignore')

    headers = {"Content-type": "application/x-www-form-urlencoded;charset=UTF-16LE"}

    try:
        resp = requests.post(inputHost, data=params_gbk, headers=headers)
        resp_diff = requests.post(inputHost_diff, data=params_diff_gbk, headers=headers)
        status = resp.reason
        status_diff = resp_diff.reason

        if status != 'OK' or status_diff != 'OK':
            print(sys.stderr, query, status, status_diff)
            ret['error'] = 'Error:未知的请求类型'
            ret['status'] = False
            return ret

        total = BeautifulSoup(resp.text)
        total_diff = BeautifulSoup(resp_diff.text)

        jzwd = jzwd_diff = BeautifulSoup("精准问答结果为空")
        rec = rec_diff = BeautifulSoup("右侧推荐结果为空")
        int = int_diff = BeautifulSoup("兴趣推荐结果为空")

        for doc in total.find_all('doc'):
            pvtype = doc.item['pvtype']
            if re.search(r'[^ ]*_[^ ]*_[^ ]*', pvtype):
                jzwd = doc
                continue
            if re.search(r'[^ ]*_[^ ]*', pvtype):
                rec = doc
                continue
            if '13' == pvtype:
                int = doc
                continue

        for doc in total_diff.find_all('doc'):
            pvtype = doc.item['pvtype']
            if re.search(r'[^ ]*_[^ ]*_[^ ]*', pvtype):
                jzwd_diff = doc
                continue
            if re.search(r'[^ ]*_[^ ]*', pvtype):
                rec_diff = doc
                continue
            if '13' == pvtype:
                int_diff = doc
                continue

        diff = difflib.HtmlDiff()

        data['total_data'] = diff.make_table(total.prettify().splitlines(), total_diff.prettify().splitlines()).replace(
            'nowrap="nowrap"', '')
        data['jzwd_data'] = diff.make_table(jzwd.prettify().splitlines(), jzwd_diff.prettify().splitlines()).replace(
            'nowrap="nowrap"', '')
        data['rec_data'] = diff.make_table(rec.prettify().splitlines(), rec_diff.prettify().splitlines()).replace(
            'nowrap="nowrap"', '')
        data['int_data'] = diff.make_table(int.prettify().splitlines(), int_diff.prettify().splitlines()).replace(
            'nowrap="nowrap"', '')

        ret['data'] = data


    except Exception as e:
        print(e)
        print(sys.stderr, sys.exc_info()[0], sys.exc_info()[1])
        ret['error'] = "Error:" + str(e)
        ret['status'] = False
    return HttpResponse(json.dumps(ret))

# @auth
def debug_save(request):
    user_id = "zhangjingjun"
    # user_id = request.COOKIES.get('uid')
    ret = {
        'status': True,
        'error': None,
        'data': None
    }
    inputHost = request.POST.get('inputHost')
    inputExpId = request.POST.get('inputExpId')
    query_from = request.POST.get('query_from')
    query = request.POST.get('query')

    try:
        models.DebugQo.objects.create(host_ip=inputHost, exp_id=inputExpId, query_from=query_from, query=query,
                                      user_fk_id=user_id)

        ret['inputHost'] = inputHost
        ret['inputExpId'] = inputExpId
        ret['query_from'] = query_from
        ret['query'] = query
    except Exception as e:
        ret['error'] = "Error:" + str(e)
        print(e)
        ret['status'] = False
    return HttpResponse(json.dumps(ret))


# @auth
def debug_del(request):
    ret = {
        'status': True,
        'error': None,
        'data': None
    }
    req_id = request.POST.get('line_id')
    try:
        models.DebugQo.objects.filter(id=req_id).delete()
    except Exception as e:
        ret['status'] = False
        ret['error'] = "Error:" + str(e)
        print(e)
    return HttpResponse(json.dumps(ret))


# @auth
def auto_cancel(request):
    ret = {'status': True, 'error': None, 'data': None}
    try:
        re_add_task_d = request.POST.get('task_id')
        models.Qps.objects.filter(id=re_add_task_d).update(status=6)
    except Exception as e:
        ret['error'] = 'error:' + str(e)
        ret['status'] = False
    return HttpResponse(json.dumps(ret))


# @auth
def auto_restart(request):
    user_id='zhangjingjun'
    # user_id = request.COOKIES.get('uid')
    ret = {'status': True, 'error': None, 'data': None}
    re_add_task_id = request.POST.get('task_id')
    try:
        task_detail = models.Qps.objects.get(id=re_add_task_id)
        testitem = models.Qps.objects.filter(id=re_add_task_id).values('testitem')

        if testitem.first()['testitem'] == 1:
            task_detail_todic = model_to_dict(task_detail)
            task_detail_todic.pop('id')
            task_detail_todic['create_time'] = get_now_time()
            task_detail_todic['start_time'] = ""
            task_detail_todic['end_time'] = ""
            task_detail_todic['testitem'] = 1
            task_detail_todic['status'] = 0
            task_detail_todic['errorlog'] = ""
            task_detail_todic['cost_test'] = ""
            task_detail_todic['cost_base'] = ""
            task_detail_todic['runningIP'] = ""
            task_detail_todic['user'] = user_id
            models.Qps.objects.create(**task_detail_todic)
        elif testitem.first()['testitem'] == 0:
            task_detail_todic = model_to_dict(task_detail)
            task_detail_todic.pop('id')
            task_detail_todic['create_time'] = get_now_time()
            task_detail_todic['start_time'] = ""
            task_detail_todic['end_time'] = ""
            task_detail_todic['testitem'] = 0
            task_detail_todic['status'] = 0
            task_detail_todic['errorlog'] = ""
            task_detail_todic['cost_test'] = ""
            task_detail_todic['cost_base'] = ""
            task_detail_todic['runningIP'] = ""
            task_detail_todic['user'] = user_id
            models.Qps.objects.create(**task_detail_todic)
    except Exception as e:
        print(e)
        ret['error'] = 'error:' + str(e)
        ret['status'] = False
    return HttpResponse(json.dumps(ret))


# @auth
def auto_detail(request, task_id):
    user_id = "zhangjingjun"
    # user_id = request.COOKIES.get('uid')
    task_detail = models.Qps.objects.filter(id=task_id)
    # diff_detail = models.Diff.objects.filter(diff_fk_id=task_id)

    testitem = models.Qps.objects.filter(id=task_id).values('testitem')

    page = request.GET.get('page')
    current_page = 1
    if page:
        current_page = int(page)

    if testitem.first()['testitem'] == 1:

        return render(request, 'webqo/auto_detail.html',
                      {'user_id': user_id, 'task_detail': task_detail})
    # elif testitem.first()['testitem'] == 0:
    #     page_obj = pagination.Page(current_page, len(diff_detail), 3, 9)
    #     data = diff_detail[page_obj.start:page_obj.end]
    #     page_str = page_obj.page_str('auto_detail_' + task_id + '.html?page=')
    #
    #     return render(request, 'webqo/diff_detail.html',
    #                   {'user_id': user_id, 'task_detail': task_detail, 'diff_detail': diff_detail, 'li': data,
    #                    'page_str': page_str})


# @auth
def auto_add(request):
    user_id = "zhangjingjun"
    # user_id = request.COOKIES.get('uid')
    ret = {'status': True, 'errro': None, 'data': None}
    test_svn = str_dos2unix(request.POST.get('qo_testsvn'))
    base_svn = str_dos2unix(request.POST.get('qo_basesvn'))
    newconfip = str_dos2unix(request.POST.get('new_conf_ip'))
    newconfuser = str_dos2unix(request.POST.get('new_conf_user'))
    newconfpassw = str_dos2unix(request.POST.get('new_conf_pass'))
    newconfpath = str_dos2unix(request.POST.get('new_conf_path'))
    newdataip = str_dos2unix(request.POST.get('new_data_ip'))
    newdatauser = str_dos2unix(request.POST.get('new_data_user'))
    newdatapassw = str_dos2unix(request.POST.get('new_data_pass'))
    newdatapath = str_dos2unix(request.POST.get('new_data_path'))
    press_qps = str_dos2unix(request.POST.get('qo_qps'))
    press_time = str_dos2unix(request.POST.get('qo_press_time'))
    press_expid = str_dos2unix(request.POST.get('qo_press_expid'))
    press_rate = str_dos2unix(request.POST.get('qo_press_rate'))

    query_ip = str_dos2unix(request.POST.get('query_ip'))
    query_user = str_dos2unix(request.POST.get('query_user'))
    query_pwd = str_dos2unix(request.POST.get('query_pwd'))
    query_path = str_dos2unix(request.POST.get('query_path'))

    testtag = str_dos2unix(request.POST.get('testtag'))

    flag = request.POST.get('radio_select')
    print("flag:", flag)
    print("press_expid", type(press_expid))
    print("press_rate", type(press_rate))

    if flag == 'press':
        if press_qps == "":
            press_qps = 1000
        if press_time == "":
            press_time = 30
        if press_expid == "":
            press_expid = 0
        if press_rate == "":
            press_rate = 0
        # print('test_svn:'+test_svn,'base_svn:'+base_svn,'newconfip:'+newconfip,'newconfuser:'+newconfuser,'newconfpassw:'+newconfpassw,'newconfpath:'+newconfpath,'newdataip:'+newdataip,'newdatauser:'+newdatauser,'newdatapassw:'+newdatapassw,'newdatapath:'+newdatapath)
        try:
            models.Qps.objects.create(create_time=get_now_time(), user=user_id, testitem=1, testsvn=test_svn,
                                      basesvn=base_svn,
                                      newconfip=newconfip, newconfuser=newconfuser, newconfpassw=newconfpassw,
                                      newconfpath=newconfpath, newdataip=newdataip, newdatauser=newdatauser,
                                      newdatapassw=newdatapassw, newdatapath=newdatapath, press_qps=press_qps,
                                      press_time=press_time, press_expid=press_expid, press_rate=press_rate,
                                      testtag=testtag)
        except Exception as e:
            print(e)
            ret['error'] = 'error:' + str(e)
            ret['status'] = False
        return HttpResponse(json.dumps(ret))
    elif flag == 'longdiff':
        if press_expid == "":
            press_expid = 0
        if press_rate == "":
            press_rate = 0
        try:
            models.Qps.objects.create(create_time=get_now_time(), user=user_id, testitem=0, testsvn=test_svn,
                                      basesvn=base_svn,
                                      newconfip=newconfip, newconfuser=newconfuser, newconfpassw=newconfpassw,
                                      newconfpath=newconfpath, newdataip=newdataip, newdatauser=newdatauser,
                                      newdatapassw=newdatapassw, newdatapath=newdatapath, press_expid=press_expid,
                                      press_rate=press_rate, query_ip=query_ip, query_user=query_user,
                                      query_pwd=query_pwd,
                                      query_path=query_path, testtag=testtag)
        except Exception as e:
            print(e)
            ret['error'] = 'error:' + str(e)
            ret['status'] = False
        return HttpResponse(json.dumps(ret))


# @auth
def auto(request, page_id):
    user_id = "zhangjingjun"
    # user_id = request.COOKIES.get('uid')
    if page_id == '':
        page_id = 1
    task_list = models.Qps.objects.order_by('id')[::-1]
    current_page = page_id
    current_page = int(current_page)
    page_obj = pagination.Page(current_page, len(task_list), 16, 9)
    data = task_list[page_obj.start:page_obj.end]
    page_str = page_obj.page_str("webqo/auto")

    return render(request, 'webqo/auto.html',{'user_id': user_id, 'req_lst': data, 'page_str': page_str})



