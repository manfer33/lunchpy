#!/usr/bin/python

from bs4 import BeautifulSoup
import  urllib2, sys, unicodedata

html='WebPage'

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        soup = BeautifulSoup(urllib2.urlopen(html).read(),"lxml")
        week, day = {}, ""

        # Get Date
        date_elem = soup.find('h4')
        date = date_elem.contents[0].replace(' ','')
        date = date[date.find(':')+1:]

        # Get weekly lunch info
        for row in soup.select("tr"):
            th, td = row.findAll("th"), row.findAll("td")
            if th:
                if len(th) == 1:
                    day = row.find(['strong','span'])
                    day = day.contents[0]
                    day = strip_accents(day[:day.find(' ')].lower())
                    week[day] = ""
            if td:
                no_serv = row.find('td', attrs={'align':'center'})
                if no_serv:
                    week[day] = [no_serv.contents[0]]
                else:
                    week[day] = [td[0].contents[0].replace('*',''), td[1].contents[0].replace('*',''), td[2].contents[0].replace('*','')]

        print date
        print week[sys.argv[1]][0]
        if len(week[sys.argv[1]]) > 1:
            print week[sys.argv[1]][1]
            print week[sys.argv[1]][2]
    else:
        print "./lunch.py <day> [lunes, martes, miercoles, jueves, viernes]"
