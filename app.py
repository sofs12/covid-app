from importlib.abc import PathEntryFinder
import numpy as np
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import date, timedelta, datetime
from random import randrange


class Player:

    def __init__(self, id, infected, day_of_infection, cohabitant, life):
        self.id = id
        self.infected = infected
        self.day_of_infection = day_of_infection
        self.cohabitant = cohabitant
        self.life = life

    def showDescription(self):
        print(f'{self.id} testou positivo no dia {self.day_of_infection}, vive com {self.cohabitant} e tem {self.life} de vida')

    def updateLife(self, current_date, cohabitant_life):

        if self.infected == True:
            if current_date >= self.day_of_infection:
                self.life = 1/7 * (current_date - self.day_of_infection).days
            else:
                self.life = 1
        
        else:
            if cohabitant_life < 1:
                self.life = cohabitant_life + 0.5
            
            else:
                self.life = 1

        if self.life > 1:
            self.life = 1

        print(f'Life updated to {self.life}')
        return self.life

#%%
all_players = ['Pepas', 'Sofia P', 'Sofia B', 'Zio', 'Sofia F', 'Simão', 'Ber', 'Diogo', 'Marisa', 'Luis', 'Catarina', 'Vitor', 'Gac', 'Figueiredo', 'Chico', 'Chica', 'Hugo', 'Ana', 'Mariana', 'Daniel', 'Filipa']
all_players = sorted(all_players)

players = ['Sofia B', 'Zio', 'Sofia F', 'Simão', 'Ber', 'Diogo', 'Marisa', 'Luis', 'Catarina', 'Vitor', 'Gac', 'Figueiredo', 'Chico', 'Chica', 'Hugo', 'Ana', 'Daniel', 'Filipa']
players = sorted(players)

infection_day = {'Sofia B': date(2022,1,16), 'Zio': date(2022,1,17),
    'Simão': date(2022,1,18), 'Diogo': date(2022,1,19), 'Luis': date(2022,1,16),
    'Daniel': date(2022,1,19), 'Chica': date(2022,1,17), 'Chico': date(2022,1,18),
    'Figueiredo': date(2022,1,17), 'Catarina': date(2022,1,20)}

infected_list = sorted(infection_day.keys())

patient_zero_list = sorted(players + ['?','Liquito', 'Bino', 'Cozinheiro Sinistro'])

#considering bfs/gfs as well
cohabitants = {'Sofia B': 'Zio', 'Zio' : 'Sofia B', 'Sofia F' : 'Simão', 'Simão': 'Sofia F', 
    'Ber': 'Diogo', 'Diogo': 'Ber', 'Luis': 'Catarina', 'Catarina': 'Luis', 
    'Chico': 'Chica', 'Chica': 'Chico', 'Daniel': 'Filipa', 'Filipa': 'Daniel',
    'Marisa' : 'Diogo', 'Hugo': 'Ana', 'Ana': 'Hugo', 'Sofia P': 'Pepas', 'Pepas': 'Sofia P'}


dinner_date = date(2022,1,15)
today = date.today()

dd = [dinner_date + timedelta(days=x) for x in range((today-dinner_date).days + 1)]

# new pd dataframe, rows are people and columns are dates; the entries are life

lifedf = pd.DataFrame()#columns=cols )
lifedf['player'] = players

lifedf['infected'] = lifedf.player.apply(lambda x: True if x in infection_day.keys() else False)
lifedf['infection_date'] = lifedf.player.apply(lambda x: infection_day[x] if x in infection_day.keys() else '')
lifedf['cohabitant'] = lifedf.player.apply(lambda x: cohabitants[x] if x in cohabitants.keys() else '')
lifedf['player_init'] = lifedf.apply(lambda x: Player(x.player, x.infected, x.infection_date, x.cohabitant, 1), axis = 1)
lifedf['cohabitant_init'] = lifedf.cohabitant.apply(lambda x: lifedf.query(f'player == "{x}"').player_init.values[0] if x !='' else '')

for day in dd:
    lifedf.apply(lambda x: x.cohabitant_init.updateLife(day, 1) if x.cohabitant != '' else '', axis = 1)
    lifedf.apply(lambda x: x.player_init.updateLife(day, x.cohabitant_init.life) if x.cohabitant !='' else x.player_init.updateLife(day, 1), axis = 1)
    lifedf[day] = lifedf.player_init.apply(lambda x: x.life)


# aux df with columns as date, player name and life
auxlifedf = lifedf.drop(['infected', 'infection_date', 'cohabitant', 'player_init', 'cohabitant_init'], axis = 1)
lifedf_unpivoted = auxlifedf.melt(id_vars = ['player'], var_name = 'date', value_name = 'life')

players_still_in_game = sorted(set(players) - set(infected_list))

#initialize dataframes
votedf = pd.DataFrame(columns = ['timestamp', 'voter_name', 'next_covid', 'patient_zero'])
formdf = pd.DataFrame()

