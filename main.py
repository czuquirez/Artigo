# Importações ***************************************
import json
import pathlib
import time
from datetime import timedelta

import mealpy.swarm_based.GWO as GWO
import mealpy.swarm_based.PSO as PSO
from mealpy import FloatVar
from tqdm import tqdm

from sim import Simulation

# Importações ***************************************


# Funções objetivo **********************************
def fo1(solution):
    data = run(solution)
    return max(data["sum_90"])


def fo2(solution):
    data = run(solution)
    return (max(data["sum_90"]) ** 2) - (2 * data["b_70"])


def fo3(solution):
    data = run(solution)
    return max(data["sum_90"]) + max(data["sum_98"])


def fo4(solution):
    data = run(solution)
    return 1.5 * data["int_90"] + data["int_98"]


def fo5(solution):
    data = run(solution)
    return data["integral"] + 2 * (data["int_90"])


def fo6(solution):
    data = run(solution)
    return sum(data["sum_90"]) + sum(data["sum_98"]) - data["b_70"]


def fo7(solution):
    data = run(solution)
    return sum(data["sum_90"]) + sum(data["sum_98"]) - 0.5 * data["b_70"]


def simular(solution):
    return sim(solution)


# Funções objetivo **********************************


# Funções auxiliares ********************************
def setparams(params, h4=0.2e-6):
    p, w, r, epsilon_r, h1, h2, h3 = params
    lum.p = p
    if r > p * 0.5:
        r = p * 0.5
    r2 = (r - w) * epsilon_r
    if r2 - w <= 0:
        r2 = w + 10e-9
    #               [tipo, nome, layer, h, x, y, r, w, material]
    return [
        [0, "layer0", 0, h4, 0, 0, 0, 0, "Ti (Titanium) - Palik"],
        [0, "layer1", 1, h3, 0, 0, 0, 0, "SiO2 (Glass) - Palik"],
        [0, "layer2", 2, h2, 0, 0, 0, 0, "Si (Silicon) - Palik"],
        [1, "ring0", 3, h1, 0, 0, r, w, "Ti (Titanium) - Palik"],
        [1, "ring1", 3, h1, 0, 0, r2, w, "Ti (Titanium) - Palik"],
    ]


def run(params):
    lum.objects = setparams(params)
    lum.config()
    pbar.update(1)
    return lum.run(data_path)


def sim(params):
    lum.objects = setparams(params)
    lum.config()
    pbar.update()
    # input()
    return 0.0


# Funções auxiliares ********************************

# Le a fila de simulações
fpath = pathlib.Path().resolve()._str
with open(fpath + "\\fila.json", "r") as f:
    fila = json.load(f)
    f.close()

# Referência os limites inferiores e superiores para o otimizador
# Valores de referência tirados do artigo do Chen
ref = [
    0.9e-6,
    55e-9,
    0.36e-6,
    0.885246,
    20.0e-9,
    0.4e-6,
    1.28e-6,
]
lb = [0.35 * x for x in ref]
ub = [1.65 * x for x in ref]

save_path = f"{fpath}\\saves\\save.fsp"  # Path para salvar a simulação
lum = Simulation()

# Loop principal percorrendo a fila

for item in fila["fila"]:
    (
        data_name,
        modelo,
        resolution,
        wl_start,
        wl_stop,
        n_freq,
        pop,
        n_itr,
        fun_obj_str,
    ) = item.values()
    fun_obj = eval(f"{fun_obj_str}")
    data_path = f"{fpath}\\data\\{data_name}.json"
    with (
        open(f"{fpath}\\data\\diario_teste.txt", "a") as f
    ):  # Abre de novo (Agora certamente o arquivo existe e tem o eixo x na 1° linha)
        f.write(
            f"Nome: {data_name}, modelo: {modelo}, Resulucao: {resolution}, Banda: {wl_stop - wl_start}{(wl_start, wl_stop)}, nfreq: {n_freq}, Populacao: {pop}, Epocas: {n_itr}, função obj: {fun_obj_str}, lb: {lb}, ub: {ub}"
        )  # Adiciona os dados do teste rodado
        # f.write("\n")  # Pula linha
        f.close()

    # Marca o tempo de início
    inicio = time.perf_counter()

    lum.objects = setparams(ref)
    lum.create(
        save_path,
        n_freq=n_freq,
        resolution=resolution,
        wl_start=wl_start,
        wl_stop=wl_stop,
    )
    pbar = tqdm(total=pop * n_itr, desc="Otimizando...")  # Barrinha de progresso

    problem = {
        "obj_func": fun_obj,
        "bounds": FloatVar(lb=lb, ub=ub, name="oi"),
        "minmax": "max",
        "log_to": f"{fpath}\\data\\{data_name}.json",
    }

    if modelo == "gwo":
        model = GWO.ChaoticGWO(
            epoch=n_itr,
            pop_size=pop,
            chaotic_name="chebyshev",
            initial_chaotic_value=0.7,
        )
        g_best = model.solve(problem)

    elif modelo == "pso":
        model = PSO.P_PSO(epoch=n_itr, pop_size=pop)
        g_best = model.solve(problem)

    fim = time.perf_counter()
    tempo_total_segundos = fim - inicio
    tempo_formatado = str(timedelta(seconds=int(tempo_total_segundos)))

    with (
        open(f"{fpath}\\data\\diario.txt", "a") as f
    ):  # Abre de novo (Agora certamente o arquivo existe e tem o eixo x na 1° linha)
        f.write(f" tempo: {tempo_formatado}")  # Adiciona os dados do teste rodado
        f.write("\n")  # Pula linha
        f.close()
