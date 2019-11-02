from . import Viz
from interface import implements
from ..utils import merge,  T,F, dicoAuto, zipl, StudyClass
import pandas as pd
import numpy as np


# from ..utils import T,F
class Study_Datas_Viz(Viz):
    # @staticmethod
    def plot_class_balance(selfo,title="Répartition des labels",percent=False,
                            allsize=16,
                            titlesizeplus=2,
                            addLabels=True,
                            addLabelsPercent=True,
                            addLabelsBrut=True,
                            returnData=False,
                            asImg=False,
                            showFig=True,
                            outside=True,
                            filename="class_balance",
                            addLabels_kwargs=dict(),
                            class_balance_kwargs=dict(),
                            plot_kwargs=dict()):
        
        self=selfo.obj
        _addLabels_kwargs=dict(textposition="auto",textfont=dict(color="white",size=allsize))
        if outside:
            _addLabels_kwargs=dict(textposition="outside",textfont=dict(color="black",size=allsize))
        addLabels_kwargs=merge(_addLabels_kwargs,addLabels_kwargs,add=F)
    
        _class_balance_kwargs=dict(normalize=percent)
        class_balance_kwargs=merge(_class_balance_kwargs,class_balance_kwargs,add=F)


        dio=dicoAuto[["xaxis","yaxis"]][['tickfont','titlefont']].size==allsize
        dio["font"]=dict(size=allsize+titlesizeplus)
        _plot_kwargs=dict(layout_update=dio,
                                                                      title=title,xTitle="Y names",
                         yTitle="Nombre")
        data=StudyClass()
        plot_kwargs=merge(_plot_kwargs,plot_kwargs,add=F)
        cb=self.class_balance(**class_balance_kwargs)
        fig=cb.iplot(kind="bar",asFigure=True,filename=filename,**plot_kwargs)
        setattr(data,"class_balance_percent" if percent else "class_balance",cb)
        if addLabels:
            if addLabelsPercent and not percent:
                class_balance_kwargs2=merge(class_balance_kwargs,dict(normalize=True),add=F)
                cb2=self.class_balance(**class_balance_kwargs2)
                #print(zipl(cb.values,cb2.values) | _ftools_.mapl(  [__[0],__[1]] %_fun_% list))
                fig.data[0].text= list(map(lambda x:"{} ({}%)".format(x[0], np.round((x[1]*100),2)),zipl(cb.values,cb2.values))) 
                setattr(data,"class_balance_percent",cb2)
            elif addLabelsBrut and percent:
                class_balance_kwargs2=merge(class_balance_kwargs,dict(normalize=False),add=F)
                cb2=self.class_balance(**class_balance_kwargs2)
                # print(cb)
                #print(zipl(cb.values,cb2.values) | _ftools_.mapl(  [__[0],__[1]] %_fun_% list))
                fig.data[0].text= list(map(lambda x:"{} ({}%)".format(x[0], np.round((x[1]*100),2)),zipl(cb2.values,cb.values))) 
                setattr(data,"class_balance",cb2)
            else:
                fig.data[0].text=cb
            for k,v in addLabels_kwargs.items():
                setattr(fig.data[0],k,v)
        if asImg:
            fig=cb.iplot(data=fig,filename=filename,asImage=True)
            return fig
        if returnData:
            if showFig:
                fig.show()
            return StudyClass(data=data,fig=fig)

        return fig if showFig else StudyClass(fig=fig)

