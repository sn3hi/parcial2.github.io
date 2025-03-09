from flask import Flask, render_template, request, jsonify
import numpy as np
import sympy as sp

app = Flask(__name__)

def lagrange_interpolation_piecewise(func, a, b):
    x = sp.symbols('x')  
    f = lambda x_val: eval(func, {'x': x_val, 'np': np})  

    points_per_segment = 5
    num_segments = 14
    segment_width = (b - a) / num_segments
    total_integral = 0

    if a == b:
        return None, "❌ Error: Los límites de integración son iguales, la integral es 0."

    try:
        x_plot = np.linspace(a, b, 1000).tolist()
        y_original = [f(xi) for xi in x_plot]
    except ZeroDivisionError:
        return None, "❌ Error: División por cero detectada en la función."

    interpolated_points = []

    for i in range(num_segments):
        seg_a = a + i * segment_width
        seg_b = seg_a + segment_width
        x_vals = np.linspace(seg_a, seg_b, points_per_segment).tolist()

        try:
            y_vals = [f(xi) for xi in x_vals]
            if any(np.isinf(y_vals)) or any(np.isnan(y_vals)):
                return None, "❌ Error: Se detectó una división por cero o un valor indefinido en la función."
        except ZeroDivisionError:
            return None, "❌ Error: División por cero detectada en la función."
        except ValueError as e:
            return None, f"❌ Error: {e}"

        interpolated_points.extend(zip(x_vals, y_vals))

        P = 0
        for j in range(points_per_segment):
            Li = 1
            for k in range(points_per_segment):
                if j != k:
                    Li *= (x - x_vals[k]) / (x_vals[j] - x_vals[k])
            P += y_vals[j] * Li

        P_simplified = sp.simplify(P)
        integral = sp.integrate(P_simplified, (x, seg_a, seg_b))
        total_integral += integral

    return {"x": x_plot, "y": y_original, "interpolated": interpolated_points}, f"✅ Integral total en [{a}, {b}]: {total_integral}"

@app.route("/", methods=["GET", "POST"])
def Home():
    return render_template("index.html", resultado=None, error=None)

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    func = data.get("funcion")
    a_str = data.get("a")
    b_str = data.get("b")

    if not a_str or not b_str:
        return jsonify({"error": "❌ Error: Debes ingresar ambos límites de integración."})

    try:
        a = sp.sympify(a_str, locals={'np': np})
        b = sp.sympify(b_str, locals={'np': np})
        graph_data, resultado = lagrange_interpolation_piecewise(func, float(a), float(b))
        if graph_data is None:
            return jsonify({"error": resultado})
        return jsonify({"graph": graph_data, "resultado": resultado})
    except Exception as e:
        return jsonify({"error": f"❌ Error en los límites de integración: {e}"})

if __name__ == "__main__":
    app.run(debug=True)


