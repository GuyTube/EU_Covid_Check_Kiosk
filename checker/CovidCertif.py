vaccine_products={ 
    "EU/1/20/1528": "Pfizer",
    "EU/1/20/1507": "Moderna",
    "EU/1/21/1529": "AstraZeneca",
    "EU/1/20/1525": "Janssen",
    "CVnCoV": "Curevac",
    "Sputnik-V": "Sputnik v",
    "Convidecia": "CanSino Biological",
    "EpiVacCorona": "institut Vector",
    "BBIBP-CorV": "Sinopharm",
    "Inactivated-SARS-CoV-2-Vero-Cell": "Sinovac Life Sciences",
    "CoronaVac": "Sinovac",
    "Covaxin": "Bharat Biotech",
    }

class CovidTest:
    def __init__(self, date, pays) :
        self.date, self.pays = date, pays

    def getDate(self):
        return self.date

    def getPays(self):
        return self.pays

class CovidVaccine:
    def __init__(self, date, nbDoseFull, nbDose, product) :
        self.date, self.nbDoseFull, self.nbDose, self.product = date, nbDoseFull, nbDose, product
        
    def getDate(self):
        return self.date
        
    def getProduct(self):
        return self.product

class CovidRecovery:
    def __init__(self, valid_start, valid_end, first_positive_test) :
        self.valid_from, self.valid_to, self.first_positive_test = valid_start, valid_end, first_positive_test

    def getValidFrom(self):
        return self.valid_from
        
    def getValidTo(self):
        return self.valid_to
        
class CovidCertif:

    def __init__(self, name, surname, c_name, c_surname, dateOfBirth):
        self.name, self.surname, self.correctedName, self.correctedSurname, self.dateOfBirth = name, surname, c_name, c_surname, dateOfBirth
        self.covidTests = {}
        self.covidVaccines = {}
        self.covidRecoveries = {}

    def addVaccine(self, vaccine):
        self.covidVaccines[vaccine.getDate()] = vaccine
        
    def addTest(self, test):
        self.covidTests[test.getDate()] = test
        
    def addRecovery(self, recovery):
        self.covidRecoveries[recovery.getValidTo()] = recovery
	
    def getType(self):
        if len(self.covidTests) > 0 :
            return "test"
        elif len(self.covidVaccines) > 0 :
            return "vaccine"
        elif len(self.covidRecoveries) > 0:
            return "recovery"
	
    def getLastVaccine(self) :
        if len(self.covidVaccines) > 0 :
            maxDate = ""
            for d in self.covidVaccines :
                if d > maxDate :
                    maxDate = d
                    lastVaccine = self.covidVaccines[d]
                    
            return lastVaccine
        else :
            return None
            
    def getLastTest(self) :
        if len(self.covidTests) > 0 :
            maxDate = ""
            for d in self.covidTests :
                if d > maxDate :
                    maxDate = d
                    lastTest = self.covidTests[d]
                    
            return lastTest
        else :
            return None

    def getLastRecovery(self) :
        if len(self.covidRecoveries) > 0 :
            maxDate = ""
            for d in self.covidRecoveries :
                if d > maxDate :
                    maxDate = d
                    lastRecovery = self.covidRecoveries[d]
                    
            return lastRecovery
        else :
            return None
