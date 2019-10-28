from .project import StudyProject
from ..base import *
import numpy as np
import copy
import os
import warnings
from .interfaceProject import IProject
from abc import abstractmethod
from interface import implements, Interface
def securerRepr(obj,ind=1,*args,**xargs):
    try:
        u=obj.__repr__(ind,*args,**xargs)
    except:
        u=obj.__repr__()
    return u

class BaseSuperviseProject(BaseSupervise,implements(IProject)):
    EXPORTABLE=["project","idDataProject","proprocessDataFromProjectFn","_isProcessedDataFromProject"]

    @abstractmethod
    def __init__(self,ID=None,datas:DatasSupervise=None,
                        models:Models=None,metric:Metric=None,project:StudyProject=None,*args,**xargs):
        super().__init__(ID,datas,models,metric)
        self._project=project

    def init(self):
        super().init()
        self._idDataProject=None
        self._proprocessDataFromProjectFn=None
        self.begin()

    def begin(self):
        self._isProcessedDataFromProject=False

    def setProject(self,p):
        self._project=p

    def getProject(self):
        return self.project

    def getProprocessDataFromProjectFn(self):
        return self.proprocessDataFromProjectFn

    def getIdData(self):
        return self._idDataProject

    def setIdData(self,i):
        self._idDataProject=i

    def setDataTrainTest(self,X_train=None,y_train=None,
                              X_test=None,y_test=None,
                              namesY=None,id_=None):
        if id_ is None and np.any(mapl(lambda a:a is None,[X_train,X_test,y_train,y_test])):
           raise KeyError("if id_ is None, all of [X_train,X_test,y_train,y_test] must be specified  ")
        if id_ is not None and self.project is None:
            raise KeyError("if id_ is specified, project must be set")
        if id_ is not None and id_ not in self.project.data:
            raise KeyError("id_ not in global")
        if id_ is not None:
            self._datas=self.project.data[id_]
            self._idDataProject=id_
        else:
            super().setDataTrainTest(X_train,y_train,X_test,y_test,namesY)

    def proprocessDataFromProject(self,fn=None,force=False):
        if self.isProcessedDataFromProject and not force:
            warnings.warn("[BaseSuperviseProject proprocessDataFromProject] processing deja fait pour les données du projet (et force est à False)")
        if fn is not None:
            self._proprocessDataFromProjectFn = fn
            super().setDataTrainTest(*fn(*self._datas.get(deep=True,optsTrain=dict(withNamesY=False))))
            self._isProcessedDataFromProject = True

    def check(self):
         if not self.isProcessedDataFromProject and self.proprocessDataFromProjectFn is not None:
            warnings.warn("Attention vous devez appeler impérativement  la méthode proprocessDataFromProject de l'object '{}' reçu pour que les données soit les bonnes".format(getClassName(self)))

    def __repr__(self,ind=1):
        txt=super().__repr__(ind=ind)
        nt="\n"+"\t"*ind
        stri=txt[:-1]+nt+"project : {},"+nt+"idDataProject : {},"+nt+"proprocessDataFromProjectFn : {},"+nt+"isProcessedDataFromProject : {}]"
        return stri.format(securerRepr(self.project)(ind+2,onlyID=True),self.idDataProject,self.proprocessDataFromProjectFn,self.isProcessedDataFromProject)




    

