from dearpygui.core import *
from dearpygui.simple import *
import numpy as np
from Table_API import *
from assembler_and_solver import *
import webbrowser

def run_checks_and_solve(sender, data):
    close_popup("Confirmation Window")
    clear_log(logger="log")
    clear_table("Results table")
    log_info("---- Solver initiated ----", logger="log")
    log_info("Running data checks...", logger="log")

    flag = 0

    elements = get_value("Number of elements")

    # -------Check material properties---------#
    E_val = np.zeros(elements)
    I_val = np.zeros(elements)
    L_val = np.zeros(elements)

    if get_value("same_mat"):  # solve for uniform

        try:
            E_val = np.full(elements, float(get_value("##material_table_0_1")))
            log_info("E values: OK", logger="log")
        except:
            log_error("Please enter a valid value for E in the Element No. 1 row.", logger="log")
            flag = 1
        try:
            I_val = np.full(elements, float(get_value("##material_table_0_2")))
            log_info("I values: OK", logger="log")
        except:
            log_error("Please enter a valid value for I in the Element No. 1 row.", logger="log")
            flag = 1

        try:
            L_val = np.zeros(elements)

            for i in range(elements):
                L_val[i] = float(get_value(f"##material_table_{i}_3"))

            log_info("L values: OK", logger="log")
        except:
            log_error("Please enter valid values for L.", logger="log")
            flag = 1

    else:  # solve for non-uniform
        try:
            for i in range(elements):
                E_val[i] = float(get_value(f"##material_table_{i}_1"))

            log_info("E values: OK", logger="log")
        except:
            log_error("Please enter valid values for E.", logger="log")
            flag = 1

        try:
            for i in range(elements):
                I_val[i] = float(get_value(f"##material_table_{i}_2"))

            log_info("I values: OK", logger="log")
        except:
            log_error("Please enter valid values for I.", logger="log")
            flag = 1

        try:
            for i in range(elements):
                L_val[i] = float(get_value(f"##material_table_{i}_3"))

            log_info("L values: OK", logger="log")
        except:
            log_error("Please enter valid values for L.", logger="log")
            flag = 1

    # -------------------------------------------------#

    # ----------Check displacement constraints---------#
    Q_val = np.zeros((elements + 1, 2))

    for i in range(elements + 1):

        d = get_value(f"##displacement_table_{i}_{1}")
        if not d:
            Q_val[i][0] = 1

        r = get_value(f"##displacement_table_{i}_{2}")
        if not r:
            Q_val[i][1] = 1

    if np.all(Q_val == 1):
        log_error("No displacement constraints found. Please select at least one.", logger="log")
        flag = 1

    else:
        log_info("Displacement constraints: OK", logger="log")

    # -------------------------------------------#

    # --------Check UDL Force----------------------#
    UDL_val = np.zeros(elements)

    try:
        for i in range(elements):
            if get_value(f"##UDL_table_{i}_1") == "":
                continue

            else:
                UDL_val[i] = float(get_value(f"##UDL_table_{i}_1"))

        log_info("UDL values: OK", logger="log")

    except:
        log_error("Please enter valid values for UDL.", logger="log")
        flag = 1

    # --------------------------------------------#
    # --------Check UVL Force----------------------#
    UVL_val = np.zeros(elements * 2)

    try:
        for i in range(elements * 2):

            if get_value(f"##UVL_table_{i}_2") == "":
                continue

            else:
                UVL_val[i] = float(get_value(f"##UVL_table_{i}_2"))

        log_info("UVL values: OK", logger="log")

    except:
        log_error("Please enter valid values for UVL.", logger="log")
        flag = 1

    # --------------------------------------------#
    # --------Check Point Force----------------------#
    point_force_val = np.zeros(elements + 1)

    try:
        for i in range(elements + 1):
            if get_value(f"##point_load_table_{i}_1") == "":
                continue

            else:
                point_force_val[i] = float(get_value(f"##point_load_table_{i}_1"))

        log_info("Point Force values: OK", logger="log")

    except:
        log_error("Please enter valid values for Point Forces.", logger="log")
        flag = 1

    # --------------------------------------------#
    # --------Check Moments----------------------#
    moment_val = np.zeros(elements + 1)

    try:
        for i in range(elements + 1):
            if get_value(f"##moment_table_{i}_1") == "":
                continue

            else:
                moment_val[i] = float(get_value(f"##moment_table_{i}_1"))

        log_info("Moment values: OK", logger="log")

    except:
        log_error("Please enter valid values for Moments.", logger="log")
        flag = 1

    # --------------------------------------------#
    if flag == 1:
        log_info("--- Solver terminated without a solution. Please resolve all errors. ---", logger="log")
        return 0

    else:
        log_info("All values have been checked and are valid.", logger="log")
        log_info("Solving...", logger="log")

        F_val, M_val = udl_vdl_point_force_solver(UDL_val, UVL_val, point_force_val, moment_val, L_val)

        element_data_val = np.zeros((elements, 4))
        temp_val = 1
        col_temp = 0
        for i in range(elements):
            for j in range(temp_val, temp_val + 4, 1):
                element_data_val[i][col_temp] = j
                col_temp += 1
            temp_val += 2
            col_temp = 0
        del temp_val, col_temp

        element_data_val = element_data_val.astype(int)

        try:
            F_M_result, Q_result = solve(element_data_val, E_val, I_val, L_val, Q_val, F_val, M_val)

            node = 1
            for i in range(0, len(F_M_result), 2):
                add_row("Results table",
                        [str(node), f"{F_M_result[i][0]:.5}", f"{F_M_result[i + 1][0]:.5}", f"{Q_result[i][0]:.5}",
                         f"{Q_result[i + 1][0]:.5}"])
                node += 1
            del node

            log_info("Solution has been calculated!", logger="log")
            log_info("---- Solver terminated ----", logger="log")

        except:
            log_error("An exception has occurred while solving. Please check the values entered and try again.",
                      logger="log")
            log_info("--- Solver terminated without a solution. ---", logger="log")


