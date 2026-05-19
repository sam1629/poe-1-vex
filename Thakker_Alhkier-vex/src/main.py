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
        wait(10, MSEC) #dbounce 10 ms
        brain.screen.set_cursor(5,1)
        brain.screen.print("Heading: ", str(inertial_1.heading()))
        brain.screen.set_cursor(6,1)
        brain.screen.print("Rotation: ", str(inertial_1.rotation()))

        brain.screen.set_cursor(8,1)
        brain.screen.print("Press the bump switch to exit")  

        brain.screen.clear_row(8)
        brain.screen.set_cursor(8,1)
        brain.screen.print("Inertial test terminated")

def driveStraightData(e):
    brain.screen.set_cursor(1,1)
    brain.screen.print("Postiion: " + str(leftMotor.position())) # Return the current motor count

    brain.screen.set_cursor(1,1)
    brain.screen.print("Rotation: " + str(inertial_1.rotation())) #Return the current rotation value

    brain.screen.set_cursor(1,1)
    brain.screen.print("Error: " + str(e)) # Return the current error


def stopMotors():

    """
    Stop both motors at the same time
    """
    rightMotor.stop()
    leftMotor.stop()
    wait(0.5, SECONDS)

def pause():
    """
    Pause for 4 seconds
    """
    wait(4, SECONDS)

def driveStraight(distance, setpoint, motorVelocity):
    """
    1. distance = distance to trave in inches
    2. setpoint = 0-degrees
    3. motorVelocity = the velocity of the motors (+) => forward, (-) => reverse
    """

    inertial_1.reset_rotation() #Reset the rotation before each driving straight test
#set stopping mode for the motors
    leftMotor.set_stopping(COAST)
    rightMotor.set_stopping(COAST)

    kP = 0.28 # proportional constant for driving straight
                #used to calculate the correction to maintain course
                #if too small, correction will occur too slowly
                # if too large, correction will occur
                #determine host value by iteratively testing
    wheelDiameter = 4 #Diameter of the wheels in inches

    #calculate the distance in terms of encoder tickets ( 1 tick = 1 degree)
    #distance (ticks) = (distance (inches) / (pi * wheel diameter)) * 360
    wheelCircumference = wheelDiameter * math.pi        #wheel circumference
    distance = (distance / wheelCircumference) * 360 #distance in terms of encoder ticks
    
    leftMotor.set_position(0, DEGREES) #Reset the left motor's position to 0 degrees
    rightMotor.set_position(0, DEGREES) #Reset the right motor's position to 0 degrees

    #Drive forward if motor velocity > 0
    if(motorVelocity > 0):
        #while loop to track the distance traveled
        while(leftMotor.position() < distance):
            error = (setpoint - inertial_1.rotation()) #Calculate error
            correction = kP * error #motor velocity correction

            #correct motor velocities
            # if error > (setpoint> rotation ) => drifting left
            # if error < (setpoint < rotation ) => drifting right

            leftMotor.set_velocity(motorVelocity + correction, PERCENT) #Increase left motor velocity to correct right drift
            rightMotor.set_velocity(motorVelocity - correction, PERCENT) #Decrease right motor velocity

            leftMotor.spin(FORWARD)
            rightMotor.spin(FORWARD)

            driveStraightData(error) #Display position, rotation, and error
    #stop the motors when the desired distance is reached
        stopMotors()
    else:

        distance *= -1 # distance= distance * -1
        while(leftMotor.position() < distance):
            error = (setpoint - inertial_1.rotation()) #Calculate error
            correction = kP * error #motor velocity correction

            #correct motor velocities
            # if error > (setpoint> rotation ) => drifting left
            # if error < (setpoint < rotation ) => drifting right

            leftMotor.set_velocity(motorVelocity + correction, PERCENT) #Increase left motor velocity to correct right drift
            rightMotor.set_velocity(motorVelocity - correction, PERCENT) #Decrease right motor velocity

            leftMotor.spin(FORWARD)
            rightMotor.spin(FORWARD)

            driveStraightData(error) #Display position, rotation, and error
    #stop the motors when the desired distance is reached
        stopMotors()

