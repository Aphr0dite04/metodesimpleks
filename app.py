from flask import Flask, render_template, request
import numpy as np
import pandas as pd

app = Flask(__name__)

def simplex_method(tableau, basis):
    steps = []

    def capture_tableau(message, pivot_info=None):
        """Capture tableau at each step with explanation of pivot."""
        df = pd.DataFrame(tableau, columns=["A", "B", "s1", "s2", "Z", "RHS"])
        df.index = basis
        step_data = {"message": message, "table": df.to_html(classes="table table-bordered")}

        if pivot_info:
            step_data["pivot_info"] = pivot_info
        steps.append(step_data)

    # Capture the initial tableau
    capture_tableau("Tabel Awal Simpleks")

    while True:
        # Menentukan kolom pivot (nilai negatif terbesar di baris Z)
        pivot_col = np.argmin(tableau[-1, :-1])  # Kolom dengan nilai Z terkecil
        if tableau[-1, pivot_col] >= 0:
            break  # Jika semua nilai di baris Z >= 0, solusi optimal tercapai

        pivot_col_value = tableau[-1, pivot_col]
        pivot_col_info = f"Kolom pivot dipilih adalah kolom {['A', 'B', 's1', 's2'][pivot_col]} dengan nilai Z = {pivot_col_value:.2f}"

        # Menentukan baris pivot menggunakan rasio
        ratios = []
        for row in range(len(tableau) - 1):
            if tableau[row, pivot_col] > 0:
                ratios.append(tableau[row, -1] / tableau[row, pivot_col])
            else:
                ratios.append(np.inf)
        pivot_row = np.argmin(ratios)

        pivot_row_value = tableau[pivot_row, pivot_col]
        pivot_row_info = f"Baris pivot dipilih adalah baris {basis[pivot_row]} dengan rasio minimum = {ratios[pivot_row]:.2f}"

        # Normalisasi baris pivot
        tableau[pivot_row, :] /= pivot_row_value

        # Eliminasi kolom pivot di baris lain
        for row in range(len(tableau)):
            if row != pivot_row:
                tableau[row, :] -= tableau[row, pivot_col] * tableau[pivot_row, :]

        # Update basis
        old_basis = basis[pivot_row]
        basis[pivot_row] = ["A", "B", "s1", "s2"][pivot_col]

        # Capture tableau after iteration
        capture_tableau(
            f"Iterasi dengan Pivot: Kolom ({basis[pivot_row]}) dan Baris ({old_basis})",
            pivot_info={
                "pivot_col_info": pivot_col_info,
                "pivot_row_info": pivot_row_info,
            },
        )

    # Return the steps and final results
    result = {
        "A": tableau[0, -1],
        "B": tableau[1, -1],
        "Z": tableau[-1, -1],
    }
    return steps, result


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        num_constraints = int(request.form["num_constraints"])
        num_variables = int(request.form["num_variables"])

        tableau = []
        for i in range(num_constraints + 1):
            row = list(map(float, request.form.getlist(f"row_{i}")))
            tableau.append(row)

        tableau = np.array(tableau, dtype=float)

        basis = [f"s{i + 1}" for i in range(num_constraints)] + ["Z"]
        steps, result = simplex_method(tableau, basis)

        return render_template("result.html", steps=steps, result=result)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