def generate_tables(sender, data):
    if get_value("Number of elements") < 1:
        log_warning("Number of elements cannot be less than 1!", logger="log")
        configure_item("Solve!", enabled=False, tip="Number of elements cannot be less than 1.")
        configure_item("Confirmation Window", show=False)

    else:
        configure_item("Solve!", enabled=True, tip="")
        configure_item("Confirmation Window", show=True)

    add_material_table()
    add_displacement_table()
    add_UDL_table()
    add_UVL_table()
    add_point_load_table()
    add_moment_table()


def add_material_table():
    if does_item_exist("2. Material properties"):
        delete_item("2. Material properties")

        with window("2. Material properties", x_pos=10, y_pos=90, no_resize=True, no_move=True, no_collapse=True,
                    no_close=True, width=450, height=237):
            add_spacing(count=2)
            add_checkbox("same_mat", label=" Material is uniform throughout",
                         tip="If the material is uniform throughout, entering the\nE and I values only in the Element "
                             "No. 1 row is enough.")
            add_spacing(count=2)
            mat_table = SmartTable("material_table")
            mat_table.add_header(
                ["Element No.", "Young's modulus (E)", "Area moment of inertia (I)", "Length of element (L)"])

            for i in range(get_value("Number of elements")):
                mat_table.add_row([str(i + 1), "", "", ""])


def add_displacement_table():
    if does_item_exist("Displacement constraints"):
        delete_item("Displacement constraints")

        add_tab("Displacement constraints", parent="BC Data")
        add_spacing(count=2)

        disp_table = SmartTable("displacement_table")
        disp_table.add_header(["Node No.", "Displacement Fixed", "Rotation Fixed"])

        for i in range(get_value("Number of elements") + 1):
            disp_table.add_row([str(i + 1), "C", ""])


def add_UDL_table():
    if does_item_exist("UDL"):
        delete_item("UDL")

        add_tab("UDL", parent="BC Data", tip="Add uniformly distributed loads on elements")
        add_spacing(count=2)
        udl_table = SmartTable("UDL_table")
        udl_table.add_header(["Element No.", "UDL Pressure value"])

        for i in range(get_value("Number of elements")):
            udl_table.add_row([str(i + 1), ""])


