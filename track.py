import json
import requests
import copy
import csv
import time                                                


'timing decorator'
def timeme(method):
    def wrapper(*args, **kw):
        startTime = int(round(time.time() * 1000))
        result = method(*args, **kw)
        endTime = int(round(time.time() * 1000))

        print(endTime - startTime,'ms')
        return result

    return wrapper




'''Uutility class for csv module  - for convenience'''
class CsvFile(object):
    def __init__(self, name):
        self.name = name
        self.data = []
        self.columns = []
    def __str__(self):
        return self.name

    def empty(self):
        self.data = []

    def fill(self):
        self.data = [x for x in csv.DictReader(open(self.name, 'rU'))]
        self.columns = csv.DictReader(open(self.name, 'rU')).fieldnames




'''
- This class is the infrastructure for sending and recieving tracking info to fedex
- It takes one argument, a list of tracking numbers 
IMPORTANT: LIMIT OF 30 for each request.... creating utility below for more
- It builds a json request and also parses the response for delivery dates 
- see EXAMPLE USAGE below


'''
class TrackingPayload():


    def __init__(self, tracking_list):
        self.data = {'data': {
                            'TrackPackagesRequest': {
                                'appType': 'wtrk',
                                'uniqueKey': '',
                                'processingParameters': {
                                    'anonymousTransaction': True,
                                    'clientId': 'WTRK',
                                    'returnDetailedErrors': True,
                                    'returnLocalizedDateTime': False
                                },
                                'trackingInfoList': []
                            }
                        },
                        'action': 'trackpackages',
                        'locale': 'en_US',
                        'format': 'json',
                        'version': 99
                        }
        self.template = {
                            'trackNumberInfo': {
                                'trackingNumber': "",
                                'trackingQualifier': '',
                                'trackingCarrier': ''
                            }
                        }
        self.tracking_list = tracking_list
        self.payload = self.insert_tracking_numbers(self.data)
        self.delivery_dates = self.get_delivery()

    def insert_tracking_numbers(self, payload):
        for x in self.tracking_list:
            copy1 = copy.deepcopy(self.template)
            copy1['trackNumberInfo']['trackingNumber'] = x
            payload['data']['TrackPackagesRequest']['trackingInfoList'].append(copy1)

        return payload

    def post_response(self):
        data = self.payload
        data['data'] = json.dumps(data['data'])
        data_response = requests.post('https://www.fedex.com/trackingCal/track', data).json()
        self.data_response = data_response
        return data_response

    def get_delivery(self):
        dates = {}
        dr = self.post_response()
        for x in dr['TrackPackagesResponse']['packageList']:
            dates.update({x['trackingNbr']:x['displayActDeliveryDt']})

        return dates

'''
#EXAMPLE usage

tracking_list = [131321321312, 499552081013948, 3016898791]

t = TrackingPayload(tracking_list)

#to get delivery dates only
print t.delivery_dates

#to get full json response:

print t.data_response

'''



'''
BATCH TRACKING

'''

class BatchTracker():


    def __init__(self, csv_file, tracking_column):
        self.tracking_column = tracking_column

        self.tracking_list = self.get_tracking_list(csv_file, tracking_column)
        self.chunks = self.get_split_list()


    def get_tracking_list(self, csv_file, tracking_column):
        cfile = CsvFile(csv_file)
        cfile.fill()
        cdata = cfile.data
        self.csv_data = cdata
        for x in self.csv_data:
            x[self.tracking_column] = x[self.tracking_column].split('<BR>')[0]
        self.csv_columns = cfile.columns
        tn = [x[tracking_column] for x in cdata]
        return tn

    def chunks(self, l, n):
        for i in xrange(0, len(l), n):
            yield l[i:i+n]

    def get_split_list(self):
        chunked = list(self.chunks(self.tracking_list, 30)) 
        return chunked

    def track(self):
        output = {}
        for x in self.chunks:
            t = TrackingPayload(x)
            for k, v in t.delivery_dates.iteritems():
                output.update({k:v})

        return output

    def write_results(self):

        ouput = self.track()
        f = open('output.csv','w')
        self.csv_columns += ['Delivery Date']
        writer = csv.DictWriter(f, fieldnames=self.csv_columns)
        headers = dict( (n,n) for n in self.csv_columns )
        writer.writerow(headers)
        for x in self.csv_data:
            try:
     
                x.update({'Delivery Date':output[x[self.tracking_column]]})
                writer.writerow(x)       
            except Exception as e:
                x.update({'Delivery Date':""})
                writer.writerow(x)
                pass
        f.close()
  

'''#Example Usage

# initialize object with 2 arguments, name of the csv file and the name of the column with tracking numbers
b = BatchTracker('tracktest1.csv','Tracking Numbers')

output = b.track()

b.write_results()


'''



