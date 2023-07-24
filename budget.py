import plotly.graph_objects as go
import pandas as pd

# import tableau excel vers pandas.DataFrame
# sort pour format diagramme (pas de croisements)
revenue_data = pd.read_excel("chart.xlsx")
revenue_data = revenue_data.sort_values(by=revenue_data.columns.tolist()[-1])

# Liste de colonnes, préparation format pour ittération 2 par 2
amount_column = revenue_data.columns.tolist()[-1]
source_columns = revenue_data.columns.tolist()
del source_columns[-1] # Retrait de amount pour le source,target
del source_columns[-1]
target_columns = revenue_data.columns.tolist()
del target_columns[-1] # Retrait de amount pour le source,target
del target_columns[0]

def add_in_map(tuple,map,index):
    """
    tuple(tuple): values in tuple to add to dictionnary, if not exist
    map(dictionnary): dictionnary to add values into
    return(dictionnary) : 
    """
    value1,value2 = tuple
    if value1 not in map.keys():
        map[value1] = index
        index +=1
    if value2 not in map.keys():
        map[value2] = index
        index +=1
    return map,index

# Ittération 2 par 2 pour source > Target > amount dans le diagramme
index_map = {}
current_index = 0
source_list = []
target_list = []
value_list = []
for source,target in zip(source_columns,target_columns):
    sub_df = revenue_data[[source,target,amount_column]].copy()
    map = {(row[source],row[target]):
           sub_df[sub_df[[source,target]].isin([row[source],row[target]]).all(axis=1)][amount_column].sum() # ***
           for index,row in sub_df.iterrows()}
    for key,amount in map.items():
        index_map,current_index = add_in_map(key,index_map,current_index)
        source,target = key
        source_index, target_index = index_map[source],index_map[target]
        source_list.append(source_index)
        target_list.append(target_index)
        value_list.append(amount)
label_list = list(index_map.keys())
# *** : sub_df[pd.Series de boolean] va retourner sub_df pour les valeurs "True" de la boolean pd.Series.
#       Ici, la méthode "isin()" permet de retourner un boolean pd.Series si et seulement si les valeurs
#       se situe dans la liste en paramètre. on va donc avoir sub_df[sub_df[a,b].isin(liste).all(axis=1)]
#       pour a et b se situant de la liste "liste".

fig = go.Figure(data=[go.Sankey(
    valueformat = ".0f",
    node = dict(
      pad = 15,
      thickness = 15,
      line = dict(color = "black", width = 1),
      label = label_list,
      color = "blue"
    ),
    link = dict(
      source = source_list,
      target = target_list,
      value = value_list,
  ))])

fig.update_layout(title_text="Répartition Budget",
                  font_size=10)
fig.write_image(file ="Répartition Budget.png", format="png", width=1280, height=720, scale=2)