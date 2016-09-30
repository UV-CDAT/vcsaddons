import vcs
import numpy
import vcsaddons


class Gpc(vcsaddons.core.VCSaddon):
    def __init__(self,name,source="default",x=None,template=None):
        self.g_name = 'Gpc'
        self.g_type = 'parallelcoordinates'
        super(Gpc, self).__init__(name, source, x, template)
        if source == "default":
            self.datawc_y1 = [1.e20]
            self.datawc_y2 = [1.e20]
            self.markercolors = None
            self.markertypes = ["dot"]
            self.markersizes = [2.]
            self.linecolors = None
            self.linetypes = ["solid"]
            self.linewidths = [1]
            self.yticlabels = ["*"]
            # self.ymtics = [""]
            del(self.yticlabels1)
            del(self.ymtics1)
            del(self.yticlabels2)
            del(self.ymtics2)
        else:
            if isinstance(source, (str, unicode)):
                gm = vcsaddons.gms[self.g_type][source]
            else:
                gm = source
    def list(self):
        print 'graphics method = ',self.g_name
        print 'name = ',self.name
        print 'datawc_x1 = ',self.datawc_x1
        print 'datawc_x2 = ',self.datawc_x2
        print 'datawc_y1 = ',self.datawc_y1
        print 'datawc_y2 = ',self.datawc_y2
        print 'xmtics1 = ',self.xmtics1
        print 'xmtics2 = ',self.xmtics2
        print 'ymtics = ',self.ymtics
        print 'xticlabels1 = ',self.xticlabels1
        print 'xticlabels2 = ',self.xticlabels2
        print 'yticlabels = ',self.yticlabels
        print 'xaxisconvert = ',self.xaxisconvert
        print 'yaxisconvert = ',self.yaxisconvert

    def drawYAxes(self,mins,maxs,labels,X,bg):
        N = len(labels)
        l = X.createline(source=self.template.box1.line)
        l.viewport = [self.template.data.x1, self.template.data.x2,
                self.template.data.y1, self.template.data.y2]
        ys = [[0,1]]*N
        xs = [[x/(N-1.),x/(N-1.)] for x in range(N)]

        l.x=xs
        l.y=ys
        l.priority = self.template.box1.priority
        X.plot(l,bg=bg)

        l1 = X.createline(source = self.template.ytic1.line)
        l2 = X.createline(source = self.template.ytic2.line)
        le1 = X.createline(source = self.template.ytic1.line)
        le2 = X.createline(source = self.template.ytic2.line)
        txt = X.createtext(To_source = self.template.ylabel1.textorientation,
                Tt_source =  self.template.ylabel1.texttable)
        xs1 = []
        xs2 = []
        xe1 = []
        xe2 = []
        ye1 = []
        ye2 = []
        ys = []
        xt = []
        yt = []
        st = []
        for i,lbl in enumerate(labels):
            x = float(i)/(N-1)
            for y in lbl:
                st.append(lbl[y])
                Y= (y - mins[i])/(maxs[i]-mins[i])
                ys.append([Y,Y])
                yt.append(Y)
                d1 = abs(self.template.ytic1.x2-self.template.ytic1.x1)
                mn = min(self.template.data.x1,self.template.data.x2)
                dt = mn - self.template.ylabel1.x
                xs1.append([x-d1,x])
                xt.append(x-dt)
                if i==0:
                    xe1.append([self.template.data.x1-d1,self.template.data.x1])
                    ye1.append([Y,Y])
                elif i==N-1:
                    xe2.append([self.template.data.x2+d2,self.template.data.x2])
                    ye2.append([Y,Y])
                d2 = abs(self.template.ytic2.x2-self.template.ytic2.x1)
                xs2.append([x+d2,x])
        l1.viewport = l.viewport
        l2.viewport = l.viewport
        le1.viewport = [0,1,self.template.data.y1, self.template.data.y2]
        le2.viewport = [0,1,self.template.data.y1, self.template.data.y2]
        txt.viewport = l.viewport
        l1.x = xs1+[[0,1,1,0]]
        l1.y = ys+[[0,0,1,1]]
        l2.x = xs2
        l2.y = ys
        le1.x = xe1
        le1.y = ye1
        le2.x = xe2
        le2.y = ye2
        txt.x = xt
        txt.y = yt
        txt.string = st
        X.plot(l1,bg=bg)
        X.plot(l2,bg=bg)
        X.plot(le1,bg=bg)
        X.plot(le2,bg=bg)
        X.plot(txt,bg=bg)


    def plot(self,array, template="default", bg=False, x=None):
        """Parallel Coordinates plot array must be of shape:
        (...,Dim1,Nlines)
        """
        if not array.ndim > 1:
            raise Exception("Array must be at least 2D")
        nlines = array.shape[-1]
        length = array.shape[-2]

        # Pad attributes related to Y axis
        for att in ["datawc_y1","datawc_y2",
                "yticlabels"]:
            # prepare local lists
            exec("%s = list(self.%s)" % (att,att))
            exec("while len(%s) < length: %s+=[%s[-1]]" % (att,att,att))

        data = array.asma()
        maxs = numpy.ma.max(data,axis=-1)
        mins = numpy.ma.min(data,axis=-1)

        t = vcs.createtemplate(source=self.template.name)
        t.blank()
        t.data.priority = 1
        for i in range(length):
            levels = vcs.mkscale(mins[i],maxs[i])
            # Do we need to create our range
            if numpy.allclose(datawc_y1[i],1.e20):
                datawc_y1[i]=levels[0]
                datawc_y2[i]=levels[-1]
            maxs[i] = datawc_y2[i]
            mins[i] = datawc_y1[i]

            # Do we have tics?
            if yticlabels[i] == "*":
                yticlabels[i]=vcs.mklabels(levels)
        if x is None:
            x = self.x
        self.drawYAxes(mins,maxs,yticlabels,x,bg) 
        ax = array.getAxis(-2)
        deflbls = {}
        for i in range(length):
            deflbls[float(i)/(length-1)] = str(ax[i])
        if self.xticlabels1 == "*":
            lbls1 = deflbls
        else:
            lbls1 = self.xticlabels1
        if self.xmtics1 == "":
            lbls1m = deflbls
        else:
            lbls1m = self.xmtics1
        if self.xticlabels2 == "*":
            lbls2 = deflbls
        else:
            lbls2 = self.xticlabels2
        if self.xmtics2 == "":
            lbls2m = deflbls
        else:
            lbls2m = self.xmtics2

        for l,lbls in enumerate([lbls1,lbls1m,lbls2,lbls2m]):
            ln = x.createline(source=self.template.xtic1.line)
            xs = []
            ys = []
            if l % 2 == 0:
                txt = x.createtext(To_source = self.template.xlabel1.textorientation,
                        Tt_source = self.template.xlabel1.texttable)
                txs = []
                tys = []
                ts = []
            for loc in lbls:
                xs.append([loc,loc])
                if l==0:
                    ys.append([self.template.xtic1.y1,self.template.xtic1.y2])
                    txs.append(loc)
                    tys.append(self.template.xlabel1.y)
                    ts.append(lbls[loc])
                    ln.priority = self.template.xtic1.priority
                    txt.priority = self.template.xlabel1.priority
                elif l == 1:
                    ys.append([self.template.xmintic1.y1,self.template.xmintic1.y2])
                    ln.priority = self.template.xmintic1.priority
                elif l == 2:
                    ys.append([self.template.xtic2.y1,self.template.xtic2.y2])
                    txs.append(loc)
                    tys.append(self.template.xlabel2.y)
                    ts.append(lbls[loc])
                    ln.priority = self.template.xtic2.priority
                    txt.priority = self.template.xlabel2.priority
                elif l == 3:
                    ys.append([self.template.xmintic2.y1,self.template.xmintic2.y2])
                    ln.priority = self.template.xmintic2.priority
            ln.x = xs
            ln.y = ys
            ln.viewport = [self.template.data.x1,self.template.data.x2,0,1]
            x.plot(ln,bg=bg)
            if l % 2 == 0:  # text on
                txt.viewport = ln.viewport
                txt.x = txs
                txt.y = tys
                txt.string = ts
                x.plot(txt,bg=bg)
            array.info()





        # Normalizes
        deltas = maxs-mins
        data = (data-mins[:,numpy.newaxis])/deltas[:,numpy.newaxis]

        # Pad attributes related to number of lines
        lineAtts = ["linetypes","linewidths",
                "markertypes","markersizes"]
        if self.markercolors is not None:
            lineAtts.append("markercolors")
        if self.linecolors is not None:
            lineAtts.append("linecolors")
        for att in lineAtts:
            # prepare local lists
            exec("%s = list(self.%s)" % (att,att))
            exec("while len(%s) < nlines: %s+=[%s[-1]]" % (att,att,att))

        if self.linecolors is None:
            linecolors = vcs.getcolors(range(nlines+1))
        if self.markercolors is None:
            markercolors = vcs.getcolors(range(nlines+1))

        for i in range(nlines):
            l = vcs.create1d()
            l.colormap = self.colormap
            l.linecolor = linecolors[i]
            l.linewidth = linewidths[i]
            l.linetype = linetypes[i]
            l.marker = markertypes[i]
            l.markercolor = markercolors[i]
            l.markersize = markersizes[i]
            l.datawc_y1 = 0.
            l.datawc_y2 = 1.
            x.plot(data[:,i],t,l,bg=bg)









    
