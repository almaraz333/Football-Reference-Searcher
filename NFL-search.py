import time
import unidecode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup, Comment
import pandas as pd
import requests
import csv
import re


def gameLog(player_link):
    website_url = requests.get(player_link).text
    soup = BeautifulSoup(website_url,'lxml')
    gamelog = soup.find(text='Gamelogs').findNext('ul')
    games = gamelog.find_all('li')
    if int(games[-1].text) < 2019:
        return games[-1].text
    else:
        return False

    
def writePlayer(list_of_players):
    with open('fooball_players_years_over_3.csv', 'w',encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for item in list_of_players:
            writer.writerow(item)
        file.close()


def getPlayers():
    players_names=[]
    players_list=[]
    website_url = requests.get("https://www.pro-football-reference.com/teams/").text
    soup = BeautifulSoup(website_url,'lxml')
    teams_table = soup.find_all('tbody')
    team_names = teams_table[0].find_all("a", href=re.compile(r"^/teams"))
    for team_name in team_names:
        website_url = requests.get("https://www.pro-football-reference.com" + team_name['href']).text
        soup = BeautifulSoup(website_url,'lxml')
        team = team_name.text
        print(team) #DELETE LATER
        team_years = soup.find_all("th", {"data-stat": "year_id"})
        for year_link in team_years:
            if year_link.text != 'Year' and 2005 <= int(year_link.text) <= 2017:
                print(year_link.text) #DELET ELATER
                website_url = requests.get("https://www.pro-football-reference.com"+team_name['href']+year_link.text+"_roster.htm").text
                soup = BeautifulSoup(website_url,'lxml')
                comments = soup.findAll(text=lambda text:isinstance(text, Comment))
                for comment in comments:
                    if 'table' in comment:
                        comment_soup = BeautifulSoup(comment, 'html.parser')
                        for tr in comment_soup.find_all('tr'):
                            td = tr.find_all('td')
                            if len(td) > 0:
                                try:
                                    name = td[0].text
                                    for letter in name:
                                        if letter == '+' or letter == '*':
                                            name = name.replace(letter, '')
                                    if td[9].text != "Rook" and int(td[9].text) >= 3 and name not in players_names:
                                        players_names.append(name)
                                        last_game_year = gameLog("https://www.pro-football-reference.com"+td[0].find('a')['href'])
                                        if last_game_year:
                                            player = []
                                            player.extend((td[0].text,td[8].text,team))
                                            players_list.append(player)
                                            print(len(players_list))
                                except:
                                    pass
    return players_list
                                    

                    
                    
                
            
writePlayer(getPlayers())


         


