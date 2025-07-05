import os
import glob

directory = '/content/kvote-backend/csv/'

def delete():
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)
delete()

import os

