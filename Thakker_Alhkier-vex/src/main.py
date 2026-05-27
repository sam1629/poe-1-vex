# ---------------------------------------------------------------------------- #
#                                                                              #
#   Module:       main.py                                                      #
#   Author:       Sam Thakker and Fares Alhkier                                #
#   Created:      5/5/2026, 9:42:24 AM                                         #
#   Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
import math

from vex import *

# Brain should be defined by default
brain = Brain()

# -------------------------------------------- Robot Configuration --------------------------------------------
rightMotor = Motor(Ports.PORT7, GearSetting.RATIO_18_1, False)  # Right drivetrain motor
leftMotor = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)  # Left drivetrain motor
# Set the leftMotor reverse property to True so that when driving forward it turns in the
# same direction as the right motor.
liftMotor = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False)  # Lifearm motor
inertial_1 = Inertial(Ports.PORT5)  # Inertial sensor
bumpSwitch = Bumper(brain.three_wire_port.a)  # Bumper switch
# --------------------------------------------------------------------------------------------------------------


# -------------------------------------------- Helper Functions --------------------------------------------
def bump():
    """
    Hold the program's execution until the button is pressed
    """

    while bumpSwitch.pressing() == False:
        wait(10, MSEC)  # Debounce the button (10 ms)

        brain.screen.set_cursor(1, 1)  # Place the cursor in upper left corner of the screen
        brain.screen.print("Press the button to start the program")
        pass

    brain.screen.clear_line(1)  # Clear the text on row 1
    brain.screen.set_cursor(1, 1)
    brain.screen.print("Program executed")
    wait(1, SECONDS)  # Wait 1 second before proceeding


def intertialCalibration():
    """
    Calibrate the inertial sensor
    A wait time of 2 seconds is required
    This function should be called at the start of the program's execution
    """

    brain.screen.clear_screen()  # Clear the brain's screen
    brain.screen.set_cursor(1, 1)  # Place the cursor in upper left corner of the screen
    brain.screen.print("Calibrating the inertial sensor")
    brain.screen.set_cursor(2, 1)  # Place the cursor on row 2
    inertial_1.calibrate()  # Calibrate the inertial sensor

    wait(2, SECONDS)  # Wait for the calibration process to complete

    brain.screen.clear_line(1)
    brain.screen.set_cursor(1, 1)
    brain.screen.print("Inertial calibration completed")


def testInertial():
    """
    Test the inertial sensor by having it display heading and total rotation
    data. Pressing the bump switch will end the test
    """

    brain.screen.clear_screen()  # Clear the brain's screen
    while bumpSwitch.pressing() == False:
        wait(10, MSEC)  # Debounce the button (10 ms)
        brain.screen.set_cursor(5, 1)
        brain.screen.print("Heading: " + str(inertial_1.heading()))
        brain.screen.set_cursor(6, 1)
        brain.screen.print("Rotation: " + str(inertial_1.rotation()))
        brain.screen.set_cursor(8, 1)
        brain.screen.print("Press the bump switch to exit")
    brain.screen.clear_line(8)
    brain.screen.set_cursor(8, 1)
    brain.screen.print("Inertial test terminated")
    
def driveStraightData(e): 
    """
    1. Report position, rotation and error values to the screen while driving
    2. Parameter: e = error value (setpoint - rotation)
    """

    brain.screen.set_cursor(1, 1)
    brain.screen.print("Position: " + str(leftMotor.position())) # Return the current motor count
    
    brain.screen.set_cursor(2, 1)
    brain.screen.print("Rotation: " + str(inertial_1.rotation())) # Return the current rotation value
    
    brain.screen.set_cursor(3, 1)
    brain.screen.print("Error: " + str(e)) # Return the current error

def stopMotors():
    rightMotor.stop()
    leftMotor.stop()
    wait(0.5, SECONDS) # Wait 0.5 seconds for the system to stabilize
    
def driveStraight(distance, setpoint, motorVelocity):
    """
    1. distance = distance to travel in inches
    2. setpoint = 0-degrees of rotation for driving straight
    3. motorVelocity = the velocity of the motors (+) => forward, (-) => reverse
    """
    
    inertial_1.reset_rotation() # Reset the rotation before each driving
    
    # Set stopping mode for the motors
    leftMotor.set_stopping(COAST)
    rightMotor.set_stopping(COAST)
    
    kP = 0.28       # Proportional constant for driving straight
                    # used to calculate the correctionto maintain course
                    # If too small, correction will occur too slowly
                    # If too large, overcorrection will occur
                    # Determine best value by iteratively testing
                    
    wheelDiameter = 4 # Wheel dia. = 4 inches
    
    # Calculate the distance in terms of encoder ticks (1 tick = 1 degreee)
    #distance (ticks) = Distance in inches / Wheel circumference * 360 (degrees in one rotation)
     
    wheelCircumference = wheelDiameter * math.pi # Wheel circumeference
    distance = (distance / wheelCircumference) * 360 # Distance in ticks
     
     # Reset the motor encoder to zero before driving
    leftMotor.set_position(0, DEGREES)
    rightMotor.set_position(0, DEGREES)
    
    # Drive forward if motor velocity > 0
    if(motorVelocity > 0):
        # While loop to track the distance traveled
        while(leftMotor.position(DEGREES) < distance):
            error = (setpoint - inertial_1.rotation()) # Caculate error
            correction = kP * error                    # Motor velocity correction

            # Correct motor velocites
            # if error > 0 (setpoint > rotation) => drifting left
            # if error < 0 (setpoint < rotation) => drifting right
            
            leftMotor.set_velocity(motorVelocity + correction, PERCENT) 
            rightMotor.set_velocity(motorVelocity - correction, PERCENT)
            
            # Spin motors
            leftMotor.spin(FORWARD)
            rightMotor.spin(FORWARD)
            
            driveStraightData(error) # Display position, rotation, and error
    
        # Stop the motors when the desired distance is reached
        stopMotors()
        
    # Drive straight in reverse if motor velocity < 0
    else:
        
        distance *= -1 # distance = distance * -1
        # While loop to track the distance traveled
        while(leftMotor.position(DEGREES) > distance):
            error = (setpoint - inertial_1.rotation()) # Caculate error
            correction = kP * error                    # Motor velocity correction

            # Correct motor velocites
            # if error > 0 (setpoint > rotation) => drifting left
            # if error < 0 (setpoint < rotation) => drifting right
            
            leftMotor.set_velocity(motorVelocity + correction, PERCENT) 
            rightMotor.set_velocity(motorVelocity - correction, PERCENT)
            
            # Spin motors
            leftMotor.spin(FORWARD)
            rightMotor.spin(FORWARD)
            
            driveStraightData(error) # Display position, rotation, and error
    
        # Stop the motors when the desired distance is reached
        stopMotors()