def add_UVL_table():
    if does_item_exist("UVL"):
        delete_item("UVL")

        add_tab("UVL", parent="BC Data", tip="Add uniformly varying loads.")
        add_spacing(count=2)
        uvl_table = SmartTable("UVL_table")
        uvl_table.add_header(["Element No.", "Node No.", "UVL Pressure value"])

        for i in range(get_value("Number of elements")):
            uvl_table.add_row([str(i + 1), "flag_1", str(i + 1)])
            uvl_table.add_row([str(i + 1), "flag_1", str(i + 2)])


def add_point_load_table():
    if does_item_exist("Point loads"):
        delete_item("Point loads")

        add_tab("Point loads", parent="BC Data")
        add_spacing(count=2)
        point_table = SmartTable("point_load_table")
        point_table.add_header(["Node No.", "Point force value"])

        for i in range(get_value("Number of elements") + 1):
            point_table.add_row([str(i + 1), ""])


def add_moment_table():
    if does_item_exist("Moments"):
        delete_item("Moments")

        add_tab("Moments", parent="BC Data")
        add_spacing(count=2)
        moment_table = SmartTable("moment_table")
        moment_table.add_header(["Node No.", "Moment value"])

        for i in range(get_value("Number of elements") + 1):
            moment_table.add_row([str(i + 1), ""])


def close_confirmation(sender, data):
    close_popup("Confirmation Window")


def close_info_window(sender, data):
    if sender == "OK":
        close_popup("Information window")

    else:
        close_popup("Information window")
        webbrowser.open("https://github.com/RahulShagri/1D-Beam-Element-2-DOF-FEM-Solver")


def switch_theme(sender, data):
    if sender == "dark_mode":

        delete_item("dark_mode")
        add_image_button("light_mode", "icons/light_mode.png", width=23, height=23, tip="Light mode", parent="Extras",
                         callback=switch_theme)

        set_theme("Grey")
        set_main_window_title("1D Beam Element 2 DOF FEM Solver")
        set_main_window_pos(x=0, y=0)
        set_main_window_size(width=1300, height=740)
        set_main_window_resizable(False)

        set_style_window_padding(4.00, 4.00)
        set_style_frame_padding(6.00, 4.00)
        set_style_item_spacing(6.00, 2.00)
        set_style_item_inner_spacing(4.00, 4.00)
        set_style_touch_extra_padding(0.00, 0.00)
        set_style_indent_spacing(21.00)
        set_style_scrollbar_size(12.00)
        set_style_grab_min_size(10.00)
        set_style_window_border_size(1.00)
        set_style_child_border_size(1.00)
        set_style_popup_border_size(1.00)
        set_style_frame_border_size(0.00)
        set_style_tab_border_size(0.00)
        set_style_window_rounding(4.00)
        set_style_child_rounding(4.00)
        set_style_frame_rounding(4.00)
        set_style_popup_rounding(4.00)
        set_style_scrollbar_rounding(4.00)
        set_style_grab_rounding(4.00)
        set_style_tab_rounding(4.00)
        set_style_window_title_align(0.50, 0.50)
        set_style_window_menu_button_position(mvDir_Left)
        set_style_color_button_position(mvDir_Right)
        set_style_button_text_align(0.50, 0.50)
        set_style_selectable_text_align(0.00, 0.00)
        set_style_display_safe_area_padding(3.00, 3.00)
        set_style_global_alpha(1.00)
        set_style_antialiased_lines(True)
        set_style_antialiased_fill(True)
        set_style_curve_tessellation_tolerance(1.25)
        set_style_circle_segment_max_error(1.60)

    else:
        delete_item("light_mode")
        add_image_button("dark_mode", "icons/dark_mode.png", width=23, height=23, tip="Dark mode", parent="Extras",
                         callback=switch_theme)

        set_theme("Light")
        set_main_window_title("1D Beam Element 2 DOF FEM Solver")
        set_main_window_pos(x=0, y=0)
        set_main_window_size(width=1300, height=740)
        set_main_window_resizable(False)

        set_style_window_padding(4.00, 4.00)
        set_style_frame_padding(6.00, 4.00)
        set_style_item_spacing(6.00, 2.00)
        set_style_item_inner_spacing(4.00, 4.00)
        set_style_touch_extra_padding(0.00, 0.00)
        set_style_indent_spacing(21.00)
        set_style_scrollbar_size(12.00)
        set_style_grab_min_size(10.00)
        set_style_window_border_size(1.00)
        set_style_child_border_size(1.00)
        set_style_popup_border_size(1.00)
        set_style_frame_border_size(0.00)
        set_style_tab_border_size(0.00)
        set_style_window_rounding(4.00)
        set_style_child_rounding(4.00)
        set_style_frame_rounding(4.00)
        set_style_popup_rounding(4.00)
        set_style_scrollbar_rounding(4.00)
        set_style_grab_rounding(4.00)
        set_style_tab_rounding(4.00)
        set_style_window_title_align(0.50, 0.50)
        set_style_window_menu_button_position(mvDir_Left)
        set_style_color_button_position(mvDir_Right)
        set_style_button_text_align(0.50, 0.50)
        set_style_selectable_text_align(0.00, 0.00)
        set_style_display_safe_area_padding(3.00, 3.00)
        set_style_global_alpha(1.00)
        set_style_antialiased_lines(True)
        set_style_antialiased_fill(True)
        set_style_curve_tessellation_tolerance(1.25)
        set_style_circle_segment_max_error(1.60)


