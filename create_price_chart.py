import matplotlib.pyplot as pyplot
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import requests
import configuration
from datetime import datetime
import itertools
import math
import matplotlib.font_manager as font_manager
from io import BytesIO

# Set the API endpoint URL and request headers
url = "https://api.tibber.com/v1-beta/gql"
headers = {
        "Authorization": 'Bearer ' + configuration.API_KEY,
        "Content-Type": "application/json",
    }

# Set the GraphQL query
query = """
{
  viewer {
    homes {
      currentSubscription{
        priceInfo{
          today {
            total
            startsAt
            level
          }
          tomorrow {
            total
            startsAt
            level
          }
        }
      }
    }
  }
}
"""

class PriceChart: 

  def transform_data(self, data_dic):
    for data in data_dic:
      data['startsAt'] = datetime.fromisoformat(data['startsAt']).strftime("%H")
      data['total'] = round(data['total'] * 100, 1)
    return data_dic

  def get_tibber_data(self):
    data = {"query": query}
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    homes = response_data['data']['viewer']['homes']

    # Iteriere über die Abonnements und speichere das Objekt "priceInfo" in der Variablen "price_infos", wenn es vorhanden ist
    price_infos = response_data["data"]["viewer"]["homes"][0]["currentSubscription"]["priceInfo"]

    # print(price_infos)

    today_data = self.transform_data(price_infos["today"])
    tomorrow_data = self.transform_data(price_infos["tomorrow"])

    # fill tomorrow with empty entries
    # falls die Preise für morgen noch nicht existieren
    if (len(tomorrow_data) == 0): 
      for x in range(0, 24):
        tomorrow_data.append({'total': float('nan'), 'startsAt': str(x).zfill(2), 'level': 'NORMAL'})

    return (today_data, tomorrow_data)


  ################################

  def mark_now(self, plt, y):
    hour_now = int(datetime.now().strftime("%-H"))
    y_list = list(y)
    # plt.vlines(x = (hour_now + 0.5), ymin=0, ymax=40, color = 'red', label = str(y_list[hour_now]), linestyles="dashed")
    plt.axvline(x=hour_now + 0.5, color="black")
    x_pos = (hour_now / 48) + 0.08

  #  y_bounds = plt.get_ylim()
  #  y_pos = (y_bounds[1] - y_bounds[0]) / 100 * (y_list[hour_now] - y_bounds[0]) - 0.05
    y_pos = 0.01
    plt.annotate(str(y_list[hour_now]), xy=(x_pos, y_pos), xycoords='axes fraction', verticalalignment='bottom', horizontalalignment="right") 

  def calculate_pricings(self, today_data, tomorrow_data):
    data = itertools.chain(today_data, tomorrow_data)
    d_min = 999
    d_max = -999
    d_sum = 0
    counter = 0
    for i, d in enumerate(data):
      val = d["total"]
      if val != None and val != float('nan'):
        d_sum += val
        d_min = min(d_min, val)
        d_max = max(d_max, val)
        counter += 1
      
    d_avg = d_sum / counter

    return d_min, d_max, d_avg    

  def filter_expensives(self, today_data, tomorrow_data, v_avg):
    values = itertools.chain(today_data, tomorrow_data)
    result_list = []
    avg_upper_border = v_avg * 1.15
    for val in values:
      if "EXPENSIVE" in val['level'] or val['total'] > avg_upper_border:
        result_list.append(val['total'])
      else: 
        result_list.append(float('nan'))

    return result_list

  def generate_chart(self):
    today_data, tomorrow_data = self.get_tibber_data()
    v_min, v_max, v_avg = self.calculate_pricings(today_data, tomorrow_data)

    x_label = [interval["startsAt"] for interval in itertools.chain(today_data, tomorrow_data)]
    x = range(0, sum(1 for x in x_label))
    y_val = list([interval["total"] for interval in itertools.chain(today_data, tomorrow_data)])
    y_val_expensive = self.filter_expensives(today_data, tomorrow_data, v_avg)

    fonts = font_manager.findSystemFonts(fontpaths="fonts/Pixelify_Sans/", fontext='ttf')
    for font_file in fonts:
        font_manager.fontManager.addfont(font_file)

    pyplot.rcParams.update({'font.size': 16, 'font.family': 'Pixelify Sans', 'font.weight': 'normal', 'text.antialiased': False}) # Basic font size
    fig, plt = pyplot.subplots(layout="constrained") # Create plot
    # fig, plt = pyplot.subplots() # Create plot
    normal_stairs = plt.stairs(y_val, color="white", linewidth=2, fill=True)
    normal_stairs.set_edgecolor("black")

    # Grid
    #plt.grid(True, which="both", axis="y", linestyle="solid", color="black")
    plt.get_yaxis().grid(True, color="black", linestyle="solid")
    plt.set_axisbelow(True)
    plt.set_ylim(ymin=v_min - 1, ymax=v_max + 1) # min/max of Y axis
    plt.spines["top"].set_visible(False)
    plt.spines["right"].set_visible(False)
    plt.spines["left"].set_linewidth(1)
    plt.spines["bottom"].set_linewidth(1)
    day_splitter = plt.axvline(x=24, color="black") # Day splitter

    # Labels
    plt.set_xticks(x, x_label)
    plt.set_xlim(0, len(x))
    for (i,l) in enumerate(plt.get_xaxis().get_ticklabels()):
      if i % 3 != 0 or l.get_text() == "00":
        l.set_visible(False)
    #plt.set_in_layout(False)
    text_on_graphics = []
    text_on_graphics.append(plt.annotate('heute', xy=(0.01, 0.95), xycoords='axes fraction'))
    text_on_graphics.append(plt.annotate('morgen', xy=(0.51, 0.95), xycoords='axes fraction'))

    title = fig.suptitle("Strompreise", fontsize=32, ha="left", fontweight='normal', position=(0.02, 1))

    # Preis für die aktuelle Stunde
    # aktuelle Stunde
    hour_now = int(datetime.now().strftime("%-H"))
    
    if hour_now < len(today_data):
      aktueller_preis = today_data[hour_now]["total"]
    else:
      aktueller_preis = "n/a"

    fig.text(0.53, 0.95, "Aktuell:          " + str(aktueller_preis) + " ct/kWh", fontsize=18, color="black")

    # Ausgabe des Durchschnittspreises, funktioniert aktuell nur, wenn bereits die Preise
    # für morgen geladen wurden
    # fig.text(0.53, 0.91, "Ø-Preis heute:      " + str(round(v_avg, 2)) + " ct/kWh", fontsize=14, color="black")  

    # Storing images
    fig.set_size_inches(configuration.display_pixels[0]/100, configuration.display_pixels[1]/100)
    chart_blk = BytesIO()
    chart_red = BytesIO()
    fig.savefig(chart_blk, transparent=False, dpi=100)

    def create_red_version(plt, normal_stairs, x, y_val, title, day_splitter, text_on_graphics):
      normal_stairs.set_color("white")
      plt.stairs(y_val_expensive, color="black", fill=True)
      self.mark_now(plt, y_val) # Mark actual 
      plt.spines["left"].set_visible(False)
      plt.spines["bottom"].set_visible(False)
      title.set_color("white")
      plt.get_xaxis().get_label().set_color("white")
      plt.tick_params(axis='x', colors='white')
      plt.get_yaxis().get_label().set_color("white")
      plt.tick_params(axis='y', colors='white')
      day_splitter.set_visible(False)
      plt.grid(False)
      for t in text_on_graphics:
        t.set_visible(False)

    def create_full_black_version(plt, x, y_val):
      self.mark_now(plt, x, y_val) # Mark actual 
      plt.stairs(y_val_expensive, color="black", fill=True)

    create_red_version(plt, normal_stairs, x, y_val, title, day_splitter, text_on_graphics)

    fig.savefig(chart_red, transparent=False, dpi=100)

    chart_blk.seek(0)
    chart_red.seek(0)
    return chart_blk, chart_red
  


chart_blk, chart_red = PriceChart().generate_chart()
with open("charts/chart_blk.png", "wb") as f:
    f.write(chart_blk.getbuffer())

with open("charts/chart_red.png", "wb") as f:
    f.write(chart_red.getbuffer())