def turnData(turnError, derivative):
    """
    Print the current heading, turning error and derivative values
    """
    brain.screen.set_cursor(1, 1)
    brain.screen.print("Heading: " + str(inertial_1.heading())) # Return the current motor count
    
    brain.screen.set_cursor(2, 1)
    brain.screen.print("Error: " + str(abs(turnError))) # Return the error value (absolute value to avoid negative error values)
    
    brain.screen.set_cursor(3, 1)
    brain.screen.print("Derivative: " + str(derivative)) # Return the derivative value

def pointTurn(setPoint):
    """
    1. Perform a point turn using using the inertial sensor and proportional and derivative control
    2. Arguement: Desired heading (setpoint)
    """

    brain.screen.clear_screen() # Clear the brain's screen
    
    # Set stopping mode for turn
    leftMotor.set_stopping(BRAKE)
    rightMotor.set_stopping(BRAKE)
    
    # Calculate the difference between setPoint and current heading
    difference = setPoint - inertial_1.heading()
    
    # Want to minimizr the amount of turn required
    if(setPoint > inertial_1.heading()):
        if(abs(difference) <= 180): # Turn CW
            clockwise = True
        else: # Turn CCW
            clockwise = False
    else:
        if(abs(difference) <= 180): # Turn CCW
            clockwise = False
        else: # Turn CW
            clockwise = True
    
    # Define the kP and kD constants for the CW and CCW turnus
    if(clockwise):      
        kP = 0.04       # Values if clockwise
        kD = 0.00
    else:               
        kP = 0.04       # Values if counterclocwise
        kD = 0.00
    
    # Define maximum velocity and previous error terms
    maxVelocity = 50          # Units : %
    previousError = 0.0       # Error from the previous iteration, used to calculate the derivative term
    
    while(True):
        turnError = setPoint - inertial_1.heading()
        derivative = turnError - previousError
        
        # Stop motors and exit the control loop when the error and
        # derivate terms are sufficiently small to ensure the
        # setpoint was reached without osillation
        if(abs(turnError) < 1 and abs(derivative) < 0.2):
            stopMotors()    # Stop the motors
            break           # Leave the loop
        
        # Proportional and Derivative correction calculation
        turnCorrection = (kP * turnError) + (kD * derivative)
        
        # Limit the corrective term to make sure we don't exceed the maximum velocity
        if(abs(turnCorrection) > 1):
            turnCorrection = 1
        
        turnVelocity =  turnCorrection * maxVelocity 
        
        if(clockwise): # Turn CW
            leftMotor.set_velocity(turnVelocity)
            rightMotor.set_velocity(-1 * turnVelocity)
        else: # Turn CCW
            leftMotor.set_velocity(-1 * turnVelocity)
            rightMotor.set_velocity(turnVelocity)
        
        # Spin the motors
        leftMotor.spin(FORWARD)
        rightMotor.spin(FORWARD)
        
        turnData(turnError, derivative) # Print the heading, error, and derivative values to the screen
        
        previousError = turnError # Update the previous error for the next iteration
        
        wait(20, MSEC) # Wait 20 ms
def liftArm(motorVelocity, liftAngle):
    liftMotor.set_stopping(HOLD) # Configure the motor to hold its position

    liftMotor.set_velocity(motorVelocity, PERCENT) # Set lift arm motor

    gearRatio = 5
    motorAngularDisplacement = liftAngle * gearRatio #calcualte motor axle's angular displacement

    liftMotor.spin_for(FORWARD, motorAngularDisplacement, DEGREES) # Spin the motor for the given angular displacment in degrees
    wait(0.5, SECONDS) 


def main():
    """
    The main() function is the program that will be executed by the brain
    """
    bump()  # call bump() to executed the program
    intertialCalibration()  # Calibrate the inertial sensor

    """
    driveStraight(83.8, 0, 50) # Call driveStaight() with distance, setpoint, and motor velocity parameters
    wait(4, SECONDS) # Wait 4 seconds before executing the next command
    driveStraight(83.8, 0, -50) # Call driveStaight() with distance, setpoint, and motor velocity parameters to drive in reverse
    """
    
    
    pointTurn(224)
    """
    wait(2, SECONDS)
    pointTurn(27)
    wait(2, SECONDS)
    pointTurn(135)
    """

main()