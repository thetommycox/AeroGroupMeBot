##imports go here
import groupMe

##Define class
class messageFlag:
    def __init__(self,message):
        self.isTrue = False
        self.willLike = False
        self.checkTrue(message)

    def checkTrue(self,message):
        print("You've found the base class somehow")

    def response(self):
        groupMe.reply("You've found the base class somehow")            
        
    



