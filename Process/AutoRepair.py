from django.http import HttpResponse
from django.template import Context,Template,RequestContext
from django.shortcuts import render_to_response
from django.db import connection,transaction
def AutoRepair(request):
  ItemToMod =request.session['ItemToMod']
  DirtyTableContentList=request.session['DirtyTableContentList']
  FDL=request.session['FDL']
  FDR=request.session['FDR']
  FDLClean=request.session['FDLClean']
  FDRClean=request.session['FDRClean']
  DirtyTable=request.session['DirtyTable']
  CleanTable=request.session['CleanTable']
  cursor = connection.cursor()
  for Item in ItemToMod:
    tid=Item[0]
    TableName=Item[1]
    Attr=Item[2]

    if Attr in FDRClean:
       SQL="select t1."+Attr+" from "+  CleanTable+" t1, "+DirtyTable+" t2 "+" where "  
       for FDLAttr in FDLClean :
          SQL=SQL+"t1."+FDLAttr+"=t2."+FDLAttr +" and "  
       SQL=SQL+" t2.id="+str(tid)
       cursor.execute(SQL)
       TempValue=cursor.fetchall()
       cursor.execute("SELECT column_name FROM information_schema.columns WHERE  table_name ="+"\'"+DirtyTable+"\'"+";")
       DirtyTableAttr=[row[0] for row in cursor.fetchall()]
       AttrNum=DirtyTableAttr.index(Attr)
       DirtyTableContentList[tid-1][AttrNum]=TempValue[0][0]    
    elif Attr in FDR:
       SQL="select t1."+Attr+" from "+  DirtyTable+" t1, "+DirtyTable+" t2 "+" where "  
       for FDLAttr in FDL :
          SQL=SQL+"t1."+FDLAttr+"=t2."+FDLAttr +" and "  
       SQL=SQL+" t1.id<t2.id and t2.id="+str(tid)
       cursor.execute(SQL)
       TempValue=cursor.fetchall()
       cursor.execute("SELECT column_name FROM information_schema.columns WHERE  table_name ="+"\'"+DirtyTable+"\'"+";")
       DirtyTableAttr=[row[0] for row in cursor.fetchall()]
       AttrNum=DirtyTableAttr.index(Attr)
       DirtyTableContentList[tid-1][AttrNum]=TempValue[0][0]

    
       '''SQL="update "+DirtyTable+" set "+Attr+"="+TempValue[0][0]+" where id="+str(tid)+";"
       cursor.execute(SQL)
       cursor.execute("commit;")'''
        
        
  
  return render_to_response('ProcessAutoRepair.html',context_instance=RequestContext(request))
