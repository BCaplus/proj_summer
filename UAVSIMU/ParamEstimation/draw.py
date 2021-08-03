n = [0 for i in range(shape[1])]
n_group_fit = [[0,0,0] for i in range(shape[1])]
map = xlrd.open_workbook("Engine map.xlsx")
sh = map.sheet_by_name("Sheet2")
group_counter = 0
group_header = 2
temp_P = [0 for i in range(shape[0])]
temp_C = [0 for i in range(shape[0])]
lower_P_bound = [20 for i in range(shape[0])]
upper_P_bound = [0 for i in range(shape[0])]
while group_counter<shape[1]:
    n[group_counter] = sh.row_values(row)[0]
    for row in range(group_header, group_header+shape[0]):
        if sh.row_values(row)[1] < lower_P_bound[group_counter]:
            lower_P_bound[group_counter] = sh.row_values(row)[1]
        if sh.row_values(row)[1] > upper_P_bound[group_counter]:
            upper_P_bound[group_counter] = sh.row_values(row)[1]
        temp_P[row - group_header] = sh.row_values(row)[1]
        temp_C[row - group_header] = sh.row_values(row)[2]
        n_group_fit[group_counter] = np.polyfit(temp_P, temp_C, 2)