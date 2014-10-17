#coding: utf-8

from django.http import HttpResponse
from django.template import Context,Template,RequestContext
from django.shortcuts import render_to_response
from django.db import connection,transaction
def ShowProb(request):


  return render_to_response('ProcessShowProb.html',context_instance=RequestContext(request))
