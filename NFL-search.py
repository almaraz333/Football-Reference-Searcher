from bs4 import BeautifulSoup, Comment
import requests
import csv
import time

alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
base_url = "https://www.pro-football-reference.com"

def writePlayer(params):
    max_transactions = params[1]
    players = params[0]

    with open('football_players.csv', 'w',encoding='utf-8', newline='') as file:
        writer = csv.writer(file)

        headers = ['Name', 'DOB', 'Birth Place', 'College', 'High School'] + \
                  ['Transaction {}'.format(i) for i in range(1, max_transactions+1)] + \
                  ['Teams by Year', 'Number of Years Played', 'List of Years Played']
        writer.writerow(headers)

        for player in players.values():
            row = [player['name'], player['dob'], player['birthplace'], player['college'], player['high_school']] + \
                  player['transactions'] + \
                  ([''] * (max_transactions - len(player['transactions']))) + \
                  [player['teams'], player['num_years_played'], player['years_played']]
            writer.writerow(row)

def getPlayers():
    players_hash={}

    for i in alphabet:
        print(f"Processing players starting with {i}...")

        website_url = requests.get(base_url + "/players/"+i+"/").text
        soup = BeautifulSoup(website_url,'lxml')
        player_table = soup.find("div", {"id": "div_players"})
        players_in_player_table = player_table.find_all("p")
        j = 0;
        highest_num_transactions = 0

        for player in players_in_player_table:
            total_transactions = 0
            j += 1

            try:
                time.sleep(2)

                start_year, end_year = player.text.split(" ")[-1].split("-")

                if int(end_year) < 1990:
                    continue;

                # YEARS PLAYED
                years_played = int(end_year) - int(start_year) + 1
                # PLAYER NAME
                player_name = player.find("a").text
                print(f"Processing player: {player_name}. {round((j / len(players_in_player_table)) * 100, 2)}% done with {i}")

                player_link = player.find("a").get('href')
                player_link_res = requests.get(base_url + player_link).text

                player_soup = BeautifulSoup(player_link_res,'lxml')
                player_info_container = player_soup.find("div", { "id":"meta" })
                player_dob_container = player_info_container.find("span", {"id":"necro-birth"}).parent
                
                try:
                    # PLAYER DOB
                    player_dob = player_info_container.find("span", {"id":"necro-birth"}).get("data-birth")
                except Exception as e:
                    player_dob = ""

                try:
                    # PLAYER BIRTHPLACE
                    player_dob_container_children = list(player_dob_container.children)
                    elems = [str(elem) for elem in player_dob_container_children if elem is not None]
                    html_string = ''.join(elems)
                
                    birthplace_soup = BeautifulSoup(html_string,'lxml')
                    birthplace_spans =  birthplace_soup.find_all("span")
                    player_birth_place = birthplace_spans[1].text.replace('\xa0', ' ').replace('in', '').strip().split(',')
                    
                except Exception as e:
                    player_birth_place = ""

                p_tags = player_info_container.find_all('p')

                player_college = ''
                player_high_school = ''

                for p in p_tags:
                    if p.text.startswith('College'):
                        # PLAYER COLLEGE
                        player_college = p.a.text 
                    elif p.text.startswith('High School'):
                        # PLAYER HIGH SCHOOL
                        player_high_school = p.a.text  

                try:
                    html_player_soup = BeautifulSoup(player_link_res,'html.parser')

                    comments = html_player_soup.find_all(string=lambda text: isinstance(text, Comment))
                    for comment in comments:
                        # Create a soup object from the comment string
                        comment_soup = BeautifulSoup(comment, 'html.parser')

                        # Now you can find elements within the comment just like you would in a normal soup object
                        div = comment_soup.find('div', {'class': 'section_content', 'id': 'div_transactions'})
                        if div is not None:
                            li_tags = div.find_all('li')
                            transactions = []
                            for li in li_tags:
                                if li.text.split()[0] != "Show":
                                    transactions.append(li.text)
                                    total_transactions += 1
                            # PLAYER TRANSACTIONS
                            player_transactions = transactions
                            if total_transactions > highest_num_transactions:
                                highest_num_transactions = total_transactions

                except Exception as e:
                    player_transactions = ""

                player_teams = {}
                player_years_played = []

                try:
                    career_game_log_link = player_soup.find('a', string='Career').get('href')
                    career_game_log_link_res = requests.get(base_url + career_game_log_link).text

                    game_log_soup = BeautifulSoup(career_game_log_link_res,'lxml')
                    table = game_log_soup.find('table', {'id': 'stats'})
                    rows = table.tbody.find_all('tr')

                    for row in rows:
                        try:
                            year = row.find('td', {'data-stat': 'year_id'}).text
                            if year in player_teams:
                                continue
                            else:
                                player_teams[year] = row.find('td', {'data-stat': 'team'}).text
                                player_years_played.append(year)
                        except:
                            continue

                    # PLAYER TEAMS
                    player_teams = ', '.join(f"{key}:{value}" for key, value in player_teams.items())
                except Exception as e:
                    player_teams = ""

                player_info = {
                    'name': player_name,
                    'dob': player_dob,
                    'birthplace': ", ".join(player_birth_place),
                    'college': player_college,
                    'high_school': player_high_school,
                    'transactions': player_transactions,
                    'teams': player_teams,
                    'num_years_played': years_played,
                    'years_played': ", ".join(player_years_played) if len(player_years_played) > 0 else ""
                }

                player_birth_place_str = ", ".join(str(bp) for bp in player_birth_place) if player_birth_place is not None else ''
                players_hash[player_name + str(player_dob) + player_birth_place_str] = player_info

            except Exception as e:
                print(player, e)
                continue

    return [players_hash, highest_num_transactions]
                                    
writePlayer(getPlayers())

