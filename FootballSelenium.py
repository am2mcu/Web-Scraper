# How many teams won the game when they scored the first goal?
# Should add a database to collect more data and analyze more games in different years and leagues
# should add Premier League 2020/2021 manualy to the database - after percentage() call database() then call piechart() for all of the data
# should change 1.link 2.database first value for each try

from selenium import webdriver
import time
import re
import matplotlib.pyplot as plt
import sqlite3


class FootballAnalyze():
    
    driver = webdriver.Chrome()

    win_game = 0
    draw_game = 0
    lose_game = 0

    def find_matches(self):
        self.driver.get("https://www.footballcritic.com/primera-division/season-2016-2017/matches/6/11907")
        time.sleep(3)

        matches_list = self.driver.find_elements_by_xpath('//*[@id="main"]/div/div[2]/div[1]/div/div[1]/div/div/div[4]/div/ul/span[position()<=52]/li/a')
        self.matches_list = [match_href.get_attribute("href") for match_href in matches_list]
        
        self.find_goals()

    
    def find_goals(self):
        for match in self.matches_list:
            self.driver.get(match)
            time.sleep(2)
            
            try:
                self.left_team = self.driver.find_element_by_xpath('//*[@id="wrapper"]/div[3]/div/div[1]/div[2]/span').text
            except:
                self.left_team = "None"
            try:
                self.right_team = self.driver.find_element_by_xpath('//*[@id="wrapper"]/div[3]/div/div[1]/div[4]/span').text
            except:
                self.right_team = "None"

            self.left_team_goal_time = re.findall("[0-9][0-9][+]..|[0-9][0-9][+].|[0-9][0-9]|[0-9]", self.left_team)
            self.right_team_goal_time = re.findall("[0-9][0-9][+]..|[0-9][0-9][+].|[0-9][0-9]|[0-9]", self.right_team)

            self.first_goal()


    def first_goal(self):
        one_digit_left_team_goal_time = [i for i in self.left_team_goal_time if len(i) == 1]
        one_digit_right_team_goal_time = [i for i in self.right_team_goal_time if len(i) == 1]

        try:
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
        except:
            if self.left_team == "None":
                self.goal = "right"
            else:
                self.goal = "left"

        self.result()


    def result(self):
        try:
            if len(self.left_team_goal_time) > len(self.right_team_goal_time):
                self.win = "left"
            elif len(self.left_team_goal_time) < len(self.right_team_goal_time):
                self.win = "right"
            else:
                self.win = "draw"
        except:
            if self.left_team == "None" and self.right_team == "None":
                self.win = "draw"
            elif self.left_team == "None":
                self.win = "right"
            else:
                self.win = "left"

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

        cursor.execute("INSERT INTO Football VALUES(?,?,?,?,?)", ("Laliga 2016/2017", self.win_game, self.draw_game, self.lose_game, self.win_game+self.draw_game+self.lose_game))

        db.commit()
        db.close()

        self.pie_chart()


    def close_browser(self):
        self.driver.close()
        self.driver.quit()


Football = FootballAnalyze()
Football.find_matches()
Football.close_browser()
Football.find_percentage()