import json
import matplotlib.pyplot as plt
import os

class Rdata:
    def __init__(self):
        pass

    def read(self, data_name):
        res = []
        data = []
        with open(data_name, "r") as f:
            for line in f:
                data.append(json.loads(line))
            f.close()
        x = data[0]
        data.pop(0)
        k=2
        for element in data:
            sum_90 = [0]
            sum_98 = [0]
            int_90 = 0
            int_98 = 0
            integral = 0
            k1 = 0
            k2 = 0
            for i in range(len(element["Y"])):
                item = element["Y"][i]
                if i != 0:
                    integral += ((item + element["Y"][i - 1]) * (x[i - 1] - x[i])) * 0.5 * 1.0e6
                if item >= 0.9:
                    if i != 0:
                        if element['Y'][i - 1] > 0.9:
                            sum_90[k1] += 1
                        else:
                            sum_90.append(0)
                            k1 += 1
                            sum_90[k1] += 1
                        int_90 = int_90 + ((item + element["Y"][i - 1]) * (x[i - 1] - x[i])) * 0.5 * 1.0e6
                    if item >= 0.98:
                        if i != 0:
                            if element['Y'][i - 1] > 0.9:
                                sum_98[k2] += 1
                            else:
                                sum_98.append(0)
                                k2 += 1
                                sum_98[k2] += 1
                            int_98 = int_98 + ((item + element["Y"][i - 1]) * (x[i - 1] - x[i])) * 0.5 * 1.0e6
            if len(sum_90)>1:
                sum_90.pop(0)
            if len(sum_98)>1:
                sum_98.pop(0)
            res.append({"i": k, "params": element["params"], "sum_90": sum_90, "sum_98": sum_98,
                        "int_90": int_90, "int_98": int_98, "integral": integral, 'fo3': max(sum_90)+max(sum_98), 'fo4': 1.5*int_90 + int_98, "Y": element["Y"]})
            k+=1
        return res, x

    def show(self, data_path, order = '', index = -1, show=True):
        data, x = self.read(data_path)
        if index >-1:
            plt.plot(x, data[index-2]['Y'])
            plt.plot(x, [0.9] * len(x))
            plt.plot(x, [0.98] * len(x))
            plt.plot(x, [1] * len(x))
            plt.show()
            print(f'params: {data[index-2]['params']}')
            return None

        def sum_90(item):
            return max(item["sum_90"])
        def sum_98(item):
            return max(item["sum_98"])
        def int_90(item):
            return item["int_90"]
        def int_98(item):
            return item["int_98"]
        def integral(item):
            return item["integral"]
        def fo3(item):
            return item["fo3"]

        if order == 'sum_90':
            data.sort(key=sum_90, reverse=True)
        elif order == 'sum_98':
            data.sort(key=sum_98, reverse=True)
        elif order == 'int_90':
            data.sort(key=int_90, reverse=True)
        elif order == 'int_98':
            data.sort(key=int_98, reverse=True)
        elif order == 'integral':
            data.sort(key=integral, reverse=True)
        elif order == 'fo3':
            data.sort(key=fo3, reverse=True)
        best = 0
        for item in data:
            print(item['i'])
            if best == 0:
                best = item['i']
            if show:
                plt.plot(x, item['Y'])
                plt.plot(x, [0.9] * len(x))
                plt.plot(x, [0.98] * len(x))
                plt.plot(x, [1] * len(x))
                plt.show()
        return best

    def erase(self, data_path):
        if os.path.exists(data_path):
            os.remove(data_path)
            print("Apagado")
        else:
            print("Não existe")

    def analise(self,data_path, key='integral'):
        data, x = self.read(data_path)
        def sum_90(item):
            return max(item["sum_90"])
        def sum_98(item):
            return max(item["sum_98"])
        def int_90(item):
            return item["int_90"]
        def int_98(item):
            return item["int_98"]
        def integral(item):
            return item["integral"]
        def fo3(item):
            return item['fo3']
        def fo4(item):
            return item['fo4']
        if key == 'sum_90':
            data.sort(key=sum_90)
        elif key == 'sum_98':
            data.sort(key=sum_98)
        elif key == 'int_90':
            data.sort(key=int_90)
        elif key == 'int_98':
            data.sort(key=int_98)
        elif key == 'integral':
            data.sort(key=integral)
        elif key == 'fo3':
            data.sort(key=fo3)
        elif key == 'fo4':
            data.sort(key=fo4)
        for item in data:
            print(f'index: {item['i']}, {key}: {item[key]}')

    def teste(self, data_path):
        data = []
        with open(data_path, "r") as f:
            for line in f:
                data.append(json.loads(line))
            f.close()
        x = data[0]
        data.pop(0)
        i=2
        for element in data:
            print(f'tamanho x: {len(x)}, tamanho y: {len(element['Y'])} i: {i}')
            i+=1

    def get_params(self, data_name, index):
        data, x = self.read(data_name)
        return data[index-2]['params']

    def evolution(self, data_path, pop, key='integral'):
        data, x = self.read(data_path)
        vec = []
        if (key == 'sum_90') or (key == 'sum_98'):
            vec = [sum(data[i][key]) for i in range(len(data))]
        else:
            vec = [data[i][key] for i in range(len(data))]
        n = round(len(data)/pop)
        plt.scatter([z for z in range(n)], [max(vec[pop * (i-1):pop * i]) for i in range(1, n + 1)])
        plt.show()


    def convergence(self, data_path, pop, key='integral'):
        data, x = self.read(data_path)
        vec = []
        if (key == 'sum_90') or (key == 'sum_98'):
            vec = [sum(data[i][key]) for i in range(len(data))]
        else:
            vec = [data[i][key] for i in range(len(data))]
        max_lim = 1.1*max(vec)
        n = round(len(data) / pop)
        for z_inicio in range(1, n, 16):
            fig, axes = plt.subplots(4, 4, figsize=(12, 9))
            axes_flat = axes.flat
            for i in range(16):
                z = z_inicio + i
                ax = axes_flat[i]
                if z >= n:
                    ax.axis('off')
                    continue
                ax.set_title(f'{z}ª geracao')
                x_data = list(range(1, pop + 1))
                y_data = vec[pop * (z - 1): pop * z]
                ax.scatter(x_data, y_data)
                ax.set_xlabel('Indivíduo')
                ax.set_ylabel('Fitness')
                ax.set_ylim(0,max_lim)

            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            fig.suptitle(f'Gerações {z_inicio} a {z_inicio + 15}', fontsize=16)
            plt.show()
#        for z in range(1,n):
#            plt.title(f'{z}° geracao')
#            plt.scatter([i for i in range(1,pop+1)], vec[pop * (z - 1):pop * z])
#            plt.show()
        return 0