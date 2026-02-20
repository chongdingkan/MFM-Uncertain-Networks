import networkx as nx
import random




def backtrack(prev, G_d4, edge_info):
    conns = [e for e in G_d4 if prev in e and G_d4[e] in ['*', '1']]
    if conns:
        return conns[0][1] if conns[0][0] == prev else conns[0][0]
    return prev


def f_a(state_dict, G_base, s, t, edge_info):
    G_temp = nx.DiGraph()
    for u, v in G_base.edges():
        state = state_dict.get((u, v))
        if state is None:
            state = state_dict.get((v, u))

        if state == '0':
            continue
        elif state == '2':
            G_temp.add_edge(u, v, capacity=BIG_CAPACITY)
            G_temp.add_edge(v, u, capacity=BIG_CAPACITY)
        else:
            real_cap = edge_info.get((u, v), edge_info.get((v, u)))['capacity']
            G_temp.add_edge(u, v, capacity=real_cap)
            G_temp.add_edge(v, u, capacity=real_cap)

    try:
        cut_val, _ = nx.minimum_cut(G_temp, s, t, capacity='capacity')
        return cut_val
    except:
        return 0


def RAN(G, edge_info, s, t, k, matrix, attack_log, observed_edges):
    G_d3 = {e: '*' for e in G.edges()}
    atk_idx = 0
    cost = 0
    while any(state in ['*', '1'] for state in G_d3.values()):
        targets = []
        if atk_idx < len(attack_log):
            for _ in range(k):
                if atk_idx < len(attack_log):
                    targets.append(attack_log[atk_idx])
                    atk_idx += 1
        for e in targets:
            if G_d3[e] == '*':
                G_d3[e] = '0' if e in observed_edges else '1'
            elif G_d3[e] == '2':
                G_d3[e] = '3'
        avail = [e for e, state in G_d3.items() if state in ['*', '1']]
        if avail:
            best = random.choice(avail)
            if G_d3[best] == '*':
                G_d3[best] = '2'
                cost += edge_info[best]['cost']
            elif G_d3[best] == '1':
                G_d3[best] = '0'
                cost += edge_info[best]['cost']
    return [e for e, state in G_d3.items() if state in ['2', '3'] and matrix.get(e, 0) == 1], cost


def GRE(G, edge_info, s, t, k, matrix, attack_log, observed_edges):
    G_d6 = {e: '*' for e in G.edges()}
    atk_idx = 0
    cost = 0
    while any(state in ['*', '1'] for state in G_d6.values()):
        targets = []
        if atk_idx < len(attack_log):
            for _ in range(k):
                if atk_idx < len(attack_log):
                    targets.append(attack_log[atk_idx])
                    atk_idx += 1
        for e in targets:
            if G_d6[e] == '*':
                G_d6[e] = '0' if e in observed_edges else '1'
            elif G_d6[e] == '2':
                continue
        avail = [e for e, state in G_d6.items() if state in ['*', '1']]
        if avail:
            best = max(avail,
                       key=lambda e: edge_info[e]['probability'] * edge_info[e]['capacity'] / edge_info[e]['cost'])
            if G_d6[best] == '*':
                G_d6[best] = '2'
                cost += edge_info[best]['cost']
            elif G_d6[best] == '1':
                G_d6[best] = '0'
                cost += edge_info[best]['cost']
    return [e for e, state in G_d6.items() if state == '2' and matrix.get(e, 0) == 1], cost


def HEU(G, edge_info, s, t, attack_log, k, matrix, observed_edges):
    G_d4 = {edge: '*' for e in G.edges()}
    atk_idx = 0
    total_cost = 0
    prev = s
    loop_count = 0
    max_loops = 5000
    while any(state in ['*', '1'] for state in G_d4.values()) and loop_count < max_loops:
        loop_count += 1
        targets = []
        if atk_idx < len(attack_log):
            for _ in range(k):
                if atk_idx < len(attack_log):
                    targets.append(attack_log[atk_idx])
                    atk_idx += 1
        for e in targets:
            if G_d4[e] == '*':
                G_d4[e] = '0' if e in observed_edges else '1'
        avail = [e for e, state in G_d4.items() if state in ['*', '1']]
        if avail:
            if any(t in e for e in avail):
                best = max([e for e in avail if t in e], key=lambda e: edge_info[e]['importance_d'])
                prev = best[0] if best[0] != prev else best[1]
            else:
                best = max(avail, key=lambda e: edge_info[e]['importance_b'])
                prev = best[0] if best[0] != prev else best[1]
            if G_d4[best] == '*':
                G_d4[best] = '2'
                total_cost += edge_info[best]['cost']
            elif G_d4[best] == '1':
                G_d4[best] = '0'
                total_cost += edge_info[best]['cost']
        else:
            bt = 0
            while prev != s :
                bt += 1
                new_prev = backtrack(prev, G_d4, edge_info)
                if new_prev == prev:
                    prev = s
                    break
                prev = new_prev
                avail = [e for e, state in G_d4.items() if state in ['*', '1']]
                if avail:
                    best = max(avail, key=lambda e: edge_info[e]['importance_b'])
                    if G_d4[best] == '*':
                        G_d4[best] = '2'
                        total_cost += edge_info[best]['cost']
                    elif G_d4[best] == '1':
                        G_d4[best] = '0'
                        total_cost += edge_info[best]['cost']
                    prev = best[0] if best[0] != prev else best[1]
                    break
            if prev == s and not avail:
                cands = [e for e, state in G_d4.items() if state in ['*', '1']]
                if cands:
                    best = max(cands, key=lambda e: edge_info[e]['importance_b'])
                    if G_d4[best] == '*':
                        G_d4[best] = '2'
                        total_cost += edge_info[best]['cost']
                    elif G_d4[best] == '1':
                        G_d4[best] = '0'
                        total_cost += edge_info[best]['cost']
                    prev = best[0] if best[0] != prev else best[1]
    return [e for e, state in G_d4.items() if state == '2' and matrix.get(e, 0) == 1], total_cost


