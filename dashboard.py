import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="white")

# import data
df_all_city = pd.read_csv("dashboard/all_city_df.csv")

# dataframe

air_quality_parameter =  ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3","TEMP", "PRES", "DEWP", "RAIN", "WSPM"] #list of air quality parameters
threshold_day = {
    "PM2.5": 75,
    "PM10": 150,
    "CO": 10000,
    "O3": 200,
    "NO2": 200,
    "SO2":150
}
threshold_year = {
    "PM2.5": 35,
    "PM10": 70,
    "CO": 4000,
    "O3": 160,
    "NO2": 40,
    "SO2":60
}
def create_df_day_month_year(df):
    df_day_month_year = df.groupby("date")[air_quality_parameter].mean(numeric_only=True).reset_index() # dataframe rata rata dalam satu hari 
    return df_day_month_year
def create_df_year_month(df):
    df["year_month"] = df["date"].astype(str).str[:7]  #  tambah kolom year_month, Ambil format "YYYY-MM"
    df_year_month = df.groupby("year_month")[air_quality_parameter].mean(numeric_only=True).reset_index() # datafram rata rata dalam satu bulan
    return df_year_month
def create_df_day(df):
    df_day = df.groupby("hour")[air_quality_parameter].mean(numeric_only=True).reset_index() # dataframe rata rata tiap jam dalam sehari
    return df_day
def create_df_season(df):
    df["month"] = pd.to_datetime(df["year_month"]).dt.month 
    def assign_season(month):
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        else:
            return "Autumn"
    df["season"] = df["month"].apply(assign_season)
    df_season = df.groupby("season")[air_quality_parameter].mean(numeric_only=True).reset_index() # dataframe rata rata dalam satu musim
    return df_season
def create_df_station(df):
    df_station = df.groupby("station")[air_quality_parameter].mean(numeric_only=True).reset_index()
    return df_station

min_date = df_all_city["date"].min()
max_date = df_all_city["date"].max()

with st.sidebar:
    start_date, end_date = st.date_input(
        label="Date Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )
    selected_param = st.selectbox(
    label="Air Quality Parameter",
    options = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
)

df_day_month_year = create_df_day_month_year(df_all_city)
df_year_month = create_df_year_month(df_all_city)
df_day = create_df_day(df_all_city)
df_season = create_df_season(df_all_city)
df_station = create_df_station(df_all_city)

main_df = df_day_month_year[
    (df_day_month_year["date"] >= str(start_date)) & (df_day_month_year["date"] <= str(end_date))
    ]
main_df["date"] = pd.to_datetime(main_df["date"], format='%Y-%m-%d' )

st.title("AIR QUALITY ANALYSIS DASHBOARD")

# tab inisialization
tab1, tab2, tab3, tab4, tab5 = st.tabs(["HOME","POLUTAN","WEATHER", "HEATMAP", "DATAFRAME"])
with tab1: #home
    st.header("Air Quality Report")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Daily Average Standard", value=threshold_day[selected_param])
    with col2:
        st.metric("Yearly Average Standard", value=threshold_year[selected_param])
    with col3:
        avgSelectedRange = round(main_df[selected_param].mean(), 2)
        st.metric("Avg Selected Range", value=avgSelectedRange)

    #PM2.5 Line Chart filtered
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        main_df["date"],
        main_df[selected_param],
        marker='o', 
        linewidth=2,
        color="#90CAF9"
    )
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)

