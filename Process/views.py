#coding: utf-8

from django.http import HttpResponse
from django.template import Context,Template,RequestContext
from django.shortcuts import render_to_response
from django.db import connection,transaction

def AddPProp(tid,TableName,Attr):
   cursor = connection.cursor()
   SQL="insert into PProp (tid,Tablename,Attr) values("
   SQL=SQL+str(tid)+",\'"+TableName+"\',\'"+Attr+"\'"
   SQL=SQL+");"
   cursor.execute(SQL) 

def AddPVar(pid,pLeftid,pRightid,pMethod):
   cursor = connection.cursor()
   SQL="insert into PVar (pid,pLeftid,pRightid,pMethod) values("
   SQL=SQL+str(pid)+","+str(pLeftid)+","+str(pRightid)+",\'"+pMethod+"\'"
   SQL=SQL+");"
   cursor.execute(SQL) 
  
def PropVar(request):
  NULL='NULL'
  #get checkbox data
  FDL=request.GET.getlist('FDL')   
  print FDL
  FDR=request.GET.getlist('FDR')
  request.session['FDL']=FDL
  request.session['FDR']=FDR  
  RIDirty=request.GET.getlist('RIDirty') 
  RIRef=request.GET.getlist('RIRef')
  FDLClean=request.GET.getlist('FDLClean') 
  FDRClean=request.GET.getlist('FDRClean') 
  request.session['FDLClean']=FDLClean
  request.session['FDRClean']=FDRClean
  #request.session['Output']=FDL+FDR+RIDirty+RIRef+FDLDirty+FDRDirty+FDLCLean+FDRCLean
  cursor = connection.cursor()
  #clear PProp and PVar
  cursor.execute(" TRUNCATE TABLE PProp")  
  cursor.execute("commit") 
  cursor.execute(" TRUNCATE TABLE PVar")  
  cursor.execute("commit") 
  #deal with FD
  #get the tuples violate FD
  SQL="select t1.id as id1,t2.id as id2 from "+ request.session['DirtyTable']+" t1, "+ request.session['DirtyTable']+" t2 "+" where "
  for FDLAttr in FDL :
    SQL=SQL+"t1."+FDLAttr+"=t2."+FDLAttr +" and "
  SQL=SQL+"("
  for FDRAttr in FDR :
    SQL=SQL+"t1."+FDRAttr+"<>t2."+FDRAttr +" or "
  SQL=SQL+" 1=0) and t1.id<t2.id"
  cursor.execute(SQL)   
  SQLResult=cursor.fetchall()
  #generate P Proportions and variables
  Vcount=0;
  Pcount=0;
  FDList=[]
  for row in SQLResult: 
    TotFDL=[]
    TotFDR=[]
    for FDLAttr in FDL:
      #generate P Proportion
      for i in range(2):
        AddPProp(row[i],request.session['DirtyTable'],FDLAttr)
        Pcount=Pcount+1;
    for FDRAttr in FDR:
      for i in range(2):
        AddPProp(row[i],request.session['DirtyTable'],FDRAttr)
        Pcount=Pcount+1;
      #generate P Variable
    ListFDL=[]
    for FDLAttr in FDL:
      pid=[]
      for i in range(2):
        SQL="select id from PProp where Tablename="
        SQL=SQL+"\'"+request.session['DirtyTable']+"\'"+" and tid="+str(row[i])+" and Attr="+"\'"+FDLAttr+"\';"
        cursor.execute(SQL) 
        temppid=cursor.fetchone()
        pid.append(str(int(temppid[0])))
        AddPVar(pid[i],NULL,NULL,NULL)
        Vcount=Vcount+1;
      #one Attr in two tuples
      AddPVar(NULL,Vcount-1,Vcount,'and')
      Vcount=Vcount+1;
      ListFDL.append(str(Vcount))
    # use the And-Attrs to build TotFDL 
    if len(ListFDL)<=1:
      TotFDL=Vcount
    else:
      for i in range(len(ListFDL)-1):
        if i==0 :
          AddPVar(NULL,ListFDL[i],ListFDL[i+1],'and')
          Vcount=Vcount+1
        else:
          AddPVar(NULL,Vcount,ListFDL[i+1],'and')
          Vcount=Vcount+1       
      TotFDL=Vcount
    ListFDR=[] 
    for FDRAttr in FDR:
      pid=[]
      for i in range(2):        
        SQL="select id from PProp where Tablename="
        SQL=SQL+"\'"+request.session['DirtyTable']+"\'"+" and tid="+str(row[i])+" and Attr="+"\'"+FDRAttr+"\';"
        cursor.execute(SQL) 
        temppid=cursor.fetchone()
        pid.append(str(int(temppid[0])))
        AddPVar(pid[i],NULL,NULL,NULL)
        Vcount=Vcount+1;  
      #one Attr in two tuples
      SQL="select * from "+ request.session['DirtyTable']+" t1, "+ request.session['DirtyTable']+" t2 "+" where "+"t1.id="+str(row[0])+" and "+"t2.id="+str(row[1])+" and t1."+FDRAttr+"="+"t2."+FDRAttr+";"
      cursor.execute(SQL) 
      if cursor.fetchall()!=():#相同
         AddPVar(NULL,Vcount-1,NULL,'not')
         AddPVar(NULL,Vcount,NULL,'not')
         Vcount=Vcount+2;      
         AddPVar(NULL,Vcount-3,Vcount-2,'and')
         AddPVar(NULL,Vcount,Vcount-1,'and')
         Vcount=Vcount+2;         
         AddPVar(NULL,Vcount,Vcount-1,'or')        
         Vcount=Vcount+1;         
         ListFDR.append(str(Vcount))
      else:#不同
         AddPVar(NULL,Vcount,Vcount-1,'and')
         Vcount=Vcount+1;         
         AddPVar(NULL,Vcount,NULL,'not')        
         Vcount=Vcount+1;            
         ListFDR.append(str(Vcount)) 
    # use the And-Attrs to build TotFDR 
    if len(ListFDR)<=1:
      TotFDR=Vcount
    else:
      for i in range(len(ListFDR)-1):
        if i==0 :
          AddPVar(NULL,ListFDR[i],ListFDR[i+1],'and')
          Vcount=Vcount+1
        else:
          AddPVar(NULL,Vcount,ListFDR[i+1],'and')
          Vcount=Vcount+1       
      TotFDR=Vcount   
    AddPVar(NULL,TotFDL,TotFDR,'and')
    AddPVar(NULL,TotFDL,NULL,'not')
    Vcount=Vcount+2
    AddPVar(NULL,Vcount,Vcount-1,'or')
    Vcount=Vcount+1     
    FDList.append(Vcount)   


       
  #deal with RI
  RIList=[]
  SQL="select max(id) from "+request.session['DirtyTable']+";"
  cursor.execute(SQL) 
  TNum=int(cursor.fetchone()[0])
  for i in range(TNum):
    SQL="select id from "+request.session['RefTable']+" where "+ str(RIRef[0])+" in (select "+ str(RIDirty[0])+" from "+request.session['DirtyTable']+" where id="+str(i+1)+");"#在RI中找，有没有DirtyT中i的引用
    Output=SQL
    cursor.execute(SQL) 
    RIid=cursor.fetchall()
    if RIid==():#RI中没有
      print("NoRI")
      SQL="select id from PProp where Tablename="+"\'"+request.session['DirtyTable']+"\' and tid="+ str(i+1)+" and Attr="+"\'"+str(RIDirty[0])+"\';"#看PProp中加没加Dirty中i元组的该属性
      cursor.execute(SQL) 
      Dirtypid=cursor.fetchall()
      if Dirtypid==():#PProp中没有加
        AddPProp(i+1,request.session['DirtyTable'],RIDirty[0])
        Pcount=Pcount+1;
        AddPVar(Pcount,NULL,NULL,NULL)
        Vcount=Vcount+1;
        AddPVar(NULL,Vcount,NULL,'not')
        Vcount=Vcount+1; 
        RIList.append(Vcount)                       
      else:#PProp中有添加
        SQL="select id from PVar where pLeftid in (select id from PVar where pid="+str(Dirtypid[0][0])+") and pMethod=\'not\';"#如果加了看看加没加not
        cursor.execute(SQL) 
        Varnotid=cursor.fetchall()
        if Varnotid==():#没有not
          SQL="select id from PVar where pid="+str(Dirtypid[0][0])+";"
          cursor.execute(SQL) 
          Varid=cursor.fetchall()#用pid找到vid
          AddPVar(NULL,Varid[0][0],NULL,'not')
          Vcount=Vcount+1
          RIList.append(Vcount)   
        else:#not加了
          RIList.append(Varnotid[0][0])
    else: #如果RI中存在参照         
      print("YesRI")
      SQL="select id from PProp where Tablename="+"\'"+request.session['DirtyTable']+"\' and tid="+ str(i+1)+" and Attr="+"\'"+str(RIDirty[0])+"\';"#看PProp中加没加Dirty中i元组的该属性
      cursor.execute(SQL) 
      Dirtypid=cursor.fetchall()
      if Dirtypid==():#如果Dirty中不存在i的该属性
        AddPProp(i+1,request.session['DirtyTable'],RIDirty[0])
        Pcount=Pcount+1;
        AddPVar(Pcount,NULL,NULL,NULL)
        Vcount=Vcount+1;
        #为被参照的Ref中属性也添加PProp
        SQL="select * from PProp where Tablename="+"\'"+request.session['RefTable']+"\' and Attr="+"\'"+RIRef[0]+"\' and tid="+str(RIid[0][0])+";"#看是不是已经有Ref的PProp
        cursor.execute(SQL) 
        RIpid=cursor.fetchall()
        if RIpid==():#RI没有加入PProp
          AddPProp(RIid[0][0],request.session['RefTable'],RIRef[0])
          Pcount=Pcount+1;
          AddPVar(Pcount,NULL,NULL,NULL)
          Vcount=Vcount+1;
          #加入关系
          AddPVar(NULL,Vcount-1,NULL,'not')
          Vcount=Vcount+1  
          AddPVar(NULL,Vcount-1,Vcount-2,'and')
          Vcount=Vcount+1  
          AddPVar(NULL,Vcount,Vcount-1,'and')
          Vcount=Vcount+1               
          RIList.append(Vcount)
        else:#RI加入了PProp
          #加入关系 
          AddPVar(NULL,Vcount,NULL,'not')
          Vcount=Vcount+1  
          AddPVar(NULL,Vcount-1,RIpid[0][0],'and')
          Vcount=Vcount+1  
          AddPVar(NULL,Vcount,Vcount-1,'and')        
          Vcount=Vcount+1               
          RIList.append(Vcount)                                 
      else:#如果Dirty中存在i的该属性
        SQL="select id from PVar where pLeftid in (select id from PVar where pid="+str(Dirtypid[0][0])+") and pMethod=\'not\';"
        cursor.execute(SQL)
        Varnotid=cursor.fetchall()
        SQL="select id from PVar where pid="+str(Dirtypid[0][0])+";"
        cursor.execute(SQL) 
        Varid=cursor.fetchall()
        if Varnotid==():#如果不存在not
          #在PVar中加入not
          AddPVar(NULL,Varid[0][0],NULL,'not')
          Vcount=Vcount+1
          #为被参照的Ref中属性也添加PProp
          SQL="select * from PProp where Tablename="+"\'"+request.session['RefTable']+"\' and Attr="+"\'"+RIRef[0]+"\' and tid="+str(RIid[0][0])+";"#看是不是已经存在
          cursor.execute(SQL) 
          RIpid=cursor.fetchall()
          if RIpid==():#PPop中不存在RI
            AddPProp(RIid[0][0],request.session['RefTable'],RIRef[0])
            Pcount=Pcount+1;
            AddPVar(Pcount,NULL,NULL,NULL)
            Vcount=Vcount+1;
            #加入关系 
            AddPVar(NULL,Varid[0][0],Vcount,'and')
            Vcount=Vcount+1  
            AddPVar(NULL,Vcount,Vcount-2,'or')     
            Vcount=Vcount+1 
            RIList.append(Vcount)
          else:#PPop中存在RI
            #加入关系 
            SQL="select id from PVar where pid="+str(RIpid[0][0])+";"
            cursor.execute(SQL) 
            RIvid=cursor.fetchall()  
            AddPVar(NULL,Varid[0][0],RIvid[0][0],'and')
            Vcount=Vcount+1    
            AddPVar(NULL,Vcount,Vcount-1,'or')    
            Vcount=Vcount+1               
            RIList.append(Vcount)      
        else:#如果存在not 
          #为被参照的Ref中属性也添加PProp
          SQL="select * from PProp where Tablename="+"\'"+request.session['RefTable']+"\' and Attr="+"\'"+RIRef[0]+"\' and tid="+str(RIid[0][0])+";"
          cursor.execute(SQL) 
          RIpid=cursor.fetchall()
          if RIpid==():
            AddPProp(RIid[0][0],request.session['RefTable'],RIRef[0])
            Pcount=Pcount+1;
            AddPVar(Pcount,NULL,NULL,NULL)
            Vcount=Vcount+1;
            #加入关系      
            AddPVar(NULL,Varid[0][0],Vcount,'and')
            Vcount=Vcount+1  
            AddPVar(NULL,Vcount,Varnotid[0][0],'or')           
            Vcount=Vcount+1
            RIList.append(Vcount)         
             
          else:#PPop中已经有参照的RI
            #加入关系      
            SQL="select id from PVar where pid="+str(RIpid[0][0])+";"
            cursor.execute(SQL) 
            RIvid=cursor.fetchall()            
            AddPVar(NULL,Varid[0][0],RIvid[0][0],'and')
            Vcount=Vcount+1  
            AddPVar(NULL,Vcount,Varnotid[0][0],'or')           
            Vcount=Vcount+1
            RIList.append(Vcount)     



  # deal with CR 
  SQL="select t1.id as id1,t2.id as id2 from "+ request.session['DirtyTable']+" t1, "+ request.session['CleanTable']+" t2 "+" where "
  for FDLAttr in FDLClean :
    SQL=SQL+"t1."+FDLAttr+"=t2."+FDLAttr +" and "
  SQL=SQL+" 1=1 ;"
  cursor.execute(SQL)   
  SQLResult=cursor.fetchall()
  #generate P Proportions and variables
  CRList=[]
  for row in SQLResult: 
    TotCRFDL=[]
    TotCRFDR=[]
    ListCRFDL=[]
    for FDLAttr in FDLClean:
      SQL="select id from PProp where Tablename="+"\'"+request.session['DirtyTable']+"\' and tid="+ str(row[0]) +" and Attr="+"\'"+FDLAttr+"\';"
      cursor.execute(SQL) 
      pid=cursor.fetchall()
      SQL="select id from PVar where pid= "+str(pid[0][0]) +";"
      cursor.execute(SQL)
      vid=cursor.fetchall()
      ListCRFDL.append(str(vid[0][0]))
    if len(ListCRFDL)<=1:
      TotCRFDL=ListCRFDL[0]
    else:
      for i in range(len(ListCRFDL)-1):
        if i==0 :
          AddPVar(NULL,ListCRFDL[i],ListCRFDL[i+1],'and')
          Vcount=Vcount+1
        else:
          AddPVar(NULL,Vcount,ListCRFDL[i+1],'and')
          Vcount=Vcount+1       
      TotCRFDL=Vcount
    ListCRFDR=[]
    for FDRAttr in FDRClean:
      SQL="select * from "+ request.session['DirtyTable']+" t1, "+ request.session['CleanTable']+" t2 "+" where "+"t1.id="+str(row[0])+" and "+"t2.id="+str(row[1])+" and t1."+FDRAttr+"="+"t2."+FDRAttr+";"
      cursor.execute(SQL) 
      if cursor.fetchall()==():
         SQL="select id from PProp where Tablename="+"\'"+request.session['DirtyTable']+"\' and tid="+ str(row[0]) +" and Attr="+"\'"+FDRAttr+"\';"
         cursor.execute(SQL) 
         pid=cursor.fetchall()     
         SQL="select id from PVar where pid= "+str(pid[0][0]) +";"
         cursor.execute(SQL)   
         vid=cursor.fetchall() 
         SQL="select id from PVar where pLeftid= "+str(vid[0][0]) +" and pMethod=\'not\' ;"
         cursor.execute(SQL)   
         vnotid=cursor.fetchall() 
         if vnotid==():         
            AddPVar(NULL,vid[0][0],NULL,'not')
            Vcount=Vcount+1
            ListCRFDR.append(str(Vcount))
         else:                
            ListCRFDR.append(str(vnotid[0][0]))
      else:
         SQL="select id from PProp where Tablename="+"\'"+request.session['DirtyTable']+"\' and tid="+ str(row[0]) +" and Attr="+"\'"+FDRAttr+"\';"
         cursor.execute(SQL) 
         pid=cursor.fetchall()
         SQL="select id from PVar where pid= "+str(pid[0][0]) +";"
         cursor.execute(SQL)
         vid=cursor.fetchall()
         ListCRFDR.append(str(vid[0][0])) 

    if len(ListCRFDR)<=1:
      TotCRFDR=ListCRFDR[0]
    else:
      for i in range(len(ListCRFDR)-1):
        if i==0 :
          AddPVar(NULL,ListCRFDL[i],ListCRFDL[i+1],'and')
          Vcount=Vcount+1
        else:
          AddPVar(NULL,Vcount,ListCRFDL[i+1],'and')
          Vcount=Vcount+1       
      TotCRFDR=Vcount   
    AddPVar(NULL,TotCRFDL,TotCRFDR,'and') 
    AddPVar(NULL,TotCRFDL,NULL,'not')
    Vcount=Vcount+2
    AddPVar(NULL,Vcount,Vcount-1,'or')
    Vcount=Vcount+1     
    CRList.append(Vcount) 
  cursor.execute("commit") 
  request.session['MList']=FDList+RIList+CRList        
  print(FDList)
  print(RIList)
  print(CRList) 
  SQL="select * from PProp;"
  cursor.execute(SQL)
  PPropContent=cursor.fetchall()
  request.session['PPropContent']=PPropContent    

  SQL="select id,pLeftid,pRightid,pMethod,pid from PVar;"
  cursor.execute(SQL)
  PVarContent=cursor.fetchall()
  request.session['PVarContent']=PVarContent  
           
  #request.session['Output']=SQLResult
  return render_to_response('ProcessPropVar.html',context_instance=RequestContext(request))


