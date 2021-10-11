class TestResult:
    def __init__(self, status, resultHTML, resultJSON, covidCertif, texte, qrCode):
        self.status, self.resultHTML, self.resultJSON, self.covidCertif = status, resultHTML, resultJSON, covidCertif
        self.texte, self.qrCode = texte, qrCode
        
    def setStatus( self, s ) :
        self.status = s
        
    def setResultHTML( self, r ) :
        self.resultHTML = r

    def setResultJSON( self, r ) :
        self.resultJSON = r

    def setCovidCertif( self, c ) :
        self.covidCertif = c

    def setTexte( self, t) :
        self.texte = t

    def setQrCode( self, q ) :
        self.qrCode = q

    def reset(self) :
        self.status, self.resultHTML, self.resultJSON, self.covidCertif = "", "", "", None
        self.texte, self.qrCode = None, ""
        