with tab2: #polutan
    st.header("AVERAGE AIR QUALITY IN A DAY")
    with st.container():
        st.subheader("Fine Particulate Matter (PM2.5 & PM10)") 
        st.write("Line Chart dibawah merupakan rata-rata konsentrasi PM2.5 dan PM10 per jam dalam sehari, rata rata diambil dari keseluruhan kota dan rentang waktu.")    
        plt.figure(figsize=(40, 10))
        plt.plot(df_day["hour"], df_day['PM2.5'], label='PM2.5', color='red')
        plt.plot(df_day["hour"], df_day['PM10'], label='PM19', color='blue')
        plt.title('PARTIKEL POLUSI ( DALAM SATUAN MIKROGRAM/METER KUBIK )', size=20)
        plt.xlabel('Hour',size=15)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.legend(fontsize=20) 
        st.pyplot(plt)
        with st.expander("See explanation"):
            st.write(
                """Berdasarkan analisis data rata-rata PM2.5 dan PM10 per jam dalam sehari dari tahun 2013 hingga 2017, terlihat bahwa kedua partikel polutan memiliki pola yang mirip, dengan kadar PM10 yang selalu lebih tinggi. Konsentrasi tertinggi terjadi pada malam hari, khususnya sekitar pukul 21:00 - 22:00, sebelum mengalami penurunan menjelang tengah malam. Sementara itu, konsentrasi terendah tercatat pada pukul 06:00 - 07:00, diikuti oleh sedikit kenaikan setelahnya dan penurunan kembali sekitar pukul 10:00. Polusi udara mulai meningkat lagi setelah pukul 15:00, menunjukkan adanya pengaruh aktivitas manusia seperti lalu lintas dan industri. Pola ini mengindikasikan bahwa kualitas udara cenderung lebih buruk pada malam hari dibandingkan pagi hari.
                """
            )
    st.subheader("Pollutant Concentration (NO2, O3, SO2, CO)")
    with st.container():
            st.write("Line Chart dibawah merupakan rata-rata konsentrasi gas polutan NO2, O3, SO2, dan CO per jam dalam sehari, rata rata diambil dari keseluruhan kota dan rentang waktu.")   
            #SO2, NO2, O3
            plt.figure(figsize=(40, 10))
            plt.plot(df_day["hour"], df_day['SO2'], label='SO₂', color='red')
            plt.plot(df_day["hour"], df_day['NO2'], label='NO₂', color='blue')
            plt.plot(df_day["hour"], df_day['O3'], label='O₃', color='green')
            plt.title('GAS POLUTAN ( DALAM SATUAN MIKROGRAM/METER KUBIK )', size=20)
            plt.xlabel('Hour',size=15)
            plt.xticks(fontsize=10)
            plt.yticks(fontsize=10)
            plt.legend(fontsize=20) 
            st.pyplot(plt)
            #CO
            plt.figure(figsize=(40, 10))
            plt.plot(df_day["hour"], df_day['CO'], label='CO', color='red')
            plt.title('GAS POLUTAN ( DALAM SATUAN MIKROGRAM/METER KUBIK )', size=20)
            plt.xlabel('Hour',size=15)
            plt.xticks(fontsize=10)
            plt.yticks(fontsize=10)
            plt.legend(fontsize=20) 
            st.pyplot(plt)      
            with st.expander("See explanation"):
                st.write(
                    """Berdasarkan analisis grafik, pola pergerakan gas polutan CO, NO₂, O₃, dan SO₂ menunjukkan dinamika yang beragam sepanjang hari. CO memiliki konsentrasi tertinggi pada tengah malam hingga pukul 01:00 - 02:00, mengalami sedikit penurunan hingga pukul 04:00, lalu kembali naik perlahan hingga mencapai puncaknya sekitar sekitar pukul 09:00 sebelum turun secara signifikan. Titik terendah CO terjadi sekitar pukul 15:00 - 16:00, kemudian meningkat tajam hingga tengah malam. Sementara itu, NO₂, O₃, dan SO₂ tidak memiliki pola yang seragam. O₃ mengalami kenaikan signifikan dari pukul 07:00 - 08:00, mencapai puncaknya di 15:00 - 16:00, lalu menurun setelahnya. NO₂ justru menurun sedikit sekitar pukul 07:00 - 08:00, mencapai titik terendah di 15:00 - 16:00, lalu naik kembali setelah itu. SO₂ menunjukkan fluktuasi yang lebih stabil, dengan sedikit kenaikan sekitar pukul 07:00 - 08:00, kemudian perlahan menurun hingga lewat tengah malam. Secara keseluruhan, tren juga ini mengindikasikan bahwa aktivitas manusia seperti kendaraan bermotor, industri, dan proses atmosferik berperan besar dalam perubahan kadar polutan sepanjang hari.
                    """
                )
    st.header("MONTHLY AVERAGE AIR QUALITY")
    st.subheader("Fine Particulate Matter (PM2.5 & PM10)") 
    with st.container():
        st.write("Line Chart dibawah merupakan rata-rata konsentrasi PM2.5 dan PM10 per bulan, rata rata diambil dari keseluruhan kota dan rentang waktu.")     
        x_labels = df_year_month["year_month"][::3]

        plt.figure(figsize=(40, 10))
        plt.plot(df_year_month["year_month"], df_year_month['PM2.5'], label='PM2.5', color='red')
        plt.plot(df_year_month["year_month"], df_year_month['PM10'], label='PM10', color='blue')     
        plt.title('GAS POLUTAN', size=20)
        plt.xlabel('Date',size=15)
        plt.xticks(fontsize=8)
        plt.xticks(ticks=x_labels, labels=x_labels, fontsize=10, rotation=45)
        plt.yticks(fontsize=10)
        plt.legend()
        st.pyplot(plt)
        with st.expander("See explanation"):
            st.write(
                """Grafik menunjukkan bahwa kadar PM10 selalu lebih tinggi dibandingkan PM2.5 sepanjang periode Maret 2013 hingga Februari 2017, dengan fluktuasi signifikan setiap bulan. Terjadi lonjakan konsentrasi pada beberapa titik, terutama di akhir ataupun awal tahun, yang kemungkinan dipengaruhi oleh faktor musiman seperti musim kemarau atau aktivitas manusia seperti kebakaran hutan dan industri. Selain itu, pola tahunan yang berulang menunjukkan bahwa kondisi lingkungan dan sumber polusi memiliki tren yang konsisten dari tahun ke tahun. Peningkatan tajam dalam beberapa periode menunjukkan kemungkinan adanya peristiwa khusus yang meningkatkan polusi udara, seperti musim kemarau atau kebakaran hutan. Secara keseluruhan, kualitas udara dalam periode ini mengalami variasi yang cukup besar dengan beberapa puncak polusi yang mencolok.
                """
            )
    st.subheader("Pollutant Concentration (NO2, O3, SO2, CO)")
    with st.container():
        st.write("Line Chart dibawah merupakan rata-rata konsentrasi NO₂, O₃, SO₂ dan CO per bulan, rata rata diambil dari keseluruhan kota dan rentang waktu.")  
        x_labels = df_year_month["year_month"][::3]

        plt.figure(figsize=(40, 10))
        plt.plot(df_year_month["year_month"], df_year_month['SO2'], label='SO2', color='red')
        plt.plot(df_year_month["year_month"], df_year_month['NO2'], label='NO2', color='blue')
        plt.plot(df_year_month["year_month"], df_year_month['O3'], label='O3', color='green')
        plt.title('GAS POLUTAN', size=20)
        plt.xlabel('Date',size=15)
        plt.xticks(fontsize=8)
        plt.xticks(ticks=x_labels, labels=x_labels, fontsize=10, rotation=45)
        plt.yticks(fontsize=10)
        plt.legend()
        st.pyplot(plt)

        x_labels = df_year_month["year_month"][::3]

        plt.figure(figsize=(40, 10))
        plt.plot(df_year_month["year_month"], df_year_month['CO'], label='CO', color='red')
        plt.title('GAS POLUTAN', size=20)
        plt.xlabel('Date',size=15)
        plt.xticks(fontsize=8)
        plt.xticks(ticks=x_labels, labels=x_labels, fontsize=10, rotation=45)
        plt.yticks(fontsize=10)
        plt.legend()
        st.pyplot(plt)
        with st.expander("See explanation"):
             st.write(
                """Data rata-rata gas polutan dari Maret 2013 hingga Februari 2017 menunjukkan pola fluktuatif dengan lonjakan signifikan pada CO di akhir tahun, kemungkinan akibat peningkatan aktivitas industri dan kendaraan. SO₂ cenderung stabil dengan sedikit fluktuasi, sementara NO₂ mengalami pola naik turun yang lebih seimbang. O₃ menunjukkan lonjakan besar di pertengahan tahun, yang bisa disebabkan oleh reaksi fotokimia akibat intensitas sinar matahari. Pola ini mengindikasikan bahwa faktor lingkungan, aktivitas manusia, dan perubahan musim berperan besar dalam variabilitas polusi udara selama periode tersebut..
                """
            )
    st.header("AVARAGE AIR QUALITY IN EVERY CITY")
    with st.container():
        st.write("Line Chart dibawah merupakan rata-rata Kualitas Udara tiap kota, rata rata diambil dari keseluruhan rentang waktu.")  
        df_station_melted = df_station.melt(id_vars="station", var_name="Pollutant", value_name="Concentration")
        #hapus pameter lingkungan
        df_station_melted = df_station_melted[~df_station_melted["Pollutant"].isin(["CO", "TEMP", "PRES", "DEWP", "RAIN", "WSPM"])]
        # Plot grouped bar chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x="station", y="Concentration", hue="Pollutant", data=df_station_melted, palette="Set2")
        # Tambahin label & judul
        plt.xlabel("station")
        plt.ylabel("Pollutant Concentration")
        plt.title("Air Pollution Levels Across Seasons")
        plt.legend(title="Pollutant")
        plt.xticks(rotation=45)  
        # Tampilkan plot
        st.pyplot(plt)
        plt.bar(x=df_station["station"], height=df_station["CO"])
        plt.xticks(rotation=80)  
        st.pyplot(plt)
        with st.expander("See explanation"):
            st.write(
                """Kota Dingling memiliki kadar rata-rata CO paling rendah, sedangkan kota dengan kadar CO tertinggi adalah Wahshouxigong. Hal ini menunjukkan bahwa tingkat pembakaran dari industri maupun kendaraan bermotor di Wahshouxigong lebih besar dibandingkan kota lainnya. Sementara itu, kadar O₃ paling rendah ditemukan di kota Wanlu, sementara kadar tertinggi terdapat di Dingling. Karena terdapat korelasi positif antara O₃ dan suhu, dapat disimpulkan bahwa Wanlu memiliki suhu rata-rata paling rendah, sedangkan Dingling memiliki suhu rata-rata tertinggi. Faktor suhu berperan penting dalam pembentukan O₃, sedangkan emisi CO lebih dipengaruhi oleh aktivitas industri dan transportasi.  
                Selain CO dan O₃, analisis terhadap gas lainnya menunjukkan pola menarik. Kota dengan kadar NO₂ yang lebih tinggi cenderung memiliki tingkat kepadatan kendaraan dan aktivitas industri yang signifikan, karena NO₂ umumnya berasal dari pembakaran bahan bakar fosil, terutama dari kendaraan bermotor dan pembangkit listrik.  
                Di sisi lain, konsentrasi SO₂ yang lebih tinggi di suatu kota dapat mengindikasikan adanya aktivitas pembakaran batu bara atau bahan bakar dengan kandungan sulfur tinggi, yang umumnya ditemukan di daerah industri. Selain itu, kadar PM₂.₅ yang tinggi dapat menjadi indikator pencemaran udara yang disebabkan oleh debu, asap industri, atau pembakaran biomassa.  
                Secara umum, kota dengan suhu lebih tinggi cenderung memiliki kadar O₃ yang lebih besar akibat proses fotokimia yang lebih aktif, sedangkan kota dengan tingkat aktivitas industri dan transportasi yang tinggi memiliki konsentrasi polutan seperti CO, NO₂, SO₂, dan PM₂.₅ yang lebih besar. Hal ini menunjukkan bahwa suhu, kepadatan kendaraan, serta keberadaan industri memainkan peran penting dalam menentukan kualitas udara di suatu kota.
                """
            )
