from skopt import BayesSearchCV
import skopt
from skopt.plots import plot_convergence, plot_regret, plot_evaluations, plot_objective
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

from ..base.base import Base, factoryCls
from ..utils import isStr, StudyDict, merge, T, F, ProgressBarCalled, randomString

from typing import Dict
import numbers
from collections import defaultdict
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np
# from evolutionary_search import EvolutionaryAlgorithmSearchCV
from cvopt.model_selection import SimpleoptCV
from cvopt.search_setting import search_category, search_numeric
from cvopt.search_setting._base import ParamDist

from bokeh.io import output_notebook
from bokeh.resources import INLINE
output_notebook(INLINE,hide_banner=True)

def to_pipeline(self,i=0,name="model"):
    return Pipeline([(name,self.models[i])])


def check_dimension(dimension,name):
    if isinstance(dimension, ParamDist):
        return dimension

    if not isinstance(dimension, (list, tuple, np.ndarray)):
        raise ValueError("Dimension has to be a list or tuple.")

    # A `Dimension` described by a single value is assumed to be
    # a `Categorical` dimension. This can be used in `BayesSearchCV`
    # to define subspaces that fix one value, e.g. to choose the
    # model type, see "sklearn-gridsearchcv-replacement.ipynb"
    # for examples.
    if len(dimension) == 1:
        return search_category(dimension)

    if len(dimension) == 2:
        if any([isinstance(d, (str, bool)) or isinstance(d, np.bool_)
                for d in dimension]):
            return search_category(dimension)
        elif all([isinstance(dim, numbers.Integral) for dim in dimension]):
            return search_numeric(dimension[0],dimension[1],"integer")
        elif any([isinstance(dim, numbers.Real) for dim in dimension]):
            return search_numeric(dimension[0],dimension[1],"float")
        else:
            raise ValueError("Invalid dimension {}. Read the documentation for"
                             " supported types.".format(dimension))

    if len(dimension) == 3:
        if (any([isinstance(dim, (float, int)) for dim in dimension[:2]]) and
            dimension[2] in ["uniform", "log-uniform"]):
            warnings.warn("""
                not Implemented [uniform,log-uniform]
                """)
            return search_numeric(dimension[0],dimension[1],"float")
        else:
            return search_category(dimension)

    if len(dimension) > 3:
        return search_category(dimension)

    raise ValueError("Invalid dimension {}. Read the documentation for "
                     "supported types.".format(dimension))
class Tuned(Base):
    EXPORTABLE=["resultat","obj","logdir","middbk","args"]
    def __init__(self,resultat=None,obj=None,logdir=None,middbk=None,args=None,ID=None):
        super(Tuned, self).__init__(ID=ID)
        # self.resultat_=resultat
        self.resultat=pd.DataFrame(resultat) if resultat is not None else  resultat
        self.obj=obj
        self.args=args
        self.logdir=logdir
        self.middbk=middbk

    def addDirToSave():
        return [self.logdir]

    def restoreDir(logdir):
        if len(logdir) >0 and self.logdir in logdir:
            self.logdir=logdir[self.logdir]

class TunedL(Base):
    EXPORTABLE=["dico"]
    def __init__(self, dico:Dict[str,Tuned]=None,ID=None):
        super().__init__(ID=ID)
        self.dico = dico

    def __getitem__(self,name):
        if self.dico is None:
            return None
        return self.dico[name]
    
    def __setitem__(self,n,v):
        if self.dico is None:
            self.dico={}
        self.dico[n]=v

