import numpy as np


def udl_vdl_point_force_solver(UDL, UVL, point_force, moments, L):

    elements = len(UDL)

    F = np.zeros(elements+1)
    M = np.zeros(elements+1)


    UVL = UVL.reshape(elements, 2)

    for i in range(elements):
        UDL_element = UDL[i]
        UVL_element = 0

        if UVL[i][0] == UVL[i][1]:
            UDL_element = UDL[i] + UVL[i][0]
            F[i] += (UDL_element * L[i]) / 2
            F[i+1] += (UDL_element * L[i]) / 2
            M[i] += (UDL_element * L[i] * L[i]) / 12
            M[i+1] += (-UDL_element * L[i] * L[i]) / 12

        elif UVL[i][0] < UVL[i][1]:
            UDL_element = UDL[i] + UVL[i][0]
            UVL_element = UVL[i][1] - UVL[i][0]

            F[i] += ((UDL_element * L[i]) / 2) + ((3 * UVL_element * L[i]) / 20)
            F[i + 1] += (UDL_element * L[i]) / 2 + ((7 * UVL_element * L[i]) / 20)
            M[i] += (UDL_element * L[i] * L[i]) / 12 + ((UVL_element * L[i] * L[i]) / 30)
            M[i + 1] += (-UDL_element * L[i] * L[i]) / 12 + ((-UVL_element * L[i] * L[i]) / 20)

        elif UVL[i][0] > UVL[i][1]:
            UDL_element = UDL[i] + UVL[i][1]
            UVL_element = UVL[i][0] - UVL[i][1]

            F[i] += ((UDL_element * L[i]) / 2) + ((7 * UVL_element * L[i]) / 20)
            F[i + 1] += (UDL_element * L[i]) / 2 + ((3 * UVL_element * L[i]) / 20)
            M[i] += (UDL_element * L[i] * L[i]) / 12 + ((UVL_element * L[i] * L[i]) / 20)
            M[i + 1] += (-UDL_element * L[i] * L[i]) / 12 + ((-UVL_element * L[i] * L[i]) / 30)

    F += point_force
    M += moments

    return F, M

def assemble_stiffness_matrix(element_keys, K, global_mat):
    a = 0
    b = 0

    for i in element_keys:

        b = 0

        for j in element_keys:
            global_mat[i - 1][j - 1] += K[a][b]

            b += 1

        a += 1

    return global_mat


def solve(element_data, E, I, L, Q, F, M):
    print("Solver initiated...")

    elements = element_data.shape[0]
    nodes = (elements + 1) * 2

    # Assembling the global force vector
    global_F = np.zeros((nodes, 1))

    j = 0

    for i in range(nodes):
        if i % 2 == 0:
            global_F[i] = F[j]
        else:
            global_F[i] = M[j]
            j += 1

    del j
    print("\nThe global force vector is")
    print(global_F)

    # Assembling the global stiffness matrix
    K_temp = np.array([])

    for e, i, l in zip(E, I, L):
        K_temp = np.append(K_temp, (e * i) / (l * l * l))

    global_K = np.zeros((nodes, nodes))

    for i in range(elements):
        K_element = np.array([[12, 6 * L[i], -12, 6 * L[i]],
                              [6 * L[i], 4 * L[i] * L[i], -6 * L[i], 2 * L[i] * L[i]],
                              [-12, -6 * L[i], 12, -6 * L[i]],
                              [6 * L[i], 2 * L[i] * L[i], -6 * L[i], 4 * L[i] * L[i]]])

        K_element = K_temp[i] * K_element

        global_K = assemble_stiffness_matrix(element_data[i], K_element, global_K)

        print("\nElement Stiffness matrix: " + str(i + 1))
        print(K_element)

    print("\nGlobal element stiffness matrix is ")
    print(global_K)

    global_Q = Q.reshape(nodes, 1).astype(float)

    X = np.where(global_Q != 1)
    rows = np.unique(X[0]).astype(int)

    for i in rows:
        for f in range(elements + 1):
            global_F[f] -= global_K[f][i] * float(global_Q[i])

    F_before_elimination = global_F
    global_F = np.delete(global_F, rows, 0)

    print("\nOn applying boundary conditions and using the elimination approach.")

    print("\nThe global force vector after elimination is:")
    print((global_F))

    global_K = np.delete(global_K, rows, 0)
    global_K = np.delete(global_K, rows, 1)

    print("\nThe global stiffness matrix after elimination is: ")
    print(global_K)

    unknown_disp = np.linalg.solve(global_K, global_F)

    i = 0

    for row in range(nodes):
        if row in rows:
            continue
        else:
            global_Q[row] = unknown_disp[i]
            i += 1

    del i

    print("\n The global displacement vector with all the known and unknown values is:")
    print(global_Q)

    print("Solver terminated.")

    return F_before_elimination, global_Q


#Test values


'''element_data_test = np.array([[1,2,3,4], [3,4,5,6]])
E_test = np.array(["210e9", "210e9"]).astype(float)     #Pa
I_test = np.array(["2e-6", "2e-6"]).astype(float)       #m^4
L_test = np.array(["1.5", "1"]).astype(float)             #m
Q_test = np.array([[0, 0], [1, 1], [0, 1]])
F_test = np.array(["-7.5e3", "-27.5e3", "0"]).astype(float)     #N
M_test = np.array(["-1.875e3", "1.875e3", "0"]).astype(float)     #N-m'''

'''element_data_test = np.array([[1, 2, 3, 4],
                              [3, 4, 5, 6]])
E_test = np.array([2.1e+11, 2.1e+11])     #Pa
I_test = np.array([2.e-06, 2.e-06])      #m^4
L_test = np.array([1.5, 1.])             #m
Q_test = np.array([[0., 0.],
                   [1., 1.],
                   [0., 1.]])
F_test = np.array([-7500., -27500., 0.])   #N
M_test = np.array([-1875., 1875., 0.])     #N-m

solve(element_data_test, E_test, I_test, L_test, Q_test, F_test, M_test)'''

'''UDL_test = np.array([12e3, 0])
UVL_test = np.array([0, 0, 12e3, 36e3])
point_force_test = np.array([0, 0, 0])
moments_test = np.array([0, -20e3, 0])
L_test = np.array([2, 3])
udl_vdl_point_force_solver(UDL_test, UVL_test, point_force_test, moments_test, L_test)'''
