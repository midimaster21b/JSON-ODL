from datetime import datetime

class Logger:
    def __init__(self, filename):
        self.filename = filename

    def log(self, message):
        log_time = datetime.today()
        log_file = open(self.filename, 'a')
        log_file.write('{0} --- {1}\n'.format(log_time, message))
        log_file.close()
