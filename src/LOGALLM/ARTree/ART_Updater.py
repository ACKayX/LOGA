import math


class ART_Updater:
    def __init__(self):
        self.threshold = 0.9
        self.updates = [
            self.calcul_a_1,
            self.calcul_a_2,
            self.calcul_a_3,
            self.calcul_a_4,
            self.calcul_a_5,
            self.calcul_a_6,
            self.calcul_a_7,
        ]
    def __getitem__(self, index):
        return self.updates[index]

    def update_status(self, conf):
        if conf > self.threshold:
            status = 2
        elif conf == self.threshold:
            status = 0
        elif conf < self.threshold:
            status = 1
            if conf < 0:
                conf = abs(conf)
        return conf, status


    def calcul_a_1(self,CA, CR, conf):
        conf = self.f_sigmoid(self.g_diff_card(CA, CR))
        return self.update_status(conf)


    def calcul_a_2(self,CA, CR, conf):
        conf = self.f_neg(self.g_max_diffval(CA, CR))
        return self.update_status(conf)

    def calcul_a_3(self,CA, CR, conf):
        conf = self.f_pos(self.g_diff_maxval(CA, CR))
        return self.update_status(conf)

    def calcul_a_4(self,CA, CR, conf):
        conf = self.f_sigmoid(self.g_diff_sum(CA, CR))
        return self.update_status(conf)

    def calcul_a_5(self,CA, CR, conf):
        conf = self.f_split(self.g_percentage(CA, CR))
        return self.update_status(conf)

    def calcul_a_6(self,CA, CR, conf):
        conf = -1
        return self.update_status(conf)

    def calcul_a_7(self, CA, CR, conf):
        A_sum = self.sum_poid_attak_relation(CA)
        C_sum = self.sum_poid_attak_relation(CR)
        the_sum = A_sum - C_sum

        new_conf = conf - the_sum
        return self.update_status(new_conf)

    
    def g_diff_card(self, CA, CR):
        return len(CA) - len(CR)

    def f_sigmoid(self, val):
        return (1 - math.exp(-val)) / (1 + math.exp(-val))

    def get_conf_list(self, nodes):
        # confs = [list(item.keys())[0].get_conf() for item in nodes] if nodes else [0]
        confs = [node.get_conf() for item in nodes for node in item.keys()] if nodes else [0]

        return confs

    def g_max_diffval(self, CA, CR):
        max = 0
        CA = self.get_conf_list(CA)
        CR = self.get_conf_list(CR)
        for i in CA:
            for j in CR:
                if i - j > max:
                    max = i-j
        return max

    def g_diff_maxval(self,CA, CR):
        CA = self.get_conf_list(CA)
        CR = self.get_conf_list(CR)
        return max(CA) - max(CR)

    def g_diff_sum(self, CA, CR):
        CA = self.get_conf_list(CA)
        CR = self.get_conf_list(CR)
        return sum(CA) - sum(CR)

    def g_percentage(self, CA, CR):
        CA = self.get_conf_list(CA)
        CR = self.get_conf_list(CR)
        return len(CA)/(len(CA) + len(CR))

    def f_neg(self, val):
        return -val

    def f_pos(self, val):
        return val
        
    def f_split(self, val):
        if val == 1:
            return -1
        else:
            return 1

    def sum_poid_attak_relation(self, nodes):
        the_sum = 0
        for i in nodes:
            for j in i:
                the_sum += j.get_conf() * i[j]
        return the_sum