with tab3: #weather
    st.header("AVERAGE WEATHER IN A DAY")
    with st.container():
        st.write("Line Chart dibawah merupakan rata-rata parameter cuaca per jam dalam sehari, rata rata diambil dari keseluruhan kota dan rentang waktu.")    
        def plot_weather(param, label, color, title):
            plt.figure(figsize=(20, 5))
            plt.plot(df_day["hour"], df_day[param], label=label, color=color)
            plt.title(title, size=20)  # Menggunakan title yang diberikan
            plt.xlabel('Hour', size=15)
            plt.xticks(fontsize=20)
            plt.yticks(fontsize=20)
            plt.legend(fontsize=20)
            st.pyplot(plt)
        plot_weather("TEMP","Temperature","red","Temperature")
        plot_weather("PRES","Pressure","orange","Pressure")
        plot_weather("DEWP","Dew Point","green","Dew Point")
        plot_weather("RAIN","Rain","blue","Rain")
        with st.expander("See explanation"):
            st.write(
                """Berdasarkan data yang dianalisis, dapat disimpulkan bahwa suhu rata-rata dalam sehari mengalami kenaikan di siang hari seperti yang diharapkan. Curah hujan cenderung lebih sering terjadi pada malam hari dibandingkan siang hari, yang mungkin disebabkan oleh pelepasan panas dan kondensasi yang lebih intens saat suhu menurun. Titik embun lebih tinggi di malam dan pagi hari, menunjukkan bahwa embun lebih mudah terbentuk pada waktu-waktu tersebut karena udara lebih dingin dan kelembapan meningkat. Sementara itu, tekanan udara relatif stabil tanpa lonjakan signifikan, menandakan kondisi atmosfer yang cenderung konsisten sepanjang hari.
                """
            )
    st.header("AVERAGE WEATHER IN A MONTH")
    with st.container():
        st.write("Line Chart dibawah merupakan rata-rata parameter cuaca per bulan, rata rata diambil dari keseluruhan kota dan rentang waktu.")
        def plot_weather(param, label, color, title):
            plt.figure(figsize=(20, 5))
            plt.plot(df_year_month["year_month"], df_year_month[param], label=label, color=color)
            plt.title(title, size=20)  # Menggunakan title yang diberikan
            plt.xlabel('Month', size=15)
            plt.xticks(df_year_month["year_month"][::3], fontsize=20, rotation=80)
            plt.yticks(fontsize=20)
            plt.legend(fontsize=20)
            st.pyplot(plt)

        plot_weather("TEMP","Temperature","red","Temperature")
        plot_weather("PRES","Pressure","orange","Pressure")
        plot_weather("DEWP","Dew Point","green","Dew Point")
        plot_weather("RAIN","Rain","blue","Rain")
        with st.expander("See explanation"):
            st.write(
                """Analisis data cuaca menunjukkan bahwa suhu meningkat secara konsisten selama musim panas, sementara suhu di pertengahan tahun relatif stabil dari tahun ke tahun. Namun, terdapat anomali pada akhir 2015 hingga awal 2016, di mana suhu musim dingin lebih dingin sekitar 5°C dibanding tahun-tahun sebelumnya. Tekanan udara cenderung menurun saat suhu meningkat, dengan titik terendah rata-rata berada di pertengahan tahun sekitar 1000 hPa, kecuali pada pertengahan 2013 yang sedikit lebih rendah. Selain itu, pola titik embun selaras dengan suhu, mencerminkan hubungan erat antara suhu dan kelembapan udara. Curah hujan juga menunjukkan intensitas tertinggi di pertengahan tahun, yang kemungkinan terkait dengan musim hujan atau perubahan pola angin. Secara keseluruhan, pola cuaca tahunan cukup stabil dengan beberapa pengecualian yang dapat menjadi indikator perubahan iklim atau fenomena cuaca ekstrem.
                """
            )
    st.header("AVERAGE WEATHER EACH CITY")
    with st.container():
        st.write("Line Chart dibawah merupakan rata-rata parameter cuaca tiap kota, rata rata diambil dari keseluruhan rentang waktu.")
        def barPlot_weather(param, color, title):
            plt.figure(figsize=(10, 5))
            plt.bar(x=df_station["station"], height=df_station[param], label=param, color=color)
            plt.title(title, size=20)  # Menggunakan title yang diberikan
            plt.xlabel('Cities', size=15)
            plt.xticks(rotation=80)
            st.pyplot(plt)
        barPlot_weather("TEMP", "red", "Temperature")
        barPlot_weather("PRES", "orange", "Pressure")
        barPlot_weather("DEWP", "green", "Dew Point")
        barPlot_weather("RAIN", "blue", "Rain")
        with st.expander("See explanation"):
            st.write(
                """Dari data rata-rata kondisi cuaca berbagai kota, dapat disimpulkan bahwa suhu dan tekanan udara relatif seragam di semua kota, dengan sedikit variasi di Huairou (lebih rendah) dan Gucheng (lebih tinggi). Namun, terdapat perbedaan yang lebih mencolok pada titik embun, di mana Changping dan Dingling memiliki titik embun terendah, sedangkan Wanhliy memiliki titik embun tertinggi. Sementara itu, curah hujan tidak menunjukkan perbedaan yang signifikan antar kota.
                """
            )
