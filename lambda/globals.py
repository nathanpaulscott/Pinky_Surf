import re
from datetime import datetime, timedelta, timezone
import os
import json
import sys
import time
import io

import boto3




#-------------------------------------------------------------------
class global_params():
    def __init__(self):
        pass
    
    ##########################################################
    #global attributes
    code_path = '.'
    #code_path = r'D:/A.Nathan/Engineering Library/Laptop/eng-calculators and tools/1a.SW Dev - Agile, REST, Testing/0a.Webpage for Pinky/aws version_v2'
    layer_path = None
    '''
    s3_images_path = dict(
        bucket='pinky-surf',
        folder='/images/'
    )
    '''

    files = dict(
        html=   'index.html',
        js=     '/js/nat_js.js',
        css=    '/css/nat_css.css',
    )
    
    tz_offset = 8
    offsets = []

    data = [
        dict(
            url = dict(prefix='http://www.stormsurfing.com/stormuser2/images/dods/indi_slp_parea_', suffix='hr.png'),
            name = 'slp',
            offsets = (-216, 180),
            filename = dict(prefix='indi_slp_parea_', suffix='hr.png'),
        ),
        dict(
            url = dict(prefix = 'http://www.stormsurfing.com/stormuser2/images/grib/indi_swell_', suffix = 'hr.png'),
            name = 'swell',
            offsets = (0, 180),
            max_offset = 180,
            filename = dict(prefix='indi_swell_', suffix='hr.png'),
        ),
        dict(
            url = dict(prefix = 'http://www.stormsurfing.com/stormuser2/images/grib/indi_per_', suffix = 'hr.png'),
            name = 'period',
            offsets = (0, 180),
            filename = dict(prefix='indi_per_', suffix='hr.png'),
        ),
        dict(
            url = dict(prefix = 'http://www.stormsurfing.com/stormuser2/images/grib/indi_wave1_', suffix = 'hr.png'),
            name = 'wave',
            offsets = (0, 180),
            filename = dict(prefix='indi_wave_', suffix='hr.png'),
        )
    ]


    ##########################################################
    #error handling    
    def error_exit(self, msg):
        response = {
            'statusCode': 400,
            'headers': {"Content-Type": "application/json"},
            'body': json.dumps({"result":"nok", "error":msg})
        }
        return response
   ##########################################################



    ##########################################################
    #trig functions    
    def deg_subtract(self, a, b):
        if a >= 360 or b >= 360 or a < 0 or b < 0:
            return 'inputs are out of limits'
        result = a-b
        if a > b:
            return result
        else:
            return 360 + result
    
    
    def deg_add(self, a, b):
        if a >= 360 or b >= 360 or a < 0 or b < 0:
            return 'inputs are out of limits'
        result = a+b
        if result >= 360:
            return result - 360
        else:
            return result
    ##########################################################


    
    
    
    ##########################################################
    #datetime management functions
    def dt_now(self, tz_offset):
        '''
        returns the dt now with the tzinfo set
        '''
        dt = datetime.utcnow()
        dt = dt.replace(tzinfo=timezone.utc)
        #change to the given tz
        tz = timezone(timedelta(hours=tz_offset))
        return dt.astimezone(tz)
        
        
    
    def dt_fromtimestamp(self, ts, tz_offset):
        '''
        returns the dt from the timestamp with the given tz_offset set in tzinfo
        remember datetime.from_timestamp(ts) returns the dt in local timezone by default, which can cause all sorts of issues
        '''
        #get the dt in local time without tzinfo set
        dt = datetime.fromtimestamp(ts)
        #set tzinfo to local time
        td = datetime.now() - datetime.utcnow()
        dt = dt.replace(tzinfo=timezone(td))
        #change to the given tz
        tz = timezone(timedelta(hours=tz_offset))
        return dt.astimezone(tz)
        
    
    
    def dt_make(self, year, month, day, hour, minute, second, tz_offset):
        '''
        returns the dt with the given tz_offset set
        '''
        #make dt in local timezone
        tz = timezone(timedelta(hours=tz_offset))
        return datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, tzinfo=tz)
        
    
    def dt_set_tz(self, dt, tz_offset):
        ''' 
        sets the tz of a dt
        '''
        tz = timezone(timedelta(hours=tz_offset))
        return dt.replace(tzinfo=tz)
    
    
    def dt_change_tz(self, dt, tz_offset):
        ''' 
        changes the tz of a dt
        '''
        tz = timezone(timedelta(hours=tz_offset))
        return dt.astimezone(tz)
    ##########################################################


    ##########################################################
    #s3 functions
    def s3_scan_folder(self, bucket, folder, num_items, recursive):
        '''
        This returns the names, dates and sizes of the given s3 path, not the contents
        This includes meta data such as file size and creation/mod date
        It gets all objects within the given folder (even in child subfolders)
        return files = [{name:name, date:date(as datetime), size:size(in bytes)}...]
        bucket is the bucket name
        folder is the folder within the bucket, eg. use '/' to get the root and all subdirectories contents, use '/some folder/' to get the contents of some folder and all its subfolders
        num_items is the number of items limit to return, actually applies to all objects in all subfolders even if recursive is false
        recursive = True/False => False, means no subfolders
        '''
        #check file_path first
        if folder[0] != '/' or folder[-1] != '/':
            raise Exception('folder needs to start and end with "/"')
        #remove the initial '/' as S3 doesn't need it 
        folder = folder[1:]
        #scan the folder
        client = boto3.client('s3')
        try:
            result = client.list_objects_v2(
                Bucket=     bucket,
                MaxKeys=    num_items,
                Prefix=     folder,
            )
            if result['IsTruncated']:
                raise Exception('Not all objects returned, try increasing max items...')
            output = [{'name':x['Key'], 'date':x['LastModified'], 'size':x['Size']} for x in result['Contents']]
            #remove the prefix from the filenames
            for i, x in enumerate(output):
                output[i]['name']  = x['name'][x['name'].find(folder)+len(folder):] 
            #remove the subfolders if recursive = False
            if not recursive:
                output = [x for x in output if x['name'].find('/') == -1]

            return output

        except Exception as e:
            self.error_exit(str(e))



    def s3_write_file_object(self, bucket, file_path, file_name, file_data):
        '''
        This writes the given file object to the given s3 folder, including meta data
        bucket is the s3 bucket name to write to
        file_name is the name to save the file as, eg 'somefile.txt'
        file_path is the path from root where to save the file => eg'/some/path/'
        file_data is the actual file data
        eg.
        r = requests.get(url)
        result = s3_write_file_object('some bucket', '/some/s3/path/, 'some file.txt', r.content)
        '''
        #check file_path first
        if file_path[0] != '/' or file_path[-1] != '/':
            raise Exception('path needs to start and end with "/"')
        #remove the initial '/' as S3 doesn't need it 
        file_path = file_path[1:]
        #make the file key
        file_key = '{}{}'.format(file_path, file_name)
        #write the file to s3
        client = boto3.client('s3')
        try:
            result = client.upload_fileobj(
                    Fileobj=    io.BytesIO(file_data),
                    Bucket=     bucket,
                    Key=        file_key,
                )
            return result
        except Exception as e:
            print(e)
            self.error_exit(str(e))




    def s3_write_file(self, bucket, file_path, file_name, local_file_path):
        '''
        This writes the given file from the local system to s3
        bucket is the s3 bucket name to write to
        file_name is the name to save the file as, eg 'somefile.txt'
        file_path is the path from root where to save the file => eg'/some/path/'
        local_file_path is the local file location
        eg.
        result = s3_write_file('some bucket', '/some/s3/path/, 'some file.txt', 'd://some/local/path/')
        '''
        #check file_path first
        if file_path[0] != '/' or file_path[-1] != '/':
            raise Exception('path needs to start and end with "/"')
        #remove the initial '/' as S3 doesn't need it 
        file_path = file_path[1:]
        #make the file key
        file_key = '{}{}'.format(file_path, file_name)
        #get local filename
        local_file = '{}{}'.format(local_file_path, file_name)
        #write the file to s3
        client = boto3.client('s3')
        try:
            result = client.upload_file(
                    Filename=   local_file,
                    Bucket=     bucket,
                    Key=        file_key,
                )
            return result
        except Exception as e:
            print(e)
            self.error_exit(str(e))

    ##########################################################
