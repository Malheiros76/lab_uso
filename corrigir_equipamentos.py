from pymongo import MongoClient

client = MongoClient("mongodb+srv://bibliotecaluizcarlos:FGVIlVhDcUDuQddG@cluster0.hth6xs5.mongodb.net/?retryWrites=true&w=majority")
db = client["controle_uso"]

def corrigir_equipamentos():
    filtros = {
        "$or": [
            {"nome": {"$exists": False}},
            {"numero": {"$exists": False}},
            {"nome": ""},
            {"numero": ""}
        ]
    }
    docs_faltando = list(db.equipamentos.find(filtros))

    if not docs_faltando:
        print("Todos os documentos de equipamentos estão corretos.")
        return

    for doc in docs_faltando:
        atualizacoes = {}
        if not doc.get("nome"):
            atualizacoes["nome"] = "Equipamento desconhecido"
        if not doc.get("numero"):
            atualizacoes["numero"] = "?"
        if atualizacoes:
            db.equipamentos.update_one({"_id": doc["_id"]}, {"$set": atualizacoes})
            print(f"Corrigido documento {doc['_id']} com {atualizacoes}")

    print("Correção finalizada.")

corrigir_equipamentos()