with window("Main"):
    set_theme("Light")
    set_main_window_title("1D Beam Element 2 DOF FEM Solver")
    set_main_window_pos(x=0, y=0)
    set_main_window_size(width=1300, height=740)
    set_main_window_resizable(False)

    set_style_window_padding(4.00, 4.00)
    set_style_frame_padding(6.00, 4.00)
    set_style_item_spacing(6.00, 2.00)
    set_style_item_inner_spacing(4.00, 4.00)
    set_style_touch_extra_padding(0.00, 0.00)
    set_style_indent_spacing(21.00)
    set_style_scrollbar_size(12.00)
    set_style_grab_min_size(10.00)
    set_style_window_border_size(1.00)
    set_style_child_border_size(1.00)
    set_style_popup_border_size(1.00)
    set_style_frame_border_size(0.00)
    set_style_tab_border_size(0.00)
    set_style_window_rounding(4.00)
    set_style_child_rounding(4.00)
    set_style_frame_rounding(4.00)
    set_style_popup_rounding(4.00)
    set_style_scrollbar_rounding(4.00)
    set_style_grab_rounding(4.00)
    set_style_tab_rounding(4.00)
    set_style_window_title_align(0.50, 0.50)
    set_style_window_menu_button_position(mvDir_Left)
    set_style_color_button_position(mvDir_Right)
    set_style_button_text_align(0.50, 0.50)
    set_style_selectable_text_align(0.00, 0.00)
    set_style_display_safe_area_padding(3.00, 3.00)
    set_style_global_alpha(1.00)
    set_style_antialiased_lines(True)
    set_style_antialiased_fill(True)
    set_style_curve_tessellation_tolerance(1.25)
    set_style_circle_segment_max_error(1.60)

with window("1. Discretization", x_pos=10, y_pos=10, no_resize=True, no_move=True, no_collapse=True, no_close=True,
            width=450, height=70):
    add_spacing(count=2)
    add_input_int("Number of elements", default_value=1, callback=generate_tables,
                  tip="Number of elements should always be greater than or equal to 1.")

with window("2. Material properties", x_pos=10, y_pos=90, no_resize=True, no_move=True, no_collapse=True, no_close=True,
            width=450, height=237):
    add_spacing(count=2)
    add_checkbox("same_mat", label=" Material is uniform throughout",
                 tip="If the material is uniform throughout, entering the\nE and I values only in the Element No. 1 "
                     "row is enough.")
    add_spacing(count=2)
    mat_table = SmartTable("material_table")
    mat_table.add_header(["Element No.", "Young's modulus (E)", "Area moment of inertia (I)", "Length of element (L)"])

    for i in range(get_value("Number of elements")):
        mat_table.add_row([str(i + 1), "", "", ""])

