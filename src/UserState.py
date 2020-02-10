import os
import csv
import time

class UserState():
    """
    This class manages storing user states to a CSV file.
    For example, if the user is currently speaking to a voice assistant device.
    """
    def __init__(self, target_ip, file_timestamp):
        # a manually-toggled switch that indicates if the user is currently speaking or not (0 or 1)
        self.user_speaking = 0
    
        curr_path = os.path.dirname(__file__)
        self.output_file_name = "csv/userstate_" + \
            str(target_ip) + "_" + file_timestamp + ".csv"
        
        self.write_to_file()  # create file including initial state

    def toggle_user_speaking_state(self):
        """
        Toggle the state of whether the user is currently speaking to a voice assistant.
        Write the new state into the CSV file.
        """
        self.user_speaking = 1 if self.user_speaking == 0 else 0
        print("\nUser begins/stops to speak to the Voice Assistant - new state: " + str(self.user_speaking))
        self.write_to_file()

    def write_to_file(self):
        """
        Append a line to the CSV file according to the current states.
        Format of each row appended to the CSV file:

        @param  timestamp           The current timestamp of the packet

        @param  user_speaking       The state of whether the user is speaking now (0 for no, 1 for yes)
        """
        timestamp = round(time.time())
        row = (timestamp, self.user_speaking)

        with open(self.output_file_name, 'a+', os.O_NONBLOCK) as output_file:
            writer = csv.writer(output_file)
            writer.writerow(row)
