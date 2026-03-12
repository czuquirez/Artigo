import pathlib

import mealpy.swarm_based.GWO as GWO
import mealpy.swarm_based.PSO as PSO
from mealpy import FloatVar
from rdata import Rdata
from sim import Simulation
from sko.GA import GA
from tqdm import tqdm

fpath = pathlib.Path().resolve().parent.parent._str

# ******************************************************************************************************************

data_name = "L3FO5_gwo_10_40_2_res7"
modelo = "cgwo"
n_freq = 100
resolution = 7
wl_start = 10.0e-6
wl_stop = 40.0e-6
pop = 40
n_itr = 50
fun_obj = "fo5"


# ******************************************************************************************************************


# ----------------------------------------FUNÇÕES OBJETIVO -----------------------------------------------
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
    return data["integral"] / +2 * (data["int_90"])


# ----------------------------------------------------------------------------------------------------------

with open(
    f"{fpath}\\dev\\data_artigo\\diario.txt", "a"
) as f:  # Abre de novo (Agora certamente o arquivo existe e tem o eixo x na 1° linha)
    f.write(
        f"Nome: {data_name}, Resulucao: {resolution}, Banda: {wl_stop - wl_start}{(wl_start, wl_stop)}, nfreq: {n_freq}, Populacao: {pop}, Epocas: {n_itr}, função obj: {fun_obj}"
    )  # Adiciona os dados do teste rodado
    f.write("\n")  # Pula linha
    f.close()

rdados = Rdata()
save_path = (
    r"C:\Users\caioz\Desktop\IC\testes\treino.fsp"  # Path para salvar a simulação
)
data_path = f"C:\\Users\\caioz\\Desktop\\IC\\dev\\data\\{data_name}.json"
temp = r"C:\Users\caioz\Desktop\IC2\dev\data\ga_temp.json"
lum = Simulation()


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
        [0, "layer0", 0, h4, 0, 0, 0, 0, "Ni (Nickel) - Palik"],
        [0, "layer1", 1, h3, 0, 0, 0, 0, "SiO2 (Glass) - Palik"],
        [0, "layer2", 2, h2, 0, 0, 0, 0, "Si (Silicon) - Palik"],
        [1, "ring0", 3, h1, 0, 0, r, w, "Ni (Nickel) - Palik"],
        [1, "ring1", 3, h1, 0, 0, r2, w, "Ni (Nickel) - Palik"],
    ]


def setparams_teste(params, h4=0.2e-6):
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
        [2, "ring0", 3, h1, 0, 0, r, w, "Ti (Titanium) - Palik"],
        [2, "ring1", 3, h1, 0, 0, r2, w, "Ti (Titanium) - Palik"],
    ]


# ref = [1.5e-6,80e-9,0.55e-6,0.885246,40.0e-9,0.8e-6,2.5e-6]
ref = [0.9e-6, 55e-9, 0.36e-6, 0.885246, 20.0e-9, 0.4e-6, 1.28e-6]
lb = [0.35 * x for x in ref]
ub = [1.65 * x for x in ref]

lum.objects = setparams(ref)
lum.create(
    save_path, n_freq=n_freq, resolution=resolution, wl_start=wl_start, wl_stop=wl_stop
)
pbar = tqdm(total=pop * n_itr, desc="Testando estruturas")  # Barrinha de progresso


def run(params):
    lum.objects = setparams(params)
    lum.config()
    pbar.update(1)
    return lum.run(data_path)


problem = {
    "obj_func": fo5,
    "bounds": FloatVar(lb=lb, ub=ub),
    "minmax": "max",
    "log_to": f"C:\\Users\\caioz\\Desktop\\IC\\dev\\data\\{data_name}.json",
}

if modelo == "gwo":
    model = GWO.RW_GWO(epoch=n_itr, pop_size=pop)
    g_best = model.solve(problem)

elif modelo == "cgwo":
    model = GWO.ChaoticGWO(
        epoch=n_itr, pop_size=pop, chaotic_name="chebyshev", initial_chaotic_value=0.7
    )
    g_best = model.solve(problem)

elif modelo == "pso":
    model = PSO.P_PSO(epoch=n_itr, pop_size=pop)
    g_best = model.solve(problem)

elif modelo == "ga":
    ga = GA(
        func=fo3,
        n_dim=7,
        size_pop=pop,
        max_iter=n_itr,
        prob_mut=0.05,
        lb=lb,
        ub=ub,
        precision=1e-8,
    )
    best_x, best_y = ga.run()