with window("3. Boundary conditions", x_pos=10, y_pos=337, no_resize=True, no_move=True, no_collapse=True,
            no_close=True, width=450, height=237):
    add_spacing(count=2)
    add_tab_bar("BC Data")

    add_tab("Displacement constraints", parent="BC Data")
    add_spacing(count=2)

    disp_table = SmartTable("displacement_table")
    disp_table.add_header(["Node No.", "Displacement Fixed", "Rotation Fixed"])

    for i in range(get_value("Number of elements") + 1):
        disp_table.add_row([str(i + 1), "C", ""])

    add_tab("UDL", parent="BC Data", tip="Add uniformly distributed loads.")
    add_spacing(count=2)

    udl_table = SmartTable("UDL_table")
    udl_table.add_header(["Element No.", "UDL Pressure value"])

    for i in range(get_value("Number of elements")):
        udl_table.add_row([str(i + 1), ""])

    add_tab("UVL", parent="BC Data", tip="Add uniformly varying loads.")
    add_spacing(count=2)

    uvl_table = SmartTable("UVL_table")
    uvl_table.add_header(["Element No.", "Node No.", "UVL Pressure value"])

    for i in range(get_value("Number of elements")):
        uvl_table.add_row([str(i + 1), "flag_1", str(i + 1)])
        uvl_table.add_row([str(i + 1), "flag_1", str(i + 2)])

    add_tab("Point loads", parent="BC Data")
    add_spacing(count=2)

    point_table = SmartTable("point_load_table")
    point_table.add_header(["Node No.", "Point force value"])

    for i in range(get_value("Number of elements") + 1):
        point_table.add_row([str(i + 1), ""])

    add_tab("Moments", parent="BC Data")
    add_spacing(count=2)

    moment_table = SmartTable("moment_table")
    moment_table.add_header(["Node No.", "Moment value"])

    for i in range(get_value("Number of elements") + 1):
        moment_table.add_row([str(i + 1), ""])

with window("Diagram", x_pos=10, y_pos=584, no_resize=True, no_move=True, no_collapse=True, no_close=True, width=450,
            height=46, no_title_bar=True):
    add_button("Generate diagram", width=442, height=36, tip="Feature still in development.", enabled=False)

with window("Solve", x_pos=10, y_pos=640, no_resize=True, no_move=True, no_collapse=True, no_close=True, width=450,
            height=46, no_title_bar=True):
    add_button("Solve!", width=442, height=36)
    add_popup("Solve!", 'Confirmation Window', modal=True, mousebutton=mvMouseButton_Left)
    add_text("Are you sure you want to solve?")
    add_button("Yes", width=150, callback=run_checks_and_solve)
    add_same_line(spacing=10)
    add_button("No", width=150, callback=close_confirmation)

with window("Results", x_pos=470, y_pos=10, no_resize=True, no_move=True, no_collapse=True, no_close=True, width=755,
            height=361):
    add_table("Results table",
              ["Node No.", "Equivalent\nForce", "Equivalent\nMoment", "Displacement", "Rotation\n(radians)"], width=740,
              height=212)

with window("Logger", x_pos=470, y_pos=381, no_resize=True, no_move=True, no_collapse=True, no_close=True, width=805,
            height=305):
    add_logger("log", log_level=0, auto_scroll=True)
    log("Welcome to the 1D beam element 2 DOF FEM Solver!", logger="log")

with window("Extras", x_pos=1230, y_pos=10, no_resize=True, no_move=True, no_collapse=True, no_close=True, width=43,
            height=80, no_title_bar=True):
    add_image_button("Help", "icons/help.png", width=23, height=23, tip="Get more information on GitHub.")
    add_spacing()
    add_separator()
    add_spacing()
    add_image_button("dark_mode", "icons/dark_mode.png", width=23, height=23, tip="Dark mode", callback=switch_theme)

    add_popup("Help", "Information window", modal=True, mousebutton=mvMouseButton_Left)
    add_spacing(count=5)
    add_text("  ->  All forces acting downwards are -ve")
    add_spacing(count=2)
    add_text("  ->  All forces acting upwards are +ve.")
    add_spacing(count=2)
    add_separator()
    add_spacing(count=2)
    add_text("  ->  All moments acting clockwise are -ve")
    add_spacing(count=2)
    add_text("  ->  All moments acting anti-clockwise are +ve.")
    add_spacing(count=5)
    add_button("OK", width=100, callback=close_info_window)
    add_same_line(spacing=5)
    add_button("Get more info on GitHub", width=250, callback=close_info_window)
    add_spacing(count=2)

start_dearpygui(primary_window="Main")