def turnData(turnError, derivative):
    """
    Print the current heading, turning error, and derivative values
    """
    brain.screen.set_cursor(1,1)
    brain.screen.print("Postiion: " + str(inertial_1.heading())) # Return the current motor count

    brain.screen.set_cursor(2,1)
    brain.screen.print("Rotation: " + str(abs(turnError))) #Return the current turning error 

    brain.screen.set_cursor(3,1)
    brain.screen.print("Error: " + str(abs(derivative))) # Return the current derivative

def pointTurn(setPoint):
    """
    1. Perform a point turn using the inertial sensor and proportional and derivative control
    2. Argument: Desired heading (setPoint)
    """
    brain.screen.clear_screen() #Clear the brain's screen

    leftMotor.set_stopping(BRAKE)
    rightMotor.set_stopping(BRAKE)

    difference = setPoint - inertial_1.heading()

    #want to minimize the amount of turn required 

    if(setPoint > inertial_1.heading()):
        if(abs(difference) > 180):
            clockwise = True
        else:
            clockwise = False
    else:
        if(abs(difference) > 180):
            clockwise = False
        else:
            clockwise = True
    
    #Define kP and kD values for the CW and CCW turns
    if (clockwise):
        kP = 0.04   #Values if clockwise
        kD = 0.00
    else:           #Values if counterclockwise
        kP = 0.04
        kD = 0.00
    
    # Define maximum velocity and previous error terms
    maxVelocity = 50    #Units %
    previousError = 0.0 #Error from the previous iteration of the control loop

    
    while(True):

        turnError = setPoint - inertial_1.heading()
        derivative = turnError - previousError

        #Stop motors and exit the control loop when the error and
        #derivative are sufficiently small to ensure the
        #set point was reached without oscillation
        if ((abs(turnError) < 1) and (abs(derivative) < 0.2)):
            stopMotors()    #Stop the motors
            break           #Leave the loop
        
        # Proportional and Derivative correction calculations
        turnCorrection = (kP * turnError) + (kD * derivative)

        # Limit the corrective term to make sure we don't exceed the maximum velocity
        if(abs(turnCorrection) > 1):
            turnCorrection = 1
        
        turnVelocity = turnCorrection * maxVelocity

        
        if(clockwise):
            leftMotor.set_velocity(turnVelocity)
            rightMotor.set_velocity(turnVelocity)
        else:
            leftMotor.set_velocity(-turnVelocity)
            rightMotor.set_velocity(-turnVelocity)
            


def driveBackwards(distance, setpoint, motorVelocity):
    """
    1. distance = distance to travel backwards in inches
    2. setpoint = 0-degrees
    3. motorVelocity = the velocity of the motors (positive value)
    """

    inertial_1.reset_rotation() #Reset the rotation before each driving straight test
    kP = 0.14 # proportional constant for driving straight in reverse
                #used to calculate the correction to maintain course
                #a smaller value helps reduce overshoot while reversing
    wheelDiameter = 4 #Diameter of the wheels in inches

    #calculate the distance in terms of encoder tickets ( 1 tick = 1 degree)
    #distance (ticks) = (distance (inches) / (pi * wheel diameter)) * 360
    wheelCircumference = wheelDiameter * math.pi        #wheel circumference
    distance = (distance / wheelCircumference) * 360 #distance in terms of encoder ticks
    
    leftMotor.set_position(0, DEGREES) #Reset the left motor's position to 0 degrees
    rightMotor.set_position(0, DEGREES) #Reset the right motor's position to 0 degrees

    #Drive backwards
    #while loop to track the distance traveled
    while(leftMotor.position() > -distance):
        error = (setpoint - inertial_1.rotation()) #Calculate error
        correction = kP * error #motor velocity correction

        #correct motor velocities for reverse direction
        leftMotor.set_velocity(motorVelocity - correction, PERCENT)
        rightMotor.set_velocity(motorVelocity + correction, PERCENT)

        leftMotor.spin(REVERSE)
        rightMotor.spin(REVERSE)

        driveStraightData(error) #Display position, rotation, and error
        wait(10, MSEC)
    #stop the motors when the desired distance is reached
    stopMotors()


def main():
    bump() #call bump to execute the program
    inertialCalibration() #calibrate the inertial sensor
    
    driveStraight(86, 0, 50) #call driveStraight with distance, setpoint, and motor velocity
    pause()
    driveBackwards(86, 0, 50) #call driveBackwards with distance, setpoint, and motor velocity
    
main()

 