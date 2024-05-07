from bs4 import BeautifulSoup #webscrapping library
import requests #request info from website
import os
import pandas as pd
import re

class parlay_boys:
    def __init__ (self):
        self.club_elo = {}
        self.url = "http://api.clubelo.com/Fixtures"
        self.directory_path = "/Users/khali/Documents/parlay_boyz"
        self.file_name = "fixtures.csv"
        
        
    #Getting Elo Data
    def scrape(self):
        """Establishes connection to website element we want information from then passes the info to format table"""
        #html_text = requests.get('http://clubelo.com/ENG').text
        html_text = requests.get("http://clubelo.com/ENG/Ranking").text
        if html_text:
            soup = BeautifulSoup(html_text, 'lxml')
            div = soup.find('div', class_ = 'blatt')
            table = div.find('table', class_= 'ranking')
            self.format_table(table)
        else:
            print("Connection Failure")
            
            
    def format_table(self, table):
        """Formats Data and puts in in a tabular form then calls prediction data"""
        headers = []
        for th in table.find_all('th'):
            headers.append(th.text.strip())
        
        data = []
        rows = table.find_all('tr')
        for row in rows:
            temp = []
            for element in row:
                temp.append(element.text.strip())
            data.append(temp)
        self.elo(data)
       
    def elo(self, data):
        """gives a hashmap of clubs and their Elo's
        """
        for i in range(len(data)):
            data[i][1] = re.sub(r'^\d*\s*', '', data[i][1])
            #data[i][1] = ' '.join(data[i][1].split(' ')[1:]) #manipulating scraped data
        club_elo = {}
        for i in range(len(data)):
            club_elo[data[i][1]] = data[i][2]
        #print(club_elo)
        self.club_elo = club_elo
        #print(self.club_elo)
        self.download_fixture_csv(self.url, self.directory_path, self.file_name)
        

    #Fixtures
    def download_fixture_csv(self, url, directory_path, file_name):
        """Download a CSV file from a given URL to a specified directory with a given file name."""
        response = requests.get(url)
        if response.status_code == 200:
            self.file_path = os.path.join(directory_path, file_name)
            with open(self.file_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded successfully: {self.file_path}")
            self.load_csv(self.file_path)
        else:
            print(f"Failed to download file. Status code: {response.status_code}")



    def load_csv(self, file_path):
        """Gives us the clubs playing in specified league in the next three days"""
        csv = pd.read_csv(file_path)
        filtered_csv = csv[csv['Country'] == 'ENG']
        clubs = {"Man City", "Liverpool", "Arsenal", "Tottenham", "Aston Villa", "Man United", "Newcastle", "Chelsea", "Brighton", "West Ham",
                 "Wolves", "Fulham", "Brentford", "Everton", "Bournemouth", "Crystal Palace"}
        filtered_csv = filtered_csv[filtered_csv['Home'].isin(clubs)]
        self.predictor(self.club_elo, filtered_csv)
        
    def predictor(self, club_elo, filtered_csv):
        for index, row in filtered_csv.iterrows(): 
            home_team = row['Home']
            away_team = row['Away']
            
            #home win probability
            elo_diff_home = int(club_elo[away_team]) - int(club_elo[home_team])
            home_prob = 1/(1+10**(elo_diff_home/400)) * 100
            
            #away win probability
            elo_diff_away = int(club_elo[home_team]) - int(club_elo[away_team])
            away_prob = 1/(1+10**(elo_diff_away/400)) * 100
            print(f"{home_team} {home_prob:.2f} vs {away_team} {away_prob:.2f}")
    
        
    

    

test = parlay_boys()
test.scrape()
#function call    
#scrape()
#fixtures()
#formula()
#download_fixture_csv("http://api.clubelo.com/Fixtures", "/Users/khali/Documents/parlay_boyz", "fixtures.csv")

