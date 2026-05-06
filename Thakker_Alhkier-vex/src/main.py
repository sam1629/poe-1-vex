# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       Sam and Fares                                                #
# 	Created:      5/5/2026, 9:38:30 AM                                         #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

# Brain should be defined by default
brain=Brain()

#---------------------------- Robot Configuration Code -----------------------#
rightMotor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
leftMotor = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)
#set the leftmotor to revesrse so that when driving forward or reverse it turns
# the same direction as the right motor
liftMotor = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False) #Liftarm motor
inertial_1 = Inertial(Ports.PORT5) #Inertial sensor
bumpSwitch = Bumper(brain.three_wire_port.a)
#------------------------------------------------------------------------------#


#---------------------------- Helper Functions -----------------------#
def bump():
    """
    Hold the program's execution until the bump switch is pressed
    """

    while(bumpSwitch.pressing() == False):
        wait(10, MSEC) #dbounce 10 ms

        brain.screen.set_cursor(1, 1) #place cursor in upper left corner
        brain.screen.print("Press the button to start the program") #print message to screen
    brain.screen.clear_line(1)
    brain.screen.set_cursor(1, 1) 
    brain.screen.print("Program executed")
    wait(1, SECONDS) #wait 1 second before clearing the screen

def inertialCalibration():
    """
    Calibrate the inertial sensor
    A wait time of 2 seconds is required
    This function should be called at the start of the program's execution
    """

    brain.screen.clear_screen()#Clear the brain's screen
    brain.screen.set_cursor(1,1)
    brain.screen.print("Calibrating Inertial Sensor")
    brain.screen.set_cursor(2,1)
    brain.screen.print("Don't move the robot!")
    inertial_1.calibrate() #Calibrate the inertial sensor

    wait(2, SECONDS) #Wait 2 seconds for the calibration process to complete

    brain.screen.clear_line(1)
    brain.screen.set_cursor(1,1)
    brain.screen.print("Intertial calibration complete")

def testIntertial():
    """
    Test the inertial sensor by having it display heading and total rotation data. Pressing the bump switch will end the test.
    """

    brain.screen.clear_screen()
    while(bumpSwitch.pressing() == False):
        brain.screen.set_cursor(5,1)
        brain.screen.print("Heading: ", str(inertial_1.heading()))
        brain.screen.set_cursor(6,1)
        brain.screen.print("Rotation: ", str(inertial_1.rotation()))
        brain.screen.set_cursor(8,1)
        brain.screen.print("Press the bump switch to exit")
        if (bumpSwitch.pressing() == True):
            break
        
        brain.screen.clear_row(8)
        brain.screen.set_cursor(8,1)
        brain.screen.print("Intertial test terminated")

    def main():
        bump() #call bump to execute the program
        inertialCalibration() #calibrate the inertial sensor
        testIntertial() #test the inertials output
    
    main()

 