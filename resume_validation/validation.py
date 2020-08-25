import os
import shutil
class validation_class():
    def validation_method(self, entities, completeName_val, baz, completename):
        count = 0
        unpredicted_entities = ["FirstName", "LastName", "email-id", "mobile-number"]
        for i in unpredicted_entities:
            with open(completeName_val, "a+") as myfile:
                if i in entities:
                    count = count + 1
                    myfile.write("predicted %s is available"%i+"\n")
                else:
                    myfile.write("predicted %s is not available"%i+"\n")
        if count >= 4:
            print(count)
            destination = (os.getcwd() + "/" + 'Working')
            shutil.move(baz, destination)
            shutil.move(completeName_val, destination)
            shutil.move(completename, destination)
        else:
            with open(completeName_val, "a+") as myfile:
                myfile.write("The predcicted Values are: %d"%count+"\n")
            destination = (os.getcwd() + "/" + 'Not_working')
            shutil.move(baz, destination)
            shutil.move(completeName_val, destination)
            shutil.move(completename, destination)
        print(count)
        return count