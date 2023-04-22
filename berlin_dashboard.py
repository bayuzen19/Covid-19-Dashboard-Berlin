import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mplcyberpunk
from PIL import Image

# create function

def run():

    # load image
    img = Image.open('./image.jpeg')
    st.image(img)

    # create title
    st.title('Covid-19 Dashboard For Berlin')

    link = '[@Developed by Bayuzen Ahmad](https://www.linkedin.com/in/bayuzenahmad/)'
    st.sidebar.markdown(link,unsafe_allow_html=True)

run()

# create title
st.write(
"""

---------
This dashboard provides daily updates of the 7-day-incidence,
the rolling 7-day-average number of new cases and the raw number of new reported Covid-19 cases.
Source from [berlin.de](https://www.berlin.de/lageso/gesundheit/infektionsepidemiologie-infektionsschutz/corona/tabelle-bezirke-gesamtuebersicht/).

"""
)

#  getting data
def get_data():
    historic_district_cases_url = 'https://www.berlin.de/lageso/_assets/gesundheit/publikationen/corona/meldedatum_bezirk.csv'
    historic_district_cases = pd.read_csv(historic_district_cases_url,sep=';',encoding='unicode_escape')

    return historic_district_cases

# load data
df = get_data()



#  adding a total columns for all berlin

# df['All Berlin'] = df.iloc[:,1:].sum(axis=1)

# convert datum to datetime
df['Datum'] = pd.to_datetime(df['Datum'])



# defining a list with the district of berlin
district = ['Lichtenberg','Mitte','Charlottenburg-Wilmersdorf',
            'Friedrichshain-Kreuzberg','Neukoelln','Tempelhof-Schoeneberg',
            'Pankow','Reinickendorf','Steglitz-Zehlendorf','Spandau',
            'Marzahn-Hellersdorf','Treptow-Koepenick']
populations = [2.91452, 3.84172, 3.42332, 2.89762, 3.29691, 3.51644, 4.07765, 2.65225, 3.08697, 2.43977, 2.68548, 2.71153]

# creating pandas dataframe
pop_dict = {'Bezirk':district,
            'Population':populations}
df_pop = pd.DataFrame(pop_dict)


# Creating a multiselect box
selected_districts = st.sidebar.multiselect(
    'Select a District(s)',
    district,
    default=['Pankow'] # Setting iniate for all berlin
)

if selected_districts == []:
    selected_districts = ['Pankow']

# create range day
days_to_show = st.sidebar.slider(
    'Number of Days to Display',
    0,365,30
)

# creating a checkbox in the sidebar to allow choose on or off mplcyberpunk
st.sidebar.write('----')
st.sidebar.write('Chart Presentation Settings: ')
nocyber = st.sidebar.checkbox('light Style')

#  Manipulating data on User Input
new_reported_cases = df['Datum']

# adding a new columns for each district
for i in selected_districts:
    new_reported_cases = pd.concat([new_reported_cases,df[i]],axis=1)

# adding 7-day-average for the selected distrid
data_to_plot = df['Datum']

for i in selected_districts:
    seven_day_average = df.rolling(window=7)[i].mean()
    new_col_name = ('Seven Days Average for %s' % i)
    historic_cases = df.copy()
    historic_cases[new_col_name] = seven_day_average
    data_to_plot = pd.concat([data_to_plot,historic_cases[new_col_name]],axis=1)

# creating a 7 day rolling sum of cases per district
for i in selected_districts:
    new_reported_cases['Seven Day Sum For %s' % i] = new_reported_cases[i].rolling(7).sum()

# getting the population for the selected districts, using that to calcualte 7-day-incidence
for i in selected_districts:
    poppo = df_pop.loc[df_pop['Bezirk']==i]
    popn = float(poppo['Population'])
    new_reported_cases['Seven Day Incidence For %s' % i] = new_reported_cases['Seven Day Sum For %s' %i] / popn


# creating a dataframe only containing 7-day-incidence
incidence = new_reported_cases['Datum']

for i in selected_districts:
    incidence = pd.concat([incidence,new_reported_cases['Seven Day Incidence For %s' %i]],axis=1)


#  creating plot

# selecting style
if nocyber == False:
    plt.style.use('cyberpunk')
else:
    plt.style.use('ggplot')

# plotting the 7 day incidence
st.write('## 7 Day Incidence')
st.write('Chart shows the 7 day incidence for the selected disctrict(s)')

incidence_data = incidence.iloc[-days_to_show:,:]

fig, ax = plt.subplots()

for i in selected_districts:
    plt.plot(incidence_data['Datum'],incidence_data['Seven Day Incidence For %s' % i])

ax.legend(selected_districts)

plt.xticks(rotation=45,
           horizontalalignment='right',
           fontweight='normal',
           fontsize='small',
           color='1')

plt.yticks(color='1')
plt.ylim((0))
plt.title('Seven Day Incidence - Last ' + str(days_to_show) + ' Days', color='1')

# removing the mplcyberpunk glow effects if checkbox selected
if nocyber == False:
    mplcyberpunk.add_glow_effects()
else:
    legend = plt.legend(selected_districts)
    plt.setp(legend.get_texts(),color='k')

#  Displaying the plot and the last 3 days' values
st.pyplot(fig)
st.table(incidence.iloc[-3:,:])

st.write('---')


# plotting 7 day average
st.write('## New Reported Cases - Rolling 7 Day Average')
st.write('This chart shows a [rolling 7-day-average](https://en.wikipedia.org/wiki/Moving_average) of newly reported cases for the selected district(s)')
st.write('This smoothes out the spikes somewhat and makes it easier to identify the real trend in cases.')

data = data_to_plot.iloc[-days_to_show:,:]

# defining figure
fig, ax = plt.subplots()

for i in selected_districts:
    plt.plot(data['Datum'],data['Seven Days Average for %s' %i])

ax.legend(selected_districts)
plt.xticks(rotation=45,
           horizontalalignment='right',
           fontweight='light',
           fontsize='small',
           color='1')
plt.ylim((0))
plt.yticks(color='1')
plt.title('Rolling 7 Days Average ' + str(days_to_show) + ' Days',color='1')

if nocyber == False:
    mplcyberpunk.add_glow_effects()
else:
    legend = plt.legend(selected_districts)
    plt.setp(legend.get_text(),color='k')

st.pyplot(fig)
st.table(data_to_plot.iloc[-10:,:])

st.write('----')

#  Plotting new cases
st.write('## Newly Reported Cases')
st.write('This chart shows the raw number of new reported cases in the selected district(s)')
st.write("Thiss will show larger variance and generally be 'noiser' than 7-day-average")

new_cases = new_reported_cases.iloc[-days_to_show:,:]

fig, ax = plt.subplots()

for i in selected_districts:
    plt.plot(new_cases['Datum'],new_cases[i])

ax.legend(selected_districts)
plt.xticks(rotation=45,
           horizontalalignment='right',
           fontweight='light',
           fontsize='small',
           color='1')
plt.ylim((0))
plt.yticks(color="1")
plt.title('New Reported Cases - Last ' + str(days_to_show) + ' Days', color='1')

if nocyber == False:
    mplcyberpunk.add_glow_effects()
else:
    legend = plt.legend(selected_districts)
    plt.setp(legend.get_texts(),color='k')

st.pyplot(fig)
number_to_limit_table = len(selected_districts) + 1

st.table(new_reported_cases.iloc[-3:,:number_to_limit_table])

st.write('----')

st.write('''
    Dashboard Created by [Bayuzen Ahmad](https://www.linkedin.com/in/bayuzenahmad/)
''')