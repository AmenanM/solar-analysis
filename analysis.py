#import packages
import streamlit as st
import plotly.express as px #for plots
import pandas as pd
import numpy as np
from pandas.tseries.offsets import MonthEnd
from unidecode import unidecode
from streamlit_extras.colored_header import colored_header 


#Page Header
colored_header(
        label="Solar Production Analysis",
        description="Study case",
        color_name="violet-70",
    )

#tas layout
tab1, tab2 = st.tabs(["Descriptive Analysis of Current Installation Data", "Identification of the Most Interesting Geographical Areas"])

with tab1:
    st.header("Installation data")
   #open installation data
    installations=pd.read_csv('data/installations-de-production-solaire-par-commune.csv', delimiter=';')
    st.dataframe(installations)
    # Distribution of the solar installations and their power in France ?
# ----
    #Evolution of the years, trends, or patterns ? 

    #the features of interest are 
    #power :Puissance de raccordement: sum_3_prod_e_kw_puissance_de_raccordement_injection[double]
    #Département: nom_dept[text]
    #'date_des_donnees'

    #create a dataframe group by for clearer distribution
    data=installations[['nom_dept','count', 'sum_3_prod_e_kw_puissance_de_raccordement_injection','date_des_donnees']]
    #format date data 
    data['date_des_donnees']=pd.to_datetime(data['date_des_donnees'],format='%Y-%m')+ MonthEnd(0)
    data1=data.groupby('nom_dept').sum().reset_index()
    #transform column for better visibility
    # data1['sum_3_prod_e_kw_puissance_de_raccordement_injection']=round(data1['sum_3_prod_e_kw_puissance_de_raccordement_injection']/1000000,1)

    #chart for distribution

    #charts for distribution
    distribution_count=px.bar(data1, 
    x='nom_dept', y='count',
    barmode='group',title='Distribution of solar installations in France', 
    labels={'nom_dept':'department',
                                                                    })
    distribution_power=px.bar(data1, 
    x='nom_dept', y='sum_3_prod_e_kw_puissance_de_raccordement_injection',
    barmode='group',title='Distribution of solar power in France', 
    labels={'nom_dept':'department','sum_3_prod_e_kw_puissance_de_raccordement_injection':'power(in millions kw)'
                                                                    })
    st.plotly_chart(distribution_count)
    st.plotly_chart(distribution_power)
    st.write('')
    st.write(f'''Departments Bouches du Rhone, Loire-Atlantique, Vendée, Isère, Hérault are among the departments 
            that count the highest values of installations in France.
    The dpt Gironde has the highest value of injected power.
            Followed by Landes, Bouches du Rhone, Var and Alpes de Hautes Provence .
            This seems logical as these regions are located in the south of France with 
            relatively warmer temperatures than the rest of France.''')


    #data for trends
    data2=data.groupby(['nom_dept','date_des_donnees']).sum().reset_index()
    # data2['sum_3_prod_e_kw_puissance_de_raccordement_injection']=round(data2['sum_3_prod_e_kw_puissance_de_raccordement_injection']/1000000,1)

    trends = px.line(data2, x="date_des_donnees", y='sum_3_prod_e_kw_puissance_de_raccordement_injection', 
                     title='Trends and patterns',
              color='nom_dept', labels={'nom_dept':'dpt','sum_3_prod_e_kw_puissance_de_raccordement_injection':
                                       'power','date_des_donnees':'date' })
    st.plotly_chart(trends)

    st.write(f'''We noticed an increase of injected power in 2018 followed by a drop in 2019 for most locations. 
             Since 2020, the injected power goes up against with a 
             sharp increase by 2021 for a few departments like Gironde and Landes.''')
    
    st.header('Correlation with the sunshine duration ?')
    #sunshine data
    sunshine=pd.read_csv('data/temps-densoleillement-par-an-par-departement-feuille-1.csv')
    sunshine=sunshine.rename(columns={sunshine.columns[1]:'time'})
    sunshine['Départements']=sunshine['Départements'].apply(lambda x: unidecode(x))
    st.dataframe(sunshine)

    st.subheader('top department for average sunshine time')
    st.dataframe(sunshine.nlargest(20, 'time'))

    st.write(f'''Bouches du Rhone, Var,Alpes de Hautes Provence, showed as some of the highest injectors 
             of power also appear in the top department with high sunshine time.''')
    
    #checking correlation between variable
#matching time and power
    dictzip=dict(zip(sunshine.Départements, sunshine.time)) #create dict to extract values
    data_corr=data1.copy()
    data_corr['nom_dept']=data_corr['nom_dept'].apply(lambda x :unidecode(x))
    data_corr['time']=data_corr['nom_dept'].apply(lambda x :dictzip[x] if x in dictzip else np.nan)
    data_corr[data_corr['time'].isnull()==False]
    #correlation
    st.subheader('Correlation')
    st.write(data_corr.corr())
    st.write('The correlation between sunshine duration and injection power is not obvious')

with tab2:
        st.header("Identification of the Most Interesting Geographical Areas")
        data_region=installations[['nom_reg','count', 'sum_3_prod_e_kw_puissance_de_raccordement_injection','date_des_donnees']]
        data_region=data_region.groupby('nom_reg').sum().reset_index()
        st.dataframe(data_region.sort_values(by=['count'], ascending=False))
        st.write('Based on the distribution of installations we can segment the data into three segments: high number of installations,average number,low number')
        # high number of installations
        st.subheader('High')
        st.write('high number of installations')
        st.dataframe(data_region[data_region['count'] >100000])
        #average number of installations
        
        st.subheader('Moderate')
        st.write('high number of installations')

        st.dataframe(data_region[(data_region['count'] >1000) & (data_region['count']<10000)])

        #low number of installations
        st.subheader('Low')
        st.write('low number of installations')

        st.dataframe(data_region[data_region['count']<1000])

        st.subheader('region would you identify as having high potential for our projects?'
                     )
        st.write(f'''regions whith high potential should be the one with low numbers of solar installations and high injection power, such as Corse, Provences-Alpes Côtes d'Azures and La Réunion''')