with tab4: #pollutant & weather correlation
    pollutants = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
    weather = ["TEMP", "PRES", "DEWP", "RAIN", "WSPM"]
    st.header("POLLUTANT & WEATHER CORRELATION")
    st.write("Heatmap dibawah menunjukan korelasi antara sesama parameter udara dan antara parameter udara dan kondisi lingkungan.")
    # korelasi antar parameter udara
    with st.container():
        st.subheader("Pollutant Correlation")
        corr_pollutants = df_all_city[pollutants].corr()
        #Plot heatmap
        plt.figure(figsize=(8, 5))
        sns.heatmap(corr_pollutants, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)

        plt.title("Korelasi Antar Polutan vs Kondisi Lingkungan", fontsize=15)
        plt.xlabel("Kondisi Lingkungan", fontsize=12)
        plt.ylabel("Tingkat Polutan", fontsize=12)
        st.pyplot(plt)
        with st.expander("See explanation"):
            st.write(
                """Berdasarkan analisis korelasi antar polutan, gas O₃ memiliki hubungan negatif dengan gas polutan lainnya (SO₂, NO₂, CO) serta partikel polutan (PM2.5 dan PM10), yang mengindikasikan bahwa peningkatan O₃ biasanya terjadi saat konsentrasi polutan lain menurun. Sementara itu, SO₂ tidak menunjukkan korelasi yang signifikan dengan polutan lain, dengan nilai korelasi yang bervariasi antara 0.5 hingga -0.2, menunjukkan bahwa faktor pembentukannya mungkin lebih independen dibandingkan gas lainnya. Di sisi lain, selain O₃ dan SO₂, polutan lainnya memiliki korelasi positif yang cukup kuat (≥0.5), menunjukkan bahwa sumber emisi atau mekanisme penyebaran mereka cenderung berhubungan erat. Hal ini mengindikasikan bahwa peningkatan polutan seperti NO₂, CO, dan partikel PM kemungkinan besar disebabkan oleh sumber pencemaran yang sama, seperti aktivitas kendaraan bermotor dan industri.
                """
            )
    # korelasi antara parameter udara dan kondisi cuaca
    with st.container():
        st.subheader("Pollutant vs Weather Correlation")
        corr_weather_polutants = df_all_city[pollutants + weather].corr()
        corr_weather_polutants = corr_weather_polutants.loc[pollutants, weather]

        #Plot heatmap
        plt.figure(figsize=(8, 5))
        sns.heatmap(corr_weather_polutants, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)

        plt.title("Korelasi Polutan vs Kondisi Lingkungan", fontsize=15)
        plt.xlabel("Kondisi Lingkungan", fontsize=12)
        plt.ylabel("Tingkat Polutan", fontsize=12)
        st.pyplot(plt)
        with st.expander("See explanation"):
            st.write(
                """Berdasarkan heatmap korelasi, suhu memiliki pengaruh signifikan terhadap polutan udara, terutama dalam meningkatkan kadar O₃ (0.59) dan menurunkan konsentrasi CO, NO₂, serta SO₂ yang berkorelasi negatif dengannya. Tekanan udara (-0.45) juga berperan dalam menghambat pembentukan O₃, sementara kecepatan angin (WSPM) membantu menyebarkan polutan, terlihat dari korelasi negatifnya dengan NO₂ (-0.40) dan CO (-0.29). Kelembaban (DEWP) memiliki hubungan positif dengan O₃ (0.31) namun negatif dengan SO₂ (-0.27), menunjukkan pengaruh uap air dalam reaksi kimia di atmosfer. Sementara itu, curah hujan tidak menunjukkan korelasi yang signifikan terhadap polutan, mengindikasikan bahwa faktor meteorologi lain lebih dominan dalam menentukan kualitas udara. Secara keseluruhan, suhu dan kecepatan angin menjadi faktor utama yang mempengaruhi konsentrasi polutan, dengan suhu tinggi yang mendorong pembentukan O₃, sementara angin berperan dalam mendispersikan polutan lainnya.
                """
            )
with tab5: #raw dataframe
    dfmultiselect = st.multiselect(
        label="Select Dataframe",
        options=["Daily_Mean", "Monthly_Mean", "Seasonly_Mean", "City_Mean", "hourPerDay_Mean"],
        default=["Daily_Mean"],
    )
    df_dict = {
        "Daily_Mean": (df_day_month_year, "Dataframe of average air quality per day"), 
        "Monthly_Mean": (df_day_month_year,"Dataframe of average air quality per month"),
        "Seasoly_Mean": (df_season, "Dataframe of average air quality seasonly"),
        "City_Mean": (df_station, "Dataframe of average air quality per station"),
        "hourPerDay_Mean": (df_day, "Dataframe of average air quality per hour")
    }
    for df_selected in dfmultiselect:
        df, caption = df_dict[df_selected]
        st.dataframe(df)
        st.caption(caption)
