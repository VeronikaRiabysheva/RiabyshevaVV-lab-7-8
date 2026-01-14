from SPARQLWrapper import SPARQLWrapper, JSON, XML
import pandas as pd
from rdflib import Graph

# Настройка SPARQL endpoint
sparql = SPARQLWrapper("http://localhost:3030/pizza_ds/sparql")
sparql.setReturnFormat(JSON)

def run_query(query):
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        return results
    except Exception as e:
        print(f"Ошибка выполнения запроса: {e}")
        return None
    
query1 = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?class ?label WHERE {
    ?class a owl:Class .
    OPTIONAL { ?class rdfs:label ?label }
} ORDER BY ?class
"""
results1 = run_query(query1)
print("Классы онтологии:")
for result in results1["results"]["bindings"]:
    print(f"{result['class']['value']} - {result.get('label', {}).get('value', 'No label')}")

query2 = """
PREFIX pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?pizza ?name WHERE {
    ?pizza rdfs:subClassOf* pizza:Pizza .
    ?pizza rdfs:label ?name .
} ORDER BY ?name
"""
results2 = run_query(query2)
print("\nВсе пиццы:")
for result in results2["results"]["bindings"]:
    print(result['name']['value'])


#######################

query3 = """
PREFIX pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?pizza ?name ?topping WHERE {
    ?pizza rdfs:subClassOf* pizza:Pizza .
    ?pizza rdfs:label ?name .
    ?pizza rdfs:subClassOf ?restriction .
    ?restriction owl:onProperty pizza:hasTopping .
    ?restriction owl:someValuesFrom ?toppingClass .
    ?toppingClass rdfs:label ?topping .
    FILTER (CONTAINS(LCASE(?topping), "mushroom"))
}
"""
results3 = run_query(query3)
if results3 and results3["results"]["bindings"]:
    print("\nПиццы с грибами:")
    for result in results3["results"]["bindings"]:
        print(f"{result['name']['value']} - {result['topping']['value']}")
else:
    print("Нет результатов для запроса 3")

query4 = """
PREFIX pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?topping (COUNT(?pizza) AS ?count) WHERE {
    ?pizza rdfs:subClassOf* pizza:Pizza .
    ?pizza rdfs:subClassOf ?restriction .
    ?restriction owl:onProperty pizza:hasTopping .
    ?restriction owl:someValuesFrom ?toppingClass .
    ?toppingClass rdfs:label ?topping .
} GROUP BY ?topping ORDER BY DESC(?count) LIMIT 10
"""
results4 = run_query(query4)
if results4 and results4["results"]["bindings"]:
    print("\nПопулярные начинки:")
    for result in results4["results"]["bindings"]:
        print(f"{result['topping']['value']}: {result['count']['value']}")
else:
    print("Нет результатов для запроса 4")

########################

query5 = """
PREFIX pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ex: <http://example.org#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
CONSTRUCT {
  ?pizza ex:isVegetarian true .
  ?pizza ex:hasTopping ?topping .
} WHERE {
  ?pizza rdfs:subClassOf* pizza:Pizza .
  ?pizza rdfs:label ?name .
  ?pizza rdfs:subClassOf ?restriction .
  ?restriction owl:onProperty pizza:hasTopping .
  ?restriction owl:someValuesFrom ?toppingClass .
  ?toppingClass rdfs:label ?topping .
  FILTER NOT EXISTS {
    ?restriction2 owl:onProperty pizza:hasTopping .
    ?restriction2 owl:someValuesFrom ?meatClass .
    ?meatClass rdfs:subClassOf* pizza:MeatTopping .
    ?pizza rdfs:subClassOf ?restriction2 .
  }
}
"""
sparql.setReturnFormat(XML)
results5 = run_query(query5)
print("CONSTRUCT запрос выполнен")
if results5:
  with open("vegetarian_pizzas.rdf", "w") as f:
    f.write(results5.serialize(format="xml"))