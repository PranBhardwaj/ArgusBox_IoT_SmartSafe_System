import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from LCD import LCD
from Keypad import Keypad
from threading import Thread
from Solenoid import Solenoid
from tilt_switch import TiltSwitch
from signal import pause
from datetime import datetime
import os
import boto3
from botocore.exceptions import NoCredentialsError

class SmartSafe:
    def __init__(self, lcd_address=0x26, keypad_address=0x27):

        self.AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
        self.AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.BUCKET_NAME = 'smartsafe-logs'


        self.keypad = Keypad(keypad_address)
        self.lcd = LCD(2, lcd_address, True)

        self.picam1 = Picamera2(camera_num=0)
        self.picam2 = Picamera2(camera_num=1)

        self.video_config1 = self.picam1.create_video_configuration(main={"size": (1920, 1080)})
        self.picam1.configure(self.video_config1)

        self.video_config2 = self.picam2.create_video_configuration(main={"size": (1920, 1080)})
        self.picam2.configure(self.video_config2)

        self.encoder1 = H264Encoder()
        self.encoder2 = H264Encoder()

        self.solenoid = Solenoid(17)

        self.tswitch = TiltSwitch(27)

        self.state = 0

        self.buffer = ""

        self.access = False

        self.picam1_recording = False
        self.picam2_recording = False

        self.password_limit = 16

        self.password = "12345678"

        self.message_displaying = False

        self.key_pressed = None

        self.monitoring = False

        self.cameraThread = None

        self.file_buffer = []

        self.delete_buffer = []

    def key_check(self):
        self.key_pressed = self.keypad.get_key()
        if self.key_pressed:
            self.access = True
        else:
            self.access = False

    
    def password_system(self):
        if self.state == 0:
            self.lcd.message("Enter Password:", 1)
            self.lcd.message(self.buffer, 2)
            key = self.key_pressed
            if key:
                if key != '#' and key != '*':
                    if len(self.buffer) < self.password_limit:
                        self.buffer += key
                        self.lcd.message(self.buffer, 2)

                elif key == '#':
                    if self.buffer == self.password:
                        Thread(target=self.solenoid.turn_on).start()
                        Thread(target=self.password_accepted).start()
                        self.buffer = ""

                    else:
                        Thread(target=self.password_error).start()
                        self.buffer = ""

                else:
                    if len(self.buffer) > 0:
                        self.buffer = self.buffer[:-1]
                        self.lcd.message(self.buffer, 2)
        
        else:
            self.lcd.message("Authorized:", 1)
            self.lcd.message("Safe Open", 2)

    
    def password_error(self):
        self.message_displaying = True
        self.lcd.message("Unauthorized:", 1)
        for i in range(5):
            #self.lcd.message("Incorrect", 1)
            self.lcd.message("Access Denied", 2)
            time.sleep(0.5)
            self.lcd.message("", 2)
            time.sleep(0.5)
        self.message_displaying = False

    def password_accepted(self):
        self.message_displaying = True
        self.lcd.message("Authorized:", 1)
        self.lcd.message("Access Granted", 2)
        
        time.sleep(5)
        self.message_displaying = False
        

    def camera_monitoring_system(self):
        self.monitoring = True
        if self.state == 0:
            if self.access:
                #self.access = False
                if not self.picam1_recording:
                    print("camera 1 recording")
                    Thread(target=self.picam1_record, daemon=True).start()
        if self.state == 1:
            if not self.picam1_recording:
                print("camera 1 recording")
                Thread(target=self.picam1_record,daemon=True).start()
            if not self.picam2_recording:
                print("camera 2 recording")
                Thread(target=self.picam2_record, daemon=True).start()
        self.monitoring = False
                    


    def picam1_record(self, duration=10):
        if not self.picam1_recording:
            self.picam1_recording = True
            current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'picam1_log_{current_time}.mp4'
            output = FfmpegOutput(filename, audio=False)
            self.picam1.start_recording(self.encoder1, output)
            time.sleep(duration)
            self.picam1.stop_recording()
            print("camera 1 stopped recording")
            self.upload_to_s3(filename, self.BUCKET_NAME, f'picamera1/{filename}')
            if os.path.exists(filename): 
                os.remove(filename)
            self.picam1_recording = False

    def picam2_record(self, duration=10):
        if not self.picam2_recording:
            self.picam2_recording = True
            current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'picam2_log_{current_time}.mp4'
            output = FfmpegOutput(filename, audio=False)
            self.picam2.start_recording(self.encoder2, output)
            time.sleep(duration)
            self.picam2.stop_recording()
            print("camera 2 stopped recording")
            self.upload_to_s3(filename, self.BUCKET_NAME, f'picamera2/{filename}')
            if os.path.exists(filename): 
                os.remove(filename)
            self.picam2_recording = False

    def get_state(self):
        return self.state
    
    def get_cam1(self):
        if self.picam1_recording:
            return 1
        else:
            return 0
        
    def get_cam2(self):
        if self.picam2_recording:
            return 1
        else:
            return 0

    def upload_to_s3(self, file_name, bucket, object_name=None):
        if object_name is None:
            object_name = file_name

        s3 = boto3.client(
            's3',
            aws_access_key_id=self.AWS_ACCESS_KEY,
            aws_secret_access_key=self.AWS_SECRET_KEY
        )

        try:
            s3.upload_file(file_name, bucket, object_name)
            print(f"Upload Successful: {object_name}")
        except FileNotFoundError:
            print("The file was not found")
        except NoCredentialsError:
            print("Credentials not available")



    def run(self):
        self.key_check()
        if not self.message_displaying:
            self.password_system()
        
        if not self.monitoring:
            #self.camera_monitoring_system()
            self.cameraThread = Thread(target=self.camera_monitoring_system, daemon=True).start()

        if self.tswitch.get_state():
            self.state = 1
        else:
            self.state = 0
    

    def cleanup(self):
        try:
            self.picam1.stop_recording()
        except:
            pass
        try:
            self.picam2.stop_recording()
        except:
            pass
        self.lcd.clear()
        print("Resources cleaned up.")
            
        
    

if __name__ == '__main__':
    try:
        smartsafe = SmartSafe()
        smartsafe.run()
    except KeyboardInterrupt:
            smartsafe.cleanup()