def HPF(G, edge_info, s, t, k, matrix, attack_log, observed_edges):
    G_dp = {e: '*' for e in G.edges()}
    atk_idx = 0
    cost = 0
    while any(state in ['*', '1'] for state in G_dp.values()):
        targets = []
        if atk_idx < len(attack_log):
            for _ in range(k):
                if atk_idx < len(attack_log):
                    targets.append(attack_log[atk_idx])
                    atk_idx += 1
        for e in targets:
            if G_dp[e] == '*':
                G_dp[e] = '0' if e in observed_edges else '1'
            elif G_dp[e] == '2':
                continue
        avail = [e for e, state in G_dp.items() if state in ['*', '1']]
        if avail:
            best = max(avail, key=lambda e: edge_info[e]['probability'])
            if G_dp[best] == '*':
                G_dp[best] = '2'
                cost += edge_info[best]['cost']
            elif G_dp[best] == '1':
                G_dp[best] = '0'
                cost += edge_info[best]['cost']
    return [e for e, state in G_dp.items() if state == '2' and matrix.get(e, 0) == 1], cost


def DEG(G, edge_info, s, t, k, matrix, attack_log, observed_edges):
    G_dd = {e: '*' for e in G.edges()}
    atk_idx = 0
    cost = 0
    while any(state in ['*', '1'] for state in G_dd.values()):
        targets = []
        if atk_idx < len(attack_log):
            for _ in range(k):
                if atk_idx < len(attack_log):
                    targets.append(attack_log[atk_idx])
                    atk_idx += 1
        for e in targets:
            if G_dd[e] == '*':
                G_dd[e] = '0' if e in observed_edges else '1'
            elif G_dd[e] == '2':
                continue
        avail = [e for e, state in G_dd.items() if state in ['*', '1']]
        if avail:
            best = max(avail,
                       key=lambda e: (G.degree[e[0]] + G.degree[e[1]]) * edge_info[e]['probability'] * edge_info[e][
                           'capacity'] / edge_info[e]['cost'])
            if G_dd[best] == '*':
                G_dd[best] = '2'
                cost += edge_info[best]['cost']
            elif G_dd[best] == '1':
                G_dd[best] = '0'
                cost += edge_info[best]['cost']
    return [e for e, state in G_dd.items() if state == '2' and matrix.get(e, 0) == 1], cost


def ADP(G, edge_info, s, t, k, matrix, attack_log, observed_edges):
    G_d10 = {e: '*' for e in G.edges()}
    atk_idx = 0
    total_cost = 0

    while any(state in ['*', '1'] for state in G_d10.values()):
        targets = []
        if atk_idx < len(attack_log):
            for _ in range(k):
                if atk_idx < len(attack_log):
                    targets.append(attack_log[atk_idx])
                    atk_idx += 1

        for e in targets:
            if G_d10[e] == '*':
                new_state = '0' if e in observed_edges else '1'
                G_d10[e] = new_state
            elif G_d10[e] == '2':
                continue

        avail = [e for e, state in G_d10.items() if state in ['*', '1']]

        if avail:
            f_a_s = f_a(G_d10, G, s, t, edge_info)

            best_u = float('-inf')
            best_edge = None

            for e in avail:
                p_e = edge_info[e]['probability']
                c_e = max(edge_info[e]['cost'], 1e-5)

                state_s_dot_e = G_d10.copy()
                state_s_dot_e[e] = '2'
                f_a_s_dot_e = f_a(state_s_dot_e, G, s, t, edge_info)

                state_s_minus_e = G_d10.copy()
                state_s_minus_e[e] = '0'
                f_a_s_minus_e = f_a(state_s_minus_e, G, s, t, edge_info)

                gain = p_e * f_a_s_dot_e + (1 - p_e) * f_a_s_minus_e - f_a_s
                util = gain / c_e

                if util > best_u + 1e-9:
                    best_u = util
                    best_edge = e
                elif abs(util - best_u) < 1e-9:
                    if edge_info[e]['capacity'] > (edge_info[best_edge]['capacity'] if best_edge else -1):
                        best_edge = e

            if best_edge:
                if G_d10[best_edge] == '*':
                    G_d10[best_edge] = '2'
                    total_cost += edge_info[best_edge]['cost']
                elif G_d10[best_edge] == '1':
                    G_d10[best_edge] = '0'
                    total_cost += edge_info[best_edge]['cost']

    sel = [e for e, state in G_d10.items() if state == '2' and matrix.get(e, 0) == 1]
    return sel, total_cost