from .DataRepository import DataRepository

class SEND:
    def send_to_databank(self, message):
        if message[0].isnumeric() and message[0] in range(5,8):
            DataRepository.append_waarde_sensor(message[0], message[1])
            try:
                DataRepository.append_waarde_sensor(message[0], message[1])
            except ValueError as error:
                print(error)

        

