Fedex-Batch-Track
=================

Python wrapper to batch track fedex shipments via CSV files
- This class is the infrastructure for sending and recieving tracking info to fedex
- It takes one argument, a list of tracking numbers 
- It builds a json request and also parses the response for delivery dates 
- for tracking numbers more than 30, use CSV as it splits it into chunks of 30 as this is the limit inherent in the fedex API

#Example Usage

tracking_list = [131321321312, 499552081013948, 3016898791]

t = TrackingPayload(tracking_list)

#to get delivery dates only
print t.delivery_dates

#to get full json response:

print t.data_response

'''



#Example Usage with CSV

- initialize object with 2 arguments, name of the csv file and the name of the column with tracking numbers
b = BatchTracker('tracktest1.csv','Tracking Numbers')

output = b.track()

b.write_results()
- creates a new csv with a column of delivery dates

'''
