class CovidTest:
    def __init__(self, date, nbDoseFull, nbDose, product) :
        self.date, self.nbDoseFull, self.nbDose, self.product = date, nbDoseFull, nbDose, product

    def getDate():
        return self.date

class CovidVaccine:
    def __init__(self, date, nbDoseFull, nbDose, product) :
        self.date, self.nbDoseFull, self.nbDose, self.product = date, nbDoseFull, nbDose, product
        
    def getDate(self):
        return self.date

class CovidRecovery:
    def __init__(self, valid_start, valid_end, first_positive_test) :
        self.valid_from, self.valid_to, self.first_positive_test = valid_start, valid_end, first_positive_test

    def getValidFrom(self):
        return self.valid_from
        
    def getValidTo(self):
        return self.valid_to
        
class covidCertif:

    def __init__(self, name, surname, c_name, c_surname, dateOfBirth):
		self.name, self.surname, self.correctedName, self.correctedSurname, self.dateOfBirth = name, surname, c_name, c_surname, datOfBirth
        self.covidTests = {}
        self.covidVaccines = {}
        self.covidRecovery = {}

    def addVaccine(self, vaccine):
        self.covidVaccines[vaccine.getDate()] = vaccine
        
    def addTest(self, test):
        self.covidTests[test.getDate()] = test
        
    def addRecovery(self, recovery):
        self.covidTests[recovery.getValidTo()] = recovery
	
	def getType(self):
		if len(covidTests) > 0 :
            return "test"
        elif len(covidVaccines) > 0 :
            return "vaccine"
        elif len(recovery) > 0:
            return "recovery"
	
    def getLastVaccine(self) :
        if len(covidVaccines) > 0 :
            maxDate = ""
            for d in covidVaccines :
                if d > maxDate :
                    maxDate = d
                    lastVaccine = covidVaccines[d]
                    
            return lastVaccine
        else :
            return None
            
	