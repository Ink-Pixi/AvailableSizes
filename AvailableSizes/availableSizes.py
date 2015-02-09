import sys, ctypes
import mysql.connector
from PyQt5.QtWidgets import QDialog, QApplication, QComboBox, QFormLayout, QTextEdit, QGroupBox, QLabel, QVBoxLayout, QMenuBar, QMenu, QMessageBox, QToolButton, QHBoxLayout, QFrame
from PyQt5.QtGui import QFont, QIcon, QPalette
from PyQt5.QtCore import Qt, QSize

class AvailableSizes(QDialog):
    def __init__(self):
        super(AvailableSizes, self).__init__()
        
        self.createCombos()
        self.createHeader()
        #self.createMenuBar()
        
        self.printOut = QTextEdit()
        self.printOut.setFont(QFont('Helvetica', 11, QFont.Bold))
        self.printOut.setReadOnly(True)
        
        mainLayout = QVBoxLayout()
        #mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.frmHeader)
        mainLayout.addWidget(self.grpBox)
        mainLayout.addWidget(self.printOut)
        #mainLayout.setAlignment(self.frmHeader, Qt.AlignRight)
        self.setLayout(mainLayout)
        
        #self.setWindowTitle("Available Sizes")
        self.setWindowFlags(Qt.FramelessWindowHint)
        bgColor = QPalette()
        bgColor.setColor(self.backgroundRole(), Qt.gray)
        self.setPalette(bgColor)
        self.setWindowIcon(QIcon('icon/PS_Icon.png'))
        self.cbSku.setFocus()
        
    def createHeader(self):
        blk = QPalette()
        blk.setColor(blk.Foreground, Qt.white)
        
        lblTitle = QLabel("Availability Checker")
        lblTitle.setFont(QFont("Times", 12, QFont.Bold ))
        lblTitle.setPalette(blk) 
         
        btnClose = QToolButton()
        btnClose.setIcon(QIcon("icon\size_exit.png"))
        btnClose.setAutoRaise(True)
        btnClose.setIconSize(QSize(25,25))
        btnClose.clicked.connect(lambda: self.close())
        
        hbHeader = QHBoxLayout()
        hbHeader.addWidget(lblTitle)
        hbHeader.addWidget(btnClose)
        hbHeader.setContentsMargins(0, 0, 0, 0)
        
        self.frmHeader = QFrame()
        self.frmHeader.setLayout(hbHeader)
        
    def createCombos(self):
        cbFont = QFont("Times", 8, QFont.Bold)
        designs = self.getDesigns()
        
        self.grpBox = QGroupBox()
        self.grpBox.setFont(QFont('Times', 10, QFont.Bold))
        layout = QFormLayout()
        
        self.cbSku = QComboBox()
        self.cbSku.addItem("Designs")
        self.cbSku.addItems(designs)
        self.cbSku.setFont(cbFont)
        self.cbSku.currentIndexChanged.connect(self.skuChanged)
        
        self.cbStyle = QComboBox()
        self.cbStyle.addItem("Styles")
        self.cbStyle.setFont(cbFont)
        self.cbStyle.currentIndexChanged.connect(self.styleChanged)
        
        layout.addRow(QLabel("Design:"), self.cbSku)
        layout.addRow(QLabel("Style:"), self.cbStyle)
        
        self.grpBox.setLayout(layout)
    
    def skuChanged(self):
        
        if self.cbStyle.count() > 0:
            self.cbStyle.clear()
            self.cbStyle.addItem("Style")
            self.cbStyle.setCurrentIndex(0)
            styles = self.getStyles(self.cbSku.currentText())
        else: 
            styles = self.getStyles(self.cbSku.currentText())
        self.cbStyle.addItems(styles)
        
    def styleChanged(self):
        self.printOut.clear()
        sizes = self.getSizes(self.cbSku.currentText(), self.cbStyle.currentText())
        if self.cbStyle.currentText() != "Styles":
            for i in sizes:
                self.printOut.insertPlainText(i + '\n')
                    
       
    def createMenuBar(self):
        self.menuBar = QMenuBar()

        self.fileMenu = QMenu("&File", self)
        self.exitAction = self.fileMenu.addAction("E&xit")
        self.menuBar.addMenu(self.fileMenu)

        self.exitAction.triggered.connect(self.accept)
        
    def getDesigns(self):
        sd = mysql_db.mysql_connect(self)
        sd.execute("""SELECT 
                            DISTINCT CONCAT(d.sku_code, " - ", d.name) design
                        FROM
                            designs d
                        JOIN packages p on p.design_id = d.id
                        ORDER BY RIGHT(d.sku_code, 3), LEFT(d.sku_code,1)""")
        ds = sd.fetchall()
        lsDesigns = []
        for i in ds:
            lsDesigns.append(i[0])
        return lsDesigns    
    
    def getStyles(self, sku):
        sd = mysql_db.mysql_connect(self)
        sd.execute("""SELECT
                            DISTINCT g.name
                        FROM 
                            garment_styles_ages g
                        JOIN packages p ON p.garment_styles_age_id = g.id
                        JOIN designs d ON d.id = p.design_id
                        WHERE d.sku_code = '""" + sku[:4] + """'
                        ORDER BY g.name""")
        ds = sd.fetchall()
        lsStyles = []
        for i in ds:
            lsStyles.append(i[0])
        return lsStyles
    
    def getSizes(self, sku, style):
        style = style.replace("'", "\\'")
        sd = mysql_db.mysql_connect(self)
        sd.execute("""
                        SELECT
                            DISTINCT CONCAT(s.name, ' - ', c.name) size
                        FROM 
                            sizes s
                        JOIN packages p ON p.size_id = s.id
                        JOIN designs d ON d.id = p.design_id
                        JOIN colors c ON c.id = p.color_id
                        JOIN garment_styles_ages g ON g.id = p.garment_styles_age_id
                        WHERE 
                            d.sku_code = '""" + sku[:4] + """'
                        AND
                            g.name = '""" + style + """'""")
        ds = sd.fetchall()
        lsSizes = []
        for i in ds:
            lsSizes.append(i[0])
        return lsSizes

    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.leftClick = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.leftClick == True:
            x=event.globalX()
            y=event.globalY()
            x_w = self.offset.x()
            y_w = self.offset.y()
            self.move(x-x_w, y-y_w)
            
    def mouseReleaseEvent(self, event):
        self.leftClick = False       
    
class mysql_db():
    def mysql_connect(self):
        try:
            mysql_db.conn = mysql.connector.connect(user = 'AI_APP', password = 'rowsby01', host = 'wampserver', database = 'xaotees-inkpixi', raise_on_warnings = True) 
            mysql_db.db = mysql_db.conn.cursor()
        except BaseException as e:
            QMessageBox.critical(self, 'Database Error', "Can not connect to the MySQL database: \n" + str(e), QMessageBox.Ok)
        
        return mysql_db.db        
        
if __name__ == "__main__":
    
    myappid = 'Available Sizes' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid) 
    
    app = QApplication(sys.argv) 
    az = AvailableSizes()
    az.show()
    sys.exit(app.exec_())