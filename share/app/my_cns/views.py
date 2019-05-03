from django.shortcuts import render, redirect
from django.views import View, generic
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse

import json
import calendar
from my_cns.scrape_cns import *
from collections import deque

import datetime
import tempfile

import io,sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Create your views here.
class LoginView(View):
    def get(self, request, *args, **kwargs):
        context = {}

        # GETパラメータの文字列を取得
        get_params = request.GET.urlencode()
        next_to = request.GET.get('next_to')
        context['next'] = next_to

        return render(request, 'my_cns/login.html', context)

    def post(self, request, *args, **kwargs):
        context = {}
        username = request.POST.get('username')
        password = request.POST.get('password')

        # cns cookie, ログイン成功情報を取得
        cns_cookies, login_successed = get_cns_cookies(username, password)

        # ログイン送信後のリダイレクト先の決定
        # todo: next_toがない時、ログイン成功後にtopics_listへリダイレクト
        next_to = request.POST.get('next')
        if not login_successed:
            context['next'] = next_to
            response = render(request, 'my_cns/login.html', context)
            get_params = 'next_to=' + next_to
            response['location'] += '?' + get_params
        if next_to == 'None' or next_to == '':
            next_to = 'my_cns:topics_list'
            response = redirect(next_to)
        else:
            response = redirect(next_to)

        # ユーザのブラウザにcns cookieを保存
        for cookie in cns_cookies:
            response.set_cookie(cookie['name'], cookie['value'], 60*60*24)

        return response

class HomeView(View):
    '''
    CNSのhome.phpをスクレイピング
    '''
    # todo: https://cns.yamanashi.ac.jp/外のurlにアクセスする時の処理
    def get(self, request, *args, **kwargs):
        context = {}

        # todo: 使用可能なcookieの存在チェック
        hello = request.COOKIES.get('hello1')
        context['hello'] = hello

        cookies = request.COOKIES
        context = scrape_cns_home(cookies)

        # ログインに失敗した時の処理
        if 'failed_login' in context:
            response = redirect('my_cns:login')
            get_params = 'next_to=my_cns:home'
            response['location'] += '?' + get_params
            return response
            #return HttpResponseRedirect(reverse('my_cns:LoginView'))

        response = render(request, 'my_cns/home.html', context)
        response.set_cookie('hello1', 'hello_world1', 60*60)
        return response

class TopicsListView(View):
    def get(self, request, *args, **kwargs):
        context = {}

        # todo: 使用可能なcookieの存在チェック
        cookies = request.COOKIES

        page = 1
        context = scrape_cns_topicslist(cookies, page)

        # ログインに失敗した時の処理
        if 'failed_login' in context:
            response = redirect('my_cns:login')
            get_params = 'next_to=my_cns:topics_list'
            response['location'] += '?' + get_params
            return response
        # レスポンス
        response = render(request, 'my_cns/topicslist.html', context)
        #response.set_cookie('hello1', 'hello_world1', 60*60)
        return response

def get_topics(request, page):
    cookies = request.COOKIES
    context = scrape_cns_topicslist(cookies, page)
    # ログインに失敗した時の処理
    if 'failed_login' in context:
        response = redirect('my_cns:login')
        get_params = 'next_to=my_cns:topics_list'
        response['location'] += '?' + get_params
        return response
    print(context)
    return JsonResponse(context)

class TopicDetailView(View):
    def get(self, request, *args, **kwargs):
        context = {}

        # todo: 使用可能なcookieの存在チェック
        cookies = request.COOKIES

        # トピック詳細のid取得
        topic_id = request.GET.get('topic_id')

        # get送信でtopic_idがなかった時、トッピクリストへリダイレクト
        next_to = 'my_cns/topicslist.html'
        if topic_id == None:
            response = redirect('my_cns:topics_list')
            return response

        context = scrape_cns_topicsdetail(cookies, topic_id)

        # ログインに失敗した時の処理
        if 'failed_login' in context:
            response = redirect('my_cns:login')
            get_params = 'next_to=my_cns:topic_detail'
            response['location'] += '?' + get_params
            return response

        # レスポンス
        next_to = 'my_cns/topicsdetail.html'
        response = render(request, next_to, context)
        #response.set_cookie('hello1', 'hello_world1', 60*60)
        return response

class GetDownloadFileView(View):
    def get(self, request, *args, **kwargs):
        # todo: 使用可能なcookieの存在チェック
        cookies = request.COOKIES
        # ダウンロードid
        download_file_name = request.GET.get('download_file_name')
        download_id        = request.GET.get('download_id')
        download_file = get_cns_download_file(cookies, download_file_name, download_id)
        response = HttpResponse(download_file)
        context = {
            'messages': download_file
        }
        response = HttpResponse(download_file)
        response = render(request, 'my_cns/home.html', context)
#        with tempfile.TemporaryFile('w+') as f:
#            print(download_file, file=f)
        #f = open('test.pdf', 'wb')
        #f.write(download_file)

        #response = HttpResponse(f)
#        response = HttpResponse(f.read())
        #f.close()
        return response