#%%
st.header('Welcome to the COVID games')

st.write('Amigos, vamos brrincarr!')

voter_name = st.selectbox('Quem és?', ['?'] + all_players, index = 0)

if voter_name !='?':

    st.write(f'Bem-vindo/a {voter_name}!')

    if voter_name in infected_list:
        st.write('Vacilaste, como te sentes? Poderás ser tu o paciente zero?')

        if voter_name == 'Catarina':
            st.write('Epah, é que tu nem tens o proveito, lamento...')

        if voter_name == 'Ber':
            st.write('Tinhas que beijar o Luis, né?')

        if voter_name == 'Simão':
            st.write('2 anos a tratar de COVIDosos, tinha que ser no Bino, né?')

    else:
        st.write('Manténs-te forte, bravo!')
        if voter_name in ['Pepas', 'Sofia P']:
            st.write('Pah, noutro país também eu...')

        if voter_name == 'Mariana':
            st.write('Sentes-te bem por abandonares os teus filhotes num jantar para eles apanharem COVID?')
        
        if voter_name == 'Marisa':
            st.write('Sentes-te confiante depois de mamares o vírus?')

        if voter_name == 'Ber':
            st.write('Mas por quanto mais tempo?')

    st.write('')

    st.header('Life-o-meter')
    st.write('Quanta vida tens tu? Quanta vida têm os teus amigos?')
    st.write('Acompanha esta alucinante viagem, atualizada a cada dia, ou a cada vez que alguém tem confirmação de um hóspede que não COVIDou para a sua vida.')


    fig = px.line(lifedf_unpivoted, x = 'date', y = 'life', color = 'player',title = 'Life-o-meter')
    fig.update_xaxes(range=[dinner_date, date.today()+ timedelta(1)])
    fig.update_yaxes(range=[-0.1,1.1])
    st.plotly_chart(fig, use_container_width=True)

    
#%%


@st.cache(allow_output_mutation=True)
def update_vote():
    return []

if voter_name != '?':

    st.header('Votações')

    col1, col2 = st.columns(2)
    next_covid = col1.selectbox('Quem é o próximo a vacilar?', ['?'] + players_still_in_game)
    patient_zero = col2.selectbox('Quem é que vamos mandar para a fogueira?', patient_zero_list)

    enter_bet = st.button('Enter')

    if enter_bet:

        new_vote = {'timestamp': datetime.today(), 
           'voter_name': voter_name, 'next_covid': next_covid, 'patient_zero': patient_zero}

        update_vote().append(new_vote)

        st.write(f'{voter_name} votou em {next_covid} para próxima vítima do COVID, e em {patient_zero} como paciente zero.')

    votedf = pd.DataFrame(update_vote())



#%%

#metrics 

nextdf = pd.DataFrame()
nextdf['next_covid'] = players_still_in_game
nextdf['vote_count'] = nextdf.next_covid.apply(lambda x: len(votedf.query(f'next_covid == "{x}"')))

next_count = nextdf.vote_count.max()
curr_next = nextdf.query(f'vote_count == {next_count}').next_covid.values
curr_next = curr_next[randrange(len(curr_next))]


zerodf = pd.DataFrame()
zerodf['patient_zero'] = patient_zero_list
zerodf['vote_count'] = zerodf.patient_zero.apply(lambda x: len(votedf.query(f'patient_zero == "{x}"')))

zero_count = zerodf.vote_count.max()
curr_zero = zerodf.query(f'vote_count == {zero_count}').patient_zero.values
curr_zero = curr_zero[randrange(len(curr_zero))]

if voter_name != '?':
    col1, col2 = st.columns(2)
    col1.metric('Próxima vítima', curr_next, str(next_count))
    col2.metric('Paciente zero', curr_zero, str(zero_count))


    #histogram for next covid and patient zero

    fig = px.histogram(votedf, x = 'next_covid', title = 'Próxima vítima',
        category_orders=dict(next_covid = sorted(votedf.next_covid.unique())))
    st.plotly_chart(fig)

    fig = px.histogram(votedf, x = 'patient_zero', title = 'Paciente zero',
        category_orders=dict(patient_zero = sorted(votedf.patient_zero.unique())))
    st.plotly_chart(fig)

#%%

st.write('')
form = st.form(key = 'my_form')
user_form = form.text_input(label = 'Tens alguma sugestão para tornar este isolamento mais divertido? Partilha a tua opinião!')
submit = form.form_submit_button(label = 'Enviar')


@st.cache(allow_output_mutation=True)
def form_user_input():
    return []


if submit:
    form.write('thanks!')
    print(user_form)

    new_user_input = {'timestamp': datetime.today(), 
           'voter_name': voter_name, 'input': user_form}

    form_user_input().append(new_user_input)

    formdf = pd.DataFrame(form_user_input())

#%%

if voter_name == 'Sofia F':

    password = st.text_input('password')

    if password == 'covid22':
        st.write(votedf)
        st.write(formdf)
