import quantools as qt  

from rich import progress

ids_various = dict(
		 ser_capa = "001582081",
		 ser_capre = "001582085",
		 ser_dem = "001585791",
		 bat_jcc="001586918",
		 bat_epa = "001586921",
		 bat_tuc = "001586923",
		 bat_apre= "001586916",
		 bat_apa = "001586917",
		 CLIMAT_FR = "001565530",
		 HIPC_FO = "001759963",
		 HICP_IG = "001759966",
		 HICP_E = "001759967",
		 HICP = "001759968",
		 IPI_CZ = "010537946")

# ids_PIB = dict(PIB_comp="010548503", 
#             PIB_export ="010548514", 
#             PIB_import ="010548508",
#             PIB_conso_menage="010548515",
#             PIB_inv_menage="010548502"
# )

ids_various_2 = dict(Indice_loyers = "001515333", 
            chomage="001688526",
            prev_invest="001582996")


ids = {**ids_various, **ids_various_2}


insee_dl = qt.InseeDownloader()


with progress.Progress() as progress:
    task_id = progress.add_task("Downloading...", total=len(ids))
    for key, id in ids.items():
        series = insee_dl.get(id=id, save=True, filename=key)
        progress.update(task_id, advance=1)
        progress.log(f"Downloaded {key}")

