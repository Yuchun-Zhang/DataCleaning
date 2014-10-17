from django.http import HttpResponse
from django.template import Context,Template,RequestContext
from django.shortcuts import render_to_response
from django.db import connection 

def DBName(request):
  return render_to_response('DBName.html')
  
def TableName(request):
  #request.session.modified = True
  DBName=request.GET['DBName']
  request.session['DBName']=DBName
  cursor = connection.cursor() 
  cursor.execute("show tables;") 
  TableName=[row[0] for row in cursor.fetchall()]
  request.session['TableName']=TableName
  return render_to_response('TableName.html',context_instance=RequestContext(request))

def ShowTable(request):
  DirtyTable=request.GET['DirtyTable']
  request.session['DirtyTable']=DirtyTable
  CleanTable=request.GET['CleanTable']
  request.session['CleanTable']=CleanTable
  RefTable=request.GET['RefTable']
  request.session['RefTable']=RefTable
  cursor = connection.cursor()
  cursor.execute("SELECT column_name FROM information_schema.columns WHERE  table_name ="+"'"+DirtyTable+"'"+";")
  DirtyTableAttr=[row[0] for row in cursor.fetchall()]
  request.session['DirtyTableAttr']=DirtyTableAttr 
  cursor.execute("SELECT column_name FROM information_schema.columns WHERE  table_name ="+"'"+CleanTable+"'"+";")
  CleanTableAttr=[row[0] for row in cursor.fetchall()]
  request.session['CleanTableAttr']=CleanTableAttr 
  cursor.execute("SELECT column_name FROM information_schema.columns WHERE  table_name ="+"'"+RefTable+"'"+";")
  RefTableAttr=[row[0] for row in cursor.fetchall()]
  request.session['RefTableAttr']=RefTableAttr 

  cursor.execute("select * from "+DirtyTable+";")
  DirtyTableContent=cursor.fetchall()
  request.session['DirtyTableContent']=DirtyTableContent 
  cursor.execute("select * from "+CleanTable+";")
  CleanTableContent=cursor.fetchall()
  request.session['CleanTableContent']=CleanTableContent 
  cursor.execute("select * from "+RefTable+";")
  RefTableContent=cursor.fetchall()  
  request.session['RefTableContent']=RefTableContent 
  return render_to_response('ShowTable.html',context_instance=RequestContext(request))
  

def Relation(request):


  return render_to_response('Relation.html',context_instance=RequestContext(request))

