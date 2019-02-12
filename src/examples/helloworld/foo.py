import os
import sys

import pytransform

#-----------------------------------------------------------
#
# Part 1: check internet time by ntp server
#
#-----------------------------------------------------------

def check_expired_date_by_ntp():
    from ntplib import NTPClient
    from time import mktime, strptime

    NTP_SERVER = 'europe.pool.ntp.org'
    EXPIRED_DATE = '20190202'

    print('The license will be expired on %s' % EXPIRED_DATE)
    print('Check internet time from %s ...' % NTP_SERVER)
    c = NTPClient()
    response = c.request(NTP_SERVER, version=3)
    if response.tx_time > mktime(strptime(EXPIRED_DATE, '%Y%m%d')):
        print("The license has been expired")
        sys.exit(1)
    print("The license is not expired")

#-----------------------------------------------------------
#
# Part 2: show license information of obfuscated scripts
#
#-----------------------------------------------------------

def show_left_days_of_license():
   try:
       rcode = pytransform.get_license_info()['CODE']
       left_days = pytransform.get_expired_days()
       if left_days == -1:
           print('This license for %s is never expired' % rcode)
       else:
           print('This license for %s will be expired in %d days' % \
                 (rcode, left_days))
   except Exception as e:
       print(e)
       sys.exit(1)

#-----------------------------------------------------------
#
# Part 3: business code
#
#-----------------------------------------------------------

def hello():
    print('Hello world!')

def sum2(a, b):
    return a + b

def main():
    hello()
    print('1 + 1 = %d' % sum2(1, 1))

if __name__ == '__main__':

    show_left_days_of_license()
    # check_expired_date_by_ntp()

    main()
