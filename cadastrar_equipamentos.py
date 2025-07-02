from pymongo import MongoClient

client = MongoClient("mongodb+srv://bibliotecaluizcarlos:FGVIlVhDcUDuQddG@cluster0.hth6xs5.mongodb.net/?retryWrites=true&w=majority")
db = client["controle_uso"]

# Limpa todos os equipamentos existentes
db.equipamentos.delete_many({})

# Dados dos equipamentos
equipamentos = {
    "Tablet": 40,
    "Chromebook": 35,
    "CPU": 24,
    "Netbook": 27
}

for nome, quantidade in equipamentos.items():
    for i in range(1, quantidade + 1):
        db.equipamentos.insert_one({
            "nome": nome,
            "numero": str(i)
        })

print("Equipamentos cadastrados com sucesso!")
