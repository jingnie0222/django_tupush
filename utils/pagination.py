#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'zhangjingjun'
__mtime__ = '2018/5/14'
# ----------Dragon be here!----------
              ┏━┓      ┏━┓
            ┏━┛ ┻━━━━━━┛ ┻━━┓
            ┃       ━       ┃
            ┃  ━┳━┛   ┗━┳━  ┃
            ┃       ┻       ┃
            ┗━━━┓      ┏━━━━┛
                ┃      ┃神兽保佑
                ┃      ┃永无BUG！
                ┃      ┗━━━━━━━━━┓
                ┃                ┣━┓
                ┃                ┏━┛
                ┗━━┓ ┓ ┏━━━┳━┓ ┏━┛
                   ┃ ┫ ┫   ┃ ┫ ┫
                   ┗━┻━┛   ┗━┻━┛
"""
from django.utils.safestring import mark_safe
class Page:
    def __init__(self,current_page,data_count,per_page_count=10,pager_num=5):
        self.current_page = current_page
        self.data_count = data_count
        self.per_page_count = per_page_count
        self.pager_num = pager_num
    @property
    def start(self):
        return (self.current_page-1)*self.per_page_count

    @property
    def end(self):
        return self.current_page * self.per_page_count

    @property
    def total_count(self):
        v,y = divmod(self.data_count,self.per_page_count)
        if y:
            v+=1
        return v

    def page_str(self,base_url):
        page_list = []
        if self.total_count < self.pager_num:
            start_index = 1
            end_index = self.total_count + 1
        else:
            if self.current_page <= (self.pager_num + 1)/2:
                start_index = 1
                end_index = self.pager_num + 1
            else:
                start_index = self.current_page - (self.pager_num - 1)/2
                end_index = self.current_page + (self.pager_num + 1)/2
                if (self.current_page+(self.pager_num - 1)/2) > self.total_count:
                    end_index = self.total_count+1
                    start_index = self.total_count - self.pager_num + 1

        if self.current_page == 1:
            prev = '<li class="page-item"><a class="page-link" href="javascript:void(0);" aria-label="Previous"><span aria-hidden="true">Previous</span></a></li>'
        else:
            prev = '<li class="page-item"><a class="page-link" href=%s%s aria-label="Previous"><span aria-hidden="true">Previous</span></a></li>' % (base_url,self.current_page -1)

        page_list.append(prev)

        for i in range(int(start_index),int(end_index)):
            temp = '<li class="page-item"><a class="page-link" href=%s%s>%s</a></li>' % (base_url, i, i)
            page_list.append(temp)

        if self.current_page == self.total_count:
            nex = '<li class="page-item"><a class="page-link" href="javascript:void(0);" aria-label="Next"><span aria-hidden="true">Next</span></a></li>'
        else:
            nex = '<li class="page-item"><a class="page-link" href=%s%s aria-label="Next"><span aria-hidden="true">Next</span></a></li>' % (base_url,self.current_page + 1)

        page_list.append(nex)

        # jump = """
        # <input type='text' /><a onclick=jumpTo(this,"%s?p=")>go</a>
        # <script>
        #     function jumpTo(ths,base){
        #         var val = ths.previousSibling.value;
        #         location.href = base + val
        #     }
        # </script>
        # """ % (base_url,)
        #
        # page_list.append(jump)

        page_str = mark_safe("".join(page_list))
        return page_str


