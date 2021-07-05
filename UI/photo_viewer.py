from PyQt5 import QtCore, QtGui, QtWidgets
from .bbx_part import CustomScene, BoxItem

class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)
    
    def __init__(self, parent, main): # scene
        super(PhotoViewer, self).__init__(parent)
        self.main = main
        self.init_state()

    def init_state(self):
        self.setMouseTracking(True)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.cnt = 0
        self._zoom = 0
        self._empty = True
        self._init = False 
        self._scene = CustomScene(self) ####
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        # -------------------------------
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse) 
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        
    def hasPhoto(self):
        return not self._empty  
    
    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                #--------------------------------------------------
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                #--------------------------------------------------
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None, init=False ):
        self._init = init
        self._zoom = 0
        
        if pixmap and not pixmap.isNull():
            
            if not self._init :
                self._empty = False
                self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            else:
                self._empty = True
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            
            self._photo.setPixmap(pixmap)
        else:
            
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)        # QtWidgets.QGraphicsView
            self._photo.setPixmap(QtGui.QPixmap())
            
        self.fitInView()
            
    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def createNewBbx(self, objName = None, color = None, rect=None, stateFlag =False, auto = True): # color ### !!!!
        # 1. get current category
        if rect is not None and len(self.main.colorMapping)>0 : # please ensure in color mapping
            if color is None:
                catego = str(self.main.catCombo.currentText()) ###
                color = self.main.colorMapping[catego]
                # --- get tmpExistNam on editor--
                tmpNamLst = self.main.tmpNamLst
                # --- get a new unique name -----
                objName = self.main.tracker.recordData.autoGenNewName(tmpNamLst)
                # --- append into list ----------
                self.main.tmpNamLst.append(objName)
                #--------------------------------
                auto = False
            
            
            #self.cnt += 1
            # 2. label view linking
            
            # =============== 1. create label list ==================
            # we can access main
            mycell = self.main.LabelLst.addRow(objName,QtGui.QColor(*color), stateFlag )
            # =============== 2. create bounding box ==================
            
            bbxitem = BoxItem(color= color , rect=rect, flag = self._photo, auto= auto ,bindCellit = mycell , useTable=self.main.LabelLst, assist = self.main.bbxSetSelected) #  #####
            self._scene.clearSelection()
            self._scene.addItem(bbxitem)
            
            # =========================================================
            self.main.bbxMapping.update({bbxitem : mycell}) # bbx -> listitem
            

class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.viewer = PhotoViewer(self)
        # 'Load image' button
        self.btnLoad = QtWidgets.QToolButton(self)
        self.btnLoad.setText('Load image')
        self.btnLoad.clicked.connect(self.loadImage)
        # Button to change from drag/pan to getting pixel info
        self.btnPixInfo = QtWidgets.QToolButton(self)
        self.btnPixInfo.setText('Enter pixel info mode')
        self.btnPixInfo.clicked.connect(self.pixInfo)
        self.editPixInfo = QtWidgets.QLineEdit(self)
        self.editPixInfo.setReadOnly(True)
        # -------
        self.viewer.photoClicked.connect(self.photoClicked)
        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.addWidget(self.viewer)
        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.setAlignment(QtCore.Qt.AlignLeft)
        HBlayout.addWidget(self.btnLoad)
        HBlayout.addWidget(self.btnPixInfo)
        HBlayout.addWidget(self.editPixInfo)
        VBlayout.addLayout(HBlayout)

    def loadImage(self):
        self.viewer.setPhoto(QtGui.QPixmap('001.png'))

    def pixInfo(self):
        self.viewer.toggleDragMode()

    def photoClicked(self, pos):
        if self.viewer.dragMode()  == QtWidgets.QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())
