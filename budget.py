import plotly.graph_objects as go
import pandas as pd

# import tableau excel vers pandas.DataFrame
# sort pour format diagramme (pas de croisements)
revenue_data = pd.read_excel("chart.xlsx")
revenue_data = revenue_data.sort_values(by=revenue_data.columns.tolist()[-1])

# Liste de colonnes, préparation format pour ittération 2 par 2
amount_column = revenue_data.columns.tolist()[-1]
source_columns = revenue_data.columns.tolist()
del source_columns[-1]  # Retrait de amount pour le source,target
del source_columns[-1]
target_columns = revenue_data.columns.tolist()
del target_columns[-1]  # Retrait de amount pour le source,target
del target_columns[0]


def add_in_map(new_values, weights, dictionnary):
    """
    :param new_values: values in tuple to add to dictionnary, if not exist
    :param weights: weights for each nodes, to update or assign
    :param dictionnary: dictionnary to add values into
    return: updated dictionnary
    """
    source_value, target_value = new_values
    source_weight, target_weight = weights
    if not dictionnary:
        dictionnary = {source_value: {"weight": source_weight, "index": 0},
                       target_value: {"weight": target_weight, "index": 1}}
        return dictionnary, 0, 1
    else:
        max_index = 0
        for key, item in dictionnary.items():
            index = item["index"]
            if index >= max_index:
                max_index = index+1
        if source_value in dictionnary:
            s_index = dictionnary[source_value]["index"]
        else:
            dictionnary[source_value] = {"weight": source_weight, "index": max_index}
            s_index = dictionnary[source_value]["index"]
            max_index += 1
        if target_value in dictionnary:
            dictionnary[target_value]["weight"] += source_weight
            t_index = dictionnary[target_value]["index"]
        else:
            dictionnary[target_value] = {"weight": target_weight, "index": max_index}
            t_index = dictionnary[target_value]["index"]
            max_index += 1
        return dictionnary, s_index, t_index


# Ittération 2 par 2 pour source > Target > amount dans le diagramme
branch_map = {}
current_index = 0
source_list = []
target_list = []
value_list = []
for source, target in zip(source_columns, target_columns):
    sub_df = revenue_data[[source, target, amount_column]].drop_duplicates(subset=[source, target]).copy()
    graph_path = {(row[source], row[target]): (revenue_data[revenue_data[source] == row[source]][amount_column].sum(),
                                               revenue_data[revenue_data[[source, target]].isin([row[source], row[target]]).
                                               all(axis=1)][amount_column].sum())  # ***
                  for index, row in sub_df.iterrows()}
    for branch, amounts in graph_path.items():
        total_amount, local_amount = amounts
        source, target = branch
        branch_map, source_index, target_index = add_in_map(branch, amounts, branch_map)

        source_list.append(source_index)
        target_list.append(target_index)
        value_list.append(local_amount)
label_list = [f"{key} : {item['weight']}€" for key, item in branch_map.items()]
# *** : sub_df[pd.Series de boolean] va retourner sub_df pour les valeurs "True" de la boolean pd.Series.
#       Ici, la méthode "isin()" permet de retourner un boolean pd.Series si et seulement si les valeurs
#       se situe dans la liste en paramètre. on va donc avoir sub_df[sub_df[a,b].isin(liste).all(axis=1)]
#       pour a et b se situant de la liste "liste".

fig = go.Figure(data=[go.Sankey(
    valueformat=".0f",
    node=dict(
      pad=15,
      thickness=15,
      line=dict(color="black", width = 1),
      label=label_list,
      color="blue"
    ),
    link=dict(
      source=source_list,
      target=target_list,
      value=value_list,
  ))])

fig.update_layout(title_text="Répartition Budget",
                  font_size=10)
fig.write_image(file="Répartition Budget.png", format="png", width=1280, height=720, scale=2)
