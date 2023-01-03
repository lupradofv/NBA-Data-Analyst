import requests, sys, json
import pandas as pd
from xhtml2pdf import pisa       
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PyPDF2 import PdfMerger
from datetime import datetime
from bs4 import BeautifulSoup

def select(df, pos):
    # Selects rows: selected team and its opponent 
    if pos%2==0:
        print(df.iloc[[pos,pos+1]])
    else:
        print(df.iloc[[pos-1,pos]])

def extract(child, team_name):

    """
    1. Contiene los nombres de todos los equipos
    2. Contiene las probabilidades de ganar de los equipos de la lista anterior'
    """
    team_names = child.select('td[class^="td text team"]')
    for i in range(len(team_names)):
        team_names[i]=team_names[i].text

    chncs= child.select('td[class="td number chance"]')
    for i in range(len(chncs)):
        chncs[i]=chncs[i].text

    df = pd.DataFrame({'Team': team_names,
                   'Chance of victory': chncs
                   })
    cols = ['Team', 'Chance of victory']
    pos = team_names.index(team_name)
    select(df,pos)

def Menu(df,team_names, team_ids):

    print('----------------------------------------------    TEAM SELECTION     ------------------------------------')
    print('1. Introduce Team Name')
    print('2. Introduce Team ID')
    mode_v = False
    modes = ['1','2']
    while not mode_v:
        mode = input('Selection mode (1/2): ')
        if mode in modes:
            mode_v = True
            mode = int(mode)
        else: 
            print('Introduce valid mode.')

    # Selection by team name
    if mode == 1:
        name_v = False
        while not name_v:
            teamName = input('Introduce Team Name: ')
            teamName = teamName.title()
            teamName = teamName.strip()
            # Check if contained in data
            if teamName in team_names:
                name_v = True
            else: 
                print('Introduce valid name.')
        # Filter df by team name selected
        team_data = df[df['Name']==teamName]

    # Selection by team id
    elif mode == 2:
        id_v = False
        while not id_v:
            try:
                teamID = int(input('Introduce Team ID: '))
                if teamID in team_ids:
                    id_v = True
                else: 
                    print('Introduce valid ID.')
            except:
                print('Introduce valid ID.')
        # Filter df by team id selected
        team_data = df[df['TeamID']==teamID]

    return team_data

if __name__=='__main__':

    with open('config.txt', 'r') as conf:
        hd = conf.readlines()
    key = str(hd[-1])
    try:
        # Load data from API
        resp = requests.request('GET', 
            'https://api.sportsdata.io/v3/nba/scores/json/TeamSeasonStats/2022', 
            headers = {'Ocp-Apim-Subscription-Key': key})

        # Data to dataframe
        data = resp.json()
        df = pd.DataFrame(data)

        # Contains all team names and team ids
        team_names = []
        team_ids = []
        for i in range(df.shape[0]):
            team_names.append(df['Name'][i])
            team_ids.append(df['TeamID'][i])

        # Process info to select data for corresponding team: returns filtered dataframe for team
        team_data = Menu(df, team_names, team_ids)

        datos = list(team_data['OpponentStat'])
        team_dicc = datos[-1]

        team_name = team_dicc['Name']
        team_abrv = team_dicc['Team']
        print(f'Loading {team_name} stats...')
        # Clean df: remove unwanted data
        dels = ['Name','Team','GlobalTeamID','FantasyPointsFanDuel','FantasyPointsDraftKings','FantasyPointsYahoo','FantasyPoints','StatID','SeasonType','Season','Updated','Minutes','Seconds','PlusMinus','FantasyPointsFantasyDraft','LineupStatus']
        for delete in dels:
            team_dicc.pop(delete)

        # Obtain data for team players from API with team abreviation 
        resp2 = requests.request('GET', 
            f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2022/{team_abrv}', 
            headers = HEADERS)
        data_players = resp2.json()
        df_players = pd.DataFrame(data_players)

        # Clean df: maintain only important data
        df_imp = df_players[['Name','Position','Games', 'EffectiveFieldGoalsPercentage', 'TwoPointersPercentage','ThreePointersPercentage', 'FreeThrowsPercentage', 'OffensiveReboundsPercentage','DefensiveReboundsPercentage', 'Assists',
        'Steals', 'BlockedShots', 'Points','TrueShootingPercentage', 'PlayerEfficiencyRating', 'TurnOversPercentage']]
        df_imp.rename({'EffectiveFieldGoalsPercentage':'FG', 'TwoPointersPercentage':'2P','ThreePointersPercentage':'3P', 'FreeThrowsPercentage':'FT', 'OffensiveReboundsPercentage':'OR','DefensiveReboundsPercentage':'DR', 'Assists':'AS','Steals':'ST', 'BlockedShots':'BS', 'Points':'PP','TrueShootingPercentage':'TS', 'PlayerEfficiencyRating':'ER', 'TurnOversPercentage':'TO'}, 
                        axis = "columns", inplace = True) 

        fig, ax =plt.subplots(figsize=(12,4))
        ax.axis('tight')
        ax.axis('off')
        tb = ax.table(cellText=df_imp.values,colLabels=df_imp.columns,loc='center',cellLoc='center')
        tb.auto_set_font_size(False)
        tb.set_fontsize(9)
        tb.auto_set_column_width(col=list(range(len(df_imp.columns))))

        # Generate PDF
        pp = PdfPages(f'Jugadores_{team_abrv}.pdf')
        pp.savefig(fig, bbox_inches='tight')
        pp.close()

        # Merge data pages (different pdfs)
        merger = PdfMerger()
        merger.append(f'Jugadores_{team_abrv}.pdf')

        # Html file content
        html_template = """<html>
        <body>
        <h2>DATA:</h2>
        <p> FG: Effective Field Goals(%), 2P: Two Pointers(%),3P: Three Pointers(%), FT: Free Throws(%), OR: Offensive Rebound (%), DR: Defensive Rebound (%), AS: Assists, ST: Steals, BS: Blocked Shots, PP: Points, TS: True Shooting (%), ER: Efficiency Rating, TO: Turn Overs (%)</p>"""
        html_template+= f'<h3>{team_name} Stats ({team_abrv}):</h3>'
        for k in team_dicc.keys():
            if team_dicc[k]:
                html_template+= f"<p>{k}: {team_dicc[k]}</p>"
        html_template+="""</body> </html>"""
    
        # Create pdf from html
        text_file = open(f'Stats_{team_abrv}.pdf', 'w+b')
        p = pisa.CreatePDF(html_template, text_file)
        text_file.close()
        merger.append(f'Stats_{team_abrv}.pdf')
        # Create pdf with all pages added
        merger.write(f'{team_abrv}.pdf')
        merger.close()

        # ----------------------------------------------------   PREDICCIÓN PARA EL SIGUIENTE PARTIDO    --------------------------------------------------------------------------------
        
        # Access page and generate soup
        r = requests.get("https://projects.fivethirtyeight.com/2023-nba-predictions/games/")
        soup = BeautifulSoup(r.content, 'html.parser')
        # First div contains all games due to be played by days
        s = soup.find('div', attrs={'class':'day-group','id':'upcoming-days'})
        s = list(s)

        team_name = team_name.split()
        team_name = team_name[-1]

        # Process data to find next game for the team
        found = False
        for i in range(len(s)):
            for child in s[i].descendants:
                if team_name in child.text and not found:
                    found=True
                    print('----------------       NEXT GAME PREDICTION         ---------------------\n')
                    print(f'DATE: {s[i].h3.text}')
                    extract(child,team_name)
    except:
        print('Error obtaining data.')






    
            




 

