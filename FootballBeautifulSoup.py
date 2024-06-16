import requests
from bs4 import BeautifulSoup
from lxml import etree
import re
import matplotlib.pyplot as plt
import sqlite3


class FootballAnalyze():
    '''How many teams have won the match when they scored the first goal?'''
    
    win_game = 0
    draw_game = 0
    lose_game = 0

    def find_matches(self):
        URL = "https://www.footballcritic.com/bundesliga/season-2016-2017/matches/3/11817"
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, "html.parser")
        soup = etree.HTML(str(soup))
        
        self.links = soup.xpath('//*[@id="main"]/div/div[2]/div[1]/div/div[1]/div/div/div[4]/div/ul/span[position()<=52]/li[position()<=10]/a/@href')
        
        self.find_goals()


    def find_goals(self):
        for link in self.links:
            page = requests.get(link)
            
            soup = BeautifulSoup(page.content, "html.parser")
            soup = etree.HTML(str(soup))

            l_goals = soup.xpath('//*[@id="wrapper"]/div[3]/div/div[1]/div[2]/span/text()')
            r_goals = soup.xpath('//*[@id="wrapper"]/div[3]/div/div[1]/div[4]/span/text()')
            l_goals = "".join(l_goals[1:])
            r_goals = "".join(r_goals[1:])
            
            self.left_team_goal_time = re.findall("[0-9][0-9][+]..|[0-9][0-9][+].|[0-9][0-9]|[0-9]", l_goals)
            self.right_team_goal_time = re.findall("[0-9][0-9][+]..|[0-9][0-9][+].|[0-9][0-9]|[0-9]", r_goals)
            
            self.first_goal()


    def first_goal(self):
        one_digit_left_team_goal_time = [i for i in self.left_team_goal_time if len(i) == 1]
        one_digit_right_team_goal_time = [i for i in self.right_team_goal_time if len(i) == 1]

        if self.left_team_goal_time == []:
            self.goal = "right"
        elif self.right_team_goal_time == []:
            self.goal = "left"
        else:
            if one_digit_left_team_goal_time == [] and one_digit_right_team_goal_time == []:
                if min(self.left_team_goal_time) > min(self.right_team_goal_time):
                    self.goal = "right"
                else:
                    self.goal = "left"
            else:
                if one_digit_left_team_goal_time != [] and one_digit_right_team_goal_time == []:
                    self.goal = "left"
                elif one_digit_left_team_goal_time == [] and one_digit_right_team_goal_time != []:
                    self.goal = "right"
                else:
                    if min(one_digit_left_team_goal_time, key=int) > min(one_digit_right_team_goal_time, key=int):
                        self.goal = "right"
                    else:
                        self.goal = "left"

        self.result()


    def result(self):
        if self.left_team_goal_time == [] or self.right_team_goal_time == []:
            if self.left_team_goal_time == [] and self.right_team_goal_time == []:
                self.win = "draw"
            elif self.left_team_goal_time == []:
                self.win = "right"
            else:
                self.win = "left"
        else:
            if len(self.left_team_goal_time) > len(self.right_team_goal_time):
                self.win = "left"
            elif len(self.left_team_goal_time) < len(self.right_team_goal_time):
                self.win = "right"
            else:
                self.win = "draw"

        self.analyze()


    def analyze(self):
        if self.goal == self.win:
            self.win_game += 1
        else:
            if self.win == "draw":
                self.draw_game += 1
            else:
                self.lose_game += 1


    def find_percentage(self):
        print(self.win_game, "Win - ", self.draw_game, "Draw - ", self.lose_game, "Lose - ", self.win_game+self.draw_game+self.lose_game, "Total")
        
        percentage = (self.win_game/(self.win_game+self.lose_game+self.draw_game))*100
        print("Win percentage:", str(percentage) + "%")

        self.database() # save it in database


    def pie_chart(self):
        db = sqlite3.connect("Football.db")
        cursor = db.cursor()

        cursor.execute("SELECT sum(Win),sum(Draw),sum(Lose) FROM Football")
        for i in cursor:
            total_win = i[0]
            total_draw = i[1]
            total_lose = i[2]
        
        db.commit()
        db.close()

        labels = ['Win', 'Draw', 'Lose'] 
        data = [total_win, total_draw, total_lose] 

        colors = ['g', 'y', 'r']

        plt.pie(data, labels = labels, colors=colors, 
                startangle=200, shadow = True, explode = (0.05, 0.05, 0.05), 
                radius = 1.2, autopct = '%0.2f%%') 

        plt.legend()
        plt.title("Football")
        plt.show()
    

    def database(self):
        db = sqlite3.connect("Football.db")
        cursor = db.cursor()

        cursor.execute("INSERT INTO Football VALUES(?,?,?,?,?)", ("Bundesliga 2016/2017", self.win_game, self.draw_game, self.lose_game, self.win_game+self.draw_game+self.lose_game))

        db.commit()
        db.close()

        self.pie_chart()


Football = FootballAnalyze()
Football.find_matches()
Football.find_percentage()