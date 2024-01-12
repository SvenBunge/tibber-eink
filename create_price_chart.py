import matplotlib.pyplot as pyplot
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import requests
import configuration
from datetime import datetime
import itertools
import math
import matplotlib.font_manager as font_manager

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

def transform_data(data_dic):
  for data in data_dic:
    data['startsAt'] = datetime.fromisoformat(data['startsAt']).strftime("%H")
    data['total'] = round(data['total'] * 100, 1)
  return data_dic


def get_tibber_data():
  data = {"query": query}
  response = requests.post(url, json=data, headers=headers)
  response_data = response.json()
  homes = response_data['data']['viewer']['homes']

  # Iteriere über die Abonnements und speichere das Objekt "priceInfo" in der Variablen "price_infos", wenn es vorhanden ist
  price_infos = response_data["data"]["viewer"]["homes"][0]["currentSubscription"]["priceInfo"]

  # Gib die Liste der Preise aus
  # print(price_infos)

  today_data = transform_data(price_infos["today"])
  tomorrow_data = transform_data(price_infos["tomorrow"])

  if (len(tomorrow_data) == 0): 
    for x in range(0, 24):
      tomorrow_data.append({'total': float('nan'), 'startsAt': str(x).zfill(2), 'level': 'NORMAL'})

  return (today_data, tomorrow_data)


################################

def mark_now(plt, y):
  hour_now = int(datetime.now().strftime("%-H"))
  y_list = list(y)
  # plt.vlines(x = (hour_now + 0.5), ymin=0, ymax=40, color = 'red', label = str(y_list[hour_now]), linestyles="dashed")
  plt.axvline(x=hour_now + 0.5, color="black")
  x_pos = (hour_now / 48) + 0.08

#  y_bounds = plt.get_ylim()
#  y_pos = (y_bounds[1] - y_bounds[0]) / 100 * (y_list[hour_now] - y_bounds[0]) - 0.05
  y_pos = 0.01
  plt.annotate(str(y_list[hour_now]), xy=(x_pos, y_pos), xycoords='axes fraction', verticalalignment='bottom', horizontalalignment="right") 

def calculate_pricings(today_data, tomorrow_data):
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

def filter_expensives(today_data, tomorrow_data, v_avg):
  values = itertools.chain(today_data, tomorrow_data)
  result_list = []
  avg_upper_border = v_avg * 1.15
  for val in values:
    if "EXPENSIVE" in val['level'] or val['total'] > avg_upper_border:
      result_list.append(val['total'])
    else: 
      result_list.append(float('nan'))

  return result_list

today_data, tomorrow_data = get_tibber_data()
v_min, v_max, v_avg = calculate_pricings(today_data, tomorrow_data)

x_label = [interval["startsAt"] for interval in itertools.chain(today_data, tomorrow_data)]
x = range(0, sum(1 for x in x_label))
y_val = list([interval["total"] for interval in itertools.chain(today_data, tomorrow_data)])
y_val_expensive = filter_expensives(today_data, tomorrow_data, v_avg)

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

# Schrift in der Legende und Beschriftung der Achsen anpassen
title = fig.suptitle("Strompreise", fontsize=32, ha="left", fontweight='normal', position=(0.02, 1))
# ylabel = plt.set_ylabel("Cent", fontsize=18, ha='center', va='top', rotation=90, labelpad=16)
# Speichere den Chart als Bilddatei
fig.set_size_inches(8, 4.8)
fig.savefig("charts/chart_blk.png", transparent=False, dpi=100)

def create_red_version(plt, normal_stairs, x, y_val, title, day_splitter, text_on_graphics):
  normal_stairs.set_color("white")
  plt.stairs(y_val_expensive, color="black", fill=True)
  mark_now(plt, y_val) # Mark actual 
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
  mark_now(plt, x, y_val) # Mark actual 
  plt.stairs(y_val_expensive, color="black", fill=True)

create_red_version(plt, normal_stairs, x, y_val, title, day_splitter, text_on_graphics)

fig.savefig("charts/chart_red.png", transparent=False, dpi=100)