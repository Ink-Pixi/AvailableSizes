import sys
import mysql.connector
from PyQt5.QtWidgets import QDialog, QApplication, QComboBox, QFormLayout, QTextEdit, QGroupBox, QLabel, QVBoxLayout, QMenuBar, QMenu, QMessageBox
from PyQt5.QtGui import QFont

class AvailableSizes(QDialog):
    def __init__(self):
        super(AvailableSizes, self).__init__()
        
        self.createCombos()
        self.createMenuBar()
        
        self.printOut = QTextEdit()
        self.printOut.setFont(QFont('Helvetica', 11, QFont.Bold))
        self.printOut.setReadOnly(True)
        
        mainLayout = QVBoxLayout()
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.grpBox)
        mainLayout.addWidget(self.printOut)
        self.setLayout(mainLayout)
        
        self.setWindowTitle("Available Sizes")
        
    def createCombos(self):
        cbFont = QFont("Times", 8, QFont.Bold)
        designs = self.getDesigns()
        
        self.grpBox = QGroupBox("Design")
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
                        WHERE CONCAT(d.sku_code, " - ", d.name) = '""" + sku + """'
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
                            CONCAT(d.sku_code, " - ", d.name) = '""" + sku + """'
                        AND
                            g.name = '""" + style + """'""")
        ds = sd.fetchall()
        lsSizes = []
        for i in ds:
            lsSizes.append(i[0])
        return lsSizes
    
class mysql_db():
    def mysql_connect(self):
        try:
            mysql_db.conn = mysql.connector.connect(user = 'AI_APP', password = 'rowsby01', host = 'wampserver', database = 'xaotees-inkpixi', raise_on_warnings = True) 
            mysql_db.db = mysql_db.conn.cursor()
        except BaseException as e:
            QMessageBox.critical(self, 'Database Error', "Can not connect to the MySQL database: \n" + str(e), QMessageBox.Ok)
        
        return mysql_db.db        
        
if __name__ == "__main__":
    
    app = QApplication(sys.argv) 
    az = AvailableSizes()
    az.show()
    sys.exit(app.exec_())