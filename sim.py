#                       IMPORTS
import importlib.util
import json
import os

import numpy as np

#                       DEFINE A CLASSE


class Simulation:
    #                   PASSANDO O ENDEREÇO DA API DO LUMERICAL

    def __init__(self):
        os.add_dll_directory(
            "C:\\Program Files\\Lumerical\\v202\\api\\python"
        )  # Para evitar um erro ao chamar a API (não sei se precisa mesmo)
        self.lumapi = importlib.util.spec_from_file_location(
            "lumapi", "C:\\Program Files\\Lumerical\\v202\\api\\python\\lumapi.py"
        ).loader.load_module()  # Carrega a API, localizada nesse path ai (pode ser diferente para cada computador)
        self.objects = []
        self.p = 0.9e-6

    def create(
        self, save_path, n_freq=300, resolution=8, wl_start=10.0e-6, wl_stop=30.0e-6
    ):  # Função que cria a simulação e a estrutura inicial
        #                   CRIANDO A SIMULAÇÃO "sim"

        # self.fdtd_sim = self.lumapi.FDTD()
        # sim = self.fdtd_sim
        self.sim = self.lumapi.FDTD()  # Cria um ambiente de simulação FDTD
        self.sim.save(save_path)  # Salva a simulação nesse path ai

        # n_freq = 300.0  Número de frequências (resolução da simulação quanto maior melhor e mais demorado)
        # resolution = 8  Resolução da simulação quanto maior melhor e mais demorado
        # wl_start = 10.0e-6 Comprimento de onda inicial da luz
        # wl_stop = 30.0e-6 Comprimento de onda final da luz

        #                   CONFIGURANDO A SIMULAÇÃO

        self.sim.addfdtd()  # Cria o espaço de simulação
        self.sim.set("dimension", "3D")  # Define a simulação para 3D
        self.sim.set("mesh accuracy", resolution)  # Define a resolução da simulação
        self.sim.set(
            "mesh refinement", "conformal variant 1"
        )  # Define esse paremetro para conformal variant 1 (aparentemente isso é bom pra metal)
        self.sim.set("x min bc", "Periodic")  # Define x como periodico
        self.sim.set("Y min bc", "Periodic")  # Define y como periodico

        for obj in self.objects:
            tipo, nome, obj_layer, obj_h, x, y, r, w, material = obj
            if tipo == 0:
                self.sim.addrect()  # Adiciona um retângulo e define os parametros dele
                self.sim.set("name", nome)
            elif tipo == 1:
                self.sim.addring()  # Adiciona um retângulo e define os parametros dele
                self.sim.set("name", nome)
            elif tipo == 2:
                self.sim.addrect()
                self.sim.set("name", f"{nome}0")
                self.sim.addrect()
                self.sim.set("name", f"{nome}1")
                self.sim.addrect()
                self.sim.set("name", f"{nome}2")
                self.sim.addrect()
                self.sim.set("name", f"{nome}3")

        self.sim.addplane()  # Adiociona uma fonte de luz e deine os parametros dela

        self.sim.set("name", "light")
        self.sim.set("direction", "Backward")
        self.sim.set("wavelength start", wl_start)
        self.sim.set("wavelength stop", wl_stop)

        self.sim.addpower()  # Adiociona o monitor de potência e define os parametros dele

        self.sim.set("name", "reflected")
        self.sim.set("monitor type", "2D Z-normal")

        self.sim.addpower()

        self.sim.set("name", "transmited")
        self.sim.set("monitor type", "2D Z-normal")

        self.sim.setglobalmonitor(
            "frequency points", n_freq
        )  # Faz parte da resolução da simulação

    def config(self):  # Configuras os parametros para os novos passados nesse metodo

        # [ tipo, nome, layer, h, x, y, r/l, w, material]
        #    0     1      2    3  4  5  6  7
        if not self.sim.layoutmode():
            self.sim.switchtolayout()
        h = 0
        last_h = 0
        layer = -1
        for obj in self.objects:
            tipo, nome, obj_layer, obj_h, x, y, r, w, material = obj
            if obj_layer == layer:
                h -= last_h
            if tipo == 0:
                self.sim.select(nome)
                self.sim.set("x", x)
                self.sim.set("x span", self.p)
                self.sim.set("y", y)
                self.sim.set("y span", self.p)
                self.sim.set("z", h + 0.5 * obj_h)
                self.sim.set("z span", obj_h)
                self.sim.set("material", material)
            elif tipo == 1:
                self.sim.select(nome)
                self.sim.set("x", x)
                self.sim.set("y", y)
                self.sim.set("z", h + 0.5 * obj_h)
                self.sim.set("z span", obj_h)
                self.sim.set("inner radius", r - w)
                self.sim.set("outer radius", r)
                self.sim.set("material", material)
            elif tipo == 2:
                # ************************************************************
                self.sim.select(f"{nome}0")
                self.sim.set("x", (r - 0.5 * w))
                self.sim.set("y", y)
                self.sim.set("x span", w)
                self.sim.set("y span", 2 * r)

                self.sim.set("material", material)
                self.sim.set("z", h + 0.5 * obj_h)
                self.sim.set("z span", obj_h)

                # ****************************************************

                self.sim.select(f"{nome}1")
                self.sim.set("x", -(r - 0.5 * w))
                self.sim.set("y", y)
                self.sim.set("x span", w)
                self.sim.set("y span", 2 * r)

                self.sim.set("material", material)
                self.sim.set("z", h + 0.5 * obj_h)
                self.sim.set("z span", obj_h)

                # ************************************************************
                self.sim.select(f"{nome}2")
                self.sim.set("x", x)
                self.sim.set("y", (r - 0.5 * w))
                self.sim.set("x span", 2 * r)
                self.sim.set("y span", w)

                self.sim.set("material", material)
                self.sim.set("z", h + 0.5 * obj_h)
                self.sim.set("z span", obj_h)

                # ****************************************************

                self.sim.select(f"{nome}3")
                self.sim.set("x", x)
                self.sim.set("y", -(r - 0.5 * w))
                self.sim.set("x span", 2 * r)
                self.sim.set("y span", w)
                self.sim.set("material", material)
                self.sim.set("z", h + 0.5 * obj_h)
                self.sim.set("z span", obj_h)

            last_h = obj_h
            h += last_h
            layer = obj_layer

        Z_sim = h + 4000e-9  # Tamanho em z do espaço de simulação

        self.sim.switchtolayout()

        self.sim.select("FDTD")
        self.sim.set("x", 0.0)
        self.sim.set("x span", self.p)
        self.sim.set("y", 0.0)
        self.sim.set("y span", self.p)
        self.sim.set("z", 0.5 * Z_sim - 1500e-9)
        self.sim.set("z span", Z_sim)

        self.sim.select("light")
        self.sim.set("x", 0.0)
        self.sim.set("x span", self.p)
        self.sim.set("y", 0.0)
        self.sim.set("y span", self.p)
        self.sim.set("z", (h + 500e-9))

        self.sim.select("reflected")
        self.sim.set("x", 0.0)
        self.sim.set("x span", self.p)
        self.sim.set("y", 0.0)
        self.sim.set("y span", self.p)
        self.sim.set("z", (h + 800e-9))

        self.sim.select("transmited")
        self.sim.set("x", 0.0)
        self.sim.set("x span", self.p)
        self.sim.set("y", 0.0)
        self.sim.set("y span", self.p)
        self.sim.set("z", -200e-9)

    def run(self, data_name):  # Roda a simulação
        #           RODANDO

        self.sim.run()  # Metodo da API para rodar a simulação

        #           ANALISANDO OS RESULTADOS

        reflected = self.sim.getresult(
            "reflected", "T"
        )  # Resultado de quanto foi refletido

        r_lambda = reflected["lambda"]  # Lista de comprimentos de onda da luz
        r_lambda = r_lambda[:, 0]
        r_T = reflected["T"]  # Lista com a refletancia em cada ponto

        transmited = self.sim.getresult(
            "transmited", "T"
        )  # Resultado de quanto foi transmitido

        t_T = transmited["T"]  # Lista com a transmissão em cada ponto
        absorved = 1 - (r_T + t_T)  # Absorção:  A = 1 - R - T

        data = {  # Dicionario com os dados para salvar em um dataset.json
            "params": [self.p, self.objects],
            "Y": np.ndarray.tolist(
                absorved
            ),  # Pontos de absorção (porém o lumerical devolve os dados em array do numpy ent tem que transformar em lista)
        }
        x = r_lambda
        b_70 = 0
        sum_90 = [0]
        sum_98 = [0]
        int_90 = 0
        int_98 = 0
        integral = 0
        k1 = 0
        k2 = 0
        for i in range(len(data["Y"])):
            item = data["Y"][i]
            if i != 0:
                integral += (
                    ((item + data["Y"][i - 1]) * (x[i - 1] - x[i])) * 0.5 * 1.0e6
                )
            if item <= 0.7:
                b_70 += 1
            elif item >= 0.9:
                if i != 0:
                    if data["Y"][i - 1] > 0.9:
                        sum_90[k1] += 1
                    else:
                        sum_90.append(0)
                        k1 += 1
                        sum_90[k1] += 1
                    int_90 = (
                        int_90
                        + ((item + data["Y"][i - 1]) * (x[i - 1] - x[i])) * 0.5 * 1.0e6
                    )
                if item >= 0.98:
                    if i != 0:
                        if data["Y"][i - 1] > 0.9:
                            sum_98[k2] += 1
                        else:
                            sum_98.append(0)
                            k2 += 1
                            sum_98[k2] += 1
                        int_98 = (
                            int_98
                            + ((item + data["Y"][i - 1]) * (x[i - 1] - x[i]))
                            * 0.5
                            * 1.0e6
                        )

        ans = {
            "b_70": b_70,
            "sum_90": sum_90,
            "sum_98": sum_98,
            "int_90": int_90,
            "int_98": int_98,
            "integral": integral,
        }

        with open(data_name, "a") as f:  # Abre o arquivo de dados
            if (
                os.stat(data_name).st_size == 0
            ):  # Testa se o arquivo do dataset esta vazio
                json.dump(
                    np.ndarray.tolist(r_lambda), f
                )  # E então cria o vetor de comprimentos de onda (eixo x)
                f.write("\n")  # Pula para proxima linha
            f.close()  # Fecha o arquivo

        with (
            open(data_name, "a") as f
        ):  # Abre de novo (Agora certamente o arquivo existe e tem o eixo x na 1° linha)
            json.dump(data, f)  # Adiciona os dados do teste rodado
            f.write("\n")  # Pula linha
            f.close()  # Fecha o arquivo

        return ans
        # Retorna os dados
        # Retirar o lambda e integral dos dados, salvar parametros como lista