factoryCls.register_class(Tuned)
class HyperTune(Base):
    EXPORTABLE=["tuned","_namesCurr","_modelCurr"]
    TYPES_=["random","grid","bayes","bayesopt","bayes_rf","bayes_gp","bayes_dummy","bayes_et","bayes_gbrt"]
    def __init__(self, tuned:Dict[str,TunedL]=None,ID=None):
        super().__init__(ID=ID)
        self.tuned=StudyDict(defaultdict(TunedL)) if tuned is None else tuned
        self._namesCurr=None
        self._modelCurr=None

    @property
    def curr(self):
        return self.tuned[self._modelCurr][self._namesCurr]
    
    def tune(self,mod,hyper_params,typeOfTune="random",cv=3,scoring="accuracy",
                    max_iter=20,n_jobs=-1,verbose=0,logdir=None, #logdir = False if not save 
                    save_estimator=2,opts={},optsFit={}):
        """
        typeOfTune: "random" RandomizedSearchCV, "grid" GridSearchCV, "bayes" or "bayes_gp" BayesSearchCV ["Gaussian Process"], "bayes_rf" BayesSearchCV ["Random Forest"], "bayes_dummy" BayesSearchCV ["Dummy"], "bayes_et" BayesSearchCV ["Extra Trees"], "bayes_gbrt" BayesSearchCV ["gradient boosted trees"]
        """
        middbk=None
        if logdir is None and typeOfTune not in ["random","randomopt"]:
            logs=TMP_DIR()
            logdir = logs.get()
        if not isinstance(hyper_params,dict):
            raise NotImplementedError("hyper_params must be a dict")
        self.hyper_params_=hyper_params
        hyper_params_=self.hyper_params_
        print(hyper_params_)
        print(hyper_params)
        self.hyper_params = {k:check_dimension(v,k) for k,v in hyper_params}
        hyper_params=self.hyper_params
        modsN=self.papa._models.mappingNamesModelsInd
        mid=self.papa._models.ID
        midd=lambda bk:str(mid)+"_"+bk+"_"+randomString()
        modsN2=self.papa._models.namesModels
        mod=modsN[mod] if isStr(mod) else mod
        modelName=mod if isStr(mod) else modsN2[mod]
        skip=False
        ## TUNINSSS
        if typeOfTune not in self.TYPES_:
            raise NotImplementedError("{} not implemented yet , only {}".format(typeOfTune,self.TYPES_))
        
        model=self.papa._models.models[mod]
        X_train=self.papa.X_train
        y_train=self.papa.y_train
        X_test=self.papa.X_test
        y_test=self.papa.y_test
        if typeOfTune == "grid":
            deff=dict(n_jobs=-1,return_train_score=True)
            opts=merge(deff,opts,add=False)
            obj=GridSearchCV(model,hyper_params_,**opts)
            obj.fit(X_train,y_train,**optsFit)
            skip=True
            argsALL=dict(model=model,hyper_params=hyper_params,hyper_params_=hyper_params_,**opts)
            argsALL["optsFit"]=optsFit

        elif typeOfTune in ["bayes","bayes_gp","bayesopt","bayesopt_gp"]:
            bk="bayesopt"
            argus= dict(model_type="GP")

        elif typeOfTune in ["random","randomopt"]:
            bk="randomopt"

        elif typeOfTune in  ["gaopt", "ga", "genetic", "evo"]:
            bk="gaopt"

        elif typeOfTune in  ["hyperopt","hyper","tpe"]:
            bk="hyperopt"
        elif typeOfTune in ["simple"] and "backend" not in opts:
            warnings.warn("""
                when typeOfTune is simple-> backend must be set (default: random)
                """)
            bk="randomopt"

        elif typeOfTune in ["simple"] and "backend" in opts:
            warnings.warn("""
                when typeOfTune is simple-> backend must be set (default: random)
                """)
            bk=opts.pop("backend")

        if skip:
            argus= dict(backend=bk)
            middbk=midd(bk)
            obj = SimpleoptCV(model, hyper_params, 
                         scoring=scoring,              # Objective of search
                         cv=cv,                          # Cross validation setting
                         max_iter=max_iter,                    # Number of search
                         n_jobs=n_jobs,                       # Number of jobs to run in parallel.
                         verbose=verbose,                      # 0: don't display status, 1:display status by stdout, 2:display status by graph 
                         logdir=logdir,        # If this path is specified, save the log.
                         model_id=middbk,                    # used estimator's dir and file name in save.
                         save_estimator=save_estimator,               # estimator save setting.
                         **argus,
                         **opts                     # hyperopt,bayesopt, gaopt or randomopt.
                         )
            argsALL=dict(model=model,hyper_params_=hyper_params_,hyper_params= hyper_params, 
                         scoring=scoring,              # Objective of search
                         cv=cv,                          # Cross validation setting
                         max_iter=max_iter,                    # Number of search
                         n_jobs=n_jobs,                       # Number of jobs to run in parallel.
                         verbose=verbose,                      # 0: don't display status, 1:display status by stdout, 2:display status by graph 
                         logdir=logdir,        # If this path is specified, save the log.
                         model_id=middbk,                    # used estimator's dir and file name in save.
                         save_estimator=save_estimator,               # estimator save setting.
                         **argus,
                         **opts                     # hyperopt,bayesopt, gaopt or randomopt.
                         )
            argsALL["optsFit"]=optsFit
            obj.fit(
                    X_train, y_train, validation_data=(X_test, y_test),
                    **optsFit)

        res=Tuned()
        res.resultat=pd.DataFrame(resultat)
        res.obj=obj
        res.logdir=logdir
        res.args=dict(argsALL)
        res.middbk=middbk
        # res.hyper_params=hyper_params
        # res.hyper_params_=hyper_params_
        # res.best_estimator_=best_estimator_
        # res.best_score_=best_score_
        # res.best_params_=best_params_
        # res.best_index_=best_index_
        # res.scorer_=scorer_
        # res.n_splits_=n_splits_
        self._modelCurr=modelName
        self.tuned[modelName][res.ID]=res
        self._namesCurr=res.ID
        if logdir is not None:
            self._tmpToSave.append(logdir)

factoryCls.register_class(HyperTune)