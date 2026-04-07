import pathlib

import mealpy.swarm_based.GWO as GWO
import mealpy.swarm_based.PSO as PSO
from mealpy import FloatVar
from tqdm import tqdm

from sim import Simulation

fpath = pathlib.Path().resolve()._str


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
    return data["integral"] + 2 * (data["int_90"])


def simular(solution):
    return sim(solution)


# ----------------------------------------------------------------------------------------------------------

# ******************************************************************************************************************

data_name = "L1FO5_pso_10_40_1_res7"
modelo = "pso"  # cgwo ou pso
n_freq = 150
resolution = 7
wl_start = 10.0e-6
wl_stop = 40.0e-6
pop = 40
n_itr = 50
fun_obj = fo5
fun_obj_str = "fo5"


# ******************************************************************************************************************

ref = [
    0.9e-6,
    55e-9,
    0.36e-6,
    0.885246,
    20.0e-9,
    0.4e-6,
    1.28e-6,
]  # Parametros do Artigo do Chen
lb = [0.35 * x for x in ref]
ub = [1.65 * x for x in ref]

with open(
    f"{fpath}\\data\\diario_teste.txt", "a"
) as f:  # Abre de novo (Agora certamente o arquivo existe e tem o eixo x na 1° linha)
    f.write(
        f"Nome: {data_name}, Resulucao: {resolution}, Banda: {wl_stop - wl_start}{(wl_start, wl_stop)}, nfreq: {n_freq}, Populacao: {pop}, Epocas: {n_itr}, função obj: {fun_obj_str}, lb: {lb}, ub: {ub}"
    )  # Adiciona os dados do teste rodado
    f.write("\n")  # Pula linha
    f.close()

save_path = f"{fpath}\\saves\\save.fsp"  # Path para salvar a simulação
data_path = f"{fpath}\\data\\{data_name}.json"
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
        [0, "layer0", 0, h4, 0, 0, 0, 0, "Ti (Titanium) - Palik"],
        [0, "layer1", 1, h3, 0, 0, 0, 0, "SiO2 (Glass) - Palik"],
        [0, "layer2", 2, h2, 0, 0, 0, 0, "Si (Silicon) - Palik"],
        [1, "ring0", 3, h1, 0, 0, r, w, "Ti (Titanium) - Palik"],
        [1, "ring1", 3, h1, 0, 0, r2, w, "Ti (Titanium) - Palik"],
    ]


lum.objects = setparams(ref)
lum.create(
    save_path, n_freq=n_freq, resolution=resolution, wl_start=wl_start, wl_stop=wl_stop
)
pbar = tqdm(total=pop * n_itr, desc="Otimizando...")  # Barrinha de progresso


def run(params):
    lum.objects = setparams(params)
    lum.config()
    pbar.update(1)
    return lum.run(data_path)


def sim(params):
    lum.objects = setparams(params)
    lum.config()
    pbar.update()
    input()
    return 0.0


problem = {
    "obj_func": fun_obj,
    "bounds": FloatVar(lb=lb, ub=ub, name="oi"),
    "minmax": "max",
    "log_to": f"{fpath}\\data\\{data_name}.json",
}

if modelo == "cgwo":
    model = GWO.ChaoticGWO(
        epoch=n_itr, pop_size=pop, chaotic_name="chebyshev", initial_chaotic_value=0.7
    )
    g_best = model.solve(problem)

elif modelo == "pso":
    model = PSO.P_PSO(epoch=n_itr, pop_size=pop)
    g_best = model.solve(problem)
