from .Database import Database
import datetime


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens
    
    @staticmethod
    def update_setting(id, value):
        if id == "manual mode":
            deviceID = 1
        else:
            return    
        sql = "UPDATE settings SET waarde = %s WHERE idsettings = %s"
        params = [value, deviceID]
        return Database.execute_sql(sql, params)
    
    @staticmethod
    def read_settings(id):
        sql = "SELECT waarde FROM settings where idsettings = %s;"
        params = [id]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_sensor(id, amount=500):
        sql = "SELECT date, waarde  FROM (SELECT * FROM tbl_sensordata where deviceID = %s ORDER BY date DESC LIMIT %s) sub ORDER BY id ASC"
        params = [id, amount]
        return Database.get_rows(sql, params)

    @staticmethod
    def append_waarde_sensor(id, waarde):
        sql = "insert into tbl_sensordata values('0', %s, %s, %s)"
        date = datetime.datetime.now().replace(microsecond=0)
        params = [id, date, waarde]
        return Database.execute_sql(sql, params)
    
    @staticmethod
    def update_pos_actuator(id, position):
        if id == "x":
            deviceID = 1
        elif id == "y":
            deviceID = 2
        else:
            return    
        sql = "UPDATE tbl_actuatorPos SET positie = %s WHERE deviceID = %s"
        params = [position, deviceID]
        return Database.execute_sql(sql, params)
