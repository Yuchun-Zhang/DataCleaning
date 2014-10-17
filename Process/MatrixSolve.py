from django.http import HttpResponse
from django.template import Context,Template,RequestContext
from django.shortcuts import render_to_response
from django.db import connection,transaction
from numpy import *
import sys
import mosek


def MatrixSolve(request):
  cursor = connection.cursor()
  SQL="select max(id) from PVar;"
  cursor.execute(SQL)
  VNum=int(cursor.fetchall()[0][0])
  SQL="select count(id) from PVar where pMethod='not';"
  cursor.execute(SQL) 
  EqNum=int(cursor.fetchall()[0][0])
  SQL="select count(id) from PVar where pMethod=\'and\' or pMethod=\'or\';"
  cursor.execute(SQL)  
  UnEqNum=int(cursor.fetchall()[0][0])
  AUnEq=zeros((UnEqNum*3,VNum))
  BUnEq=zeros((UnEqNum*3,1))
  AEq=zeros((EqNum,VNum))
  BEq=zeros((EqNum,1)) 
  CMax=zeros((1,VNum))
  MList=request.session['MList']
  MNum=len(MList)
  CountUnEq=0
  CountEq=0
  CountMax=0
  for i in range(VNum):
    SQL="select id,pid,pLeftid,pRightid,pMethod from PVar where id="+str(i+1)+";"
    cursor.execute(SQL)
    Form=cursor.fetchall()[0]
    if Form[4]=='NULL':
      SQL="select Attr from PProp where id in (select pid from PVar where id="+str(i+1)+");"
      cursor.execute(SQL)
      Attr=cursor.fetchall()
      if Attr[0][0] in request.session['FDL']:
        CMax[0,Form[0]-1]=2
      else:
        CMax[0,Form[0]-1]=1
    if Form[4]=='and':
      AUnEq[CountUnEq,Form[0]-1]=1
      AUnEq[CountUnEq,Form[2]-1]=-1
      CountUnEq=CountUnEq+1
      AUnEq[CountUnEq,Form[0]-1]=1
      AUnEq[CountUnEq,Form[3]-1]=-1
      CountUnEq=CountUnEq+1     
      AUnEq[CountUnEq,Form[0]-1]=-1
      AUnEq[CountUnEq,Form[2]-1]=1
      AUnEq[CountUnEq,Form[3]-1]=1      
      BUnEq[CountUnEq,0]=1 
      CountUnEq=CountUnEq+1 
    if Form[4]=='or':
      AUnEq[CountUnEq,Form[0]-1]=-1
      AUnEq[CountUnEq,Form[2]-1]=1
      CountUnEq=CountUnEq+1
      AUnEq[CountUnEq,Form[0]-1]=-1
      AUnEq[CountUnEq,Form[3]-1]=1
      CountUnEq=CountUnEq+1     
      AUnEq[CountUnEq,Form[0]-1]=1
      AUnEq[CountUnEq,Form[2]-1]=-1
      AUnEq[CountUnEq,Form[3]-1]=-1      
      CountUnEq=CountUnEq+1 
    if Form[4]=='not':
      AEq[CountEq,Form[0]-1]=1 
      AEq[CountEq,Form[2]-1]=1 
      BEq[CountEq,0]=1
      CountEq=CountEq+1;

  print(CMax)
  request.session['InforContent']=[];
  def streamprinter(text):
    request.session['InforContent'].append(text)
    sys.stdout.write(text)
    sys.stdout.flush()
    


  # Make a MOSEK environment
  env = mosek.Env ()
  # Attach a printer to the environment
  env.set_Stream (mosek.streamtype.log, streamprinter)
  
  # Create a task
  task = env.Task(0,0)
  # Attach a printer to the task
  task.set_Stream (mosek.streamtype.log, streamprinter)

  bkc=[]
  blc=[]
  buc=[]
  bkx=[]
  blx=[]
  bux=[]
  asub=[]
  aval=[]
  c=[]
  for i in range(UnEqNum*3):
    aval.append(AUnEq[i])
    bkc.append( mosek.boundkey.up)
    blc.append(-inf)
    buc.append(BUnEq[i,0])
  for i in range(EqNum):
    aval.append(AEq[i])
    bkc.append( mosek.boundkey.fx)
    blc.append(1)
    buc.append(1)    
  for i in range(MNum):
    ATemp=zeros((1,VNum))
    ATemp=ATemp[0]
    ATemp[MList[i]-1]=1;
    aval.append(ATemp)
    bkc.append( mosek.boundkey.fx)
    blc.append(1)
    buc.append(1)         
    
  for i in range(UnEqNum*3+EqNum+MNum):
    asub.append(arange(VNum))
  for i in range(VNum):
    bkx.append(mosek.boundkey.ra)
    blx.append(0)
    bux.append(1)
    c.append(CMax[0,i])
  numvar = len(bkx)
  numcon = len(bkc)

  # Append 'numcon' empty constraints.
  # The constraints will initially have no bounds. 
  task.appendcons(numcon)
     
  #Append 'numvar' variables.
  # The variables will initially be fixed at zero (x=0). 
  task.appendvars(numvar)
 



  for j in range(numvar):
    # Set the linear term c_j in the objective.
    task.putcj(j,c[j])
    # Set the bounds on variable j
    # blx[j] <= x_j <= bux[j] 
    task.putbound(mosek.accmode.var,j,bkx[j],blx[j],bux[j])

  for i in range(numcon):
    task.putarow(i,                  # Variable (row) index.
                 asub[i],            # Row index of non-zeros in column j.
                 aval[i])            # Non-zero Values of column j. 

    task.putbound(mosek.accmode.con,i,bkc[i],blc[i],buc[i])
        
  # Input the objective sense (minimize/maximize)
  task.putobjsense(mosek.objsense.maximize)
       
  # Define variables to be integers

  task.putvartypelist(arange(VNum),
                      [ mosek.variabletype.type_int,
                      ]*VNum)
        
  # Optimize the task
  task.optimize()

  if task.solutiondef(mosek.soltype.itg):

    # Output a solution
    xx=zeros(numvar, float)
    task.getsolutionslice(mosek.soltype.itg,
                          mosek.solitem.xx,
                          0, numvar,
                         xx)
    print "x =", xx
  else:
    print "Integer solution not defined. Probably a problem with 'mosekglb' optimizer."
  OptResult=xx
  ItemToMod=[]
  for i in range(VNum):
    if OptResult[i]==0:
      SQL="select tid,Tablename,Attr from PProp where id in (select pid from PVar where pMethod=\'NULL\'and id="+str(i+1)+");"
      cursor.execute(SQL)
      Pid=cursor.fetchall()
      if Pid!=():
        #print(i+1,Pid)
        ItemToMod.append(Pid[0])
  print(ItemToMod)

  DirtyTable=request.session['DirtyTable']
  cursor.execute("SELECT column_name FROM information_schema.columns WHERE  table_name ="+"\'"+DirtyTable+"\'"+";")
  DirtyTableAttr=[row[0] for row in cursor.fetchall()]
  request.session['ItemToMod']=ItemToMod 
  ItemToModNum=[]
  for row in range(len(ItemToMod)):
    ItemToModNum.append(list(ItemToMod[row]))
    AttrNum=DirtyTableAttr.index(ItemToMod[row][2])
    ItemToModNum[row][2]=AttrNum
  print ItemToModNum


  DirtyTableContent=request.session['DirtyTableContent']
  DirtyTableContentProb=list(DirtyTableContent)  
  DirtyTableContentList=list(DirtyTableContent)  
  for row in  range(len(DirtyTableContent)):
    DirtyTableContentList[row]=list(DirtyTableContent[row])
    DirtyTableContentProb[row]=list(DirtyTableContent[row])    
    for attr in range(len(DirtyTableContent[row])):
       if [row+1,request.session['DirtyTable'],attr] in ItemToModNum:
           DirtyTableContentProb[row][attr]='<td bgcolor=\"red\">'+str(DirtyTableContent[row][attr])+'</td>'
       else:
           DirtyTableContentProb[row][attr]='<td>'+str(DirtyTableContent[row][attr])+'</td>'

  request.session['DirtyTableContentProb']=DirtyTableContentProb
  request.session['DirtyTableContentList']=DirtyTableContentList
  
  for line in range(len(request.session['InforContent'])):
     newline=request.session['InforContent'][line].replace('\n','')
     request.session['InforContent'][line]=newline

  
  return render_to_response('ProcessMatrixSolve.html',context_instance=RequestContext(request))
